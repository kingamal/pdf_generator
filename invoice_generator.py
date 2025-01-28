from fpdf import FPDF
from io import BytesIO

def calculate_totals(items, tax_rate):
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax
    return subtotal, tax, total

def generate_invoice(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        _add_business_info(pdf, data['business_name'], data['business_address'])
        _add_customer_info(pdf, data['customer_name'], data['customer_address'])
        _add_items_table(pdf, data['items'], data['tax_rate'])
        _add_totals(pdf, data['items'], data['tax_rate'])
        
        pdf_buffer = BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)
        return pdf_buffer
    except Exception as e:
        print(f"Error generating invoice: {e}")
        raise

def _add_business_info(pdf, business_name, business_address):
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, business_name, ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, business_address, ln=True)
    pdf.ln(10)

def _add_customer_info(pdf, customer_name, customer_address):
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Invoice To:', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, customer_name, ln=True)
    pdf.cell(0, 10, customer_address, ln=True)
    pdf.ln(10)

def _add_items_table(pdf, items, tax_rate):
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(80, 10, 'Description', border=1)
    pdf.cell(30, 10, 'Quantity', border=1, align='C')
    pdf.cell(40, 10, 'Unit Price', border=1, align='C')
    pdf.cell(40, 10, 'Total', border=1, align='C')
    pdf.ln(10)

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

def _add_totals(pdf, items, tax_rate):
    subtotal, tax, total = calculate_totals(items, tax_rate)

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