/*jshint esversion: 6 */
$('document').ready(function () {
    emailjs.init("user_OI2X9ilOsTtFTtOq5tbXy");

    let emailForm = $("#contactForm");
    let btn = $("#contactForm div button");

    emailForm.submit(function (event) {
        event.preventDefault();

        btn.text('Sending...');

        let serviceId = 'service_s4d2bbs';
        let templateId = 'recipe_template';

        emailjs.sendForm(serviceId, templateId, this).then(
                function () {
                    btn.text('SEND');
                    alert('The email has been sent successfully!');
                }),
            function (err) {
                btn.text('SEND');
                alert("Sending email has failed!\r\n Please try again later.\r\n Response:\n" + JSON.stringify(err));
            };
    });
})