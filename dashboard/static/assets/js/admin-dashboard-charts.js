// Admin Dashboard Charts

document.addEventListener('DOMContentLoaded', function() {
    // Initialize both charts
    let monthlyIncomeChart = null;
    let doughnutChart = null;

    // Function to format currency values
    function formatCurrency(value) {
        return '₹' + value.toLocaleString('en-IN');
    }

    // Initialize doughnut chart
    function initDoughnutChart(data) {
        const ctx = document.getElementById('doughnutChart').getContext('2d');
        
        if (doughnutChart) {
            doughnutChart.destroy();
        }

        doughnutChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Service Billing', 'Equipment Sales', 'Additional Services'],
                datasets: [{
                    data: [data.total_bills || 0, data.equipment_sales || 0, data.additional_services || 0],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Function to initialize the monthly income chart
    function initMonthlyIncomeChart(data) {
        const ctx = document.getElementById('monthlyIncomeChart').getContext('2d');
        
        if (monthlyIncomeChart) {
            monthlyIncomeChart.destroy();
        }

        monthlyIncomeChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [
                    {
                        label: 'Total Sales',
                        data: data.total_amounts || [],
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Base Amount',
                        data: data.base_amounts || [],
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'GST',
                        data: data.gst_amounts || [],
                        backgroundColor: 'rgba(255, 206, 86, 0.5)',
                        borderColor: 'rgba(255, 206, 86, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + formatCurrency(context.raw);
                            }
                        }
                    },
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Function to load initial dashboard data
    function loadDashboardData() {
        fetch('/get-dashboard-data/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Initialize doughnut chart with overall data
                initDoughnutChart(data);
                
                // Update summary statistics
                if (data.total_gsk) {
                    document.querySelector('.total-gsk').textContent = data.total_gsk;
                }
                if (data.total_billing) {
                    document.querySelector('.total-billing').textContent = data.total_billing;
                }
            })
            .catch(error => {
                console.error('Error loading dashboard data:', error);
            });
    }

    // Function to update monthly data based on selected year
    function updateMonthlyData(year) {
        const chartCanvas = document.getElementById('monthlyIncomeChart');
        if (chartCanvas) {
            chartCanvas.style.opacity = '0.5';
        }

        fetch(`/get-monthly-income-data/?year=${year}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // Update the chart
                initMonthlyIncomeChart(data);
                
                // Update summary cards with null checks
                const cards = {
                    'thisMonthSales': data.this_month?.total_amount || 0,
                    'thisMonthBase': data.this_month?.base_amount || 0,
                    'thisMonthGST': data.this_month?.gst_amount || 0
                };

                Object.entries(cards).forEach(([id, value]) => {
                    const element = document.getElementById(id);
                    if (element) {
                        element.textContent = formatCurrency(value);
                    }
                });

                // Update monthly totals
                document.querySelectorAll('.monthly-sales, .monthly-base, .monthly-gst').forEach(element => {
                    if (element) {
                        const type = element.classList[0].split('-')[1];
                        const value = data.this_month?.[`${type === 'sales' ? 'total' : type}_amount`] || 0;
                        element.textContent = formatCurrency(value);
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching monthly data:', error);
            })
            .finally(() => {
                if (chartCanvas) {
                    chartCanvas.style.opacity = '1';
                }
            });
    }

    // Load initial dashboard data
    loadDashboardData();

    // Event listeners for year selectors
    ['incomeYearSelector', 'analysisYearSelector'].forEach(selectorId => {
        const selector = document.getElementById(selectorId);
        if (selector) {
            selector.addEventListener('change', function() {
                updateMonthlyData(this.value);
            });

            // Initial load if this selector exists
            if (selector === document.getElementById('incomeYearSelector')) {
                updateMonthlyData(selector.value);
            }
        }
    });
}); 