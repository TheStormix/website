const statusTitle = document.getElementById('status-title');
  const statusText = document.getElementById('status-text');
  const statusIcon = document.getElementById('status-icon');

  setTimeout(() => {
    statusTitle.textContent = "Обробка заявки...";
    statusText.textContent = "Надсилання листа на пошту...";
  }, 1000);

  

  setTimeout(() => {
    document.querySelector('.confirmation-container').style.display = 'none';
    document.getElementById('final-content').style.display = 'block';
    document.getElementById('status-icon').style.display = 'none';
}, 3000);