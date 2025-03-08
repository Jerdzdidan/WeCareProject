$(document).ready(function() {
    // Toggle the sidebar visibility by collapsing its width.
    $('#sidebarToggle').on('click', function() {
      $('#sidebar').toggleClass('sidebar-hidden');
    });
  
    // Close the sidebar when the close button is clicked (if it exists)
    if ($('#sidebarClose').length) {
      $('#sidebarClose').on('click', function() {
        $('#sidebar').addClass('sidebar-hidden');
      });
    }

    // Sidebar dropdown functionality
    $(document).ready(function () {
      $("#patientToggle").click(function (e) {
        e.preventDefault();
        $("#patientDropdown").slideToggle(300); 
        $(this).toggleClass("active"); 
      });
    });

    $(document).ready(function () {
      $("#reportsToggle").click(function (e) {
        e.preventDefault();
        $("#reportsDropdown").slideToggle(300); 
        $(this).toggleClass("active"); 
      });
    });
    
    $('a.nav-link.rounded[data-bs-toggle="collapse"]').on('click', function(e) {
      e.preventDefault(); 
      
      var targetSelector = $(this).attr('href');
      var $target = $(targetSelector);
      
      $target.slideToggle(300);
      
      var expanded = $(this).attr('aria-expanded') === 'true';
      $(this).attr('aria-expanded', !expanded);
    });

    // Clock functionality: update clock every second if the clock element exists
    if ($('#clock').length) {
      function updateClock() {
        const now = new Date();
        const month = now.toLocaleString('en-US', { month: 'short' });
        const day = now.getDate();
        const year = now.getFullYear();
        const formattedDate = `${month}. ${day}, ${year}`;
        const formattedTime = now.toLocaleTimeString();
        $('#clock').html(`${formattedDate}, ${formattedTime}`);
      }
      updateClock();
      setInterval(updateClock, 1000);
    }

    // DataTables
    const $dataTable = $('#dataTable').DataTable({
      buttons: [{
        extend: 'csv',
        exportOptions: {
            format: {
                footer: function(data, row, column, node) {
                    return '';
                }
            }
        }
      }],
      order: [0, 'asc'], 
      layout: {
          topStart: null,
          topEnd: null,
          bottomStart: null,
          bottomEnd: null,
          bottom: null,
      },
      language: {
          emptyTable: "No data available in table"
      },
      responsive: true,
      autoWidth: false,
    //   "paging": true,
    //   "ordering": true,
    //   "info": true,
    //   "lengthChange": true,
    //   "autoWidth": true,
    //   "responsive": true,
    //   "searching": true,
    //   "scrollX": true,
    //   "scrollY": true,
    //   "scrollCollapse": true,
    //   "pagingType": "simple",
    //   "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    //   "language": {
    //     "lengthMenu": "Display _MENU_ records per page",
    //     "zeroRecords": "No records found",
    //     "info": "Showing page _PAGE_ of _PAGES_",
    //     "infoEmpty": "No records available",
    //     "infoFiltered": "(filtered from _MAX_ total records)",
    //     "search": "Search:",
    //     "paginate": {
    //       "first": "First",
    //       "last": "Last",
    //       "next": "Next",
    //       "previous": "Previous"
    //     }
    //   }
    });


    // Custom DataTable Functions:
    const $dataTableEntries = $('#customEntries');
    const $dataTableSearch = $('#searchBar');
    const $dataTablePagination = $('#customPagination');

    $dataTableEntries.on('change', function() {
        var newLength = parseInt($(this).val(), 10);
        $dataTable.page.len(newLength).draw();
    });

    $dataTableSearch.on('keyup', function() {
        $dataTable.search(this.value).draw();
    });

    function updatePagination() {
        var info = $dataTable.page.info();
        var paginationHtml = '';
    
        // Previous button
        paginationHtml += '<ul class="pagination justify-content-start ms-2">';
        if (info.page > 0) {
            paginationHtml += '<li class="page-item"><a href="#" class="page-link text-success" data-page="' + (info.page - 1) + '">Prev</a></li>';
        }
      
        for (var i = 0; i < info.pages; i++) {
            if (i === info.page) {
            paginationHtml += '<li class="page-item active"><a href="#" class="page-link bg-success text-white" data-page="' + i + '">' + (i + 1) + '</a></li>';
            } else {
            paginationHtml += '<li class="page-item"><a href="#" class="page-link text-success" data-page="' + i + '">' + (i + 1) + '</a></li>';
            }
        }
      
        if (info.page < info.pages - 1) {
            paginationHtml += '<li class="page-item"><a href="#" class="page-link text-success" data-page="' + (info.page + 1) + '">Next</a></li>';
        }
        paginationHtml += '</ul>';
    
        $dataTablePagination.html(paginationHtml);
      }
    
      $dataTable.on('draw', function() {
        updatePagination();
      });
    
      $dataTablePagination.on('click', 'a.page-link', function(e) {
        e.preventDefault();
        var page = $(this).data('page');
        $dataTable.page(page).draw('page');
      });
    
      updatePagination();
    
    // === PRINTING AND EXPORTING
    $('#exportBtn').on('click', function() {
        console.log("ok");
        $dt.button('.buttons-csv').trigger();
    });

    function printTable() {
      const dt = $dt;
      const printWindow = window.open('', '', 'height=600,width=1000');
      const tableElement = document.getElementById('voyageTable');
      
      const clonedTable = tableElement.cloneNode(true);
      clonedTable.classList.add('table-sm', 'w-100', 'print-table');

      $(clonedTable).find('tbody').empty();
      var allRows = dt.rows({ search: 'applied' }).nodes();
      $(clonedTable).find('tbody').append($(allRows).clone());

      const tfoot = clonedTable.querySelector('tfoot');
      if (tfoot) {
          const summaryTbody = document.createElement('tbody');
          summaryTbody.className = 'summary-tbody'; 
          while (tfoot.rows.length > 0) {
              const row = tfoot.rows[0];
              row.className = 'summary-row'; 
              summaryTbody.appendChild(row);
          }
          clonedTable.appendChild(summaryTbody);
          clonedTable.removeChild(tfoot);
      }

      printWindow.document.write('<html><head><title>Print Table</title>');
      printWindow.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.2/dist/css/bootstrap.min.css">');
      printWindow.document.write('<style>');
      printWindow.document.write(`
          @media print {
              .print-table thead th {
                  background-color: rgb(219, 219, 219) !important;
                  -webkit-print-color-adjust: exact; 
                  color-adjust: exact;
              }
              .summary-tbody td {
                  background-color: #e9ecef !important;
                  -webkit-print-color-adjust: exact; 
                  color-adjust: exact;
                  font-weight: bold;
              }
              .print-table .text-end {
                  text-align: right !important;
              }
              .print-table tfoot th,
              .print-table tfoot td {
                  color: black !important; 
                  font-weight: bold;
                  background-color: #e9ecef !important;
                  border-top: 2px solid #000 !important;
                  font-weight: bold;
              }
          }
          .print-table .text-end {
              text-align: right !important;
          }
          .print-table {
              width: 100% !important;
              font-size: 12px !important;
          }
          .print-table th, 
          .print-table td {
              padding: 4px !important;
          }
          .print-table thead th {
              background-color: rgb(219, 219, 219) !important;
          }
          .summary-tbody td {
              color: black !important; 
              font-weight: bold;
              background-color: #e9ecef !important;
              border-top: 2px solid #000 !important;
          }
          .print-table tfoot th,
          .print-table tfoot td {
              color: black !important; 
              font-weight: bold;
              background-color: #e9ecef !important;
              border-top: 2px solid #000 !important;
              font-weight: bold;
          }
      `);
      printWindow.document.write('</style></head><body>');

      const customContent = `
          <div class="container">
              <div class="mb-3">
                  <div class="text-left" style="font-size: 20px; font-weight: bold;">
                      MAAYO SHIPPING INC.
                  </div>
                  <div class="text-left" style="font-size: 10px;">
                      Tampi, San Jose, Negros Oriental<br>
                      Contact No. +63-917-710-7080 / +63-35-527-2818<br>
                      VAT REG TIN 000-612-056-000 / RDOC NO. 94-790-000346
                  </div>
                  <hr class="my-2" style="border-top: 1px solid #000;">
                  <div class="text-center" style="font-size: 30px; margin: 13px 0px 13px;">
                      <h5> VOYAGE PER ROUTE REPORT </h5>
                  </div>
                  <div class="text-left" style="font-size: 12px;">
                  </div>
              </div>
              <div class="table-responsive">
                  ${clonedTable.outerHTML}
              </div>
              <div class="text-left mt-4"><small>Prepared by: _____________________________</small></div>
              <div class="text-left mb-5" style="padding-left: 135px;"><small>Name</small></div>
          </div>
      `;

      printWindow.document.write(customContent);

      printWindow.document.write(`
              <div style="position: fixed; bottom: -12px; left: 0; width: 100%; text-align: center; font-size: 12px; padding: 10px; overflow: hidden;">
                  <div style="background-color: white; height: auto;">
                      <hr class="my-0" style="border-top: 1px solid #000;">
                      Printed By: <?= session()->get('username') ?>, ${new Date().toLocaleString('en-US', {month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' })}
                  </div>
              </div>
          `);
      printWindow.document.close();

      setTimeout(() => {
          printWindow.print();
      }, 500);
  }

  $('#printBtn').on('click', function() {
      printTable();
  });

});