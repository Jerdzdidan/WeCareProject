$(document).ready(function() {
    // ==================== Stocks DataTable ====================
    const $stocksDataTable = $('#stocksDataTable').DataTable({
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
    const $stocksEntries = $('#stocksCustomEntries');
    const $stocksSearch = $('#stocksSearchBar');
    const $stocksPagination = $('#stocksCustomPagination');

    // Stock Controls Event Handlers
    $stocksEntries.on('change', function() {
        $stocksDataTable.page.len(parseInt(this.value, 10)).draw();
    });

    $stocksSearch.on('keyup', function() {
        $stocksDataTable.search(this.value).draw();
    });

    // Stock Pagination Function
    function updateStocksPagination() {
        const info = $stocksDataTable.page.info();
        let paginationHtml = '<ul class="pagination justify-content-center">';
        
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
        
        $stocksPagination.html(paginationHtml + '</ul>');
    }

    // Stock Pagination Events
    $stocksDataTable.on('draw', updateStocksPagination);
    $stocksPagination.on('click', 'a.page-link', function(e) {
        e.preventDefault();
        $stocksDataTable.page(parseInt($(this).data('page'), 10).draw('page'));
    });
    updateStocksPagination();

});