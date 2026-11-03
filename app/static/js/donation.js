/**
 * श्री देवस्थान विश्वस्त व्यवस्था - ऑनलाइन देणगी प्रणाली जावास्क्रिप्ट
 * कार्यक्षमता: देणगी रक्कम निवड, फॉर्म प्रमाणीकरण, Razorpay Checkout एकत्रीकरण
 */

document.addEventListener('DOMContentLoaded', function () {
    const amountButtons = document.querySelectorAll('.amount-btn');
    const amountInput = document.getElementById('donation-amount');
    const donationForm = document.getElementById('donation-form');
    const submitBtn = document.getElementById('btn-submit-donation');
    const donationAlert = document.getElementById('donation-error-alert');

    // जलद रक्कम निवड बटणे (Quick Amount Buttons)
    if (amountButtons && amountInput) {
        amountButtons.forEach(btn => {
            btn.addEventListener('click', function () {
                amountButtons.forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const val = this.getAttribute('data-amount');
                amountInput.value = val;
                hideError();
            });
        });

        // जेव्हा वापरकर्ता स्वतःहून रक्कम टाईप करेल
        amountInput.addEventListener('input', function () {
            let currentVal = this.value;
            let matched = false;
            amountButtons.forEach(b => {
                if (b.getAttribute('data-amount') === currentVal) {
                    b.classList.add('active');
                    matched = true;
                } else {
                    b.classList.remove('active');
                }
            });
            if (!matched) {
                amountButtons.forEach(b => b.classList.remove('active'));
            }
            hideError();
        });
    }

    function showError(msg) {
        if (donationAlert) {
            donationAlert.textContent = msg;
            donationAlert.classList.remove('d-none');
            donationAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            alert(msg);
        }
    }

    function hideError() {
        if (donationAlert) {
            donationAlert.classList.add('d-none');
        }
    }

    // देणगी फॉर्म सबमिशन आणि Razorpay Checkout
    if (donationForm) {
        donationForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            hideError();

            const fullName = document.getElementById('donor-name').value.trim();
            const email = document.getElementById('donor-email').value.trim();
            const phone = document.getElementById('donor-phone').value.trim();
            const amount = parseFloat(amountInput.value);

            // मराठी प्रमाणीकरण (Marathi Form Validations)
            if (!fullName) {
                showError('कृपया आपले पूर्ण नाव प्रविष्ट करा.');
                return;
            }
            if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                showError('कृपया वैध ई-मेल पत्ता प्रविष्ट करा.');
                return;
            }
            if (!phone || !/^[6-9]\d{9}$/.test(phone)) {
                showError('कृपया १० अंकी वैध भारतीय मोबाईल क्रमांक प्रविष्ट करा.');
                return;
            }
            if (isNaN(amount) || amount < 10) {
                showError('किमान देणगी रक्कम ₹१० असणे आवश्यक आहे.');
                return;
            }

            // बटण निष्क्रिय करा
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> कृपया प्रतीक्षा करा... सुरक्षित पेमेंट विंडो उघडत आहे...';

            try {
                // पायरी १: बॅकएंडवर Razorpay ऑर्डर तयार करा
                const response = await fetch('/api/donations/create-order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
                    },
                    body: JSON.stringify({
                        full_name: fullName,
                        email: email,
                        phone: phone,
                        amount: amount
                    })
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.message || 'ऑर्डर तयार करताना त्रुटी आली. कृपया पुन्हा प्रयत्न करा.');
                }

                // जर Razorpay SDK लोड झाले नसेल तर माहिती द्या
                if (typeof Razorpay === 'undefined') {
                    // विकास/डेमो मोड फॉलबॅक
                    console.warn('Razorpay SDK उपलब्ध नाही. विकास सिम्युलेशन मोडमध्ये जात आहे.');
                    window.location.href = `/donation-success?donation_id=${data.donation_id}&receipt_number=${data.receipt_number || 'STT-DEV'}`;
                    return;
                }

                // पायरी २: Razorpay Checkout पॉपअप उघडा
                const options = {
                    key: data.razorpay_key_id,
                    amount: data.amount_paise,
                    currency: "INR",
                    name: "श्री देवस्थान विश्वस्त व्यवस्था",
                    description: "मंदिर सर्वसाधारण देणगी",
                    image: "/static/images/logo.svg",
                    order_id: data.order_id,
                    prefill: {
                        name: fullName,
                        email: email,
                        contact: phone
                    },
                    theme: {
                        color: "#E65100"
                    },
                    handler: async function (response) {
                        // पायरी ३: बॅकएंडवर स्वाक्षरी पडताळणी करा
                        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> देणगी पावती तयार होत आहे...';
                        
                        try {
                            const verifyRes = await fetch('/api/donations/verify-payment', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]')?.value || ''
                                },
                                body: JSON.stringify({
                                    razorpay_order_id: response.razorpay_order_id,
                                    razorpay_payment_id: response.razorpay_payment_id,
                                    razorpay_signature: response.razorpay_signature,
                                    donation_id: data.donation_id
                                })
                            });

                            const verifyData = await verifyRes.json();
                            if (verifyRes.ok && verifyData.success) {
                                window.location.href = verifyData.redirect_url;
                            } else {
                                window.location.href = `/donation-failed?error=${encodeURIComponent(verifyData.message || 'पडताळणी अयशस्वी')}`;
                            }
                        } catch (err) {
                            window.location.href = `/donation-failed?error=${encodeURIComponent('पेमेंट पडताळणी दरम्यान तांत्रिक अडचण आली.')}`;
                        }
                    },
                    modal: {
                        ondismiss: function () {
                            submitBtn.disabled = false;
                            submitBtn.innerHTML = 'देणगी द्या <i class="bi bi-arrow-right ms-1"></i>';
                        }
                    }
                };

                const rzp = new Razorpay(options);
                rzp.on('payment.failed', function (response) {
                    window.location.href = `/donation-failed?error=${encodeURIComponent(response.error.description || 'पेमेंट अयशस्वी')}`;
                });
                rzp.open();

            } catch (err) {
                showError(err.message || 'देणगी प्रक्रिया सुरू करताना त्रुटी आली. कृपया पुन्हा प्रयत्न करा.');
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'देणगी द्या <i class="bi bi-arrow-right ms-1"></i>';
            }
        });
    }
});
