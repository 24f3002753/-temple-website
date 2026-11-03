import os
from app import create_app

env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    # पोर्ट ५००० वर स्थानिक चाचणीसाठी सुरू करा
    print("=" * 60)
    print("श्री देवस्थान विश्वस्त व्यवस्था (Temple Trust) संकेतस्थळ सुरू होत आहे...")
    print("स्थानिक पत्ता: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
