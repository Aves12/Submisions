import datetime
import locale
import os
from decimal import Decimal
from typing import List, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class InvoiceGenerator:
    """Generates invoices for orders placed on an e-commerce platform."""

    def __init__(self,
                 seller_details: Dict,
                 billing_details: Dict,
                 shipping_details: Dict,
                 order_details: Dict,
                 invoice_details: Dict,
                 item_details: List[Dict],
                 reverse_charge: str,
                 signature_image_path: str,
                 output_filename: str = 'invoice.pdf'):

        self.seller_details = seller_details
        self.billing_details = billing_details
        self.shipping_details = shipping_details
        self.order_details = order_details
        self.invoice_details = invoice_details
        self.item_details = item_details
        self.reverse_charge = reverse_charge
        self.signature_image_path = signature_image_path
        self.output_filename = output_filename

    def generate_invoice(self):
        """Generates the invoice as a PDF document."""

        # Compute derived parameters
        self._compute_item_details()

        # Create a new PDF document
        doc = SimpleDocTemplate(
            self.output_filename,
            pagesize=letter,
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )

        # Create the invoice elements
        elements = [
            self._create_header(),
            Spacer(1, 0.2 * inch),
            self._create_seller_details(),
            Spacer(1, 0.2 * inch),
            self._create_billing_details(),
            Spacer(1, 0.2 * inch),
            self._create_shipping_details(),
            Spacer(1, 0.2 * inch),
            self._create_order_details(),
            Spacer(1, 0.2 * inch),
            self._create_invoice_details(),
            Spacer(1, 0.2 * inch),
            self._create_item_details_table(),
            Spacer(1, 0.2 * inch),
            self._create_total_row(),
            Spacer(1, 0.2 * inch),
            self._create_amount_in_words(),
            Spacer(1, 0.2 * inch),
            self._create_reverse_charge_statement(),
            Spacer(1, 0.2 * inch),
            self._create_signature(),
        ]

        # Build the PDF document
        doc.build(elements)

    def _create_header(self):
        """Creates the header section of the invoice."""

        styles = getSampleStyleSheet()
        header = Paragraph("<b>amazon.in</b>", styles['Heading1'])
        return header

    def _create_seller_details(self):
        """Creates the seller details section of the invoice."""

        styles = getSampleStyleSheet()
        seller_details = [
            Paragraph("<b>Sold By:</b>", styles['Normal']),
            Paragraph(f"{self.seller_details['name']}", styles['Normal']),
            Paragraph(f"{self.seller_details['address']}", styles['Normal']),
            Paragraph(
                f"{self.seller_details['city']}, {self.seller_details['state']}, {self.seller_details['pincode']}",
                styles['Normal'],
            ),
            Paragraph(f"PAN No: {self.seller_details['pan_no']}", styles['Normal']),
            Paragraph(
                f"GST Registration No: {self.seller_details['gst_registration_no']}", styles['Normal']
            ),
        ]
        return seller_details

    def _create_billing_details(self):
        """Creates the billing details section of the invoice."""

        styles = getSampleStyleSheet()
        billing_details = [
            Paragraph("<b>Billing Address:</b>", styles['Normal']),
            Paragraph(f"{self.billing_details['name']}", styles['Normal']),
            Paragraph(f"{self.billing_details['address']}", styles['Normal']),
            Paragraph(
                f"{self.billing_details['city']}, {self.billing_details['state']}, {self.billing_details['pincode']}",
                styles['Normal'],
            ),
            Paragraph(
                f"State/UT Code: {self.billing_details['state_ut_code']}", styles['Normal']
            ),
        ]
        return billing_details

    def _create_shipping_details(self):
        """Creates the shipping details section of the invoice."""

        styles = getSampleStyleSheet()
        shipping_details = [
            Paragraph("<b>Shipping Address:</b>", styles['Normal']),
            Paragraph(f"{self.shipping_details['name']}", styles['Normal']),
            Paragraph(f"{self.shipping_details['address']}", styles['Normal']),
            Paragraph(
                f"{self.shipping_details['city']}, {self.shipping_details['state']}, {self.shipping_details['pincode']}",
                styles['Normal'],
            ),
            Paragraph(
                f"State/UT Code: {self.shipping_details['state_ut_code']}", styles['Normal']
            ),
        ]
        return shipping_details

    def _create_order_details(self):
        """Creates the order details section of the invoice."""

        styles = getSampleStyleSheet()
        order_details = [
            Paragraph(f"<b>Order Number:</b> {self.order_details['order_no']}", styles['Normal']),
            Paragraph(
                f"<b>Order Date:</b> {self.order_details['order_date'].strftime('%d.%m.%Y')}",
                styles['Normal'],
            ),
        ]
        return order_details

    def _create_invoice_details(self):
        """Creates the invoice details section of the invoice."""

        styles = getSampleStyleSheet()
        invoice_details = [
            Paragraph(
                f"<b>Invoice Number:</b> {self.invoice_details['invoice_no']}", styles['Normal']
            ),
            Paragraph(
                f"<b>Invoice Details:</b> {self.invoice_details['invoice_details']}",
                styles['Normal'],
            ),
            Paragraph(
                f"<b>Invoice Date:</b> {self.invoice_details['invoice_date'].strftime('%d.%m.%Y')}",
                styles['Normal'],
            ),
        ]
        return invoice_details

    def _compute_item_details(self):
        """Computes the derived parameters for each item."""

        for item in self.item_details:
            item['net_amount'] = Decimal(item['unit_price']) * Decimal(item['quantity']) - Decimal(
                item['discount']
            )
            if (
                self.billing_details['state'] == self.shipping_details['state']
                and self.billing_details['city'] == self.shipping_details['city']
            ):
                item['tax_type'] = 'CGST'
                item['tax_rate'] = Decimal(0.09)  # 9% CGST
                item['tax_amount'] = item['net_amount'] * Decimal(0.09)
                item['total_amount'] = item['net_amount'] + item['tax_amount']
                item['tax_amount_sgst'] = item['net_amount'] * Decimal(0.09)
                item['total_amount_sgst'] = item['net_amount'] + item['tax_amount_sgst']
            else:
                item['tax_type'] = 'IGST'
                item['tax_rate'] = Decimal(0.18)  # 18% IGST
                item['tax_amount'] = item['net_amount'] * Decimal(0.18)
                item['total_amount'] = item['net_amount'] + item['tax_amount']
                item['tax_amount_sgst'] = Decimal(0)
                item['total_amount_sgst'] = Decimal(0)

    def _create_item_details_table(self):
        """Creates the table for item details."""

        data = [
            ['SI. No', 'Description', 'Unit Price', 'Qty', 'Net Amount', 'Tax Rate', 'Tax Type', 'Tax Amount', 'Total Amount'],
        ]
        for index, item in enumerate(self.item_details):
            data.append(
                [
                    index + 1,
                    item['description'],
                    item['unit_price'],
                    item['quantity'],
                    item['net_amount'],
                    item['tax_rate'],
                    item['tax_type'],
                    item['tax_amount'],
                    item['total_amount'],
                ]
            )

        table = Table(data)

        style = TableStyle(
            [
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, 'gray'),
                ('BOX', (0, 0), (-1, -1), 0.25, 'gray'),
            ]
        )

        table.setStyle(style)
        return table

    def _create_total_row(self):
        """Creates the total row of the invoice."""

        styles = getSampleStyleSheet()
        total_amount = sum(
            [Decimal(item['total_amount']) for item in self.item_details]
        )
        total_row = [
            Paragraph("<b>TOTAL:</b>", styles['Normal']),
            Spacer(1, 0.2 * inch),
            Paragraph(f"<b>{total_amount:.2f}</b>", styles['Normal']),
        ]
        return total_row

    def _create_amount_in_words(self):
        """Creates the amount in words section of the invoice."""

        styles = getSampleStyleSheet()
        total_amount = sum(
            [Decimal(item['total_amount']) for item in self.item_details]
        )
        amount_in_words = Paragraph(
            f"<b>Amount in Words:</b> {locale.format_string('%a', total_amount, grouping=True)} only",
            styles['Normal'],
        )
        return amount_in_words

    def _create_reverse_charge_statement(self):
        """Creates the reverse charge statement section of the invoice."""

        styles = getSampleStyleSheet()
        reverse_charge_statement = Paragraph(
            f"<b>Whether tax is payable under reverse charge - {self.reverse_charge}</b>",
            styles['Normal'],
        )
        return reverse_charge_statement

    def _create_signature(self):
        """Creates the signature section of the invoice."""

        styles = getSampleStyleSheet()
        signature = [
            Paragraph(
                f"<b>For {self.seller_details['name']}:</b>", styles['Normal']
            ),
            Spacer(1, 0.2 * inch),
            self._insert_signature_image(),
            Spacer(1, 0.2 * inch),
            Paragraph(
                "<b>Authorized Signatory</b>", styles['Normal']
            ),
        ]
        return signature

    def _insert_signature_image(self):
        """Inserts the signature image."""

        c = canvas.Canvas('temp.pdf', pagesize=letter)
        c.drawImage(self.signature_image_path, 500, 50, width=100, height=50)
        c.save()
        with open('temp.pdf', 'rb') as f:
            image_data = f.read()
        os.remove('temp.pdf')

        return Paragraph("<img src='data:image/png;base64,%s' />" % image_data, getSampleStyleSheet()['Normal'])


