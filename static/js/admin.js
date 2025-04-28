// === Перемикання вкладок в адмін-панелі ===
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
  
    tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        // Активувати тільки одну кнопку
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
  
        // Показати тільки потрібний вміст
        const target = button.getAttribute('data-tab');
        tabContents.forEach(content => {
          if (content.id === target) {
            content.style.display = 'block';
          } else {
            content.style.display = 'none';
          }
        });
      });
    });
  
    // При старті: відкрити першу вкладку
    if (tabButtons.length > 0 && tabContents.length > 0) {
      tabButtons[0].classList.add('active');
      tabContents.forEach((content, index) => {
        content.style.display = index === 0 ? 'block' : 'none';
      });
    }
  });
     // === Логіка вибору рейтингу зірочками (admin.html) ===
     document.querySelectorAll('.complete-btn:not([disabled])').forEach(btn => {
        btn.addEventListener('click', () => {
          document.querySelectorAll('.star-modal').forEach(m => m.style.display = 'none');
          btn.closest('.action-cell').querySelector('.star-modal').style.display = 'block';
        });
      });
    
      document.querySelectorAll('.star-modal .star').forEach((star, idx) => {
        const siblings = Array.from(star.closest('.star-modal').querySelectorAll('.star'));
        star.addEventListener('mouseover', () => {
          siblings.forEach((s, i) => s.classList.toggle('hover', i <= idx));
        });
        star.addEventListener('mouseout', () => {
          siblings.forEach(s => s.classList.remove('hover'));
        });
        star.addEventListener('click', () => {
          siblings.forEach((s, i) => s.classList.toggle('selected', i <= idx));
          const val = star.dataset.value;
          const form = star.closest('form');
          const inp = document.createElement('input');
          inp.type = 'hidden';
          inp.name = 'rating';
          inp.value = val;
          form.appendChild(inp);
          form.submit();
        });
      });
    
      document.addEventListener('click', e => {
        if (!e.target.closest('.action-cell')) {
          document.querySelectorAll('.star-modal').forEach(m => m.style.display = 'none');
        }
      });