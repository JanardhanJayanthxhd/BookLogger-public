// Year in footer
var currentYear = new Date().getFullYear()
var year_element = document.getElementById("year")
year_element.setAttribute("datetime", currentYear)
year_element.textContent = currentYear


// Greeter in dash board
var greetSpan = document.getElementById("greeter")
var currentHour = new Date().getHours()
var greeting

if (currentHour > 12) {
    greeting = "Afternoon"
} else if (currentHour > 18) {
    greeting = "Evening"
} else {
    greeting = "Morning"
}

greetSpan.textContent = greeting