document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing retailer dashboard charts...');
    
    // Utility function to format currency in Indian Rupees
    function formatIndianRupees(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    // Generate random colors for the chart
    function generateRandomColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            colors.push(`hsl(${Math.random() * 360}, 70%, 50%)`);
        }
        return colors;
    }

    // Check if data is empty
    function isDataEmpty(data) {
        if (!data) return true;
        if (Array.isArray(data)) return data.length === 0;
        if (typeof data === 'object') return Object.keys(data).length === 0;
        return false;
    }

    // Show no data message on canvas
    function showNoDataMessage(ctx, message) {
        ctx.font = '14px Arial';
        ctx.fillStyle = '#6c757d';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(message, ctx.canvas.width / 2, ctx.canvas.height / 2);
    }

    // Initialize the services distribution chart
    let servicesChart;

    function initializeServicesChart() {
        const ctx = document.getElementById('servicesDistributionChart').getContext('2d');
        servicesChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Function to update the dashboard data
    function updateDashboardData() {
        fetch('/retailer/services-distribution/')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error fetching data:', data.error);
                    return;
                }

                // Update the chart
                servicesChart.data.labels = data.labels;
                servicesChart.data.datasets[0].data = data.data;
                servicesChart.data.datasets[0].backgroundColor = generateRandomColors(data.labels.length);
                servicesChart.update();

                // Update the statistics
                document.getElementById('totalServices').textContent = data.total_services;
                document.getElementById('totalBilling').textContent = formatIndianRupees(data.total_billing);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    // Initialize everything when the document is ready
    initializeServicesChart();
    updateDashboardData();

    // Update data every 5 minutes
    setInterval(updateDashboardData, 5 * 60 * 1000);

    // Handle window resize
    window.addEventListener('resize', function() {
        if (servicesChart) {
            servicesChart.resize();
        }
    });
}); 