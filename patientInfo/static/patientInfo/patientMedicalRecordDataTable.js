$(document).ready(function() {
    // ==================== patientMedicalRecord DataTable ====================
    const $patientMedicalRecordDataTable = $('#patientMedicalRecordDataTable').DataTable({
        order: [2, 'desc'],
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
    const $patientMedicalRecordEntries = $('#patientMedicalRecordCustomEntries');
    const $patientMedicalRecordSearch = $('#patientMedicalRecordSearchBar');
    const $patientMedicalRecordPagination = $('#patientMedicalRecordCustomPagination');

    // Stock Controls Event Handlers
    $patientMedicalRecordEntries.on('change', function() {
        $patientMedicalRecordDataTable.page.len(parseInt(this.value, 10)).draw();
    });

    $patientMedicalRecordSearch.on('keyup', function() {
        $patientMedicalRecordDataTable.search(this.value).draw();
    });

    // Stock Pagination Function
    function updatepatientMedicalRecordPagination() {
        const info = $patientMedicalRecordDataTable.page.info();
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
        
        $patientMedicalRecordPagination.html(paginationHtml + '</ul>');
    }

    // Stock Pagination Events
    $patientMedicalRecordDataTable.on('draw', updatepatientMedicalRecordPagination);
    $patientMedicalRecordPagination.on('click', 'a.page-link', function(e) {
        e.preventDefault();
        $patientMedicalRecordDataTable.page(parseInt($(this).data('page'), 10).draw('page'));
    });
    updatepatientMedicalRecordPagination();


});