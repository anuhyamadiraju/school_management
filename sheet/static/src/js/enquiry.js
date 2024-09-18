
document.addEventListener('DOMContentLoaded', function () {
    const enquiryForm = document.getElementById('enquiry_form');

    if (enquiryForm) {
        enquiryForm.addEventListener('submit', function (event) {
            event.preventDefault(); 
            
            const formData = new FormData(enquiryForm);
            
            fetch('/enquiry/submit', {  
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'  
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/enquiry/success'; 
                } else {
                    alert('There was an error processing your enquiry.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }
});
