document.addEventListener('DOMContentLoaded', function() {
    // Dark mode toggle functionality with enhanced animation
    const darkModeToggle = document.getElementById('darkModeToggle');
    const themeText = document.getElementById('themeText');
    const htmlElement = document.documentElement;
    
    // Set default theme to dark if not specified
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const defaultTheme = prefersDarkScheme ? 'dark' : 'light';
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || defaultTheme;
    
    // Apply theme immediately to prevent flash of wrong theme
    htmlElement.setAttribute('data-bs-theme', savedTheme);
    if (themeText) {
        updateThemeText(savedTheme);
    }
    
    // Toggle theme when button is clicked with smooth transition
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            // Add transition for smooth theme change
            document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
            
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Apply the new theme
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update toggle button
            updateThemeText(newTheme);
            
            // Add a class to trigger animation
            document.body.classList.add('theme-transition');
            
            // Remove the transition class after animation completes
            setTimeout(() => {
                document.body.classList.remove('theme-transition');
                document.body.style.transition = '';
            }, 300);
        });
    }
    
    function updateThemeText(theme) {
        if (themeText) {
            const icon = darkModeToggle.querySelector('i');
            
            if (theme === 'dark') {
                themeText.textContent = 'Light Mode';
                icon.className = 'fas fa-sun me-1';
                darkModeToggle.classList.remove('btn-outline-dark');
                darkModeToggle.classList.add('btn-outline-light');
                // Add ripple animation
                darkModeToggle.classList.add('btn-ripple');
                setTimeout(() => {
                    darkModeToggle.classList.remove('btn-ripple');
                }, 700);
            } else {
                themeText.textContent = 'Dark Mode';
                icon.className = 'fas fa-moon me-1';
                darkModeToggle.classList.remove('btn-outline-light');
                darkModeToggle.classList.add('btn-outline-dark');
                // Add ripple animation
                darkModeToggle.classList.add('btn-ripple');
                setTimeout(() => {
                    darkModeToggle.classList.remove('btn-ripple');
                }, 700);
            }
        }
    }
    
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Set auto-close for alerts
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    // Implement notification system base
    function requestNotificationPermission() {
        if ('Notification' in window) {
            if (Notification.permission !== 'granted' && Notification.permission !== 'denied') {
                Notification.requestPermission().then(function (permission) {
                    if (permission === 'granted') {
                        console.log('Notification permission granted.');
                    }
                });
            }
        }
    }
    
    // Request notification permission on page load
    requestNotificationPermission();
});

// Function to show notification (to be used where needed)
function showNotification(title, message) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: message,
            icon: '/static/favicon.ico'
        });
        
        notification.onclick = function() {
            window.focus();
            this.close();
        };
    } else {
        // Fallback to in-app notification
        Swal.fire({
            title: title,
            text: message,
            icon: 'info',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000
        });
    }
}

// Page transition animations
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements for animation
    const fullscreenLoader = document.getElementById('fullscreenLoader');
    const mainContent = document.getElementById('mainContent');
    
    // Show initial loading animation when page first loads
    if (fullscreenLoader) {
        fullscreenLoader.style.display = 'flex';
        setTimeout(() => {
            fullscreenLoader.style.opacity = '0';
            setTimeout(() => {
                fullscreenLoader.style.display = 'none';
            }, 500);
        }, 800);
    }
    
    // Add initial fade-in animation to main content
    if (mainContent) {
        mainContent.style.animation = 'fadeIn 0.5s ease-out';
    }
    
    // Add animations for page loads
    document.addEventListener('beforeunload', function() {
        if (mainContent) {
            mainContent.style.opacity = '0';
            mainContent.style.transform = 'translateY(20px)';
        }
    });
    
    // Add CSS animations to the page
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; transform: translateY(0); }
            to { opacity: 0; transform: translateY(-20px); }
        }
        
        .fade-in {
            animation: fadeIn 0.3s ease-out;
        }
        
        .fade-out {
            animation: fadeOut 0.3s ease-out;
        }
        
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .btn:after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 5px;
            height: 5px;
            background: rgba(255, 255, 255, 0.5);
            opacity: 0;
            border-radius: 100%;
            transform: scale(1, 1) translate(-50%);
            transform-origin: 50% 50%;
        }
        
        .btn:focus:not(:active)::after {
            animation: ripple 1s ease-out;
        }
        
        @keyframes ripple {
            0% {
                transform: scale(0, 0);
                opacity: 0.5;
            }
            20% {
                transform: scale(25, 25);
                opacity: 0.3;
            }
            100% {
                opacity: 0;
                transform: scale(40, 40);
            }
        }
    `;
    document.head.appendChild(styleElement);
});
