from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing
from datetime import datetime
import uuid

# Register a font that supports the ₹ symbol (ensure 'fonts.ttf' is available)
pdfmetrics.registerFont(TTFont('CustomFont', 'fonts.ttf'))

# Define background color for the entire page
background_color = colors.lightgrey  # Can be changed (e.g., colors.white, colors.Color(0.9, 0.9, 0.9))

# Class to represent a single item
class Item:
    def __init__(self, particulars, hsn, quantity, rate):
        self.particulars = particulars
        self.hsn = hsn
        self.quantity = quantity if quantity > 0 else 1  # Ensure positive quantity
        self.rate = rate if rate >= 0 else 0  # Ensure non-negative rate
        self.amount = self.quantity * self.rate

    def get_table_row(self, sl_no):
        """Return data formatted for the PDF table."""
        return [
            str(sl_no),
            self.particulars,
            self.hsn,
            str(self.quantity),
            f"₹{self.rate:.2f}",
            f"₹{self.amount:.2f}"
        ]

# Class to manage the entire invoice
class Invoice:
    def __init__(self, shop_details, customer_details, tax_rate=0.1):
        self.shop_details = shop_details
        self.customer_details = customer_details
        self.tax_rate = tax_rate
        self.items = []
        self.invoice_number = self.generate_invoice_number()
        self.invoice_date = self.generate_timestamp()
        self.due_date = self.invoice_date
        self.subtotal = 0
        self.tax = 0
        self.total = 0

    def generate_invoice_number(self):
        unique_id = str(uuid.uuid4())
        return f"YOUR/INV/24-25/001-{unique_id}"

    def generate_timestamp(self):
        return datetime.now().strftime("%d/%m/%Y %I:%M %p")

    def add_item(self, particulars, hsn, quantity, rate):
        """Add a new item to the invoice and recalculate totals."""
        item = Item(particulars, hsn, quantity, rate)
        self.items.append(item)
        self.calculate_totals()

    def calculate_totals(self):
        """Calculate subtotal, tax, and total based on items."""
        self.subtotal = sum(item.amount for item in self.items)
        self.tax = self.subtotal * self.tax_rate
        self.total = self.subtotal + self.tax

# Define invoice data
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

# Create invoice instance
invoice = Invoice(shop_details, customer_details)

# Add items using the class method (equivalent to the provided list)
invoice.add_item(particulars='Item 1', hsn='HSN1', quantity=2, rate=100)
invoice.add_item(particulars='Item 2', hsn='HSN2', quantity=1, rate=200)

# Generate filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"invoice_{timestamp}.pdf"

# Function to draw background color
def draw_background(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(background_color)
    canvas.rect(0, 0, letter[0], letter[1], fill=1)
    canvas.restoreState()

# Create the PDF with background color
doc = SimpleDocTemplate(filename, pagesize=letter, onPage=draw_background)
styles = getSampleStyleSheet()
elements = []

# Page dimensions
page_width, page_height = letter

# Add logo (ensure 'logo.png' exists)
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
for i, item in enumerate(invoice.items, start=1):
    table_data.append(item.get_table_row(i))
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
    ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0, 255, 0))
]))
elements.append(totals_layout)

# Build the PDF
doc.build(elements)
print(f"Invoice generated as '{filename}'!")