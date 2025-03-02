$(document).ready(function() {
    // ==================== patientMedicineTracking DataTable ====================
    const $patientMedicineTrackingDataTable = $('#patientMedicineTrackingDataTable').DataTable({
        order: [5, 'desc'],
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
    const $patientMedicineTrackingEntries = $('#patientMedicineTrackingCustomEntries');
    const $patientMedicineTrackingSearch = $('#patientMedicineTrackingSearchBar');
    const $patientMedicineTrackingPagination = $('#patientMedicineTrackingCustomPagination');

    // Stock Controls Event Handlers
    $patientMedicineTrackingEntries.on('change', function() {
        $patientMedicineTrackingDataTable.page.len(parseInt(this.value, 10)).draw();
    });

    $patientMedicineTrackingSearch.on('keyup', function() {
        $patientMedicineTrackingDataTable.search(this.value).draw();
    });

    // Stock Pagination Function
    function updatepatientMedicineTrackingPagination() {
        const info = $patientMedicineTrackingDataTable.page.info();
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
        
        $patientMedicineTrackingPagination.html(paginationHtml + '</ul>');
    }

    // Stock Pagination Events
    $patientMedicineTrackingDataTable.on('draw', updatepatientMedicineTrackingPagination);
    $patientMedicineTrackingPagination.on('click', 'a.page-link', function(e) {
        e.preventDefault();
        $patientMedicineTrackingDataTable.page(parseInt($(this).data('page'), 10).draw('page'));
    });
    updatepatientMedicineTrackingPagination();


});