document.addEventListener('DOMContentLoaded', () => {
    const   btnArray     = document.querySelectorAll('.broker-img'), 
            content1 = document.getElementsByClassName('form-second-part'),
            content2 = document.getElementsByClassName('form-third-part');
    
    btnArray.forEach(function(btn) {
        btn.addEventListener('click', () => {
            content1[0].style.display = "block";
            content2[0].style.display = "block";
        });
    });
});