var emailjs;

let form = document.getElementById("contact");

//Function to activate Emalijs API
function sendMail(contactForm) {
    emailjs.send("gmail", "registration", {
        "from_name": contactForm.user_first.value,
        "from_email": contactForm.user_email.value,
    });
}