// const header = document.querySelector("header");

// window.addEventListener("scroll", function () {
//   header.classList.toggle("sticky", window.scrollY > 0);
// });

const header = document.querySelector("header");
const homeSection = document.getElementById("home");

let lastScrollTop = window.scrollY;

window.addEventListener("scroll", function () {
  const scrollTop = window.scrollY;
  const homeBottom = homeSection.offsetTop + homeSection.offsetHeight;

  // Check if we've scrolled past home section
  if (scrollTop > homeBottom) {
    if (scrollTop > lastScrollTop) {
      // Scrolling down → hide header fully
      header.style.transform = "translateY(calc(-100% - 20px))";
    } else {
      // Scrolling up → show header
      header.style.transform = "translateY(0)";
    }
  } else {
    // Inside or above home section → always show header
    header.style.transform = "translateY(0)";
  }

  // Sticky class toggle
  header.classList.toggle("sticky", scrollTop > 0);

  lastScrollTop = scrollTop;
});

let items = document.querySelectorAll(".slider .list .item");
let next = document.getElementById("next");
let prev = document.getElementById("prev");
let thumbnails = document.querySelectorAll(".thumbnail .item");

// config param
let countItem = items.length;
let itemActive = 0;
// event next click
next.onclick = function () {
  itemActive = itemActive + 1;
  if (itemActive >= countItem) {
    itemActive = 0;
  }
  showSlider();
};
//event prev click
prev.onclick = function () {
  itemActive = itemActive - 1;
  if (itemActive < 0) {
    itemActive = countItem - 1;
  }
  showSlider();
};
// auto run slider
let refreshInterval = setInterval(() => {
  next.click();
}, 5000);
function showSlider() {
  // remove item active old
  let itemActiveOld = document.querySelector(".slider .list .item.active");
  let thumbnailActiveOld = document.querySelector(".thumbnail .item.active");
  itemActiveOld.classList.remove("active");
  thumbnailActiveOld.classList.remove("active");

  // active new item
  items[itemActive].classList.add("active");
  thumbnails[itemActive].classList.add("active");

  // clear auto time run slider
  clearInterval(refreshInterval);
  refreshInterval = setInterval(() => {
    next.click();
  }, 5000);
}

// click thumbnail
thumbnails.forEach((thumbnail, index) => {
  thumbnail.addEventListener("click", () => {
    itemActive = index;
    showSlider();
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const profileLink = document.getElementById("profile-link");
  if (profileLink) {
    profileLink.addEventListener("click", function (e) {
      e.preventDefault(); // prevent default link
      alert("Please login first!");
      window.location.href = profileLink.dataset.loginUrl;
    });
  }
});


