import os
from app import create_app
from app.extensions import db
from app.models.trust import TrustDetails, TrustMember, ChairpersonMessage, PublicDocument
from app.models.stream import LiveStreamSettings, AartiSchedule
from app.models.content import GalleryImage, TrustUpdate
from app.models.admin import AdminUser

def seed_database():
    app = create_app('development')
    with app.app_context():
        print("डेटाबेस टेबल्स तयार करत आहे...")
        db.create_all()

        # १. मंदिर संस्थान माहिती (TrustDetails)
        if not TrustDetails.query.first():
            print("संस्थान माहिती भरत आहे...")
            trust = TrustDetails(
                trust_name="श्री देवस्थान विश्वस्त व्यवस्था",
                establishment_year="१९६५",
                registration_number="महा./१२३४/ट्रस्ट (महाराष्ट्र सार्वजनिक विश्वस्त व्यवस्था अधिनियम, १९५०)",
                introduction=(
                    "श्री देवस्थान विश्वस्त व्यवस्था ही महाराष्ट्र राज्यातील लाखो भाविकांचे आराध्य स्थान असलेल्या "
                    "मंदिराचे व्यवस्थापन करणारी अधिकृत धर्मादाय संस्था आहे. मंदिर संवर्धन, अखंड अन्नदान आणि सामाजिक "
                    "कल्याण ही विश्वस्त व्यवस्थेची मूलभूत उद्दिष्टे आहेत."
                ),
                history=(
                    "मंदिराचा इतिहास अनेक शतके जुना असून यादवकालीन हेमाडपंथी स्थापत्यकलेचा हा एक उत्कृष्ट नमुना आहे. "
                    "बाराव्या शतकात स्थापन झालेल्या या देवस्थानाचा जीर्णोद्धार छत्रपती शिवाजी महाराजांच्या काळात आणि नंतर पेशवे "
                    "काळात करण्यात आला. मंदिराच्या दगडी भिंती, भव्य दीपमाळा आणि नक्षीदार खांब आजही अखंड दिमाखात उभे आहेत."
                ),
                address="श्री देवस्थान संकुल, मुख्य मंदिर मार्ग, तीर्थक्षेत्र देवस्थान, तालुका व जिल्हा - पुणे, महाराष्ट्र - ४१२३०१",
                helpline_phone="०२२-१२३४५६७८ / ७९",
                contact_email="info@templetrust.org",
                visiting_hours="सकाळी ०५:०० ते रात्री १०:००",
                logo_path="images/logo.svg"
            )
            db.session.add(trust)

        # २. अध्यक्षांचा संदेश (ChairpersonMessage)
        if not ChairpersonMessage.query.first():
            print("अध्यक्षांचा संदेश भरत आहे...")
            chairperson = ChairpersonMessage(
                chairperson_name="श्री. रमेशचंद्र जोशी",
                designation="अध्यक्ष",
                photograph="images/default-trustee.svg",
                message=(
                    "प्रिय भाविक बंधू आणि भगिनींनो, नमस्कार. श्री देवस्थानच्या पावन भूमीत येणाऱ्या प्रत्येक भाविकाला "
                    "आत्मिक शांती, ऊर्जा आणि सेवाभाव मिळावा यासाठी विश्वस्त मंडळ कटिबद्ध आहे. मंदिराचे पारंपरिक पावित्र्य "
                    "राखून आम्ही डिजिटल तंत्रज्ञानाचा अवलंब केला असून घरबसल्या थेट आरती व पारदर्शक देणगी सुविधा सुरू केली आहे. "
                    "मंदिराच्या भक्तनिवास व धर्मार्थ रुग्णालय प्रकल्पात आपल्या सर्वांचे सहकार्य सदैव स्मरणात राहील."
                ),
                vision=(
                    "मंदिराचा सर्वंकष विकास करणे, अत्याधुनिक भक्तनिवास संकुल उभारणे, नित्य अन्नछत्र अखंड चालू ठेवणे "
                    "आणि संस्थेचा कारभार १००% पारदर्शक व लोकाभिमुख ठेवणे हे आमचे प्रमुख ध्येय आहे."
                )
            )
            db.session.add(chairperson)

        # ३. विश्वस्त मंडळ (TrustMembers)
        if TrustMember.query.count() == 0:
            print("विश्वस्त मंडळ सदस्य भरत आहे...")
            members = [
                TrustMember(full_name="श्री. रमेशचंद्र जोशी", designation="अध्यक्ष", description="सामाजिक कार्यकर्ते व मुख्य मार्गदर्शक", display_order=1),
                TrustMember(full_name="श्री. विनायकराव कदम", designation="उपाध्यक्ष", description="मंदिर विधी व उत्सव व्यवस्थापन प्रमुख", display_order=2),
                TrustMember(full_name="श्री. आनंदराव पाटील", designation="सचिव", description="प्रशासकीय समन्वय व कायदेशीर बाबी", display_order=3),
                TrustMember(full_name="श्री. गजानन मोरे", designation="सहसचिव", description="माहिती तंत्रज्ञान व भक्त संपर्क", display_order=4),
                TrustMember(full_name="श्री. सुधीर देशपांडे", designation="खजिनदार", description="आर्थिक हिशोब, देणगी व लेखापरीक्षण", display_order=5),
                TrustMember(full_name="श्रीमती सुलक्षणा कुलकर्णी", designation="विश्वस्त", description="महिला भाविक सुरक्षा व अन्नछत्र", display_order=6),
                TrustMember(full_name="श्री. प्रभाकर शिंदे", designation="विश्वस्त", description="मंदिर वास्तू देखभाल व विकास प्रकल्प", display_order=7),
                TrustMember(full_name="श्री. दत्तात्रय वाघमारे", designation="विश्वस्त", description="सुरक्षा व्यवस्था व आपत्ती व्यवस्थापन", display_order=8),
            ]
            db.session.add_all(members)

        # ४. थेट आरती सेटिंग्ज (LiveStreamSettings)
        if not LiveStreamSettings.query.first():
            print("थेट आरती सेटिंग्ज भरत आहे...")
            stream_setting = LiveStreamSettings(
                provider="youtube",
                video_id="jfKfPfyJRdk",
                is_enabled=True,
                unavailable_message="सध्या थेट आरती सुरू नाही. कृपया पुढील आरतीच्या वेळी पुन्हा भेट द्या.",
                notice="थेट आरती सकाळी व संध्याकाळी नियमित सुरू असते."
            )
            db.session.add(stream_setting)

        # ५. दैनिक आरती वेळापत्रक (AartiSchedule)
        if AartiSchedule.query.count() == 0:
            print("आरती वेळापत्रक भरत आहे...")
            aartis = [
                AartiSchedule(aarti_name="काकड आरती", start_time="05:30", end_time="06:15", marathi_time="पहाटे ०५:३० वाजता", description="पहाटेचे मंगलमय आद्य दर्शन व भूपाळी गायन", display_order=1),
                AartiSchedule(aarti_name="महापूजा व अभिषेक", start_time="08:00", end_time="09:30", marathi_time="सकाळी ०८:०० वाजता", description="मुख्य गाभाऱ्यात वैदिक मंत्रोच्चारात पंचामृत अभिषेक", display_order=2),
                AartiSchedule(aarti_name="माध्यान्ह (दुपारची) आरती", start_time="12:00", end_time="12:30", marathi_time="दुपारी १२:०० वाजता", description="नैवेद्य समर्पण व मध्यान्ह आरती विधी", display_order=3),
                AartiSchedule(aarti_name="धूपारती (संध्या आरती)", start_time="19:00", end_time="19:45", marathi_time="संध्याकाळी ०७:०० वाजता", description="दीप प्रज्वलन, धूपदीप व सायंकाळचे स्तोत्रपठण", display_order=4),
                AartiSchedule(aarti_name="शेजारती", start_time="22:00", end_time="22:30", marathi_time="रात्री १०:०० वाजता", description="दिवसाची सांगता व मंदिर शयन विधी", display_order=5),
            ]
            db.session.add_all(aartis)

        # ६. छायाचित्र संग्रह (GalleryImage)
        if GalleryImage.query.count() == 0:
            print("छायाचित्र संग्रह भरत आहे...")
            images = [
                GalleryImage(title="काकड आरती मंगल दर्शन", description="पहाटेची मंगल काकड आरती", category="aarti", image_path="images/sample-gallery.svg", display_order=1),
                GalleryImage(title="प्राचीन हेमाडपंथी वास्तुकला", description="मुख्य मंदिराचे ऐतिहासिक शिखर", category="campus", image_path="images/hero-temple.svg", display_order=2),
                GalleryImage(title="वार्षिक पालखी उत्सव सोहळा", description="महाशिवरात्री पालखी सोहळा", category="festival", image_path="images/sample-gallery.svg", display_order=3),
                GalleryImage(title="अखंड अन्नछत्र महाप्रसाद सेवा", description="नित्य मोफत अन्नदान वाटप", category="social", image_path="images/sample-gallery.svg", display_order=4),
                GalleryImage(title="संध्या धूपारती व दीप प्रज्वलन", description="संध्याकाळची आरती व दीपमाळ", category="aarti", image_path="images/sample-gallery.svg", display_order=5),
                GalleryImage(title="त्रिपुरारी पौर्णिमा दीपोत्सव", description="५१,००० दिव्यांची भव्य आरास", category="festival", image_path="images/hero-temple.svg", display_order=6),
            ]
            db.session.add_all(images)

        # ७. ताज्या बातम्या व उपक्रम (TrustUpdate)
        if TrustUpdate.query.count() == 0:
            print("संस्थेच्या बातम्या व उपक्रम भरत आहे...")
            updates = [
                TrustUpdate(
                    title="वार्षिक महाशिवरात्री उत्सव नियोजन व दर्शन व्यवस्था",
                    category="धार्मिक उत्सव",
                    description="आगामी महाशिवरात्री उत्सवानिमित्त स्वतंत्र महिला व पुरुष दर्शन रांगा, ज्येष्ठ नागरिकांसाठी विशेष सोय आणि २४ तास अखंड अन्नछत्राचे नियोजन करण्यात आले आहे."
                ),
                TrustUpdate(
                    title="भव्य मोफत नेत्र तपासणी व आरोग्य शिबिर संपन्न",
                    category="सामाजिक सेवा",
                    description="देवस्थानच्या वतीने परिसरातील ५०० ज्येष्ठ नागरिकांची मोफत नेत्र तपासणी करण्यात आली असून पात्र रुग्णांची मोफत मोतीबिंदू शस्त्रक्रिया करण्यात येत आहे."
                ),
                TrustUpdate(
                    title="अत्याधुनिक नवीन भक्तनिवास संकुलाचे भूमिपूजन",
                    category="विकास प्रकल्प",
                    description="दूरवरून येणाऱ्या भाविकांच्या निवासासाठी १०० खोल्यांचे आधुनिक भक्तनिवास व वाहनतळ प्रकल्पाचे काम लवकरच सुरू होत आहे."
                ),
                TrustUpdate(
                    title="सणासुदीच्या काळातील मंदिर दर्शन वेळेतील बदल",
                    category="परिपत्रक",
                    description="सणांच्या काळात भाविकांची गर्दी लक्षात घेऊन मंदिर पहाटे ०४:३० वाजता उघडले जाईल आणि रात्री ११:०० वाजेपर्यंत दर्शनासाठी खुले राहील."
                )
            ]
            db.session.add_all(updates)

        # ८. पारदर्शकता कागदपत्रे (PublicDocument)
        if PublicDocument.query.count() == 0:
            print("पारदर्शकता कागदपत्रे भरत आहे...")
            docs = [
                PublicDocument(title="संस्थेचे नोंदणी प्रमाणपत्र", document_type="नोंदणी प्रमाणपत्र", file_path="docs/registration_cert.pdf", published_year="१९६५"),
                PublicDocument(title="वार्षिक लेखापरीक्षण अहवाल २०२५-२६", document_type="ऑडिट रिपोर्ट", file_path="docs/audit_report_2025_26.pdf", published_year="२०२५-२६"),
                PublicDocument(title="वार्षिक कार्यवृत्तांत अहवाल", document_type="कार्यवृत्तांत", file_path="docs/annual_report.pdf", published_year="२०२५-२६"),
                PublicDocument(title="देणगी विनियोग अहवाल", document_type="देणगी अहवाल", file_path="docs/donation_utilization.pdf", published_year="२०२५-२६")
            ]
            db.session.add_all(docs)

        # ९. प्रशासक खाते (AdminUser)
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            print("प्रशासक खाते (Admin) तयार करत आहे...")
            admin = AdminUser(
                username='admin',
                full_name='मुख्य विश्वस्त व्यवस्थापक',
                role='superadmin'
            )
            admin.set_password('TempleTrust@2026')
            db.session.add(admin)

        db.session.commit()
        print("सर्व डेटाबेस टेबल्स आणि नमुना मराठी माहिती यशस्वीरित्या जतन झाली!")

if __name__ == '__main__':
    seed_database()
