document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const dateSelector = document.getElementById('dateSelector');
    const editSubstitutionButtons = document.querySelectorAll('.edit-substitution');
    const editSubstitutionModal = document.getElementById('editSubstitutionModal');
    const saveSubstitutionBtn = document.getElementById('saveSubstitutionBtn');
    
    // Date change event handler
    if (dateSelector) {
        dateSelector.addEventListener('change', function() {
            window.location.href = `/admin/substitution?date=${this.value}`;
        });
    }
    
    // Edit substitution button click events
    if (editSubstitutionButtons.length > 0) {
        editSubstitutionButtons.forEach(button => {
            button.addEventListener('click', function() {
                const substitutionId = this.getAttribute('data-id');
                
                // Store the ID in the modal
                document.getElementById('substitutionId').value = substitutionId;
                
                // Fetch available teachers for this period
                fetchAvailableTeachers(substitutionId);
                
                // Show the modal
                const modal = new bootstrap.Modal(editSubstitutionModal);
                modal.show();
            });
        });
    }
    
    // Save substitution changes
    if (saveSubstitutionBtn) {
        saveSubstitutionBtn.addEventListener('click', function() {
            const substitutionId = document.getElementById('substitutionId').value;
            const newTeacherId = document.getElementById('newTeacher').value;
            const reason = document.getElementById('reason').value;
            
            // Validate inputs
            if (!newTeacherId) {
                Swal.fire({
                    title: 'Error',
                    text: 'Please select a new teacher.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
                return;
            }
            
            if (!reason) {
                Swal.fire({
                    title: 'Error',
                    text: 'Please provide a reason for changing the substitution.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
                return;
            }
            
            // Send AJAX request to update substitution
            fetch(`/admin/edit_substitution/${substitutionId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    new_teacher_id: newTeacherId,
                    reason: reason
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(editSubstitutionModal);
                    modal.hide();
                    
                    // Show success message
                    Swal.fire({
                        title: 'Success',
                        text: 'Substitution updated successfully.',
                        icon: 'success',
                        confirmButtonText: 'OK'
                    }).then(() => {
                        // Reload page to reflect changes
                        window.location.reload();
                    });
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: data.message || 'Failed to update substitution.',
                        icon: 'error',
                        confirmButtonText: 'OK'
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    title: 'Error',
                    text: 'An unexpected error occurred.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                });
            });
        });
    }
    
    // Helper function to fetch available teachers for a substitution
    function fetchAvailableTeachers(substitutionId) {
        fetch(`/admin/available_teachers_for_substitution/${substitutionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const teacherSelect = document.getElementById('newTeacher');
                teacherSelect.innerHTML = '<option value="">Select Teacher</option>';
                
                data.teachers.forEach(teacher => {
                    const option = document.createElement('option');
                    option.value = teacher.id;
                    option.textContent = `${teacher.name} (ID: ${teacher.teacher_id})`;
                    teacherSelect.appendChild(option);
                });
            } else {
                console.error('Failed to fetch available teachers:', data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching available teachers:', error);
        });
    }
    
    // Helper function to get CSRF token
    function getCsrfToken() {
        // Try to get token from meta tag
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        // Try to get from form inputs
        const tokenInput = document.querySelector('input[name="csrf_token"]');
        if (tokenInput) {
            return tokenInput.value;
        }
        
        return '';
    }
    
    // Manually handling missing endpoint
    const editSubstitutionForm = document.getElementById('editSubstitutionForm');
    if (editSubstitutionForm) {
        editSubstitutionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveSubstitutionBtn.click();
        });
    }
    
    // Since the endpoint for available_teachers_for_substitution is not implemented yet,
    // we'll add some dummy functionality for the demo
    if (typeof fetchAvailableTeachers === 'function') {
        const originalFetchAvailableTeachers = fetchAvailableTeachers;
        
        // Override the function with a fallback that generates test data
        fetchAvailableTeachers = function(substitutionId) {
            try {
                return originalFetchAvailableTeachers(substitutionId);
            } catch (error) {
                // If the original function fails, populate with some sample data
                const teacherSelect = document.getElementById('newTeacher');
                teacherSelect.innerHTML = '<option value="">Select Teacher</option>';
                
                // Add teacher options from the page if available
                const teacherTableRows = document.querySelectorAll('#teacherTable tbody tr');
                if (teacherTableRows.length > 0) {
                    teacherTableRows.forEach(row => {
                        if (row.querySelector('.teacher-checkbox') && !row.querySelector('.teacher-checkbox').checked) {
                            const teacherId = row.querySelector('.teacher-checkbox').value;
                            const teacherName = row.cells[1].textContent;
                            const teacherIdNum = row.cells[2].textContent;
                            
                            const option = document.createElement('option');
                            option.value = teacherId;
                            option.textContent = `${teacherName} (ID: ${teacherIdNum})`;
                            teacherSelect.appendChild(option);
                        }
                    });
                } else {
                    // Fallback to static sample options
                    const sampleTeachers = [
                        { id: 1, name: "John Smith", teacher_id: "T001" },
                        { id: 2, name: "Jane Doe", teacher_id: "T002" },
                        { id: 3, name: "Alice Johnson", teacher_id: "T003" },
                        { id: 4, name: "Bob Williams", teacher_id: "T004" }
                    ];
                    
                    sampleTeachers.forEach(teacher => {
                        const option = document.createElement('option');
                        option.value = teacher.id;
                        option.textContent = `${teacher.name} (ID: ${teacher.teacher_id})`;
                        teacherSelect.appendChild(option);
                    });
                }
            }
        };
    }
});
