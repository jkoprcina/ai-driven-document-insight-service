"""
Script to generate test documents for the Document QA API.
Creates sample PDF and image files for testing.
"""
import os
from pathlib import Path

def create_sample_pdf():
    """Create a sample PDF document."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        
        os.makedirs("test_docs", exist_ok=True)
        
        pdf_path = "test_docs/sample_contract.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "SERVICE AGREEMENT")
        
        c.setFont("Helvetica", 12)
        y = 720
        lines = [
            "This agreement is entered into as of January 1, 2024.",
            "",
            "PARTIES:",
            "Client: Acme Corporation",
            "Vendor: Tech Services Inc.",
            "",
            "TERMS:",
            "1. Service Period: 12 months",
            "2. Contract Amount: $50,000 USD",
            "3. Payment Terms: Net 30 days",
            "4. Delivery: Monthly reports required",
            "",
            "SCOPE OF WORK:",
            "- System maintenance and support",
            "- 24/7 technical assistance",
            "- Quarterly performance reviews",
            "- Emergency response within 2 hours",
            "",
            "CONFIDENTIALITY:",
            "All information is strictly confidential.",
        ]
        
        for line in lines:
            c.drawString(50, y, line)
            y -= 20
        
        c.save()
        print(f"✓ Created {pdf_path}")
        
    except ImportError:
        print("⚠ reportlab not installed. Install with: pip install reportlab")

def create_sample_image():
    """Create a sample image document."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        os.makedirs("test_docs", exist_ok=True)
        
        # Create image
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw text
        text_lines = [
            "INVOICE #INV-2024-001",
            "Date: January 10, 2024",
            "",
            "BILL TO:",
            "Customer Name: John Smith",
            "Email: john@example.com",
            "",
            "DESCRIPTION          QTY    RATE      AMOUNT",
            "Software License     1      $5,000    $5,000",
            "Setup Fee            1      $1,000    $1,000",
            "Support (12 months)  1      $2,000    $2,000",
            "",
            "TOTAL DUE: $8,000 USD",
            "Due Date: February 10, 2024",
        ]
        
        y = 20
        for line in text_lines:
            draw.text((20, y), line, fill='black')
            y += 30
        
        img_path = "test_docs/sample_invoice.png"
        img.save(img_path)
        print(f"✓ Created {img_path}")
        
    except ImportError:
        print("⚠ Pillow not installed. Install with: pip install Pillow")

if __name__ == "__main__":
    print("Generating test documents...")
    create_sample_pdf()
    create_sample_image()
    print("\nTest documents created in test_docs/")
