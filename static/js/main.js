let hamb = document.querySelector('.hamb')
let navMenu = document.querySelector('.nav__menu')

hamb.addEventListener("click", mobileMenu);

function mobileMenu(){
  hamb.classList.toggle("active");
  navMenu.classList.toggle("active");
}

const navLink = document.querySelectorAll('.nav__link')

navLink.forEach(n => n.addEventListener("click", closeMenu));

function closeMenu() {
  hamb.classList.remove("active");
  navMenu.classList.remove("active");
}

const themes = {
  default: {
    "--bg-color": "#eae9ea",
    "--text-color": "#475569",
    "--hamb-color": "#101010",
    "--header-color": "#f5f5f5",
    "--nav-shadow": "#1a1a1a",
    "--code-border": "#ccc",
    "--footer-color": "#f5f5f5",
  },
  dark: {
    "--bg-color": "#181c1f",
    "--text-color": "#d2d2d2",
    "--hamb-color": "#d2d2d2",
    "--header-color": "#2f3235",
    "--nav-shadow": "#cccccc",
    "--code-border": "#d2d2d2",
    "--footer-color": "#2f3235",
  },
};

if (!localStorage.getItem("isDarkTheme")) {
  localStorage.setItem("isDarkTheme", false);
}

const switchThemeBtn = document.querySelector('#switch__theme__btn');
const root = document.querySelector(':root');

let isDarkTheme = JSON.parse(localStorage.getItem("isDarkTheme"));
changeTheme(isDarkTheme);

switchThemeBtn.addEventListener("click", switchThemeBtnHandler);

function switchThemeBtnHandler(e) {
  e.preventDefault();
  isDarkTheme = !isDarkTheme;
  localStorage.setItem("isDarkTheme", isDarkTheme);
  changeTheme(isDarkTheme)
}

function changeTheme(isDarkTheme) {
  const theme = isDarkTheme ? "dark" : "default";
  Object.entries(themes[theme]).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
  switchThemeBtn.innerHTML = !isDarkTheme ? "Тёмная тема" : "Светлая тема";
  closeMenu()
}
