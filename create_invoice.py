import json
from fpdf import FPDF

def calculate_totals(items, tax_rate):
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax
    return subtotal, tax, total

def generate_invoice(data, output_filename):
    # Extract data
    business_name = data['business_name']
    business_address = data['business_address']
    customer_name = data['customer_name']
    customer_address = data['customer_address']
    items = data['items']
    tax_rate = data['tax_rate']

    # Calculate totals
    subtotal, tax, total = calculate_totals(items, tax_rate)

    # Create PDF instance
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)

    # Business Info
    pdf.cell(0, 10, business_name, ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, business_address, ln=True)
    pdf.ln(10)

    # Customer Info
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Invoice To:', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, customer_name, ln=True)
    pdf.cell(0, 10, customer_address, ln=True)
    pdf.ln(10)

    # Table Header
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 10, 'Description', border=1)
    pdf.cell(30, 10, 'Quantity', border=1, align='C')
    pdf.cell(40, 10, 'Unit Price', border=1, align='C')
    pdf.cell(40, 10, 'Total', border=1, align='C')
    pdf.ln(10)

    # Table Content
    pdf.set_font('Arial', '', 12)
    for item in items:
        description = item['description']
        quantity = item['quantity']
        unit_price = item['unit_price']
        total_price = quantity * unit_price

        pdf.cell(80, 10, description, border=1)
        pdf.cell(30, 10, str(quantity), border=1, align='C')
        pdf.cell(40, 10, f"${unit_price:.2f}", border=1, align='C')
        pdf.cell(40, 10, f"${total_price:.2f}", border=1, align='C')
        pdf.ln(10)

    # Totals
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 10, 'Subtotal:', align='R')
    pdf.cell(40, 10, f"${subtotal:.2f}", align='C')
    pdf.ln(10)
    pdf.cell(150, 10, 'Tax:', align='R')
    pdf.cell(40, 10, f"${tax:.2f}", align='C')
    pdf.ln(10)
    pdf.cell(150, 10, 'Total:', align='R')
    pdf.cell(40, 10, f"${total:.2f}", align='C')

    # Save PDF
    pdf.output(output_filename)
    print(f"Invoice saved as {output_filename}")

if __name__ == "__main__":
    # Load JSON data
    input_filename = "invoice_data.json"
    output_filename = "invoice.pdf"

    with open(input_filename, 'r') as f:
        data = json.load(f)

    # Generate Invoice
    generate_invoice(data, output_filename)