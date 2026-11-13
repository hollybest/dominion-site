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

  /* Google Analytics: solo en el dominio real. El consentimiento por defecto es "denegado". */
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
      if (v === "granted") {
        window.gtag("consent", "update", { ad_storage: "granted", ad_user_data: "granted", ad_personalization: "granted", analytics_storage: "granted" });
      }
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
})();
