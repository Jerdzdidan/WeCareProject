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
  
    // Clock functionality: update clock every second if the clock element exists
    if ($('#clock').length) {
      function updateClock() {
        const now = new Date();
        const formattedDate = now.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        });
        const formattedTime = now.toLocaleTimeString();
        $('#clock').html(`${formattedDate}, ${formattedTime}`);
      }
      updateClock();
      setInterval(updateClock, 1000);
    }
    
    // DataTables
    const $dataTable = $('#dataTable').DataTable({
        layout: {
            topStart: null,
            topEnd: null,
            bottomStart: null,
            bottomEnd: null,
            bottom: null,

        },
        language: {
            emptyTable: "No data available in table"
        }
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
        paginationHtml += '<ul class="pagination justify-content-center">';
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
    

});