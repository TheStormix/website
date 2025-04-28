// === Випадаюче меню профілю (index.html) ===
function toggleMenu() {
    document.getElementById("dropdown").classList.toggle("show");
  }
  
  window.addEventListener('click', function(event) {
    if (!event.target.closest('.profile-menu')) {
      document.getElementById("dropdown").classList.remove('show');
    }
  });

  // === Перемикання вкладок в профілі (profile.html) ===
document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');
  
    tabs.forEach(btn => {
      btn.addEventListener('click', () => {
        tabs.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        contents.forEach(c => c.style.display = 'none');
        document.getElementById(btn.dataset.tab).style.display = 'block';
      });
    });
  
    // При старті показати першу вкладку
    if (tabs.length > 0 && contents.length > 0) {
      tabs[0].classList.add('active');
      contents.forEach((content, index) => {
        content.style.display = (index === 0) ? 'block' : 'none';
      });
    }
  });
  
 
  // === Логіка вибору типу продукту і розрахунку складності (request.html) ===
  function showForm(type) {
    document.getElementById('user_choice').style.display = 'none';
    document.getElementById('new_user_form').style.display = (type === 'new') ? 'block' : 'none';
    document.getElementById('login_form').style.display = (type === 'existing') ? 'block' : 'none';
  }
  
  function showOptions() {
    const t = document.getElementById('product_type').value;
    document.getElementById('website_options').style.display = t === 'website' ? 'block' : 'none';
    document.getElementById('app_options').style.display = t === 'app' ? 'block' : 'none';
    document.getElementById('bot_options').style.display = t === 'bot' ? 'block' : 'none';
    document.getElementById('site_type_block').style.display = t === 'website' ? 'block' : 'none';
    if (t !== 'website') {
      document.getElementById('site_type').value = '';
    }
    calculateComplexity();
  }
  
  function calculateComplexity() {
    let score = 0;
    const t = document.getElementById('product_type').value;
    if (t === 'website') {
      if (document.getElementById('pages').value === '3+') score += 2;
      if (document.getElementById('admin_panel').value === '1') score += 2;
      if (document.getElementById('auth').value === '1') score += 1;
    }
    if (t === 'app') {
      if (document.getElementById('platform').value === 'both') score += 2;
      if (document.getElementById('login').value === '1') score += 1;
      if (document.getElementById('user_profile').value === '1') score += 2;
    }
    if (t === 'bot') {
      if (document.getElementById('bot_commands').value === 'many') score += 2;
      if (document.getElementById('bot_payments').value === '1') score += 2;
      if (document.getElementById('bot_database').value === '1') score += 1;
    }
    let c = 'low';
    if (score >= 3 && score < 5) c = 'medium';
    if (score >= 5) c = 'high';
    document.getElementById('complexity').value = c;
  }
  