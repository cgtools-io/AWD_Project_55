document.addEventListener('DOMContentLoaded', () => {
    const   btnArray    = document.querySelectorAll('.broker-img'), 
            content0    = document.getElementsByClassName('form-first-part'),
            content1    = document.getElementsByClassName('form-second-part'),
            content2    = document.getElementsByClassName('form-third-part'),
            backBtn     = document.getElementById('back-btn'),
            formState   = document.getElementById('form-state').dataset.form_state;

    if (formState === '1' || formState === null) {
        content0[0].style.display = "block";
        content1[0].style.display = "none";
        content2[0].style.display = "none";
    }
    else if (formState === '2') {
        content0[0].style.display = "none";
        content1[0].style.display = "block";
        content2[0].style.display = "block";
    }

    btnArray.forEach(function(btn) {
        btn.addEventListener('click', () => {
            content0[0].style.display = "none";
            content1[0].style.display = "block";
            content2[0].style.display = "block";
        });
    });
    backBtn.addEventListener('click', () => {
        content0[0].style.display = "block";
        content1[0].style.display = "none";
        content2[0].style.display = "none";
    });
});