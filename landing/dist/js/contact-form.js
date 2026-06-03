/**
 * Formulario de contacto de la landing → POST /api/landing/contact/
 * - getjobrhythm.com: mismo origen (nginx → api.jobrhythm.net / schema public)
 * - Local: api.chalanpro.net:8000 o ?api_base=
 */
(function () {
  /** Cuenta dígitos antes de la posición del cursor (para restaurar selección). */
  function countDigitsBefore(str, pos) {
    var n = 0;
    for (var i = 0; i < pos && i < str.length; i++) {
      if (/\d/.test(str.charAt(i))) n++;
    }
    return n;
  }

  function positionAfterDigits(formatted, digitCount) {
    if (digitCount <= 0) return 0;
    var seen = 0;
    for (var i = 0; i < formatted.length; i++) {
      if (/\d/.test(formatted.charAt(i))) {
        seen++;
        if (seen === digitCount) return i + 1;
      }
    }
    return formatted.length;
  }

  /**
   * Formato al escribir:
   * - 10 dígitos (NANP): (555) 123-4567
   * - 11 dígitos empezando por 1: +1 (555) 123-4567
   * - Con "+": código país + bloque nacional
   */
  function formatPhoneInput(value) {
    if (!value) return "";
    var trimmed = value.trim();
    var startsWithPlus = trimmed.charAt(0) === "+";
    var digits = value.replace(/\D/g, "");
    if (!digits) return startsWithPlus ? "+" : "";

    if (!startsWithPlus && digits.length === 11 && digits.charAt(0) === "1") {
      return formatPhoneInput("+" + digits);
    }

    var useIntl = startsWithPlus || digits.length > 10;
    if (!useIntl) {
      var d = digits.slice(0, 10);
      if (d.length <= 3) return d.length ? "(" + d : "";
      if (d.length <= 6) return "(" + d.slice(0, 3) + ") " + d.slice(3);
      return (
        "(" +
        d.slice(0, 3) +
        ") " +
        d.slice(3, 6) +
        "-" +
        d.slice(6, 10)
      );
    }

    var ccLen = digits.length > 10 ? digits.length - 10 : 1;
    var cc = digits.slice(0, ccLen);
    var nat = digits.slice(ccLen, ccLen + 10);
    var out = "+" + cc;
    if (!nat) return out;
    if (nat.length <= 3) return out + " (" + nat;
    if (nat.length <= 6) {
      return out + " (" + nat.slice(0, 3) + ") " + nat.slice(3);
    }
    return (
      out +
      " (" +
      nat.slice(0, 3) +
      ") " +
      nat.slice(3, 6) +
      "-" +
      nat.slice(6, 10)
    );
  }

  function initPhoneFormatting(form) {
    var phoneInput = form.querySelector('input[name="phone"]');
    if (!phoneInput) return;

    phoneInput.setAttribute("maxlength", "40");

    phoneInput.addEventListener("input", function () {
      var el = phoneInput;
      var start = el.selectionStart || 0;
      var digitsBefore = countDigitsBefore(el.value, start);
      var formatted = formatPhoneInput(el.value);
      if (formatted === el.value) return;
      el.value = formatted;
      var pos = positionAfterDigits(formatted, digitsBefore);
      try {
        el.setSelectionRange(pos, pos);
      } catch (_e) {
        /* input type=tel en algunos navegadores */
      }
    });

    phoneInput.addEventListener("blur", function () {
      var formatted = formatPhoneInput(phoneInput.value);
      if (formatted !== phoneInput.value) phoneInput.value = formatted;
    });
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

  function resolveContactUrl() {
    var params = new URLSearchParams(window.location.search);
    var override = params.get("api_base");
    if (override) {
      return override.replace(/\/$/, "") + "/api/landing/contact/";
    }
    var host = window.location.hostname;
    if (isMarketingHost(host)) {
      return "/api/landing/contact/";
    }
    if (isLocalDevHost(host)) {
      return "http://api.chalanpro.net:8000/api/landing/contact/";
    }
    var meta = document.querySelector('meta[name="jobrhythm-api-base"]');
    if (meta && meta.content) {
      return meta.content.replace(/\/$/, "") + "/api/landing/contact/";
    }
    return "https://api.jobrhythm.net/api/landing/contact/";
  }

  function initContactForm() {
    var form = document.getElementById("landing-contact-form");
    if (!form) return;

    var okEl = document.getElementById("contact-form-success");
    var errEl = document.getElementById("contact-form-error");
    var endpoint = resolveContactUrl();
    var locale =
      (form.getAttribute("data-locale") || document.documentElement.lang || "en")
        .toLowerCase()
        .indexOf("es") === 0
        ? "es"
        : "en";

    var messages = {
      es: {
        success: "Mensaje enviado. Te responderemos pronto.",
        genericError:
          "No se pudo enviar el mensaje. Inténtalo de nuevo más tarde.",
        networkError:
          "Error de red. Comprueba tu conexión e inténtalo de nuevo.",
      },
      en: {
        success: "Message sent. We will get back to you soon.",
        genericError: "Could not send your message. Please try again later.",
        networkError: "Network error. Check your connection and try again.",
      },
    };
    var copy = messages[locale] || messages.en;

    initPhoneFormatting(form);

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (okEl) {
        okEl.classList.add("hidden");
        okEl.textContent = "";
      }
      if (errEl) {
        errEl.classList.add("hidden");
        errEl.textContent = "";
      }

      var submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      var fd = new FormData(form);
      var payload = {
        name: fd.get("name"),
        email: fd.get("email"),
        phone: fd.get("phone"),
        subject: fd.get("subject"),
        team_size: fd.get("team_size"),
        message: fd.get("message"),
        locale: locale,
      };

      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
        .then(function (r) {
          return r.json().then(function (d) {
            return { status: r.status, data: d };
          });
        })
        .then(function (res) {
          if (
            res.status >= 200 &&
            res.status < 300 &&
            res.data &&
            res.data.success
          ) {
            if (okEl) {
              okEl.textContent = copy.success;
              okEl.classList.remove("hidden");
            }
            form.reset();
          } else if (errEl) {
            errEl.textContent =
              (res.data && res.data.error) || copy.genericError;
            errEl.classList.remove("hidden");
          }
        })
        .catch(function () {
          if (errEl) {
            errEl.textContent = copy.networkError;
            errEl.classList.remove("hidden");
          }
        })
        .finally(function () {
          if (submitBtn) submitBtn.disabled = false;
        });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initContactForm);
  } else {
    initContactForm();
  }
})();
