
var settingsDefault = {
    "settings.color.background": "#000000",
    "settings.color.foreground": "#ffffff",
    "settings.color.border": "#008000",
    "settings.color.player-border": "#ffffff50",
    "settings.calc.strategy": "optimistic"
};

function settingsReset(){
    for (let settingName in settingsDefault){
        settingsSet(settingName, settingsDefault[settingName]);
    }
}

function settingsSet(name, val) {
    setCookie(name, val, 365);
}

function settingsGet(name) {
    let defaultVal = settingsDefault[name];
    return getCookie(name, defaultVal);
}

function setCookie(cname, cvalue, days) {
    var d = new Date();
    d.setTime(d.getTime() + (days*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + "; SameSite=Strict; path=/";
}

function getCookie(cname, defaultVal) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return (defaultVal === undefined ? "" : defaultVal);
}