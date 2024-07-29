document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registration-form");
    const progressBar = document.getElementById("progress-bar");
    const totalFields = form.querySelectorAll("input, select").length;
    form.addEventListener("input", function () {
        const filledFields = Array.from(
            form.querySelectorAll("input, select")
        ).filter((input) => input.value.trim() !== "").length;
        const progress = Math.round((filledFields / totalFields) * 100);
        progressBar.style.width = progress + "%";
        progressBar.setAttribute("aria-valuenow", progress);
    });
});