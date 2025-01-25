from flask import Flask, request, jsonify, send_file, render_template
from invoice_generator import generate_invoice
from io import BytesIO

app = Flask(__name__)

@app.route('/generate_invoice', methods=['POST'])
def generate_invoice_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        pdf_buffer = generate_invoice(data)
        return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='invoice.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/form', methods=['GET', 'POST'])
def invoice_form():
    if request.method == 'POST':
        try:
            data = {
                "business_name": request.form['business_name'],
                "business_address": request.form['business_address'],
                "customer_name": request.form['customer_name'],
                "customer_address": request.form['customer_address'],
                "items": [
                    {"description": request.form['item1_desc'], "quantity": int(request.form['item1_qty']), "unit_price": float(request.form['item1_price'])},
                    {"description": request.form['item2_desc'], "quantity": int(request.form['item2_qty']), "unit_price": float(request.form['item2_price'])}
                ],
                "tax_rate": float(request.form['tax_rate'])
            }

            pdf_buffer = generate_invoice(data)
            return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='invoice.pdf')
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    return render_template('form.html')

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Invoice Generator API!"})

if __name__ == '__main__':
    app.run(debug=True)