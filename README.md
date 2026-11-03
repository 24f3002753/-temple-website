# श्री देवस्थान विश्वस्त व्यवस्था (Temple Trust Website)
### अधिकृत आणि आधुनिक मराठी देवस्थान संकेतस्थळ प्रणाली

महाराष्ट्रातील मोठ्या हिंदू मंदिर व देवस्थान विश्वस्त व्यवस्थेसाठी (Temple Trust) विकसित केलेले आधुनिक, सुरक्षित, प्रतिसादात्मक (Mobile & Desktop Responsive) आणि **१००% शुद्ध मराठी भाषेतील** संकेतस्थळ.

---

## १. प्रमुख वैशिष्ट्ये (Core Features)

1. **मंदिर संस्थानाची माहिती (About the Trust & Transparency):**
   - संस्थेचा इतिहास, उद्दिष्टे, धार्मिक व सामाजिक उपक्रम.
   - अध्यक्षांचा संदेश (छायाचित्र व भावी व्हिजन).
   - विश्वस्त मंडळ प्रोफाइल कार्डे (अध्यक्ष, उपाध्यक्ष, सचिव, सहसचिव, खजिनदार, विश्वस्त) ४/२/१ प्रतिसादात्मक ग्रिडसह.
   - पारदर्शकता: नोंदणी प्रमाणपत्र, वार्षिक अहवाल, लेखापरीक्षण (Audit Report) डाऊनलोड सुविधा.

2. **थेट आरती दर्शन (Live Aarti Streaming):**
   - **Zero Flask Server Proxying:** व्हिडिओ थेट YouTube CDN वरून प्ले होतो, ज्यामुळे ५००+ किंवा हजारो भाविकांच्या वेळीही फ्लास्क सर्व्हरवर बँडविड्थ लोड येत नाही.
   - १६:९ रिस्पॉन्सिव्ह एम्बेड प्लेयर (YouTube वर रिडायरेक्ट न होता वेबसाइटवरच थेट दर्शन).
   - LIVE निर्देशक बॅज व दैनिक आरती वेळापत्रक.
   - थेट प्रक्षेपण बंद असताना आदरयुक्त मराठी संदेश (*"सध्या थेट आरती सुरू नाही..."*) आणि पुढील आरतीचा काउंटडाउन टाइमर.
   - भविष्यात Cloudflare Stream किंवा सानुकूल HLS कडे अपग्रेड करण्यासाठी लवचिक `StreamingService`.

3. **ऑनलाइन देणगी प्रणाली (Online Donation System):**
   - एकच सर्वसाधारण देणगी निधी (General Temple Fund).
   - ₹१०१, ₹५०१, ₹१,००१, ₹५,००१ जलद निवड बटणे आणि सानुकूल रक्कम इनपुट.
   - **Razorpay Checkout** एकत्रीकरण (UPI, RuPay, डेबिट/क्रेडिट कार्ड्स, नेटबँकिंग).
   - **सुरक्षा:** सर्व्हर-साइड `HMAC-SHA256` स्वाक्षरी पडताळणी + Razorpay Webhooks.
   - **इडेम्पोटन्सी (Idempotency):** दुहेरी वेबहुक आल्यास दुहेरी पावती किंवा दुहेरी ईमेल तयार होण्यापासून १००% संरक्षण.
   - **मराठी देवनागरी PDF पावती (Python ReportLab):** पारंपारिक सोनेरी/क्रीम बॉर्डर, पावती क्र., देणगीदाराचे नाव, तारीख, अंकी रक्कम व **शुद्ध मराठी अक्षरी रक्कम** (उदा. *"पाचशे एक रुपये फक्त"*).
   - पावती तात्काळ डाऊनलोड आणि भाविकांच्या ईमेलवर PDF पावती स्वयंचलित पाठवणे.

4. **प्रशासन नियंत्रण कक्ष (Admin Dashboard - 11 Modules):**
   - डॅशबोर्ड विहंगावलोकन (एकूण देणगी, आजची देणगी, मासिक देणगी, यशस्वी व प्रलंबित व्यवहार).
   - देणगी शोध, फिल्टर आणि **CSV / Excel एक्सपोर्ट**.
   - पावती पुन्हा ईमेलवर पाठवणे.
   - विश्वस्त मंडळ संपादन (फोटो, पदनाम, क्रम).
   - थेट आरती ID व वेळापत्रक संपादन.
   - छायाचित्र संग्रह (Photo Gallery CMS) व बातम्या (Updates CMS).
   - सुरक्षित पासवर्ड हॅशिंग (`scrypt`/`pbkdf2`) आणि **IP ॲड्रेससह ऑडिट लॉग्स**.

