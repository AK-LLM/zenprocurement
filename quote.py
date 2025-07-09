from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime

def generate_quote_pdf(product_name: str, quantity: int):
    """
    Generates a PDF quote with basic product and quantity information.
    Saves the PDF as 'quote.pdf' in the local directory.
    """
    filename = "quote.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "Quotation")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}")
    c.drawString(50, height - 120, f"Product: {product_name}")
    c.drawString(50, height - 140, f"Quantity: {quantity}")
    c.drawString(50, height - 180, "Thank you for your business.")

    c.save()
    return filename
