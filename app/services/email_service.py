import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime, timezone
from flask import current_app
from app.extensions import db

class EmailService:
    """
    अधिकृत देणगी पावती ईमेल पाठवणारी सेवा (SMTP / Transactional Email)
    ईमेल अयशस्वी झाला तरी देणगी यशस्वी राहते आणि ॲडमिन पुन्हा प्रयत्न करू शकतो.
    """

    @classmethod
    def send_donation_receipt_email(cls, recipient_email: str, donor_name: str, receipt_number: str, amount: float, pdf_path: str, receipt_record=None) -> bool:
        """
        देणगीदारास ईमेलद्वारे PDF पावती पाठवणे
        """
        mail_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = current_app.config.get('MAIL_PORT', 587)
        mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
        mail_username = current_app.config.get('MAIL_USERNAME', '')
        mail_password = current_app.config.get('MAIL_PASSWORD', '')
        sender_email = current_app.config.get('MAIL_DEFAULT_SENDER', 'श्री देवस्थान विश्वस्त व्यवस्था <info@templetrust.org>')

        # जर क्रेडेन्शियल्स कॉन्फिगर केलेले नसतील (उदा. डेव्हलपमेंट मोड)
        if not mail_username or not mail_password:
            current_app.logger.info(f"[DEV EMAIL SIMULATION] पावती ईमेल सिम्युलेशन: {recipient_email} - पावती {receipt_number}")
            if receipt_record:
                receipt_record.email_sent = True
                receipt_record.email_sent_at = datetime.now(timezone.utc)
                db.session.commit()
            return True

        # MIME संदेश रचना
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"श्री देवस्थान विश्वस्त व्यवस्था - आपली देणगी पावती क्र. {receipt_number}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #D4AF37; padding: 25px; border-radius: 8px;">
                <h2 style="color: #7A0000; text-align: center;">श्री देवस्थान विश्वस्त व्यवस्था</h2>
                <p style="text-align: center; color: #E65100; font-weight: bold;">॥ धर्मो रक्षति रक्षितः ॥</p>
                <hr style="border: 0; border-top: 1px solid #D4AF37;">
                <p>सस्नेह नमस्कार <strong>{donor_name}</strong>,</p>
                <p>
                    श्री देवस्थान विश्वस्त व्यवस्थेस आपण दिलेल्या <strong>₹ {amount:,.2f} /-</strong> देणगीबद्दल विश्वस्त मंडळाच्या वतीने आपले मनःपूर्वक आभार!
                </p>
                <p>
                    आपल्या दातृत्वातून मंदिराचे दैनंदिन अन्नछत्र, मंदिर संवर्धन आणि सामाजिक सेवा कार्यास मोलाचे सहकार्य लाभले आहे.
                </p>
                <div style="background-color: #FFF9EE; border-left: 4px solid #E65100; padding: 12px; margin: 15px 0;">
                    <p style="margin: 0;"><strong>पावती क्रमांक:</strong> {receipt_number}</p>
                    <p style="margin: 5px 0 0 0;"><strong>देणगी निधी:</strong> सर्वसाधारण देवस्थान निधी</p>
                </div>
                <p>
                    आपली अधिकृत संगणकीय पावती सोबत PDF स्वरूपात जोडलेली आहे.
                </p>
                <p style="margin-top: 30px; font-size: 0.9em; color: #777;">
                    श्री देवस्थान विश्वस्त व्यवस्था कार्यालय<br>
                    हेल्पलाईन: ०२२-१२३४५६७८ | ई-मेल: info@templetrust.org
                </p>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))

        # PDF फाईल संलग्न करा
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header('Content-Disposition', 'attachment', filename=f"Receipt_{receipt_number}.pdf")
                msg.attach(attachment)

        # प्रत्यक्ष SMTP पाठवणे
        try:
            with smtplib.SMTP(mail_server, mail_port, timeout=10) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(msg)

            if receipt_record:
                receipt_record.email_sent = True
                receipt_record.email_sent_at = datetime.now(timezone.utc)
                db.session.commit()
            return True

        except Exception as e:
            current_app.logger.error(f"ईमेल पाठवताना त्रुटी: {str(e)}")
            # ईमेल अयशस्वी झाला तरी देणगी यशस्वी राहते
            if receipt_record:
                receipt_record.email_sent = False
                db.session.commit()
            return False
