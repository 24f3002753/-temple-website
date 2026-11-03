import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.services.marathi_num_to_words import number_to_marathi_words

class ReceiptService:
    """
    अधिकृत मराठी देवनागरी देणगी पावती निर्मिती सेवा (ReportLab PDF Engine)
    पारंपारिक मंदिर-प्रेरित सुवर्ण व भगवी रंगसंगती, देवनागरी युनिकोड फॉन्ट
    """
    _font_registered = False
    REGULAR_FONT = 'Mukta'
    BOLD_FONT = 'Mukta-Bold'

    @classmethod
    def register_fonts(cls, base_dir: str):
        if cls._font_registered:
            return

        fonts_dir = os.path.join(base_dir, 'app', 'static', 'fonts')
        mukta_reg = os.path.join(fonts_dir, 'Mukta-Regular.ttf')
        mukta_bold = os.path.join(fonts_dir, 'Mukta-Bold.ttf')

        try:
            if os.path.exists(mukta_reg) and os.path.exists(mukta_bold):
                pdfmetrics.registerFont(TTFont(cls.REGULAR_FONT, mukta_reg))
                pdfmetrics.registerFont(TTFont(cls.BOLD_FONT, mukta_bold))
                cls._font_registered = True
                return
        except Exception:
            pass

        # Windows Nirmala.ttc Fallback
        nirmala_path = r'C:\Windows\Fonts\Nirmala.ttc'
        if os.path.exists(nirmala_path):
            try:
                pdfmetrics.registerFont(TTFont(cls.REGULAR_FONT, nirmala_path, subfontIndex=0))
                pdfmetrics.registerFont(TTFont(cls.BOLD_FONT, nirmala_path, subfontIndex=1))
                cls._font_registered = True
                return
            except Exception:
                pass

        # जर काहीच नसेल तर Helvetica
        cls.REGULAR_FONT = 'Helvetica'
        cls.BOLD_FONT = 'Helvetica-Bold'
        cls._font_registered = True

    @classmethod
    def generate_receipt_pdf(cls, donation, donor, payment, trust_details, output_dir: str, base_dir: str) -> str:
        """
        देणगी पावती PDF तयार करून फाईल सेव्ह करणे आणि संचिका पथ परत करणे
        """
        cls.register_fonts(base_dir)

        os.makedirs(output_dir, exist_ok=True)
        filename = f"{donation.receipt_number}.pdf"
        filepath = os.path.join(output_dir, filename)

        # A4 आकार (595 x 842 pt)
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        # रंगसंगती
        color_saffron = colors.HexColor('#C84700')
        color_maroon = colors.HexColor('#6A0000')
        color_gold = colors.HexColor('#B8860B')
        color_cream = colors.HexColor('#FDFBF7')
        color_dark = colors.HexColor('#1F140E')
        color_border = colors.HexColor('#D4AF37')

        # १. बाह्य पार्श्वभूमी व सुवर्ण बॉर्डर
        c.setFillColor(color_cream)
        c.rect(15, 15, width - 30, height - 30, fill=1, stroke=0)

        # दुहेरी पारंपारिक बॉर्डर
        c.setStrokeColor(color_border)
        c.setLineWidth(3)
        c.rect(25, 25, width - 50, height - 50, fill=0, stroke=1)
        c.setLineWidth(1)
        c.rect(29, 29, width - 58, height - 58, fill=0, stroke=1)

        # चारही कोपऱ्यांवर मांगलिक ठिपके
        corner_r = 5
        c.setFillColor(color_saffron)
        for cx, cy in [(35, 35), (width - 35, 35), (35, height - 35), (width - 35, height - 35)]:
            c.circle(cx, cy, corner_r, fill=1, stroke=0)

        # २. हेडर - संस्थान नाव व ब्रीदवाक्य
        c.setFont(cls.BOLD_FONT, 14)
        c.setFillColor(color_maroon)
        c.drawCentredString(width / 2, height - 60, "॥ ॐ नमः शिवाय ॥ धर्मो रक्षति रक्षितः ॥")

        c.setFont(cls.BOLD_FONT, 22)
        c.setFillColor(color_maroon)
        trust_name = trust_details.trust_name if trust_details else "श्री देवस्थान विश्वस्त व्यवस्था"
        c.drawCentredString(width / 2, height - 90, trust_name)

        c.setFont(cls.REGULAR_FONT, 10)
        c.setFillColor(color_dark)
        reg_no = trust_details.registration_number if trust_details else "नोंदणी क्र. महा./१२३४/ट्रस्ट"
        c.drawCentredString(width / 2, height - 108, reg_no)

        addr = trust_details.address if trust_details else "श्री देवस्थान संकुल, तीर्थक्षेत्र, महाराष्ट्र"
        c.drawCentredString(width / 2, height - 124, addr)

        # आडवी सुवर्ण रेषा
        c.setStrokeColor(color_gold)
        c.setLineWidth(1.5)
        c.line(45, height - 138, width - 45, height - 138)

        # ३. पावती शीर्षक पट्टी
        c.setFillColor(color_maroon)
        c.roundRect(width / 2 - 180, height - 175, 360, 26, 6, fill=1, stroke=0)
        c.setFont(cls.BOLD_FONT, 13)
        c.setFillColor(colors.white)
        c.drawCentredString(width / 2, height - 167, "अधिकृत देणगी पावती (DONATION ACKNOWLEDGEMENT)")

        # ४. पावती मेटा माहिती (पावती क्र. व दिनांक)
        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(color_maroon)
        c.drawString(45, height - 205, f"पावती क्र.: {donation.receipt_number}")

        issue_date = donation.paid_at or datetime.now(timezone.utc)
        date_str = issue_date.strftime("%d-%m-%Y")
        c.drawRightString(width - 45, height - 205, f"पावती दिनांक: {date_str}")

        # ५. देणगीदार माहिती टेबल (Donor Info Box)
        box_y = height - 220
        c.setStrokeColor(colors.HexColor('#E0D3C1'))
        c.setFillColor(colors.white)
        c.setLineWidth(1)
        c.roundRect(45, box_y - 120, width - 90, 120, 6, fill=1, stroke=1)

        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(color_maroon)
        c.drawString(60, box_y - 25, "देणगीदार भाविकाचे नाव:")
        c.setFont(cls.REGULAR_FONT, 12)
        c.setFillColor(color_dark)
        c.drawString(220, box_y - 25, f"{donor.full_name}")

        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(color_maroon)
        c.drawString(60, box_y - 55, "ई-मेल पत्ता (Email):")
        c.setFont(cls.REGULAR_FONT, 11)
        c.setFillColor(color_dark)
        c.drawString(220, box_y - 55, f"{donor.email}")

        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(color_maroon)
        c.drawString(60, box_y - 85, "मोबाईल क्रमांक (Mobile):")
        c.setFont(cls.REGULAR_FONT, 11)
        c.setFillColor(color_dark)
        c.drawString(220, box_y - 85, f"{donor.phone}")

        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(color_maroon)
        c.drawString(60, box_y - 110, "देणगी निधी प्रकार (Fund):")
        c.setFont(cls.REGULAR_FONT, 11)
        c.setFillColor(color_saffron)
        c.drawString(220, box_y - 110, "सर्वसाधारण देवस्थान निधी (General Temple Fund)")

        # ६. देणगी रक्कम व व्यवहार तपशील बॉक्स
        pay_y = box_y - 140
        c.setStrokeColor(color_border)
        c.setFillColor(colors.HexColor('#FFF9EE'))
        c.roundRect(45, pay_y - 150, width - 90, 150, 6, fill=1, stroke=1)

        amount_val = int(donation.amount)
        amount_words = number_to_marathi_words(amount_val)

        c.setFont(cls.BOLD_FONT, 12)
        c.setFillColor(color_maroon)
        c.drawString(60, pay_y - 30, "प्राप्त देणगी रक्कम (अंकी):")
        c.setFont(cls.BOLD_FONT, 16)
        c.setFillColor(color_saffron)
        c.drawString(230, pay_y - 30, f"₹ {amount_val:,.2f} /-")

        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(color_maroon)
        c.drawString(60, pay_y - 65, "देणगी रक्कम (अक्षरी):")
        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(color_dark)
        c.drawString(230, pay_y - 65, f"{amount_words}")

        payment_id_str = payment.razorpay_payment_id if payment else "pay_direct_verified"
        c.setFont(cls.BOLD_FONT, 10)
        c.setFillColor(color_maroon)
        c.drawString(60, pay_y - 100, "व्यवहार संदर्भ (Transaction Ref):")
        c.setFont(cls.REGULAR_FONT, 10)
        c.setFillColor(color_dark)
        c.drawString(230, pay_y - 100, f"{payment_id_str}")

        c.setFont(cls.BOLD_FONT, 10)
        c.setFillColor(color_maroon)
        c.drawString(60, pay_y - 130, "पेमेंट स्थिती (Status):")
        c.setFont(cls.BOLD_FONT, 11)
        c.setFillColor(colors.HexColor('#2E7D32'))
        c.drawString(230, pay_y - 130, "यशस्वी प्राप्त (Paid & Verified)")

        # ७. नियम व पारदर्शकता टीप
        note_y = pay_y - 175
        c.setFont(cls.REGULAR_FONT, 9)
        c.setFillColor(colors.HexColor('#555555'))
        c.drawString(45, note_y, "१. ही संगणकीय अधिकृत देणगी पावती असून मंदिर संवर्धन, अन्नछत्र व सामाजिक जनकल्याणासाठी वापरली जाईल.")
        c.drawString(45, note_y - 15, "२. सदर पावती देणगीदारास ईमेलद्वारे देखील पाठवण्यात आलेली आहे.")
        c.drawString(45, note_y - 30, "३. ही देणगी पावती असून आयकर कलम ८०जी अंतर्गत अधिकृत मान्यतेच्या अधीन आहे.")

        # ८. स्वाक्षरी व शिक्का विभाग (Signature Box)
        sig_y = note_y - 100
        c.setStrokeColor(color_gold)
        c.setLineWidth(1)
        c.line(width - 240, sig_y + 40, width - 45, sig_y + 40)

        c.setFont(cls.BOLD_FONT, 10)
        c.setFillColor(color_maroon)
        c.drawCentredString(width - 142, sig_y + 24, "अधिकृत स्वाक्षरी / मुख्य खजिनदार")
        c.setFont(cls.REGULAR_FONT, 9)
        c.setFillColor(color_dark)
        c.drawCentredString(width - 142, sig_y + 8, "श्री देवस्थान विश्वस्त व्यवस्था")

        # ९. तळटीप
        c.setFont(cls.REGULAR_FONT, 8)
        c.setFillColor(colors.HexColor('#888888'))
        c.drawCentredString(width / 2, 40, f"पावती तयार दिनांक व वेळ: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | www.templetrust.org")

        c.save()
        return filepath
