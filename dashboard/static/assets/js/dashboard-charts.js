document.addEventListener('DOMContentLoaded', function() {
    let barChart = null;
    let doughnutChart = null;
    const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    // Format currency values
    function formatCurrency(value) {
        return '₹' + value.toLocaleString('en-IN');
    }

    // Check if data is empty
    function isDataEmpty(data) {
        if (Array.isArray(data)) {
            return data.every(val => val === 0 || val === null || val === undefined);
        }
        return !data || Object.values(data).every(val => val === 0 || val === null || val === undefined);
    }

    // Show no data message on canvas
    function showNoDataMessage(ctx, message = 'No data available') {
        const canvas = ctx.canvas;
        ctx.save();
        ctx.fillStyle = '#666';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(message, canvas.width / 2, canvas.height / 2);
        ctx.restore();
    }

    // Initialize bar chart
    function initBarChart(yearData) {
        const barCtx = document.getElementById('barChart')?.getContext('2d');
        if (!barCtx) return;
        
        if (barChart) {
            barChart.destroy();
        }

        // Check if data is empty
        if (!yearData || isDataEmpty(yearData)) {
            showNoDataMessage(barCtx, 'No transaction data available for selected year');
            return;
        }
        
        barChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: monthLabels.map(month => `${month}`),
                datasets: [
                    {
                        label: 'Total Billing',
                        data: yearData.billing || yearData,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                    },
                    {
                        label: 'Total Services',
                        data: yearData.services || [],
                        backgroundColor: 'rgba(75, 192, 192, 0.5)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
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
                                return context.dataset.label + ': ' + formatCurrency(context.raw || 0);
                            }
                        }
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    // Initialize doughnut chart
    function initDoughnutChart() {
        const doughnutCtx = document.getElementById('doughnutChart')?.getContext('2d');
        if (!doughnutCtx) return;
            
            if (doughnutChart) {
                doughnutChart.destroy();
            }

        let serviceDistribution;
        try {
            const serviceDistributionElement = document.getElementById('serviceDistributionData');
            serviceDistribution = serviceDistributionElement ? JSON.parse(serviceDistributionElement.value) : null;
        } catch (error) {
            console.error('Error parsing service distribution data:', error);
            serviceDistribution = null;
        }

        // Check if data is empty
        if (!serviceDistribution || isDataEmpty(serviceDistribution)) {
            showNoDataMessage(doughnutCtx, 'No service distribution data available');
            return;
        }
            
            doughnutChart = new Chart(doughnutCtx, {
                type: 'doughnut',
                data: {
                labels: ['Total Services', 'Total Billing', 'Additional Services'],
                    datasets: [{
                    data: [
                        serviceDistribution.total_services || 0,
                        serviceDistribution.total_billing || 0,
                        serviceDistribution.additional_services || 0
                    ],
                        backgroundColor: [
                        'rgba(75, 192, 192, 0.7)',  // Services - Teal
                        'rgba(54, 162, 235, 0.7)',  // Billing - Blue
                        'rgba(255, 206, 86, 0.7)'   // Additional - Yellow
                        ],
                        borderColor: [
                            'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                const value = context.raw || 0;
                                const label = context.label;
                                if (label.includes('Billing')) {
                                    return label + ': ' + formatCurrency(value);
                                }
                                return label + ': ' + value;
                                }
                            }
                        }
                    }
                }
            });
    }

    // Handle year selection change
    if (document.getElementById('yearSelector')) {
        let yearlyData;
        try {
            const yearlyDataElement = document.getElementById('yearlyData');
            yearlyData = yearlyDataElement ? JSON.parse(yearlyDataElement.value) : null;
        } catch (error) {
            console.error('Error parsing yearly data:', error);
            yearlyData = null;
        }

        const yearSelector = document.getElementById('yearSelector');
        
        // Initialize with current year's data
        if (yearlyData && yearSelector) {
        initBarChart(yearlyData[yearSelector.value]);
        
        // Update chart when year changes
        yearSelector.addEventListener('change', function() {
            const selectedYear = this.value;
            initBarChart(yearlyData[selectedYear]);
        });
        } else {
            const barCtx = document.getElementById('barChart')?.getContext('2d');
            if (barCtx) {
                showNoDataMessage(barCtx, 'No yearly data available');
            }
        }
    }

    // Initialize doughnut chart
    initDoughnutChart();

    // Update dashboard statistics
    function updateDashboardStats(data) {
        const elements = {
            totalServices: document.querySelector('.total-services'),
            totalBilling: document.querySelector('.total-billing'),
            monthlyServices: document.querySelector('.monthly-services'),
            monthlyBilling: document.querySelector('.monthly-billing')
        };

        if (elements.totalServices) {
            elements.totalServices.textContent = data?.total_services || '0';
        }
        if (elements.totalBilling) {
            elements.totalBilling.textContent = formatCurrency(data?.total_billing || 0);
        }
        if (elements.monthlyServices) {
            elements.monthlyServices.textContent = data?.monthly_services || '0';
        }
        if (elements.monthlyBilling) {
            elements.monthlyBilling.textContent = formatCurrency(data?.monthly_billing || 0);
        }
    }

    // Auto-refresh data every 5 minutes
    function refreshData() {
        fetch('/distributor/dashboard-data/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data && !isDataEmpty(data)) {
                    updateDashboardStats(data);
                    initDoughnutChart();
                } else {
                    const elements = document.querySelectorAll('.total-services, .total-billing, .monthly-services, .monthly-billing');
                    elements.forEach(element => {
                        if (element) {
                            element.textContent = element.classList.contains('total-billing') || 
                                                element.classList.contains('monthly-billing') ? 
                                                formatCurrency(0) : '0';
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error refreshing dashboard data:', error);
                // Show error state in UI
                const elements = document.querySelectorAll('.total-services, .total-billing, .monthly-services, .monthly-billing');
                elements.forEach(element => {
                    if (element) {
                        element.textContent = 'Error';
                    }
                });
            });
    }

    // Initial load and set up auto-refresh
    refreshData();
    setInterval(refreshData, 300000); // 5 minutes

    // Handle window resize
    window.addEventListener('resize', function() {
        if (barChart) {
            barChart.resize();
        }
        if (doughnutChart) {
            doughnutChart.resize();
        }
    });
}); 