(function($) {
  'use strict';
  $.fn.andSelf = function() {
    return this.addBack.apply(this, arguments);
  }
  $(function() {
    if ($("#currentBalanceCircle").length) {
      var bar = new ProgressBar.Circle(currentBalanceCircle, {
        color: '#000',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 12,
        trailWidth: 12,
        trailColor: '#0d0d0d',
        easing: 'easeInOut',
        duration: 1400,
        text: {
          autoStyleContainer: false
        },
        from: { color: '#d53f3a', width: 12 },
        to: { color: '#d53f3a', width: 12 },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
      
          var value = Math.round(circle.value() * 100);
          circle.setText('');
      
        }
      });

      bar.text.style.fontSize = '1.5rem';
      bar.animate(0.4);  // Number from 0.0 to 1.0
    }
    if($('#audience-map').length) {
      $('#audience-map').vectorMap({
        map: 'world_mill_en',
        backgroundColor: 'transparent',
        panOnDrag: true,
        focusOn: {
          x: 0.5,
          y: 0.5,
          scale: 1,
          animate: true
        },
        series: {
          regions: [{
            scale: ['#3d3c3c', '#f2f2f2'],
            normalizeFunction: 'polynomial',
            values: {

              "BZ": 75.00,
              "US": 56.25,
              "AU": 15.45,
              "GB": 25.00,
              "RO": 10.25,
              "GE": 33.25
            }
          }]
        }
      });
    }
    if ($("#transaction-history").length) {
      var areaData = {
        labels: ['Total Centers', 'Total Bills', 'Total Services'],
        datasets: [{
            data: [{ total_centers },
              { total_bills },
              { total_services }],
            backgroundColor: [
              "#111111","#00d25b","#ffab00"
            ]
          }
        ]
      };
      var areaOptions = {
        responsive: true,
        maintainAspectRatio: true,
        segmentShowStroke: false,
        cutoutPercentage: 70,
        elements: {
          arc: {
              borderWidth: 0
          }
        },      
        legend: {
          display: false
        },
        tooltips: {
          enabled: true
        }
      }
      var transactionhistoryChartPlugins = {
        beforeDraw: function(chart) {
          var width = chart.chart.width,
              height = chart.chart.height,
              ctx = chart.chart.ctx;
      
          ctx.restore();
          var fontSize = 1;
          ctx.font = fontSize + "rem sans-serif";
          ctx.textAlign = 'left';
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#ffffff";
      
          var text = "67%", 
              textX = Math.round((width - ctx.measureText(text).width) / 2),
              textY = height / 2.4;
      
          ctx.fillText(text, textX, textY);

          ctx.restore();
          var fontSize = 0.75;
          ctx.font = fontSize + "rem sans-serif";
          ctx.textAlign = 'left';
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#6c7293";

          var texts = "Total", 
              textsX = Math.round((width - ctx.measureText(text).width) / 1.93),
              textsY = height / 1.7;
      
          ctx.fillText(texts, textsX, textsY);
          ctx.save();
        }
      }
      var transactionhistoryChartCanvas = $("#transaction-history").get(0).getContext("2d");
      var transactionhistoryChartCanvas = new Chart(transactionhistoryChartCanvas, {
        type: 'doughnut',
        data: areaData,
        options: areaOptions,
        plugins: transactionhistoryChartPlugins
      });
    }
    if ($("#transaction-history-arabic").length) {
      var areaData = {
        labels: ["Total GSK", "Total Billing","Total Services"],
        datasets: [{
          data: [{ total_centers }, { total_bills }, { total_services }],
            backgroundColor: [
              "#111111","#00d25b","#ffab00"
            ]
          }
        ]
      };
      var areaOptions = {
        responsive: true,
        maintainAspectRatio: true,
        segmentShowStroke: false,
        cutoutPercentage: 70,
        elements: {
          arc: {
              borderWidth: 0
          }
        },      
        legend: {
          display: false
        },
        tooltips: {
          enabled: true
        }
      }
      var transactionhistoryChartPlugins = {
        beforeDraw: function(chart) {
          var width = chart.chart.width,
              height = chart.chart.height,
              ctx = chart.chart.ctx;
      
          ctx.restore();
          var fontSize = 1;
          ctx.font = fontSize + "rem sans-serif";
          ctx.textAlign = 'left';
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#ffffff";
      
          var text = "67%", 
              textX = Math.round((width - ctx.measureText(text).width) / 2),
              textY = height / 2.4;
      
          ctx.fillText(text, textX, textY);

          ctx.restore();
          var fontSize = 0.75;
          ctx.font = fontSize + "rem sans-serif";
          ctx.textAlign = 'left';
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#6c7293";

          var texts = "مجموع", 
              textsX = Math.round((width - ctx.measureText(text).width) / 1.93),
              textsY = height / 1.7;
      
          ctx.fillText(texts, textsX, textsY);
          ctx.save();
        }
      }
      var transactionhistoryChartCanvas = $("#transaction-history-arabic").get(0).getContext("2d");
      var transactionhistoryChartCanvas = new Chart(transactionhistoryChartCanvas, {
        type: 'doughnut',
        data: areaData,
        options: areaOptions,
        plugins: transactionhistoryChartPlugins
      });
    }
    if ($('#owl-carousel-basic').length) {
      $('#owl-carousel-basic').owlCarousel({
        loop: true,
        margin: 10,
        dots: false,
        nav: true,
        autoplay: true,
        autoplayTimeout: 4500,
        navText: ["<i class='mdi mdi-chevron-left'></i>", "<i class='mdi mdi-chevron-right'></i>"],
        responsive: {
          0: {
            items: 1
          },
          600: {
            items: 1
          },
          1000: {
            items: 1
          }
        }
      });
    }
    var isrtl = $("body").hasClass("rtl");
    if ($('#owl-carousel-rtl').length) {
      $('#owl-carousel-rtl').owlCarousel({
        loop: true,
        margin: 10,
        dots: false,
        nav: true,
        rtl: isrtl,
        autoplay: true,
        autoplayTimeout: 4500,
        navText: ["<i class='mdi mdi-chevron-right'></i>", "<i class='mdi mdi-chevron-left'></i>"],
        responsive: {
          0: {
            items: 1
          },
          600: {
            items: 1
          },
          1000: {
            items: 1
          }
        }
      });
    }
    });
})(jQuery);

