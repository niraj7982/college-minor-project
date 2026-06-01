/*
=========================================================
  BEGINNER FRIENDLY JAVASCRIPT GUIDE - DIGITAL CAMPUS
=========================================================
This JavaScript file adds simple interactivity to the 
website. JavaScript makes web pages "alive" by allowing 
them to react to what the user does (like clicking buttons).

To make it easy to understand, each part is explained with comments.
=========================================================
*/

// Wait for the entire webpage to load before running any code
document.addEventListener('DOMContentLoaded', function() {
    // ---------------------------------------------------------
    // 1. SIMPLE CONSOLE MESSAGE
    // ---------------------------------------------------------
    // The console is a tool for developers (press F12 in your browser).
    // It helps us check if our script is working!
    console.log("Digital Campus is ready! Welcome to the console.");

    // ---------------------------------------------------------
    // 2. INTERACTIVE ALERTS (Popup Messages)
    // ---------------------------------------------------------
    // Let's find all buttons with the class 'btn-primary'
    // 'const' means we are creating a variable that won't change
    const primaryButtons = document.querySelectorAll('.btn-primary');

    // We can loop through all the buttons we found
    primaryButtons.forEach(function(button) {
        // We 'listen' for a click on each button
        button.addEventListener('click', function() {
            // When clicked, we show a small popup!
            // Note: We use setTimeout to let the page navigate to the link if it has one
            // Uncomment the line below to show an alert on every blue button click!
            // alert("You clicked a primary button!");
        });
    });

    // ---------------------------------------------------------
    // 3. FADING OUT MESSAGES (Notifications)
    // ---------------------------------------------------------
    // When the website shows a success or error message,
    // it's nice if it disappears automatically after a few seconds.

    // Find all elements with the 'alert' class
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alertBox) {
        // Set a timer for 5000 milliseconds (5 seconds)
        setTimeout(function() {
            // After 5 seconds, use Bootstrap's alert feature to close it
            // We only do this if the alert hasn't already been closed manually
            if (alertBox && document.body.contains(alertBox)) {
                // The newest Bootstrap version allows closing elements with this line:
                const bsAlert = new bootstrap.Alert(alertBox);
                bsAlert.close();
            }
        }, 5000); // 5000ms = 5s
    });

    // ---------------------------------------------------------
    // 4. ANIMATING CARDS ON HOVER
    // ---------------------------------------------------------
    // JavaScript can also help with animations, although we did most 
    // of the card hovering in CSS. Here's a tiny JS effect doing a similar thing:

    // Find all 'card' elements
    const cards = document.querySelectorAll('.card');

    cards.forEach(function(card) {
        // When the mouse enters the card area...
        card.addEventListener('mouseenter', function() {
            // Change the border color to our cyan 'primary' color temporarily
            card.style.borderColor = "#00e5ff";
        });

        // When the mouse leaves the card area...
        card.addEventListener('mouseleave', function() {
            // Reset the border color back to normal
            // (Empty string means "go back to what was set in CSS")
            card.style.borderColor = ""; 
        });
    });

    // ---------------------------------------------------------
    // 5. GLOBAL FILE SIZE VALIDATION (Vercel 4.5MB Payload Limit)
    // ---------------------------------------------------------
    // Vercel serverless functions restrict the payload size to 4.5 MB.
    // To prevent a generic 413 error screen, we check file inputs on change and form submission.
    
    const MAX_FILE_SIZE_BYTES = 4 * 1024 * 1024; // 4.0 MB (4,194,304 bytes) limit for safety

    document.addEventListener('change', function(event) {
        const target = event.target;
        if (target && target.type === 'file') {
            validateFileInput(target);
        }
    });

    document.addEventListener('submit', function(event) {
        const form = event.target;
        const fileInputs = form.querySelectorAll('input[type="file"]');
        let isValid = true;
        
        fileInputs.forEach(function(input) {
            if (!validateFileInput(input)) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            event.preventDefault();
            // Scroll to the first error container
            const firstError = form.querySelector('.file-size-error');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    function validateFileInput(input) {
        if (!input.files || input.files.length === 0) {
            removeFileLimitError(input);
            return true;
        }

        const file = input.files[0];
        if (file.size > MAX_FILE_SIZE_BYTES) {
            // Clear the invalid file selection so it doesn't get submitted
            input.value = '';
            
            // Format size strings
            const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
            const limitSizeMB = (MAX_FILE_SIZE_BYTES / (1024 * 1024)).toFixed(2);
            
            // Show the error UI
            showFileLimitError(input, `File <strong>${escapeHtml(file.name)}</strong> is too large (${fileSizeMB} MB). The maximum allowed size is <strong>${limitSizeMB} MB</strong> due to cloud server payload limits. Please choose a smaller file or compress it.`);
            return false;
        } else {
            removeFileLimitError(input);
            return true;
        }
    }

    function showFileLimitError(input, message) {
        // Clean existing errors first
        removeFileLimitError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'file-size-error';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
        
        // Insert it after the input or its parent if it's in an input group
        const insertAfterNode = input.closest('.input-group') || input;
        if (insertAfterNode.parentNode) {
            insertAfterNode.parentNode.insertBefore(errorDiv, insertAfterNode.nextSibling);
        }
    }

    function removeFileLimitError(input) {
        const wrapper = input.closest('.input-group') || input;
        const parent = wrapper.parentNode;
        if (parent) {
            const errors = parent.querySelectorAll('.file-size-error');
            errors.forEach(function(err) {
                err.remove();
            });
        }
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
