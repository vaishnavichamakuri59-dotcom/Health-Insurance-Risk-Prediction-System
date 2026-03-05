document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");
    const button = document.getElementById("predictBtn");
    const spinner = document.getElementById("spinner");
    const btnText = document.getElementById("btnText");

    if (form && button && spinner && btnText) {
        form.addEventListener("submit", function () {
            spinner.classList.remove("d-none");
            btnText.innerText = " Predicting...";
            button.disabled = true;
        });
    }

});