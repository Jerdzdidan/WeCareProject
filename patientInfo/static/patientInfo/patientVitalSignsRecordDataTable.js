$(document).ready(function() {
    // ==================== patientVitalSigns DataTable ====================
    const $patientVitalSignsDataTable = $('#patientVitalSignsDataTable').DataTable({
        order: [0, 'desc'],
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
    const $patientVitalSignsEntries = $('#patientVitalSignsCustomEntries');
    const $patientVitalSignsSearch = $('#patientVitalSignsSearchBar');
    const $patientVitalSignsPagination = $('#patientVitalSignsCustomPagination');

    // Stock Controls Event Handlers
    $patientVitalSignsEntries.on('change', function() {
        $patientVitalSignsDataTable.page.len(parseInt(this.value, 10)).draw();
    });

    $patientVitalSignsSearch.on('keyup', function() {
        $patientVitalSignsDataTable.search(this.value).draw();
    });

    // Stock Pagination Function
    function updatepatientVitalSignsPagination() {
        const info = $patientVitalSignsDataTable.page.info();
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
        
        $patientVitalSignsPagination.html(paginationHtml + '</ul>');
    }

    // Stock Pagination Events
    $patientVitalSignsDataTable.on('draw', updatepatientVitalSignsPagination);
    $patientVitalSignsPagination.on('click', 'a.page-link', function(e) {
        e.preventDefault();
        $patientVitalSignsDataTable.page(parseInt($(this).data('page'), 10).draw('page'));
    });
    updatepatientVitalSignsPagination();


});