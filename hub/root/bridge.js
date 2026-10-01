/* Starship Manuel hub bridge: status readout. Same-origin only. */
(function () {
  function $(id) { return document.getElementById(id); }
  function tick() {
    var d = new Date();
    var t = d.toLocaleString("en-US", { timeZone: "America/New_York", weekday: "short", month: "short", day: "numeric", hour: "numeric", minute: "2-digit", second: "2-digit" }) + " ET";
    if ($("clock")) $("clock").textContent = t;
    var start = new Date(d.getFullYear(), 0, 0);
    var doy = Math.floor((d - start) / 86400000);
    if ($("sd")) $("sd").textContent = d.getFullYear() + "." + ("00" + doy).slice(-3);
  }
  tick(); setInterval(tick, 1000);
  var lamp = $("sentLamp"), txt = $("sent");
  if (!window.fetch || !lamp) return;
  fetch("/api/account-status", { credentials: "same-origin", cache: "no-store" })
    .then(function (r) { if (!r.ok) throw 0; return r.json(); })
    .then(function (j) {
      lamp.className = "lamp ok";
      txt.textContent = "hub online · " + (j && j.exists ? "Captain aboard" : "no account");
    })
    .catch(function () { lamp.className = "lamp lhold"; txt.textContent = "hub status unavailable (offline copy)"; });
})();
