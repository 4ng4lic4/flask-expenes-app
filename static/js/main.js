document.addEventListener("DOMContentLoaded", (event) => {
    const button = document.getElementsByClassName("btn-close")[0];
    const element = document.getElementsByClassName("alert")[0];
    if (button){
        button.addEventListener("click", (event) => {
            element.remove();
        });
    }

    const test = document.createElement("input");
    test.type = "month";
    const native_datepicker = document.querySelector(".native_datepicker");
    const alternative_datepicker = document.querySelector(".alternative_datepicker");

    if (test.type === "text"){
        native_datepicker.style.display = "none";
        alternative_datepicker.style.display = "inline-flex";
        const alternative_datepicker_month = document.getElementsByClassName("month");
        const alternative_datepicker_year = document.getElementsByClassName("year");
        native_datepicker.required = false;
        alternative_datepicker_month.required = true;
        alternative_datepicker_year.required = true;
    }; 
});