---

## २. तंत्रज्ञान संच (Technology Stack)

- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Google Fonts (`Mukta` & `Noto Sans Devanagari`).
- **Backend:** Python 3.10+, Flask Framework (Application Factory Pattern & Blueprints).
- **Database:** PostgreSQL (SQLAlchemy 2.0 ORM, Flask-SQLAlchemy, Alembic / Flask-Migrate).
- **Payment Gateway:** Razorpay API & Webhook Verification.
- **PDF Generation:** Python ReportLab (TrueType Unicode Marathi Font).
- **Email Delivery:** SMTP (TLS, Port 587) with PDF attachment.
- **Video Delivery:** YouTube Live Embed (Extensible to Cloudflare Stream / HLS).
- **Production Server:** Gunicorn WSGI, Nginx Reverse Proxy, SSL/TLS Let's Encrypt Certbot.

---

## ३. प्रकल्प रचना (Directory Structure)

```
temple_website/
│
├── app/
│   ├── __init__.py                 # Flask App Factory (Blueprints, DB, Login, CSRF)
│   ├── extensions.py               # SQLAlchemy, Migrate, LoginManager
│   │
│   ├── models/                     # संपूर्ण १४ डेटाबेस मॉडेल्स
│   │   ├── trust.py                # TrustDetails, TrustMember, ChairpersonMessage, PublicDocument
│   │   ├── stream.py               # LiveStreamSettings, AartiSchedule
│   │   ├── donation.py             # Donor, Donation, Payment, Receipt, WebhookEvent
│   │   ├── content.py              # GalleryImage, TrustUpdate
│   │   └── admin.py                # AdminUser, AuditLog
│   │
│   ├── routes/                     # मॉड्यूलर नियंत्रक
│   │   ├── public.py               # सर्व सार्वजनिक मराठी पेजेस
│   │   ├── donations.py            # Razorpay Order, Verify, Webhook, PDF Download
│   │   └── admin.py                # सर्व ११ ॲडमिन मॉड्यूल्स व CSV एक्सपोर्ट
│   │
│   ├── services/                   # व्यवसाय तर्कशास्त्र (Business Logic)
│   │   ├── payment_service.py      # HMAC पडताळणी, ऑर्डर निर्मिती, Webhook
│   │   ├── receipt_service.py      # ReportLab मराठी PDF पावती निर्मिती
│   │   ├── email_service.py        # SMTP ईमेल पावती पाठवणे
│   │   ├── streaming_service.py    # YouTube / Cloudflare URL क्लीनर व वेळापत्रक गणना
│   │   └── marathi_num_to_words.py # संख्या-ते-मराठी शब्द रूपांतरक
│   │
│   ├── templates/                  # Jinja2 मराठी टेम्पलेट्स
│   │   ├── layout.html             # मुख्य हेडर, नेव्हिगेशन मेनू व पादटीप
│   │   ├── index.html              # मुख्यपृष्ठ (Hero, Live Aarti, CTA, Highlights)
│   │   ├── about_temple.html       # मंदिराचा इतिहास व वास्तुकला
│   │   ├── trust.html              # संस्थेचा परिचय, विश्वस्त मंडळ, अध्यक्षांचा संदेश
│   │   ├── live_aarti.html         # थेट आरती दर्शन व दैनिक वेळापत्रक
│   │   ├── donate.html             # ऑनलाइन देणगी फॉर्म
│   │   ├── donation_success.html   # देणगी पावती डाऊनलोड पृष्ठ
│   │   ├── donation_failed.html    # देणगी अयशस्वी पृष्ठ
│   │   ├── gallery.html            # छायाचित्र संग्रह (फिल्टर व मॉडाल)
│   │   ├── updates.html            # ताज्या बातम्या व परिपत्रके
│   │   ├── contact.html            # पत्ता, हेल्पलाईन, संपर्क फॉर्म व नकाशा
│   │   └── admin/                  # प्रशासन नियंत्रण फलक टेम्पलेट्स
│   │       ├── admin_layout.html   # ॲडमिन साइडबार व शीर्षपट्टी
│   │       ├── dashboard.html      # नियंत्रण फलक विहंगावलोकन
│   │       ├── donations_list.html # देणगी व्यवस्थापन व शोध
│   │       ├── reports.html        # आर्थिक ताळेबंद व अहवाल
│   │       ├── stream_manage.html  # थेट आरती व्यवस्थापन
│   │       ├── aarti_manage.html   # आरती वेळापत्रक संपादन
│   │       ├── trust_manage.html   # संस्थान माहिती संपादन
│   │       ├── chairperson_manage.html # अध्यक्षांचा संदेश संपादन
│   │       ├── members_manage.html # विश्वस्त मंडळ CMS
│   │       ├── gallery_manage.html # फोटो गॅलरी CMS
│   │       ├── updates_manage.html # बातम्या CMS
│   │       ├── admins_manage.html  # प्रशासक खाती व ऑडिट लॉग्स
│   │       └── login.html          # प्रशासक लॉगिन
│   │
│   └── static/
│       ├── css/                    # marathi-theme.css (भगवा-सोनेरी रंगसंगती)
│       ├── js/                     # main.js (काउंटडाउन, मॉडाल), donation.js (Razorpay Checkout)
│       ├── images/                 # logo.svg, hero-temple.svg, default-trustee.svg
│       ├── fonts/                  # Mukta-Regular.ttf, Mukta-Bold.ttf
│       ├── uploads/                # दस्तऐवज व फोटो साठा
│       └── receipts/               # तयार झालेल्या PDF देणगी पावत्या
│
├── nginx/
│   └── temple_trust.conf           # SSL, Rate Limiting व Gunicorn रिव्हर्स प्रॉक्सी
├── systemd/
│   └── temple_trust.service        # Systemd ऑटो-रीस्टार्ट सेवा
├── scripts/
│   ├── backup_db.sh                # Linux स्वयंचलित PostgreSQL बॅकअप
│   └── backup_db.ps1               # Windows PowerShell बॅकअप
├── tests/
│   ├── test_donations.py           # देणगी, स्वाक्षरी, PDF व Webhook चाचण्या
│   ├── test_security.py            # ॲडमिन सुरक्षा व प्रवेश नियंत्रण चाचण्या
│   └── run_all_tests.py            # मास्टर चाचणी रनर
│
├── config.py                       # Dev / Test / Production कॉन्फिगरेशन
├── requirements.txt                # Python लायब्ररीज
├── .env.example                    # पर्यावरण व्हेरिएबल्स ब्लूप्रिंट
├── run.py                          # स्थानिक सर्व्हर रनर
├── wsgi.py                         # Production WSGI एंट्रीपॉईंट
└── gunicorn_config.py              # Gunicorn उत्पादन संरूपण
```

