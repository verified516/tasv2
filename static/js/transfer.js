document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const transferRequestButtons = document.querySelectorAll('.approve-transfer, .reject-transfer');
    
    // Handle approve/reject transfer requests
    if (transferRequestButtons.length > 0) {
        transferRequestButtons.forEach(button => {
            button.addEventListener('click', function() {
                const transferId = this.getAttribute('data-id');
                const action = this.classList.contains('approve-transfer') ? 'approve' : 'reject';
                const url = `/admin/${action}_transfer/${transferId}`;
                
                // Confirm action
                Swal.fire({
                    title: `${action.charAt(0).toUpperCase() + action.slice(1)} Transfer?`,
                    text: `Are you sure you want to ${action} this transfer request?`,
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonText: `Yes, ${action} it`,
                    cancelButtonText: 'No, cancel'
                }).then((result) => {
                    if (result.isConfirmed) {
                        // Send AJAX request
                        fetch(url, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCsrfToken()
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                // Show success message
                                Swal.fire({
                                    title: 'Success',
                                    text: `Transfer request ${action}d successfully.`,
                                    icon: 'success',
                                    confirmButtonText: 'OK'
                                }).then(() => {
                                    // Reload page to reflect changes
                                    window.location.reload();
                                });
                            } else {
                                Swal.fire({
                                    title: 'Error',
                                    text: data.message || `Failed to ${action} transfer.`,
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
                    }
                });
            });
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
    
    // Transfer request form validation
    const transferForm = document.querySelector('form[action*="transfer"]');
    if (transferForm) {
        transferForm.addEventListener('submit', function(e) {
            const reasonInput = this.querySelector('#reason, [name="reason"]');
            const teacherSelect = this.querySelector('#new_teacher_id, [name="new_teacher_id"]');
            
            let isValid = true;
            let errorMessage = '';
            
            // Validate reason
            if (reasonInput && !reasonInput.value.trim()) {
                isValid = false;
                errorMessage = 'Please provide a reason for the transfer request.';
                reasonInput.classList.add('is-invalid');
            } else if (reasonInput) {
                reasonInput.classList.remove('is-invalid');
            }
            
            // Validate teacher selection
            if (teacherSelect && (!teacherSelect.value || teacherSelect.value === '')) {
                isValid = false;
                errorMessage = errorMessage || 'Please select a teacher for the transfer.';
                teacherSelect.classList.add('is-invalid');
            } else if (teacherSelect) {
                teacherSelect.classList.remove('is-invalid');
            }
            
            // Show error message and prevent submission if validation fails
            if (!isValid) {
                e.preventDefault();
                Swal.fire({
                    title: 'Form Incomplete',
                    text: errorMessage,
                    icon: 'warning',
                    confirmButtonText: 'OK'
                });
                return false;
            }
            
            // Confirm submission
            e.preventDefault();
            Swal.fire({
                title: 'Confirm Transfer Request',
                text: 'Are you sure you want to request this substitution transfer?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonText: 'Yes, submit request',
                cancelButtonText: 'No, cancel'
            }).then((result) => {
                if (result.isConfirmed) {
                    transferForm.submit();
                }
            });
        });
    }
});
