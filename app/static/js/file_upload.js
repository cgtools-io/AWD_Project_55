document.addEventListener('DOMContentLoaded', () => {
    const   content0    = document.getElementById('form-first-part'),
            content1    = document.getElementById('form-second-part'),
            content2    = document.getElementById('form-third-part'),
            formState   = document.getElementById('form-state').dataset.form_state;;

    if (formState === '1' || formState === null) {
        content0.style.display = "block";
        content1.style.display = "none";
        content2.style.display = "none";
    }
    else if (formState === '2') {
        content0.style.display = "none";
        content1.style.display = "block";
        content2.style.display = "block";
    }
    
    document.querySelectorAll('.broker-img').forEach(function(img) {
        img.addEventListener('click', function() {
            // Scroll to the file upload section smoothl
            content1.style.display = "block";
            content2.style.display = "block";

            content1.scrollIntoView({ behavior: 'smooth', alignToTop: false});
            
            setTimeout(() => {
                content0.style.display = "none";
            }, 500);
        });
    });

    document.querySelector('#back-btn').addEventListener('click', function() {
        // Scroll to the file upload section smoothly
        content0.style.display = "block";

        content0.scrollIntoView({ behavior: 'smooth', block: 'start'});

        content1.style.display = "none";
        content2.style.display = "none";
        
    });
});