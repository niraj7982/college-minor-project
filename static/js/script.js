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
});
