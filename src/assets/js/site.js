/* Dominion Enterprises SL: menú, consentimiento de cookies y eventos de conversión */
(function () {
  var body = document.body;

  /* Menú móvil */
  var burger = document.querySelector(".burger"), nav = document.getElementById("nav");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* Google Analytics: solo en el dominio real. Medición activa por defecto; "Rechazar" la desactiva. */
  var gaId = body.getAttribute("data-ga");
  if (body.getAttribute("data-analytics") === "1" && gaId) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + gaId;
    document.head.appendChild(s);
    window.gtag("config", gaId);
  }

  /* Aviso de cookies */
  var ck = document.getElementById("ck"), saved = null;
  try { saved = localStorage.getItem("dm_consent"); } catch (e) {}
  if (ck && !saved) ck.hidden = false;
  if (ck) {
    ck.addEventListener("click", function (e) {
      var b = e.target.closest("[data-ck]");
      if (!b) return;
      var v = b.getAttribute("data-ck");
      try { localStorage.setItem("dm_consent", v); } catch (err) {}
      var st = v === "granted" ? "granted" : "denied";
      window.gtag("consent", "update", { ad_storage: st, ad_user_data: st, ad_personalization: st, analytics_storage: st });
      ck.hidden = true;
    });
  }
  /* Enlace "Cambiar mis preferencias de cookies" */
  document.addEventListener("click", function (e) {
    var r = e.target.closest("[data-ck-reset]");
    if (!r || !ck) return;
    e.preventDefault();
    try { localStorage.removeItem("dm_consent"); } catch (err) {}
    ck.hidden = false;
  });

  /* Eventos de conversión (mismos nombres que en el sitio anterior, para no perder las conversiones de Google Ads) */
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest(".dm-wa,.dm-tel,.dm-map");
    if (!a) return;
    var name = a.classList.contains("dm-wa") ? "whatsapp_click" : a.classList.contains("dm-tel") ? "phone_click" : "map_click";
    var service = body.getAttribute("data-service") || "general";
    if (window.gtag) window.gtag("event", name, { service: service });
    (window.dataLayer = window.dataLayer || []).push({ event: name + "_dm", service: service });
  });

  /* Mapa de Google Maps: solo se carga al pulsar (privacidad y velocidad). Evento propio, distinto de map_click. */
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest("[data-map-load]");
    if (!btn) return;
    var box = btn.closest(".mapbox");
    if (!box || box.querySelector("iframe")) return;
    var f = document.createElement("iframe");
    f.src = box.getAttribute("data-map");
    f.title = "Mapa: Dominion Enterprises SL, C. Pino 2A, Alicante";
    f.loading = "lazy";
    f.referrerPolicy = "no-referrer-when-downgrade";
    box.appendChild(f);
    var inner = box.querySelector(".mapbox-in");
    if (inner) inner.hidden = true;
    if (window.gtag) window.gtag("event", "map_view", { service: body.getAttribute("data-service") || "general" });
  });
})();
