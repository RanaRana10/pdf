from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import uuid

# Register a font that supports the ₹ symbol (ensure 'fonts.ttf' is available)
pdfmetrics.registerFont(TTFont('CustomFont', 'fonts.ttf'))

# Define the Invoice class to handle all invoice data and calculations
class Invoice:
    def __init__(self, shop_details, customer_details, items, tax_rate=0.1):
        self.shop_details = shop_details
        self.customer_details = customer_details
        self.items = items
        self.tax_rate = tax_rate
        self.invoice_number = self.generate_invoice_number()
        self.invoice_date = self.generate_timestamp()
        self.due_date = self.invoice_date  # Due date same as invoice date
        self.calculated_items = self.calculate_items()
        self.subtotal = sum(item['amount'] for item in self.calculated_items)
        self.tax = self.subtotal * self.tax_rate
        self.total = self.subtotal + self.tax

    def generate_invoice_number(self):
        unique_id = str(uuid.uuid4())
        return f"YOUR/INV/24-25/001-{unique_id}"

    def generate_timestamp(self):
        return datetime.now().strftime("%d/%m/%Y %I:%M %p")

    def calculate_items(self):
        calculated = []
        for i, item in enumerate(self.items, start=1):
            quantity = item.get('quantity', 1)
            rate = item.get('rate', 0)
            amount = quantity * rate
            calculated.append({
                'sl_no': str(i),
                'particulars': item['particulars'],
                'hsn': item['hsn'],
                'quantity': str(quantity),
                'rate': rate,
                'amount': amount
            })
        return calculated

# Define invoice data directly in code
shop_details = {
    'name': 'Your Shop Name',
    'address': 'Your Shop Address',
    'gstin': 'Your GSTIN',
    'pan': 'Your PAN',
    'email': 'your@email.com'
}

customer_details = {
    'name': 'Customer Name',
    'address': 'Customer Address'
}

items = [
    {'particulars': 'Item 1', 'hsn': 'HSN1', 'quantity': 2, 'rate': 100},
    {'particulars': 'Item 2', 'hsn': 'HSN2', 'quantity': 1, 'rate': 200}
]

# Create an instance of the Invoice class
invoice = Invoice(shop_details, customer_details, items)

# Generate a timestamp for the filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"invoice_{timestamp}.pdf"

# Create the PDF
doc = SimpleDocTemplate(filename, pagesize=letter)
styles = getSampleStyleSheet()
elements = []

# Page dimensions
page_width, page_height = letter

# Add logo (ensure 'logo.png' is in the working directory)
logo = Image('logo.png', width=page_width * 0.25, height=page_height * 0.15)
logo.hAlign = 'RIGHT'
elements.append(logo)

# Header: Shop Details
elements.append(Paragraph("TAX INVOICE", styles['Heading2']))
elements.append(Paragraph("ORIGINAL FOR RECIPIENT", styles['Normal']))
elements.append(Paragraph(invoice.shop_details['name'], styles['Heading1']))
elements.append(Paragraph(invoice.shop_details['address'], styles['Normal']))
elements.append(Paragraph(f"GSTIN: {invoice.shop_details['gstin']}", styles['Normal']))
elements.append(Paragraph(f"PAN Number: {invoice.shop_details['pan']}", styles['Normal']))
elements.append(Paragraph(f"Email: {invoice.shop_details['email']}", styles['Normal']))
elements.append(Spacer(1, 12))

# Invoice Details
inv_table = [
    ["Invoice Number:", invoice.invoice_number],
    ["Invoice Date:", invoice.invoice_date],
    ["Due Date:", invoice.due_date]
]
inv_layout = Table(inv_table, colWidths=[100, 200])
inv_layout.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
elements.append(inv_layout)
elements.append(Spacer(1, 12))

# Customer Details
elements.append(Paragraph("SHIP TO", styles['Heading2']))
elements.append(Paragraph(invoice.customer_details['name'], styles['Normal']))
elements.append(Paragraph(invoice.customer_details['address'], styles['Normal']))
elements.append(Spacer(1, 12))

# Itemized List
table_data = [['SL No', 'Particulars', 'HSN', 'Quantity', 'Rate', 'Amount']]
for item in invoice.calculated_items:
    table_data.append([
        item['sl_no'],
        item['particulars'],
        item['hsn'],
        item['quantity'],
        f"₹{item['rate']:.2f}",
        f"₹{item['amount']:.2f}"
    ])
table = Table(table_data, colWidths=[50, 150, 80, 50, 50, 60])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTNAME', (0, 1), (-1, -1), 'CustomFont')
]))
elements.append(table)
elements.append(Spacer(1, 12))

# Totals
totals_table = [
    ["Subtotal:", f"₹ {invoice.subtotal:.2f}"],
    ["Tax:", f"₹ {invoice.tax:.2f}"],
    ["Total:", f"₹ {invoice.total:.2f}"]
]
totals_layout = Table(totals_table, colWidths=[100, 100])
totals_layout.setStyle(TableStyle([
    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
    ('FONTNAME', (0, 0), (-1, -1), 'CustomFont'),
    ('FONTSIZE', (0, 0), (-1, -1), 12),
    ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0, 255, 0))  # Matches original
]))
elements.append(totals_layout)

# Build the PDF
doc.build(elements)
print(f"Invoice generated as '{filename}'!") 