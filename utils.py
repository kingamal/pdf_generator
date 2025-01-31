import os

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

def save_pdf_to_file(pdf_buffer, filename, invoices_directory):
    filepath = os.path.join(invoices_directory, filename)
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    return filepath