document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const teacherSearch = document.getElementById('teacherSearch');
    const teacherCheckboxes = document.querySelectorAll('.teacher-checkbox');
    const selectAllCheckbox = document.getElementById('selectAll');
    const selectedTeachersList = document.getElementById('selectedTeachersList');
    const cancelBtn = document.getElementById('cancelBtn');
    const teacherTable = document.getElementById('teacherTable');
    const dateInput = document.querySelector('input[name="date"]');
    const daySelect = document.querySelector('select[name="day"]');
    
    // Initialize date and day mapping
    const dayMap = {
        0: 'Day 1',
        1: 'Day 2',
        2: 'Day 3',
        3: 'Day 4',
        4: 'Day 5',
        5: 'Day 1', // Weekend defaults to Day 1
        6: 'Day 1'  // Weekend defaults to Day 1
    };
    
    // Update day based on selected date
    function updateDayFromDate() {
        if (dateInput.value) {
            const selectedDate = new Date(dateInput.value);
            const dayOfWeek = selectedDate.getDay();
            daySelect.value = dayMap[dayOfWeek];
        }
    }
    
    // Initial update
    if (dateInput && daySelect) {
        updateDayFromDate();
        
        // Add event listener for date changes
        dateInput.addEventListener('change', updateDayFromDate);
    }
    
    // Search functionality
    if (teacherSearch) {
        teacherSearch.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = teacherTable.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const teacherName = row.cells[1].textContent.toLowerCase();
                const teacherId = row.cells[2].textContent.toLowerCase();
                const teacherEmail = row.cells[4].textContent.toLowerCase();
                
                if (teacherName.includes(searchTerm) || 
                    teacherId.includes(searchTerm) || 
                    teacherEmail.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
    
    // Select all functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            
            teacherCheckboxes.forEach(checkbox => {
                const row = checkbox.closest('tr');
                if (row.style.display !== 'none') {
                    checkbox.checked = isChecked;
                    updateSelectedTeachersList();
                }
            });
        });
    }
    
    // Update selected teachers panel
    function updateSelectedTeachersList() {
        if (!selectedTeachersList) return;
        
        // Clear current list
        selectedTeachersList.innerHTML = '';
        
        // Count selected teachers
        let selectedCount = 0;
        
        // Add each selected teacher to the list
        teacherCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selectedCount++;
                const row = checkbox.closest('tr');
                const teacherName = row.cells[1].textContent;
                const teacherId = row.cells[2].textContent;
                
                const listItem = document.createElement('li');
                listItem.className = 'list-group-item';
                listItem.innerHTML = `
                    <div>${teacherName} <small class="text-muted">(${teacherId})</small></div>
                    <button type="button" class="btn btn-sm btn-outline-danger remove-teacher" data-id="${checkbox.value}">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                
                selectedTeachersList.appendChild(listItem);
            }
        });
        
        // Show message if no teachers selected
        if (selectedCount === 0) {
            const emptyMessage = document.createElement('li');
            emptyMessage.className = 'list-group-item text-center text-muted';
            emptyMessage.innerHTML = '<i class="fas fa-info-circle me-2"></i>No teachers selected';
            selectedTeachersList.appendChild(emptyMessage);
        }
        
        // Add event listeners to remove buttons
        const removeButtons = document.querySelectorAll('.remove-teacher');
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const teacherId = this.getAttribute('data-id');
                const checkbox = document.querySelector(`.teacher-checkbox[value="${teacherId}"]`);
                if (checkbox) {
                    checkbox.checked = false;
                    updateSelectedTeachersList();
                }
            });
        });
    }
    
    // Add change event listeners to all teacher checkboxes
    teacherCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedTeachersList);
    });
    
    // Initialize the selected teachers list
    updateSelectedTeachersList();
    
    // Cancel button functionality
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function() {
            window.location.href = '/admin/dashboard';
        });
    }
    
    // Form validation before submission
    const absenceForm = document.getElementById('absenceForm');
    if (absenceForm) {
        absenceForm.addEventListener('submit', function(e) {
            console.log("Form submission intercepted");
            e.preventDefault(); // Always prevent default first
            
            // Check if any teachers are selected
            let hasSelectedTeachers = false;
            let selectedCount = 0;
            let selectedTeachers = [];
            
            teacherCheckboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    hasSelectedTeachers = true;
                    selectedCount++;
                    selectedTeachers.push(checkbox.value);
                    console.log("Selected teacher ID:", checkbox.value);
                }
            });
            
            console.log("Selected teachers count:", selectedCount);
            
            if (!hasSelectedTeachers) {
                console.log("No teachers selected");
                Swal.fire({
                    title: 'No Teachers Selected',
                    text: 'Please select at least one teacher to mark as absent.',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                return false;
            }
            
            // Confirm submission
            console.log("Showing confirmation dialog");
            Swal.fire({
                title: 'Confirm Absence',
                text: `Are you sure you want to mark ${selectedCount} teacher(s) as absent?`,
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes, proceed',
                cancelButtonText: 'No, cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    console.log("Confirmed, submitting form");
                    
                    // Manual submission with FormData for better control
                    const formData = new FormData(absenceForm);
                    
                    // Ensure selected teachers are properly included
                    // First clear any existing entries
                    for (const pair of formData.entries()) {
                        if (pair[0] === 'selected_teachers') {
                            formData.delete('selected_teachers');
                        }
                    }
                    
                    // Then add all selected teachers
                    selectedTeachers.forEach(teacherId => {
                        formData.append('selected_teachers', teacherId);
                    });
                    
                    console.log("Submitting with selected teachers:", selectedTeachers);
                    
                    // Get CSRF token
                    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
                    
                    // Use fetch for form submission
                    fetch(absenceForm.action, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => {
                        if (response.redirected) {
                            window.location.href = response.url;
                            return null;
                        } 
                        
                        // Check content type to decide how to parse the response
                        const contentType = response.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                            return response.json();
                        } else {
                            return response.text();
                        }
                    })
                    .then(data => {
                        if (!data) return; // Response was redirected
                        
                        if (typeof data === 'object') {
                            // Handle JSON response
                            console.log("Got JSON response:", data);
                            
                            if (data.success) {
                                // Success response from server
                                if (data.redirect) {
                                    console.log("Redirecting to:", data.redirect);
                                    window.location.href = data.redirect;
                                } else {
                                    // No redirect URL provided, go to substitution page
                                    window.location.href = '/admin/substitution';
                                }
                            } else {
                                // Error response from server
                                Swal.fire({
                                    title: 'Error',
                                    text: data.message || 'An error occurred while processing absences.',
                                    icon: 'error',
                                    confirmButtonText: 'OK'
                                });
                            }
                        } else {
                            // Handle HTML response (fallback)
                            console.log("Got HTML response, redirecting to substitution page");
                            window.location.href = '/admin/substitution';
                        }
                    })
                    .catch(error => {
                        console.error("Error submitting form:", error);
                        alert("An error occurred while submitting the form. Please try again.");
                    });
                } else {
                    console.log("Cancelled form submission");
                }
            }).catch(error => {
                console.error("SweetAlert error:", error);
                // Fallback submission in case of error
                if (confirm("Are you sure you want to mark the selected teachers as absent?")) {
                    absenceForm.submit();
                }
            });
        });
    }
});