// Bar Charts Starts

google.charts.load('current', {
  'packages': ['bar']
});
google.charts.setOnLoadCallback(drawStuff);

function drawStuff() {
  var data = new google.visualization.arrayToDataTable([
    ['Opening Move', 'Percentage'],
    ["King's pawn (e4)", 44],
    ["Queen's pawn (d4)", 31],
    ["Knight to King 3 (Nf3)", 12],
    ["Queen's bishop pawn (c4)", 10],
    ['Other', 3]
  ]);

  var options = {
    title: 'Approximating Normal Distribution',
    legend: {
      position: 'none'
    },
    colors: ['#76C1FA'],

    chartArea: {
      width: 401
    },
    hAxis: {
      ticks: [-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1]
    },
    bar: {
      gap: 0
    },

    histogram: {
      bucketSize: 0.02,
      maxNumBuckets: 200,
      minValue: -1,
      maxValue: 1
    }
  };

  var chart = new google.charts.Bar(document.getElementById('Bar-chart'));
  chart.draw(data, options);


// Doughnut Chart Configuration
if (document.getElementById("doughnutChart")) {
  try {
      // Ensure variables are available
      if (typeof total_centers !== 'undefined' && typeof total_bills !== 'undefined' && typeof total_services !== 'undefined') {
          console.log("Doughnut Chart Data:", total_centers, total_bills, total_services);

          var doughnutChartCanvas = document.getElementById("doughnutChart").getContext("2d");
          var areaData = {
              labels: ["Total GSK", "Total Billing", "Total Services"],
              datasets: [{
                  data: [total_centers, total_bills, total_services], // Use variables from Django
                  backgroundColor: ["#111111", "#00d25b", "#ffab00"]
              }]
          };

          var doughnutChartOptions = {
              responsive: true,
              animation: {
                  animateScale: true,
                  animateRotate: true
              }
          };

          new Chart(doughnutChartCanvas, {
              type: 'doughnut',
              data: areaData,
              options: doughnutChartOptions
          });

      } else {
          console.error("Doughnut Chart: Missing data variables (total_centers, total_bills, total_services). Ensure these are defined in the template.");
      }
  } catch (error) {
      console.error("Doughnut Chart Error:", error);
  }
} else {
  console.warn("Doughnut Chart: Canvas element with ID 'doughnutChart' not found.");
}

// Other existing chart configurations and logic (if any) should remain here.

// Ensure existing functionality for progress bars and carousel remains intact.

// Progress bar animation logic
$(document).ready(function () {
  $('.progress-bar').each(function () {
      var width = $(this).attr('aria-valuenow');
      $(this).css('width', width + '%');
  });
});

// Carousel functionality
if ($("#carouselExampleIndicators").length) {
  var carouselElement = $("#carouselExampleIndicators");
  carouselElement.carousel();
}


};


// Bar Charts Ends


