$(document).ready(function() {
    // ==================== Stocks DataTable ====================
    const $trackingDataTable = $('#trackingDataTable').DataTable({
        order: [],
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
    });

    // Stock Table Elements (correct IDs)
    const $trackingEntries = $('#trackingCustomEntries');
    const $trackingSearch = $('#trackingSearchBar');
    const $trackingPagination = $('#trackingCustomPagination');

    // Stock Controls Event Handlers
    $trackingEntries.on('change', function() {
        $trackingDataTable.page.len(parseInt(this.value, 10)).draw();
    });

    $trackingSearch.on('keyup', function() {
        $trackingDataTable.search(this.value).draw();
    });

    // Stock Pagination Function
    function updatetrackingPagination() {
        const info = $trackingDataTable.page.info();
        let paginationHtml = '<ul class="pagination justify-content-start ms-2">';
        
        // Previous Button
        if (info.page > 0) {
            paginationHtml += `<li class="page-item">
                <a class="page-link text-success" data-page="${info.page-1}" href="#">Prev</a>
            </li>`;
        }

        // Page Numbers
        for (let i = 0; i < info.pages; i++) {
            paginationHtml += `<li class="page-item ${i === info.page ? 'active' : ''}">
                <a class="page-link ${i === info.page ? 'bg-success text-white' : 'text-success'}" 
                   data-page="${i}" href="#">${i+1}</a>
            </li>`;
        }

        // Next Button
        if (info.page < info.pages - 1) {
            paginationHtml += `<li class="page-item">
                <a class="page-link text-success" data-page="${info.page+1}" href="#">Next</a>
            </li>`;
        }
        
        $trackingPagination.html(paginationHtml + '</ul>');
    }

    // Stock Pagination Events
    $trackingDataTable.on('draw', updatetrackingPagination);
    $trackingPagination.on('click', 'a.page-link', function(e) {
        e.preventDefault();
        $trackingDataTable.page(parseInt($(this).data('page'), 10).draw('page'));
    });
    updatetrackingPagination();


});