from flask import Flask, request, jsonify, send_file, render_template
from invoice_generator import generate_invoice
from io import BytesIO
import traceback

app = Flask(__name__)

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


@app.route('/generate_invoice', methods=['POST'])
def generate_invoice_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        validate_invoice_data(data)

        pdf_buffer = generate_invoice(data)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='invoice.pdf'
        )
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/form', methods=['GET', 'POST'])
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
            pdf_buffer = generate_invoice(data)
            return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name='invoice.pdf')
        except Exception as e:
            print(traceback.format_exc())
            return jsonify({"error": str(e)}), 400

    return render_template('form.html')

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Invoice Generator API!"})

if __name__ == '__main__':
    app.run(debug=True)