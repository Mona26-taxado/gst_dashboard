$(document).ready(function() {
  /* ChartJS
   * -------
   * Data and config for chartjs
   */
  'use strict';
  
  // Debug flag
  const DEBUG = true;

  // Theme Colors
  const themeColors = {
    primary: '#0090e7',
    success: '#00d25b',
    warning: '#ffab00',
    danger: '#fc424a',
    info: '#8f5fe8',
    secondary: '#0c161f',
    gradients: {
      primary: ['rgba(0, 144, 231, 0.5)', 'rgba(0, 144, 231, 0.05)'],
      success: ['rgba(0, 210, 91, 0.5)', 'rgba(0, 210, 91, 0.05)'],
      info: ['rgba(143, 95, 232, 0.5)', 'rgba(143, 95, 232, 0.05)']
    }
  };

  // Utility Functions
  const utils = {
    formatCurrency: function(amount) {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount);
    },

    createGradient: function(ctx, colors) {
      const gradient = ctx.createLinearGradient(0, 0, 0, 400);
      gradient.addColorStop(0, colors[0]);
      gradient.addColorStop(1, colors[1]);
      return gradient;
    },

    getRandomColor: function(opacity = 0.2) {
      const r = Math.floor(Math.random() * 255);
      const g = Math.floor(Math.random() * 255);
      const b = Math.floor(Math.random() * 255);
      return `rgba(${r}, ${g}, ${b}, ${opacity})`;
    },

    generateColors: function(count, opacity = 0.2) {
      return Array(count).fill().map(() => this.getRandomColor(opacity));
    },

    // Default chart colors
    chartColors: {
      primary: 'rgba(54, 162, 235, 0.5)',
      success: 'rgba(75, 192, 192, 0.5)',
      warning: 'rgba(255, 206, 86, 0.5)',
      danger: 'rgba(255, 99, 132, 0.5)',
      info: 'rgba(153, 102, 255, 0.5)',
      secondary: 'rgba(255, 159, 64, 0.5)'
    },

    // Function to destroy existing chart if it exists
    destroyChart: function(chartInstance) {
      if (chartInstance) {
        chartInstance.destroy();
      }
    },

    debug: function(message, data) {
      if (DEBUG) {
        console.log('Debug:', message, data || '');
      }
    }
  };

  // Chart Configurations
  const chartConfigs = {
    commonOptions: {
    responsive: true,
      maintainAspectRatio: false,
    animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      },
      layout: {
        padding: {
          left: 0,
          right: 0,
          top: 0,
          bottom: 0
      }
    },
    scales: {
      yAxes: [{
        gridLines: {
            color: 'rgba(204, 204, 204, 0.1)',
            drawBorder: false,
            zeroLineColor: 'rgba(204, 204, 204, 0.1)'
          },
          ticks: {
            beginAtZero: true,
            padding: 10,
            callback: function(value) {
              return utils.formatCurrency(value);
            },
            fontColor: '#9ca3af'
        }
      }],
      xAxes: [{
        gridLines: {
            display: false,
            drawBorder: false
          },
          ticks: {
            padding: 10,
            fontColor: '#9ca3af'
          }
        }]
      },
      legend: {
        display: true,
        position: 'top',
        labels: {
          fontColor: '#9ca3af',
          usePointStyle: true,
          padding: 20,
          boxWidth: 8
        }
      },
      tooltips: {
        mode: 'index',
        intersect: false,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFontColor: '#fff',
        bodyFontColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 4,
        xPadding: 10,
        yPadding: 10,
        callbacks: {
          label: function(tooltipItem, data) {
            return data.datasets[tooltipItem.datasetIndex].label + ': ' + utils.formatCurrency(tooltipItem.yLabel);
          }
        }
      }
    },

    pieOptions: {
      responsive: true,
      maintainAspectRatio: false,
      legend: {
        position: 'right',
        labels: {
          boxWidth: 12
        }
      },
      animation: {
        animateScale: true,
        animateRotate: true
      }
    }
  };

  // Track chart instances
  let charts = {
    income: null,
    barChart: null,
    lineChart: null,
    pieChart: null,
    doughnutChart: null,
    areaChart: null,
    trend: null
  };

  // Chart Data Fetching Functions
  const api = {
    getDashboardData: function() {
      return $.ajax({
        url: '/get-dashboard-data/',
        method: 'GET'
      });
    },
    getMonthlyIncome: function() {
      return $.ajax({
        url: '/get-monthly-income-data/',
        method: 'GET'
      });
    }
  };

  // Chart Initialization Functions
  function initIncomeChart() {
    utils.debug('Initializing Income Chart');
    
    const canvas = document.getElementById('incomeChart');
    if (!canvas) {
      utils.debug('Income Chart canvas not found');
      return;
    }

    // Destroy existing chart if it exists
    if (charts.income) {
      charts.income.destroy();
    }

    const ctx = canvas.getContext('2d');
    const gradient = utils.createGradient(ctx, themeColors.gradients.primary);
    
    // Set default data in case API fails
    const defaultData = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      data: [10000, 15000, 20000, 25000, 30000, 35000]
    };

    // First create chart with default data
    charts.income = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: defaultData.labels,
        datasets: [{
          label: 'Monthly Income',
          data: defaultData.data,
          backgroundColor: gradient,
          borderColor: themeColors.primary,
          borderWidth: 2,
          borderRadius: 5,
          hoverBackgroundColor: themeColors.primary,
          pointBackgroundColor: '#fff',
          pointBorderColor: themeColors.primary,
          pointHoverBackgroundColor: themeColors.primary,
          pointHoverBorderColor: '#fff'
        }]
      },
      options: {
        ...chartConfigs.commonOptions,
        barRoundness: 1,
    scales: {
          ...chartConfigs.commonOptions.scales,
      yAxes: [{
            ...chartConfigs.commonOptions.scales.yAxes[0],
            ticks: {
              ...chartConfigs.commonOptions.scales.yAxes[0].ticks,
              maxTicksLimit: 6
        }
      }]
    }
  }
    });

    // Then fetch real data
    $.ajax({
      url: '/get-monthly-income-data/',
      method: 'GET',
      success: function(response) {
        utils.debug('Income data received', response);
        
        if (response && response.labels && response.total_centers && response.total_bills) {
          charts.income.data.labels = response.labels;
          charts.income.data.datasets = [
            {
              label: 'Total Centers',
              data: response.total_centers,
              backgroundColor: utils.chartColors.primary,
              borderColor: utils.chartColors.primary,
              borderWidth: 2,
              borderRadius: 5
      },
      {
              label: 'Total Bills',
              data: response.total_bills,
              backgroundColor: utils.chartColors.danger,
              borderColor: utils.chartColors.danger,
              borderWidth: 2,
              borderRadius: 5
      }
          ];
          charts.income.update();
        }
      },
      error: function(error) {
        utils.debug('Error fetching income data:', error);
      }
    });
  }

  function initBarChart() {
    const ctx = document.getElementById('barChart');
    if (!ctx) return;

    const data = {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      datasets: [{
        label: 'Sales',
        data: [15000, 20000, 25000, 30000, 35000, 40000],
        backgroundColor: Object.values(utils.chartColors),
        borderColor: Object.values(utils.chartColors),
        borderWidth: 1
      }]
    };

    charts.barChart = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: chartConfigs.commonOptions
    });
  }

  function initLineChart() {
    const ctx = document.getElementById('lineChart');
    if (!ctx) return;

    const data = {
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
      datasets: [{
        label: 'Revenue',
        data: [25000, 30000, 27000, 35000, 40000, 45000],
        borderColor: utils.chartColors.primary,
        tension: 0.4,
        fill: false
      }]
    };

    charts.lineChart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: chartConfigs.commonOptions
    });
  }

  function initDoughnutChart() {
    const ctx = document.getElementById('doughnutChart');
    if (!ctx) return;

    const data = {
      labels: ['Online', 'Offline', 'Other'],
      datasets: [{
        data: [45000, 35000, 20000],
        backgroundColor: [
          utils.chartColors.primary,
          utils.chartColors.success,
          utils.chartColors.warning
        ]
      }]
    };

    charts.doughnutChart = new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: chartConfigs.pieOptions
    });
  }

  function initTrendChart() {
    utils.debug('Initializing Trend Chart');
    
    const canvas = document.getElementById('trendChart');
    if (!canvas) {
      utils.debug('Trend Chart canvas not found');
      return;
    }

    // Destroy existing chart if it exists
    if (charts.trend) {
      charts.trend.destroy();
    }

    const ctx = canvas.getContext('2d');
    const gradient = utils.createGradient(ctx, themeColors.gradients.success);
    
    // Set default data in case API fails
    const defaultData = {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      data: [5000, 8000, 12000, 15000, 20000, 25000]
    };

    // First create chart with default data
    charts.trend = new Chart(ctx, {
      type: 'line',
      data: {
        labels: defaultData.labels,
        datasets: [{
          label: 'Sales Trend',
          data: defaultData.data,
          backgroundColor: gradient,
          borderColor: themeColors.success,
          borderWidth: 3,
          pointRadius: 4,
          pointBackgroundColor: '#fff',
          pointBorderColor: themeColors.success,
          pointHoverRadius: 6,
          pointHoverBackgroundColor: themeColors.success,
          pointHoverBorderColor: '#fff',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        ...chartConfigs.commonOptions,
        elements: {
          line: {
            tension: 0.4
          }
        }
      }
    });

    // Then fetch real data
    $.ajax({
      url: '/get-dashboard-data/',
      method: 'GET',
      success: function(response) {
        utils.debug('Trend data received', response);
        
        if (response && response.trend && response.trend.labels && response.trend.total_services && response.trend.total_bills) {
          charts.trend.data.labels = response.trend.labels;
          charts.trend.data.datasets = [
            {
              label: 'Total Services',
              data: response.trend.total_services,
              backgroundColor: utils.chartColors.success,
              borderColor: utils.chartColors.success,
              borderWidth: 2,
              borderRadius: 5
            },
            {
              label: 'Total Bills',
              data: response.trend.total_bills,
              backgroundColor: utils.chartColors.danger,
              borderColor: utils.chartColors.danger,
              borderWidth: 2,
              borderRadius: 5
            }
          ];
          charts.trend.update();
        } else if (response && response.trend && response.trend.labels && response.trend.data) {
          // fallback for old data
          charts.trend.data.labels = response.trend.labels;
          charts.trend.data.datasets[0].data = response.trend.data;
          charts.trend.update();
        }
      },
      error: function(error) {
        utils.debug('Error fetching trend data:', error);
      }
    });
  }

  // Update Dashboard Statistics
  function updateDashboardStats(data) {
    utils.debug('Updating dashboard stats', data);
    
    if (data.monthly) {
      $('#monthlyAmount').text(utils.formatCurrency(data.monthly.total_amount || 0));
      $('#monthlyOrders').text(data.monthly.total_orders || 0);
    }
    if (data.yearly) {
      $('#yearlyAmount').text(utils.formatCurrency(data.yearly.total_amount || 0));
      $('#yearlyOrders').text(data.yearly.total_orders || 0);
    }
  }

  // Handle Window Resize
  let resizeTimer;
  $(window).on('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      utils.debug('Window resized, reinitializing charts');
      initIncomeChart();
      initTrendChart();
    }, 250);
  });

  // Auto-refresh data every 5 minutes
  let refreshInterval = setInterval(function() {
    utils.debug('Refreshing charts');
    initIncomeChart();
    initTrendChart();
  }, 300000);

  // Initialize everything when document is ready
  utils.debug('Starting chart initialization');
  initIncomeChart();
  initTrendChart();

  // Year selector change event
  $('#yearSelector').on('change', function() {
    initIncomeChart();
    initTrendChart();
  });
});

