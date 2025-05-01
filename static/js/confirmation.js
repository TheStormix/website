const statusTitle = document.getElementById('status-title');
const statusText = document.getElementById('status-text');
const statusIcon = document.getElementById('status-icon');

const t = window.translations?.confirmation || {};

setTimeout(() => {
  statusTitle.textContent = t.processing || "Обробка заявки...";
  statusText.textContent = t.sending || "Надсилання листа на пошту...";
}, 1000);

setTimeout(() => {
  document.querySelector('.confirmation-container').style.display = 'none';
  document.getElementById('final-content').style.display = 'block';
  document.getElementById('status-icon').style.display = 'none';
}, 3000);
