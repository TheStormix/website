// === Перемикання вкладок в адмін-панелі ===
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
  
    tabButtons.forEach(button => {
      button.addEventListener('click', () => {
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
  
        const target = button.getAttribute('data-tab');
        tabContents.forEach(content => {
          content.style.display = (content.id === target) ? 'block' : 'none';
        });
  
        if (target === 'tab-statistics') {
          setTimeout(() => {
            renderProductChart();
            renderComplexityChart();
          }, 100);
        }
      });
    });
  
    if (tabButtons.length > 0 && tabContents.length > 0) {
      tabButtons[0].classList.add('active');
      tabContents.forEach((content, index) => {
        content.style.display = index === 0 ? 'block' : 'none';
      });
    }
  });
  
  let productChartInstance = null;
  let complexityChartInstance = null;
  
  function renderProductChart() {
    if (
      !window.chartData ||
      !Array.isArray(window.chartData.stats) ||
      window.chartData.stats.length === 0
    ) {
      console.warn("Немає даних для productChart");
      return;
    }
  
    const ctx = document.getElementById('productChart').getContext('2d');
    if (productChartInstance) productChartInstance.destroy();
  
    const stats = window.chartData.stats;
    console.log("Дані для productChart:", stats);
  
    const productData = {
      labels: stats.map(s => s.product_type),
      datasets: [{
        label: "Кількість заявок",
        data: stats.map(s => s.count),
        backgroundColor: ['#4285F4', '#EA4335', '#FBBC05']
      }]
    };
  
    productChartInstance = new Chart(ctx, {
        type: 'bar',
        data: productData,
        options: {
          responsive: false,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1 }
            }
          }
        }
      });
    }
    
    
  
  function renderComplexityChart() {
    if (!window.chartData || !window.chartData.complexity_stats || window.chartData.complexity_stats.length === 0) {
      console.warn("Немає даних для complexityChart");
      return;
    }
    const ctx = document.getElementById('complexityChart').getContext('2d');
    if (complexityChartInstance) complexityChartInstance.destroy();
  
    const complexityStats = window.chartData.complexity_stats;
    const complexityData = {
      labels: complexityStats.map(c => c.complexity),
      datasets: [{
        label: 'Розподіл складності',
        data: complexityStats.map(c => c.count),
        backgroundColor: ['#34A853', '#F9AB00', '#EA4335']
      }]
    };
  
    complexityChartInstance = new Chart(ctx, {
      type: 'pie',
      data: complexityData,
      options: {
        responsive: false,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          }
        }
      }
    });
  }
  
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