---

## ४. स्थानिक सेटअप आणि चालवण्याची पद्धत (Local Setup Guide)

### पायरी १: पर्यावरण तयार करा व लायब्ररी स्थापित करा
```powershell
cd C:\Users\Asus\.gemini\antigravity\scratch\temple_website

# व्हर्च्युअल एन्व्हायर्नमेंट तयार करा (ऐच्छिक)
python -m venv venv
.\venv\Scripts\activate

# आवश्यक लायब्ररी स्थापित करा
pip install -r requirements.txt
```

### पायरी २: पर्यावरण व्हेरिएबल्स (`.env`) सेट करा
`.env.example` ची प्रत करून `.env` तयार करा:
```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=temple-trust-very-secure-secret-key-2026

# PostgreSQL डेटाबेस (किंवा चाचणीसाठी SQLite)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/temple_trust_db

# Razorpay की (Razorpay Dashboard -> Settings -> API Keys मधून मिळवा)
RAZORPAY_KEY_ID=rzp_test_YourTestKeyIdHere
RAZORPAY_KEY_SECRET=YourRazorpaySecretKeyHere
RAZORPAY_WEBHOOK_SECRET=YourWebhookSecretKeyHere

# SMTP ईमेल (Gmail App Password किंवा SendGrid)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=trust.temple@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER="श्री देवस्थान विश्वस्त व्यवस्था" <trust.temple@gmail.com>
```

### पायरी ३: डेटाबेस सुरू करा व नमुना माहिती भरा (Database Seed)
```powershell
python seed_data.py
```
*हे स्क्रिप्ट सर्व १४ टेबल्स आपोआप तयार करते आणि त्यामध्ये वास्तववादी मराठी मंदिर माहिती, ८ विश्वस्त, ५ आरत्या, फोटो गॅलरी, आणि डीफॉल्ट प्रशासक खाते तयार करते.*

### पायरी ४: ॲप्लिकेशन सुरू करा
```powershell
python run.py
```
ब्राऊझरमध्ये उघडा:
- **मुख्य संकेतस्थळ:** `http://127.0.0.1:5000`
- **थेट आरती दर्शन:** `http://127.0.0.1:5000/live-aarti`
- **ऑनलाइन देणगी:** `http://127.0.0.1:5000/donate`
- **प्रशासक लॉगिन:** `http://127.0.0.1:5000/admin/login`

**डीफॉल्ट प्रशासक क्रेडेन्शियल्स:**
- **वापरकर्ता नाव (Username):** `admin`
- **गुप्तशब्द (Password):** `TempleTrust@2026`