if __name__ == '__main__':
    # Sample data for invoice generation
    seller_details = {
        'name': 'Varasiddhi Silk Exports',
        'address': '*75, 3rd Cross, Lalbagh Road',
        'city': 'BENGALURU',
        'state': 'KARNATAKA',
        'pincode': 560027,
        'pan_no': 'AACFV3325K',
        'gst_registration_no': '29AACFV3325K1ZY',
    }

    billing_details = {
        'name': 'Madhu B',
        'address': 'Eurofins IT Solutions India Pvt Ltd,, 1st Floor, Maruti Platinum, Lakshminarayana Pura, AECS Layou',
        'city': 'BENGALURU',
        'state': 'KARNATAKA',
        'pincode': 560037,
        'state_ut_code': 29,
    }

    shipping_details = {
        'name': 'Madhu B',
        'address': 'Eurofins IT Solutions India Pvt Ltd,, 1st Floor, Maruti Platinum, Lakshminarayana Pura, AECS Layou',
        'city': 'BENGALURU',
        'state': 'KARNATAKA',
        'pincode': 560037,
        'state_ut_code': 29,
    }

    order_details = {
        'order_no': '403-3225714-7676307',
        'order_date': datetime.datetime(2019, 10, 28),
    }

    invoice_details = {
        'invoice_no': 'IN-761',
        'invoice_details': 'KA-310565025-1920',
        'invoice_date': datetime.datetime(2019, 10, 28),
    }

    item_details = [
        {
            'description': 'Varasiddhi Silks Men\'s Formal Shirt (SH-05-42, Navy Blue, 42) | B07KGF3KW8 (SH-05--42)',
            'unit_price': '538.10',
            'quantity': 1,
            'discount': 0,
            'net_amount': None,
            'tax_rate': None,
            'tax_type': None,
            'tax_amount': None,
            'total_amount': None,
        },
        {
            'description': 'Shipping Charges',
            'unit_price': '30.96',
            'quantity': 1,
            'discount': 0,
            'net_amount': None,
            'tax_rate': None,
            'tax_type': None,
            'tax_amount': None,
            'total_amount': None,
        },
        {
            'description': 'Varasiddhi Silks Men\'s Formal Shirt (SH-05-40, Navy Blue, 40) | B07KGCS2X7 (SH-05--40)',
            'unit_price': '538.10',
            'quantity': 1,
            'discount': 0,
            'net_amount': None,
            'tax_rate': None,
            'tax_type': None,
            'tax_amount': None,
            'total_amount': None,
        },
        {
            'description': 'Shipping Charges',
            'unit_price': '30.96',
            'quantity': 1,
            'discount': 0,
            'net_amount': None,
            'tax_rate': None,
            'tax_type': None,
            'tax_amount': None,
            'total_amount': None,
        },
    ]

    reverse_charge = 'No'

    # Path to the signature image
    signature_image_path = 'signature.png'

    # Generate the invoice
    invoice_generator = InvoiceGenerator(
        seller_details=seller_details,
        billing_details=billing_details,
        shipping_details=shipping_details,
        order_details=order_details,
        invoice_details=invoice_details,
        item_details=item_details,
        reverse_charge=reverse_charge,
        signature_image_path=signature_image_path,
        output_filename='invoice.pdf',
    )
    invoice_generator.generate_invoice()
