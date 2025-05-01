document.addEventListener('DOMContentLoaded', function() {
    const resendBtn = document.getElementById('resend-btn');
    let timerInterval; 
    const t = window.translations?.confirm || {};

    function startTimer() {
        let secondsLeft = 60;

        resendBtn.disabled = true;
        resendBtn.classList.remove('btn-primary');
        resendBtn.style.backgroundColor = '#ccc';
        resendBtn.style.cursor = 'not-allowed';
        resendBtn.textContent = `${t.resend || 'Надіслати код повторно'} (${secondsLeft})`;

        timerInterval = setInterval(() => {
            secondsLeft--;
            resendBtn.textContent = `${t.resend || 'Надіслати код повторно'} (${secondsLeft})`;

            if (secondsLeft <= 0) {
                clearInterval(timerInterval);
                resendBtn.disabled = false;
                resendBtn.classList.add('btn-primary');
                resendBtn.style.backgroundColor = '';
                resendBtn.style.cursor = 'pointer';
                resendBtn.textContent = t.resend || 'Надіслати код повторно';
            }
        }, 1000);
    }

    function showTemporaryMessage(message, type = 'info') {
        const existing = document.querySelector('.flash-message-dynamic');
        if (existing) {
            existing.remove();
        }

        const div = document.createElement('div');
        div.className = `flash-message-dynamic ${type}`;
        div.textContent = message;

        div.style.padding = '12px 20px';
        div.style.marginBottom = '20px';
        div.style.borderRadius = '8px';
        div.style.textAlign = 'center';
        div.style.fontSize = '16px';
        div.style.fontWeight = 'bold';
        div.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        div.style.maxWidth = '600px';
        div.style.margin = '20px auto';

        if (type === 'success') {
            div.style.backgroundColor = '#d4edda';
            div.style.color = '#155724';
            div.style.border = '1px solid #c3e6cb';
        } else if (type === 'error') {
            div.style.backgroundColor = '#f8d7da';
            div.style.color = '#721c24';
            div.style.border = '1px solid #f5c6cb';
        } else {
            div.style.backgroundColor = '#cce5ff';
            div.style.color = '#004085';
            div.style.border = '1px solid #b8daff';
        }

        const parentContainer = document.querySelector('.form-container');
        parentContainer.insertBefore(div, parentContainer.firstChild);

        setTimeout(() => {
            div.remove();
        }, 4000);
    }

    if (resendBtn) {
        startTimer();

        resendBtn.addEventListener('click', async () => {
            resendBtn.disabled = true;
            resendBtn.classList.remove('btn-primary');
            resendBtn.style.backgroundColor = '#ccc';
            resendBtn.style.cursor = 'not-allowed';
            resendBtn.textContent = t.sending || 'Надсилання...';

            try {
                const response = await fetch('/resend_code', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });

                if (!response.ok) {
                    throw new Error(t.error_sending || 'Помилка при надсиланні коду');
                }

                clearInterval(timerInterval);
                startTimer();
                showTemporaryMessage(t.resent_success || 'Код підтвердження надіслано повторно.', 'success');

            } catch (error) {
                showTemporaryMessage(error.message || t.connection_error || 'Помилка з’єднання.', 'error');
                resendBtn.disabled = false;
                resendBtn.classList.add('btn-primary');
                resendBtn.style.backgroundColor = '';
                resendBtn.style.cursor = 'pointer';
                resendBtn.textContent = t.resend || 'Надіслати код повторно';
            }
        });
    }
});

setTimeout(() => {
    const flashMessages = document.querySelectorAll('.flash-messages li');
    flashMessages.forEach(msg => {
        msg.classList.add('fade-out');
        setTimeout(() => {
            msg.remove();
        }, 500);
    });
}, 4000);
