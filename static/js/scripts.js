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
  
  document.addEventListener('DOMContentLoaded', function () {
    const optionButtons = document.querySelectorAll('.option-btn');
  
    optionButtons.forEach(button => {
      button.addEventListener('click', () => {
        button.classList.toggle('active');
        const targetId = button.dataset.target;
        const targetInput = document.getElementById(targetId);
        if (targetInput) {
          const newValue = targetInput.value === '1' ? '0' : '1';
          targetInput.value = newValue;
          calculateComplexity();
        }
      });
    });
  });
  
  let currentStep = 0;
  const steps = document.querySelectorAll('.form-step');
  const nextBtn = document.getElementById('nextBtn');
  const prevBtn = document.getElementById('prevBtn');
  const submitBtn = document.getElementById('submitBtn');
  
  function showStep(step) {
    steps.forEach((el, idx) => {
      el.classList.toggle('active', idx === step);
    });
    prevBtn.style.display = step === 0 ? 'none' : 'inline-block';
    nextBtn.style.display = step === steps.length - 1 ? 'none' : 'inline-block';
    submitBtn.style.display = step === steps.length - 1 ? 'inline-block' : 'none';
  
    if (step === steps.length - 1) {
      fillPreview();
    }
  }
  
  function nextStep() {
    const currentFormStep = steps[currentStep];
    const inputs = currentFormStep.querySelectorAll('input, select, textarea');
  
    for (const input of inputs) {
      if (!input.checkValidity()) {
        input.reportValidity();
        return;
      }
    }
  
    if (currentStep < steps.length - 1) {
      currentStep++;
      showStep(currentStep);
    }
  }
  
  function prevStep() {
    if (currentStep > 0) {
      currentStep--;
      showStep(currentStep);
    }
  }
  
  function fillPreview() {
    const t = window.translations || {};
    const preview = document.getElementById('previewArea');
    const form = document.getElementById('requestForm');
    const formData = new FormData(form);
  
    const getValue = (key) => formData.get(key) || '-';
    const badges = [];
  
    const productType = getValue('product_type');
  
    if (productType === 'website') {
      if (getValue('admin_panel') === '1') badges.push(t.admin_panel || 'Admin panel');
      if (getValue('auth') === '1') badges.push(t.auth || 'Authorization');
    }
    if (productType === 'app') {
      if (getValue('login') === '1') badges.push(t.login || 'Login');
      if (getValue('user_profile') === '1') badges.push(t.user_profile || 'User Profile');
    }
    if (productType === 'bot') {
      if (getValue('bot_database') === '1') badges.push(t.bot_database || 'Database Integration');
      if (getValue('bot_payments') === '1') badges.push(t.bot_payments || 'Payments');
    }
  
    preview.innerHTML = `
    <div class="preview-card">
      <h3>📋 ${t.preview_title || 'Review your request:'}</h3>
      <div class="preview-item"><span>👤</span> <strong>${t.name || 'Name'}:</strong> ${getValue('name')}</div>
      <div class="preview-item"><span>📧</span> <strong>${t.email || 'Email'}:</strong> ${getValue('email')}</div>
      <div class="preview-item"><span>🔧</span> <strong>${t.product_type || 'Product Type'}:</strong> ${t[`product_${productType}`] || productType}</div>

      ${productType === 'website' ? `
        <div class="preview-item"><span>🌐</span> <strong>${t.site_type || 'Site Type'}:</strong> ${t[`site_${getValue('site_type')}`] || getValue('site_type')}</div>
        <div class="preview-item"><span>📄</span> <strong>${t.pages || 'Number of Pages'}:</strong> ${getValue('pages')}</div>
      ` : ''}

      ${productType === 'app' ? `
        <div class="preview-item"><span>📱</span> <strong>${t.platform || 'Platform'}:</strong> ${getValue('platform')}</div>
      ` : ''}

      ${productType === 'bot' ? `
        <div class="preview-item"><span>🤖</span> <strong>${t.bot_commands || 'Number of Commands'}:</strong> ${getValue('bot_commands')}</div>
      ` : ''}

      ${badges.length > 0 ? `
        <div class="preview-item"><span>🛠️</span> <strong>${t.extra_features || 'Additional Features'}:</strong>
          <div class="preview-badges">
            ${badges.map(text => `<span class="preview-badge">${text}</span>`).join('')}
          </div>
        </div>
      ` : ''}

      <div class="preview-item"><span>📃</span> <strong>${t.description || 'Project Description'}:</strong> ${getValue('description')}</div>
      <div class="preview-item"><span>⏰</span> <strong>${t.contact_time || 'Best time to contact you'}:</strong> ${t[`time_${getValue('contact_time')}`] || getValue('contact_time')}</div>
    </div>
  `;


  }
  
  if (document.getElementById('requestForm')) {
    showStep(currentStep);
  
    document.getElementById('requestForm').addEventListener('submit', function (e) {
      const t = window.translations || {};
      console.log(t.form_sending || 'Form is being submitted...');
    });
  }
  