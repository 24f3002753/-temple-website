/**
 * श्री देवस्थान विश्वस्त व्यवस्था - मुख्य क्लायंट जावास्क्रिप्ट
 * कार्यक्षमता: नेव्हिगेशन, गॅलरी मॉडेल, आरती काउंटडाउन, देवनागरी अंक
 */

document.addEventListener('DOMContentLoaded', function () {
    // देवनागरी अंकांमध्ये रूपांतर करण्याचे कार्य (Convert English to Devanagari numerals)
    window.toDevanagari = function (num) {
        const devanagariDigits = ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'];
        return String(num).replace(/[0-9]/g, function (w) {
            return devanagariDigits[+w];
        });
    };

    // गॅलरी प्रतिमा पाहण्यासाठी लाइटबॉक्स मॉडाल (Gallery Image Viewer)
    const galleryItems = document.querySelectorAll('.gallery-clickable');
    const modalImage = document.getElementById('galleryModalImage');
    const modalTitle = document.getElementById('galleryModalTitle');

    if (galleryItems.length > 0 && modalImage) {
        galleryItems.forEach(item => {
            item.addEventListener('click', function () {
                const src = this.getAttribute('data-img-src') || this.querySelector('img').src;
                const title = this.getAttribute('data-title') || '';
                modalImage.src = src;
                if (modalTitle) modalTitle.textContent = title;
            });
        });
    }

    // आरती वेळापत्रक पुढील आरती काउंटडाउन (Countdown to Next Aarti if elements exist)
    const countdownEl = document.getElementById('aarti-countdown');
    if (countdownEl) {
        // उदा. 30 मिनिटांचा सिम्युलेटेड काउंटडाउन किंवा रिअल-टाइम वेळ
        let secondsRemaining = 1800;
        function updateTimer() {
            if (secondsRemaining <= 0) {
                countdownEl.innerHTML = '<span class="text-success fw-bold">आरती सुरू आहे!</span>';
                return;
            }
            const mins = Math.floor(secondsRemaining / 60);
            const secs = secondsRemaining % 60;
            countdownEl.textContent = `${toDevanagari(mins)} मिनिटे ${toDevanagari(secs)} सेकंद`;
            secondsRemaining--;
        }
        updateTimer();
        setInterval(updateTimer, 1000);
    }
});
