/* Lead form guard for saleshub.info
   - Work email only (free and throwaway email providers are rejected)
   - Hidden honeypot field and a minimum fill time stop bots without bothering people
   - Name sanity check (no digits, links or known spam patterns)
   - Keeps the visitor's Google Ads UTM tags for the session and writes them into the lead Description
   - Fires the Google Ads "Contact Us" conversion only after every check passes
   - Adds "Checks: website-v1" to the Description so a Salesforce validation rule can reject
     Web-to-Lead posts that did not come through this form */
(function () {
  var FREE = ["gmail.com","googlemail.com","ymail.com","rocketmail.com","msn.com","icloud.com","me.com","mac.com",
    "aol.com","aim.com","proton.me","protonmail.com","pm.me","mail.com","email.com","zohomail.com","inbox.com",
    "mail.ru","qq.com","163.com","126.com","sina.com","rediffmail.com","tutanota.com","tuta.io","fastmail.com",
    "hushmail.com","att.net","comcast.net","verizon.net","sbcglobal.net","bellsouth.net","cox.net","charter.net",
    "earthlink.net","optonline.net","btinternet.com","web.de","libero.it","orange.fr","free.fr","laposte.net",
    "naver.com","daum.net","hanmail.net","seznam.cz","wp.pl","o2.pl","juno.com","frontier.com","windstream.net",
    "mailinator.com","guerrillamail.com","sharklasers.com","10minutemail.com","temp-mail.org","yopmail.com",
    "trashmail.com","getnada.com","dispostable.com","maildrop.cc","throwawaymail.com","fakeinbox.com",
    "mintemail.com","moakt.com","emailondeck.com","spamgourmet.com","mailnesia.com","tempmail.dev","tempail.com"];
  var FREE_FAMILY = /^(yahoo|hotmail|outlook|live|gmx|yandex|tempmail|temp-mail|guerrillamail|10minutemail)\.[a-z.]+$/;
  var MARKER = "Checks: website-v1";
  var MIN_MS = 3000;

  function domainOf(email) { var m = /@([^@\s]+)$/.exec(String(email).trim().toLowerCase()); return m ? m[1] : ""; }
  function isFreeEmail(email) { var d = domainOf(email); return !d || FREE.indexOf(d) > -1 || FREE_FAMILY.test(d); }
  function badName(v) { v = String(v || ""); return !v.trim() || v.length > 40 || /\d|https?:|www\.|[<>@]/i.test(v) || /goafegm/i.test(v); }

  // Keep UTM tags from the landing page for this visit (ads land on /offshore-delivery-pod, the form is on /contact-us)
  var UTM_KEYS = ["utm_source","utm_medium","utm_campaign","utm_content","utm_term","gclid"];
  var q = new URLSearchParams(location.search), utm = {};
  try { utm = JSON.parse(sessionStorage.getItem("sh_utm") || "{}"); } catch (_) {}
  var fresh = false;
  UTM_KEYS.forEach(function (k) { if (q.get(k)) { utm[k] = q.get(k); fresh = true; } });
  if (fresh) { try { sessionStorage.setItem("sh_utm", JSON.stringify(utm)); } catch (_) {} }
  if (!utm.landing && fresh) { utm.landing = location.pathname; try { sessionStorage.setItem("sh_utm", JSON.stringify(utm)); } catch (_) {} }

  var f = document.querySelector("form.lead");
  if (!f) return;
  var started = Date.now();

  // Honeypot: invisible to people, bots fill it in
  var hp = document.createElement("div");
  hp.setAttribute("aria-hidden", "true");
  hp.style.cssText = "position:absolute;left:-10000px;top:auto;width:1px;height:1px;overflow:hidden";
  hp.innerHTML = '<label for="hp_site">Company website</label><input id="hp_site" name="company_website" type="text" tabindex="-1" autocomplete="off">';
  f.appendChild(hp);

  function showErr(input, msg) {
    var box = input.parentNode, e = box.querySelector(".lg-err");
    if (!e) { e = document.createElement("div"); e.className = "lg-err"; e.setAttribute("role", "alert"); e.style.cssText = "color:#c62828;font-size:13px;margin-top:4px"; box.appendChild(e); }
    e.textContent = msg; input.setAttribute("aria-invalid", "true");
  }
  function clearErr(input) { var e = input.parentNode.querySelector(".lg-err"); if (e) e.remove(); input.removeAttribute("aria-invalid"); }
  [].forEach.call(f.querySelectorAll("input,select,textarea"), function (i) { i.addEventListener("input", function () { clearErr(i); }); });

  function fakeSuccess() {
    f.innerHTML = '<div class="full"><b>Thanks, we have it.</b> We reply within one business day.</div>';
  }

  f.addEventListener("submit", function (ev) {
    var g = function (n) { var el = f.querySelector('[name="' + n + '"]'); return el ? el.value.trim() : ""; };

    // Bots: drop silently, no lead, no conversion
    if (g("company_website") || Date.now() - started < MIN_MS) { ev.preventDefault(); fakeSuccess(); return; }

    var ok = true, first = null;
    var fn = f.querySelector('[name="first_name"]'), ln = f.querySelector('[name="last_name"]'),
        em = f.querySelector('[name="email"]'), co = f.querySelector('[name="company"]');
    function fail(el, msg) { showErr(el, msg); ok = false; if (!first) first = el; }
    if (fn && badName(fn.value)) fail(fn, "Please add your first name.");
    if (ln && badName(ln.value)) fail(ln, "Please add your last name.");
    if (em) {
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em.value.trim())) fail(em, "Please add a valid work email.");
      else if (isFreeEmail(em.value)) fail(em, "Please use your work email. Personal addresses like Gmail, Yahoo or Outlook are not accepted. No work email? Write to support@saleshub.info.");
    }
    if (co && (co.value.trim().length < 2 || /^(google|n\/?a|none|test|self|personal|individual)$/i.test(co.value.trim()))) fail(co, "Please add your company name.");
    if (!ok) { ev.preventDefault(); first.focus(); return; }

    // Build the Description Salesforce receives
    var s = f.querySelector("#int"), m = f.querySelector("#msg");
    var utmLine = ["utm_source","utm_medium","utm_campaign","utm_content","utm_term"].map(function (k) { return utm[k]; }).filter(Boolean).join(" / ") || "none";
    var d = document.createElement("input"); d.type = "hidden"; d.name = "description";
    d.value = [
      (s ? s.value : "") + (m && m.value ? ": " + m.value : "") + " (" + location.pathname + ")",
      "UTM: " + utmLine + (utm.gclid ? " / gclid" : ""),
      "Landing: " + (utm.landing || location.pathname),
      "Referrer: " + (document.referrer || "direct"),
      MARKER
    ].join("\n");
    if (s) s.removeAttribute("name");
    if (m) m.removeAttribute("name");
    hp.remove();
    f.appendChild(d);

    // Send the conversion before the browser leaves the page, then post to Salesforce
    ev.preventDefault();
    var sent = false, go = function () { if (sent) return; sent = true; f.submit(); };
    try {
      gtag("event", "generate_lead", { form: "saleshub.info", interest: s ? s.value : "" });
      gtag("event", "ads_conversion_Contact_Us_1", { event_callback: go, event_timeout: 1500 });
    } catch (_) {}
    setTimeout(go, 1800);
  });
})();
