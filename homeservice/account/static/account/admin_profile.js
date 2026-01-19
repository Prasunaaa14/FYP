document.addEventListener("DOMContentLoaded", function () {
    const roleField = document.getElementById("id_role");
    const certificateRow = document.querySelector(".field-certificate");

    function toggleCertificate() {
        if (roleField.value === "provider") {
            certificateRow.style.display = "block";
        } else {
            certificateRow.style.display = "none";
        }
    }

    if (roleField && certificateRow) {
        toggleCertificate();
        roleField.addEventListener("change", toggleCertificate);
    }
});
location = models.CharField(max_length=255)
