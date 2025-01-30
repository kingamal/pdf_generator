from flask import Flask, request, jsonify, send_file, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from invoice_generator import generate_invoice
from io import BytesIO
import traceback
import os
import uuid
import logging
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

invoices_directory = 'invoices'
if not os.path.exists(invoices_directory):
    os.makedirs(invoices_directory)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(150), nullable=False)
    data = db.Column(db.Text, nullable=False)

def validate_invoice_data(data):
    required_fields = ['business_name', 'business_address', 'customer_name', 'customer_address', 'items', 'tax_rate']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    if not isinstance(data['items'], list) or not data['items']:
        raise ValueError("Items must be a non-empty list")
    for item in data['items']:
        if not all(key in item for key in ['description', 'quantity', 'unit_price']):
            raise ValueError("Each item must contain 'description', 'quantity', and 'unit_price'")

def save_pdf_to_file(pdf_buffer, filename):
    filepath = os.path.join(invoices_directory, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    return filepath

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('invoice_form'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

            data = {
                "business_name": request.form['business_name'],
                "business_address": request.form['business_address'],
                "customer_name": request.form['customer_name'],
                "customer_address": request.form['customer_address'],
                "items": items,
                "tax_rate": float(request.form['tax_rate'])
            }

            validate_invoice_data(data)

            pdf_buffer = generate_invoice(data)
            pdf_buffer.seek(0)

            unique_filename = f"{uuid.uuid4()}.pdf"
            filepath = save_pdf_to_file(pdf_buffer, unique_filename)

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

    return render_template('form.html')

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
    return jsonify({"message": "Welcome to the Invoice Generator API!"})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)