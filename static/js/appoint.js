const header = document.querySelector("header");

window.addEventListener("scroll", function () {
  header.classList.toggle("sticky", window.scrollY > 0);
});

// Date restriction
const dateInput = document.getElementById("date");
const today = new Date();
today.setDate(today.getDate() + 3); // 3 days after today
const yyyy = today.getFullYear();
const mm = String(today.getMonth() + 1).padStart(2, "0");
const dd = String(today.getDate()).padStart(2, "0");
const minDate = `${yyyy}-${mm}-${dd}`;
dateInput.min = minDate;
dateInput.value = minDate; // Optional: pre-fill with minimum date

// Ensure time is within 09:00 to 18:00
const timeInput = document.getElementById("time");

// Set min and max in 24-hour format
const minTime = "09:00";
const maxTime = "18:00";

// Pre-fill with minimum time
timeInput.value = minTime;

timeInput.addEventListener("input", function () {
  let time = this.value;
  if (time < minTime) this.value = minTime;
  if (time > maxTime) this.value = maxTime;
});

// Optional: Show 12-hour format placeholder (just for display)
timeInput.addEventListener("blur", function () {
  if (this.value) {
    let [hours, minutes] = this.value.split(":");
    let period = +hours >= 12 ? "PM" : "AM";
    hours = +hours % 12 || 12;
    this.setAttribute("data-time-display", `${hours}:${minutes} ${period}`);
  }
});

// Driving License validation
const form = document.querySelector("form");
form.addEventListener("submit", function (e) {
  const licenseNo = document.querySelector(
    'input[name="driving_license"][value="No"]'
  );
  if (licenseNo.checked) {
    e.preventDefault();
    alert("You need a driver's license to book an appointment");
  }
});