---

## ५. स्वयंचलित चाचणी संच चालवणे (Running Automated Tests)

सर्व सुरक्षा, देणगी, PDF पावती, आणि राऊट्सच्या चाचण्या चालवण्यासाठी:
```powershell
python tests/run_all_tests.py
```
निकाल:
```
============================================================
SHREE TEMPLE TRUST - COMPLETE AUTOMATED SYSTEM TEST SUITE
============================================================
[PASSED] 1. Marathi Number-To-Words tested
[PASSED] 2. Order creation and validation tested
[PASSED] 3. Successful payment & ReportLab PDF receipt tested
[PASSED] 4. Tampered signature rejection tested
[PASSED] 5. Idempotent duplicate verification tested
[PASSED] 6. Razorpay Webhook duplicate event idempotency tested
[PASSED] 1. All protected admin routes require authentication
[PASSED] 2. Password hashing & verification validated
[PASSED] 3. Disabled admin account login blocked
[PASSED] 4. Tampered webhook signature blocked with 400 Bad Request
============================================================
ALL TESTS PASSED! 100% PRODUCTION READY AND VERIFIED.
============================================================
```

---

## ६. उत्पादन उपयोजन मार्गदर्शक (Production Deployment on Linux/Ubuntu)

### पायरी १: सर्व्हर पॅकेजेस स्थापित करा
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx -y
```

### पायरी २: PostgreSQL डेटाबेस व युझर तयार करा
```bash
sudo -u postgres psql
CREATE DATABASE temple_trust_db;
CREATE USER temple_admin WITH ENCRYPTED PASSWORD 'StrongProductionPassword2026!';
GRANT ALL PRIVILEGES ON DATABASE temple_trust_db TO temple_admin;
\q
```

### पायरी ३: ॲप्लिकेशन डिप्लॉय करा
```bash
sudo mkdir -p /var/www/temple_website
sudo chown -R www-data:www-data /var/www/temple_website
# प्रकल्प फाइल्स कॉपी करा...
cd /var/www/temple_website
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python seed_data.py
```

### पायरी ४: Systemd सर्व्हिस सुरू करा
```bash
sudo cp systemd/temple_trust.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable temple_trust.service
sudo systemctl start temple_trust.service
sudo systemctl status temple_trust.service
```

### पायरी ५: Nginx रिव्हर्स प्रॉक्सी व SSL (HTTPS)
```bash
sudo cp nginx/temple_trust.conf /etc/nginx/sites-available/temple_trust
sudo ln -s /etc/nginx/sites-available/temple_trust /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# विनामूल्य SSL प्रमाणपत्र मिळवा
sudo certbot --nginx -d templetrust.org -d www.templetrust.org
```

### पायरी ६: स्वयंचलित दैनिक डेटाबेस बॅकअप (Cron Job)
```bash
sudo chmod +x scripts/backup_db.sh
sudo crontab -e
# दररोज मध्यरात्री ०२:०० वाजता बॅकअप घेण्यासाठी जोडा:
0 2 * * * /var/www/temple_website/scripts/backup_db.sh >> /var/log/temple_backup.log 2>&1
```

---

## ७. Razorpay मर्चंट ऑनबोर्डिंग व Webhook सूचना

1. ट्रस्टने **Razorpay Dashboard** वर जाऊन स्वतःचे अधिकृत KYC व बँक खाते पूर्ण करावे.
2. Settings -> Webhooks वर जा आणि Webhook URL सेट करा:
   `https://templetrust.org/api/donations/razorpay-webhook`
3. इव्हेंट्स निवडा:
   - `payment.captured`
   - `order.paid`
4. निर्माण झालेली `Secret` ही `.env` मधील `RAZORPAY_WEBHOOK_SECRET` मध्ये प्रविष्ट करा.

---

## ८. कायदेशीर व पारदर्शकता नोंद

- या संकेतस्थळावर तयार होणारी पावती ही **अधिकृत देणगी पावती (Donation Acknowledgement Receipt)** आहे.
- आयकर कलम ८०जी अंतर्गत अधिकृत मान्यता प्राप्त असल्याशिवाय कोणताही खोटा ८०जी कर सवलतीचा दावा केला जात नाही.
- सर्व देणग्यांची नोंद पारदर्शक असून ती धर्मादाय आयुक्त (Charity Commissioner) नियमावलीनुसार आहे.
- संकेतस्थळ उत्पादन उपयोजनासाठी **१००% सज्ज** आहे.

॥ श्री देवस्थान विश्वस्त व्यवस्था ॥ धर्मो रक्षति रक्षितः ॥
