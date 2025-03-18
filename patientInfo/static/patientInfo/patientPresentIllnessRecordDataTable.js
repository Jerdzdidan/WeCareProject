$(document).ready(function() {
    // ==================== patientPresentIllness DataTable ====================
    const $patientPresentIllnessDataTable = $('#patientPresentIllnessDataTable').DataTable({
        order: [1, 'desc'],
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
    const $patientPresentIllnessEntries = $('#patientPresentIllnessCustomEntries');
    const $patientPresentIllnessSearch = $('#patientPresentIllnessSearchBar');
    const $patientPresentIllnessPagination = $('#patientPresentIllnessCustomPagination');

    // Stock Controls Event Handlers
    $patientPresentIllnessEntries.on('change', function() {
        $patientPresentIllnessDataTable.page.len(parseInt(this.value, 10)).draw();
    });

    $patientPresentIllnessSearch.on('keyup', function() {
        $patientPresentIllnessDataTable.search(this.value).draw();
    });

    // Stock Pagination Function
    function updatepatientPresentIllnessPagination() {
        const info = $patientPresentIllnessDataTable.page.info();
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
        
        $patientPresentIllnessPagination.html(paginationHtml + '</ul>');
    }

    // Stock Pagination Events
    $patientPresentIllnessDataTable.on('draw', updatepatientPresentIllnessPagination);
    $patientPresentIllnessPagination.on('click', 'a.page-link', function(e) {
        e.preventDefault();
        $patientPresentIllnessDataTable.page(parseInt($(this).data('page'), 10).draw('page'));
    });
    updatepatientPresentIllnessPagination();


});