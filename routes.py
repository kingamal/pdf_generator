from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import db, User, Business, Invoice
from invoice_generator import generate_invoice
from utils import validate_invoice_data, save_pdf_to_file
import uuid
import logging
import os

logger = logging.getLogger(__name__)

def create_routes(app):
    invoices_directory = 'invoices'
    if not os.path.exists(invoices_directory):
        os.makedirs(invoices_directory)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                login_user(user)
                return redirect(url_for('user_panel'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/form', methods=['GET', 'POST'])
    @login_required
    def invoice_form():
        businesses = Business.query.all()
        if request.method == 'POST':
            try:
                items = []
                for key, value in request.form.items():
                    if key.startswith('item') and '_desc' in key:
                        index = key.split('_')[0][4:]
                        items.append({
                            "description": request.form[f"item{index}_desc"],
                            "quantity": int(request.form.get(f"item{index}_qty", 0)),
                            "unit_price": float(request.form.get(f"item{index}_price", 0.0))
                        })

                business_id = request.form['business_id']
                business = Business.query.get(business_id)

                data = {
                    "business_name": business.name,
                    "business_address": business.address,
                    "customer_name": request.form['customer_name'],
                    "customer_address": request.form['customer_address'],
                    "items": items,
                    "tax_rate": float(request.form['tax_rate'])
                }

                validate_invoice_data(data)

                pdf_buffer = generate_invoice(data)
                pdf_buffer.seek(0)

                unique_filename = f"{uuid.uuid4()}.pdf"
                filepath = save_pdf_to_file(pdf_buffer, unique_filename, invoices_directory)

                invoice = Invoice(user_id=current_user.id, filename=unique_filename, data=str(data))
                db.session.add(invoice)
                db.session.commit()

                return send_file(filepath, mimetype='application/pdf', as_attachment=True, download_name=unique_filename)
            except ValueError as ve:
                logger.warning(f"Validation error: {ve}")
                return jsonify({"error": str(ve)}), 400
            except Exception as e:
                logger.error(f"Error generating invoice: {e}")
                return jsonify({"error": str(e)}), 400

        return render_template('form.html', businesses=businesses)

    @app.route('/invoices')
    @login_required
    def invoices():
        user_invoices = Invoice.query.filter_by(user_id=current_user.id).all()
        return render_template('invoices.html', invoices=user_invoices)

    @app.route('/get_invoice/<filename>', methods=['GET'])
    @login_required
    def get_saved_invoice(filename):
        try:
            filepath = os.path.join(invoices_directory, filename)
            if not os.path.exists(filepath):
                return jsonify({"error": "Invoice not found"}), 404
            return send_file(filepath, mimetype='application/pdf')
        except Exception as e:
            logger.error(f"Error retrieving invoice: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('user_panel'))
        return render_template('home.html')

    @app.route('/user_panel')
    @login_required
    def user_panel():
        return render_template('user_panel.html')

    @app.route('/businesses', methods=['GET', 'POST'])
    @login_required
    def manage_businesses():
        if request.method == 'POST':
            name = request.form['name']
            address = request.form['address']
            business = Business(name=name, address=address)
            db.session.add(business)
            db.session.commit()
            flash('Business added successfully!', 'success')
            return redirect(url_for('manage_businesses'))
        businesses = Business.query.all()
        return render_template('businesses.html', businesses=businesses)