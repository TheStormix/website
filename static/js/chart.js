const stats = window.chartData.stats;
const complexityStats = window.chartData.complexity_stats;
const t = window.translations?.statistics || {};

const productData = {
  labels: stats.map(obj => obj.product_type),
  datasets: [{
    label: t.product_types || 'Типи продуктів',
    data: stats.map(obj => obj.count),
    backgroundColor: ['#4285F4', '#EA4335', '#FBBC05']
  }]
};

const complexityData = {
  labels: complexityStats.map(obj => obj.complexity),
  datasets: [{
    label: t.complexity || 'Складність',
    data: complexityStats.map(obj => obj.count),
    backgroundColor: ['#34A853', '#F9AB00', '#EA4335']
  }]
};

new Chart(document.getElementById('productChart'), {
  type: 'bar',
  data: productData
});

new Chart(document.getElementById('complexityChart'), {
  type: 'pie',
  data: complexityData
});
