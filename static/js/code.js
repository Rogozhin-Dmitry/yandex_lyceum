changeTheme(isDarkTheme);

function changeTheme(isDarkTheme) {
  const theme = isDarkTheme ? "dark" : "default";
  const code__iframe = document.querySelectorAll('iframe');
  Object.entries(themes[theme]).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
  switchThemeBtn.innerHTML = !isDarkTheme ? "Тёмная тема" : "Светлая тема";
  closeMenu()
  if (code__iframe) {
    if (isDarkTheme){
      code__iframe.forEach(function(item, i, arr) {
        item.className = 'iframe__dark';
        console.log(item)
      });
    } else {
      code__iframe.forEach(function(item, i, arr) {
        item.className = '';
      });
    }
  }
}
