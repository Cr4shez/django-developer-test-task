document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("[data-clear-input]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = document.getElementById(button.getAttribute("data-clear-input"));
            if (!input) return;
            input.value = "";
            input.focus();
        });
    });
});