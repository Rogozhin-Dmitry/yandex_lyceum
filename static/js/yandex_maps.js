ymaps.ready(function () {
    var myMap = new ymaps.Map('map', {
            center: [55.475423, 37.300687],
            zoom: 14
        }, {
            searchControlProvider: 'yandex#search'
        }),

        MyIconContentLayout = ymaps.templateLayoutFactory.createClass(
            '<div style="color: #101010; font-weight: bold;">$[properties.iconContent]</div>'
        ),

        school = new ymaps.Placemark([55.475423, 37.300687], {
            hintContent: 'Тут я учусь',
            balloonContent: 'Это моя школа'
        }, {
            iconLayout: 'default#image',
            iconImageHref: '../static/images/school.png',
            iconImageSize: [42, 30],
            iconImageOffset: [-5, -38]
        }),

        home = new ymaps.Placemark([55.465193, 37.288206], {
            hintContent: 'Тут я живу',
            balloonContent: 'Это мой домик',
        }, {
            iconLayout: 'default#imageWithContent',
            iconImageHref: '../static/images/home.png',
            iconImageSize: [30, 30],
            iconImageOffset: [-24, -24],
        }),

        bytic = new ymaps.Placemark([55.470201, 37.295333], {
            hintContent: 'Тут я учился програмированию',
            balloonContent: 'Это Байтик, шикарное заведение на базе которого был Яндекс Лицей',
        }, {
            iconLayout: 'default#image',
            iconImageHref: '../static/images/school.png',
            iconImageSize: [42, 30],
            iconImageOffset: [-5, -38]
        });

    myMap.geoObjects
        .add(school)
        .add(bytic)
        .add(home);
});
changeTheme(isDarkTheme);

function changeTheme(isDarkTheme) {
  const theme = isDarkTheme ? "dark" : "default";
  const map = document.querySelector('#map');
  Object.entries(themes[theme]).forEach(([key, value]) => {
    root.style.setProperty(key, value);
  });
  switchThemeBtn.innerHTML = !isDarkTheme ? "Тёмная тема" : "Светлая тема";
  closeMenu()
  if (map) {
    if (isDarkTheme){
      map.className = 'map__content_dark';
    } else {
      map.className = 'map__content';
    }
  }
}
