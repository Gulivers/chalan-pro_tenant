/**
 * Precios desde GET /api/billing/public-plans/ (modelo Plan, schema public).
 * - getjobrhythm.com: ruta relativa (nginx → backend, mismo origen).
 * - Local / LAN: http://api.chalanpro.net:8000 (ubuntu-house).
 * - Fallback: ?api_base=https://... o meta jobrhythm-api-base.
 */
(function () {
  var FALLBACK_PLANS = {
    starter: { monthly: 436, annual: 4447 },
    professional: { monthly: 877, annual: 8945 },
    enterprise: { monthly: 1758, annual: 17931 },
  };

  var PERIOD_LABELS = {
    es: { monthly: "/ mes", annual: "/ año" },
    en: { monthly: "/ month", annual: "/ year" },
  };

  var planPrices = null;

  function pageLang() {
    var lang = (document.documentElement.lang || "en").toLowerCase();
    return lang.indexOf("es") === 0 ? "es" : "en";
  }

  function isLocalDevHost(hostname) {
    return (
      hostname === "localhost" ||
      hostname === "127.0.0.1" ||
      /^192\.168\./.test(hostname) ||
      hostname.endsWith(".local")
    );
  }

  function isMarketingHost(hostname) {
    return (
      hostname === "getjobrhythm.com" ||
      hostname === "www.getjobrhythm.com"
    );
  }

  /** URL completa del endpoint REST de planes (público). */
  function resolvePlansUrl() {
    var params = new URLSearchParams(window.location.search);
    var override = params.get("api_base");
    if (override) {
      return override.replace(/\/$/, "") + "/api/billing/public-plans/";
    }

    var host = window.location.hostname;

    if (isMarketingHost(host)) {
      return "/api/billing/public-plans/";
    }

    if (isLocalDevHost(host)) {
      return "http://api.chalanpro.net:8000/api/billing/public-plans/";
    }

    var meta = document.querySelector('meta[name="jobrhythm-api-base"]');
    if (meta && meta.content) {
      return meta.content.replace(/\/$/, "") + "/api/billing/public-plans/";
    }

    return "https://api.jobrhythm.net/api/billing/public-plans/";
  }

  function formatPrice(amount) {
    var n = Number(amount);
    if (Number.isNaN(n)) return String(amount);
    return "$" + n.toLocaleString("en-US", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    });
  }

  function plansToPriceMap(plans) {
    var map = {};
    (plans || []).forEach(function (plan) {
      if (!plan || !plan.slug) return;
      var monthly = parseFloat(plan.monthly_price, 10);
      var annual = plan.yearly_price
        ? parseFloat(plan.yearly_price, 10)
        : null;
      if (Number.isNaN(monthly)) return;
      map[plan.slug] = {
        monthly: monthly,
        annual: Number.isNaN(annual) ? null : annual,
      };
    });
    return map;
  }

  function setBillingPeriod(period) {
    var prices = planPrices || FALLBACK_PLANS;
    var isAnnual = period === "annual";
    var labels = PERIOD_LABELS[pageLang()] || PERIOD_LABELS.en;

    document.querySelectorAll("[data-plan]").forEach(function (card) {
      var key = card.getAttribute("data-plan");
      var row = prices[key];
      if (!row) return;

      var priceEl = card.querySelector("[data-plan-price]");
      var periodEl = card.querySelector("[data-plan-period]");
      var saveBadge = card.querySelector("[data-plan-save]");

      var amount = isAnnual ? row.annual : row.monthly;
      if (amount == null && isAnnual) {
        amount = row.monthly;
      }

      if (priceEl && amount != null) {
        priceEl.textContent = formatPrice(amount);
      }
      if (periodEl) {
        periodEl.textContent = isAnnual ? labels.annual : labels.monthly;
      }
      if (saveBadge) {
        saveBadge.classList.toggle("is-visible", isAnnual);
      }

      card.querySelectorAll("[data-billing-note]").forEach(function (note) {
        var notePeriod = note.getAttribute("data-billing-note");
        note.classList.toggle("hidden", notePeriod !== period);
      });
    });

    document
      .querySelectorAll("#billing-toggle [data-billing]")
      .forEach(function (btn) {
        var active = btn.getAttribute("data-billing") === period;
        btn.classList.toggle("billing-toggle-btn--active", active);
        btn.setAttribute("aria-pressed", active ? "true" : "false");
      });
  }

  function initToggle() {
    var billingToggle = document.getElementById("billing-toggle");
    if (!billingToggle) return;

    billingToggle.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-billing]");
      if (!btn) return;
      setBillingPeriod(btn.getAttribute("data-billing"));
    });
    setBillingPeriod("monthly");
  }

  function loadPlans() {
    var url = resolvePlansUrl();

    return fetch(url, {
      credentials: "omit",
      mode: "cors",
      headers: { Accept: "application/json" },
    })
      .then(function (res) {
        if (!res.ok) {
          throw new Error("HTTP " + res.status + " for " + url);
        }
        return res.json();
      })
      .then(function (data) {
        var map = plansToPriceMap(data.plans);
        if (!Object.keys(map).length) {
          throw new Error("empty plans list");
        }
        planPrices = map;
        if (typeof console !== "undefined" && console.debug) {
          console.debug("[JobRhythm pricing] loaded from API", url, map);
        }
      })
      .catch(function (err) {
        planPrices = FALLBACK_PLANS;
        if (typeof console !== "undefined" && console.warn) {
          console.warn(
            "[JobRhythm pricing] API failed, using fallback prices:",
            err && err.message ? err.message : err,
            "| URL:",
            url
          );
        }
      })
      .finally(initToggle);
  }

  if (document.querySelector("[data-plan]")) {
    loadPlans();
  }
})();
