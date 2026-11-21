/* Card app (Hair Salon / Barber) — customer screens. No frameworks, works offline, no tracking. */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const RTL = new Set(["ar", "fa", "ur", "ps", "ckb", "prs", "he"]);
const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
let C = null, L = "en", API = true;
const S = { cat: "", who: "", hair: "", bk: { step: 0 }, heroI: 0, ticket: localStorage.getItem("queue_ticket") || "" };

function t(k) { const d = I18N[L] || I18N[I18N_FALLBACK[L]] || {}; return d[k] || I18N.en[k] || k; }
function tx(o) { if (!o) return ""; if (typeof o === "string") return o; return o[L] || o[C.default_language] || Object.values(o)[0] || ""; }
function money(p) { if (p === "" || p == null) return ""; const n = Number(p); return "£" + (Number.isInteger(n) ? n : n.toFixed(2)); }
function loc() { return { zh: "zh-CN", prs: "fa-AF", kmr: "ku", ckb: "ckb" }[L] || L; }
function waNum(n) { return (n || "").replace(/^0/, "44").replace(/\D/g, ""); }
function hit(e) { if (API && C.modules.analytics) fetch("/api/hit", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ event: e }) }).catch(() => {}); }
async function api(path, body) {
  let r;
  try { r = await fetch("/api/" + path, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); }
  catch (e) { const n = new Error("offline"); n.network = true; throw n; }
  let j = {}; try { j = await r.json(); } catch (e) { }
  if (!r.ok) { const n = new Error(j.message || (r.status === 404 ? "preview" : "Something went wrong")); if (j.alternatives) n.alternatives = j.alternatives; throw n; }
  return j;
}
const tm = s => +s.slice(0, 2) * 60 + +s.slice(3);
const hm = m => String(Math.floor(m / 60)).padStart(2, "0") + ":" + String(m % 60).padStart(2, "0");
function isoDay(d) { return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0"); }
function hoursFor(d) { const h = C.hours[(d.getDay() + 6) % 7]; if (!h || h.closed || (C.closed_dates || []).includes(isoDay(d))) return null; return h; }
function openNow() { const n = new Date(), h = hoursFor(n); if (!h) return false; const m = n.getHours() * 60 + n.getMinutes(); return m >= tm(h.open) && m < tm(h.close); }
function dayName(i, style = "long") { const d = new Date(2024, 0, 1 + i); try { return d.toLocaleDateString(loc(), { weekday: style }); } catch (e) { return d.toLocaleDateString("en-GB", { weekday: style }); } }
function staffName(id) { const s = C.staff.find(x => x.id === id); return s ? s.name : t("any_staff"); }
function initial(n) { return (n || "?").trim().slice(0, 1).toUpperCase(); }
function optLabel(list, v) { const o = (C.service_options[list] || []).find(x => x[0] === v); return o ? (t(v) !== v ? t(v) : o[1]) : v; }

/* ------------------------------------------------------------------ render */
function render() {
  document.documentElement.lang = L; document.documentElement.dir = RTL.has(L) ? "rtl" : "ltr";
  const st = document.documentElement.style, c = C.colours;
  st.setProperty("--p", c.primary); st.setProperty("--a", c.accent); st.setProperty("--bg", c.bg); st.setProperty("--t", c.text); st.setProperty("--s", c.surface || "#fff");
  st.setProperty("--r", C.radius || "16px"); st.setProperty("--fd", C.fonts.display); st.setProperty("--fb", C.fonts.body);
  document.body.dataset.preset = C.preset;
  const M = C.modules, open = openNow(), today = (new Date().getDay() + 6) % 7, th = C.hours[today];
  const heroes = C.hero_images.length ? C.hero_images : ["img/pattern.svg"];
  const wa = waNum(C.whatsapp);
  const avg = C.reviews.length ? (C.reviews.reduce((a, r) => a + r.stars, 0) / C.reviews.length) : 0;
  $("#app").innerHTML = `
  ${C.demo ? `<div class="demo">${esc(t("demo"))}${C.demo_note ? `<br><small>${esc(C.demo_note)}</small>` : ""}</div>` : ""}
  ${C.static_copy ? `<div class="offer"><b>ℹ</b>${esc(C.static_note || "")}</div>` : ""}
  <div class="offline">${esc(t("offline"))}</div>
  ${M.offers && C.offer_on && tx(C.offer) ? `<div class="offer"><b>${esc(t("offers"))}</b>${esc(tx(C.offer))}</div>` : ""}
  <div class="bar"><div class="mono">${C.logo ? `<img src="${esc(C.logo)}" alt="">` : esc(initial(C.name))}</div><div class="nm">${esc(C.name)}</div>
    ${C.languages.length > 1 ? `<select id="lang" aria-label="Language">${C.languages.map(l => `<option value="${l}" ${l === L ? "selected" : ""}>${esc(C.lang_names[l] || l)}</option>`).join("")}</select>` : ""}
    ${M.accessibility ? `<button class="ibtn" id="a11yb" aria-label="${esc(t("access"))}">Aa</button>` : ""}</div>
  ${M.hero ? `<header class="hero"><div class="bgimg" id="heroimg" style="background-image:url('${esc(heroes[0])}')"></div>
    ${heroes.length > 1 ? `<div class="dots">${heroes.map((_, i) => `<i class="${i ? "" : "on"}"></i>`).join("")}</div>` : ""}
    <div class="in"><span class="pill ${open ? "" : "shut"}">${esc(open ? t("open_now") : t("closed_now"))}${th && !th.closed ? ` · ${th.open}–${th.close}` : ""}</span>
      <h1>${esc(C.name)}</h1>${tx(C.tagline) ? `<p class="tag">${esc(tx(C.tagline))}</p>` : ""}
      <div class="cta">${C.booking_mode ? `<a class="btn acc" href="#book" data-hit="book_start">${esc(t("book_now"))}</a>` : ""}
      ${M.walkin_queue ? `<a class="btn light" href="#queue">${esc(t("queue_join"))}</a>` : ""}
      ${M.contact_bar && wa ? `<a class="btn light" href="https://wa.me/${wa}" data-hit="whatsapp">${esc(t("whatsapp"))}</a>` : ""}</div></div></header>` : ""}
  <div class="strip"><div><b>${th && !th.closed ? esc(th.open + "–" + th.close) : esc(t("closed"))}</b>${esc(dayName(today, "short"))}</div>
    <div><b>${C.services.length ? esc(money(Math.min(...C.services.filter(s => s.price_from).map(s => +s.price_from)))) || "—" : "—"}</b>${esc(t("from"))}</div>
    <div><b>${avg ? avg.toFixed(1) + " ★" : esc(C.postcode || "—")}</b>${avg ? esc(t("reviews")) : esc(t("find_us"))}</div></div>
  <main>
  ${M.services ? `<section id="services"><div class="kick">${esc(C.name)}</div><h2>${esc(t("services"))}</h2><div id="svcwrap"></div><p class="small muted">${esc(t("price_note"))}</p></section>` : ""}
  ${C.booking_mode ? `<section id="book"><div class="kick">${esc(t("book"))}</div><h2>${esc(t("book_now"))}</h2><div class="bk" id="bk"></div></section>` : ""}
  ${M.walkin_queue ? `<section id="queue"><div class="kick">${esc(t("queue"))}</div><h2>${esc(t("queue_join"))}</h2><div id="qw"></div></section>` : ""}
  ${M.staff && C.staff.length ? `<section id="team"><div class="kick">${esc(C.staff_word_plural)}</div><h2>${esc(t("team"))}</h2><div class="team">${C.staff.map(personCard).join("")}</div></section>` : ""}
  ${M.gallery && C.gallery.length ? `<section id="gallery"><div class="kick">${esc(t("gallery"))}</div><h2>${esc(t("gallery"))}</h2><div class="gal">${C.gallery.map(g => `<figure><img loading="lazy" src="${esc(g.image)}" alt="${esc(tx(g.caption))}">${tx(g.caption) ? `<figcaption>${esc(tx(g.caption))}</figcaption>` : ""}</figure>`).join("")}</div></section>` : ""}
  ${M.before_after && C.before_after.length ? `<section id="ba"><div class="kick">${esc(t("gallery"))}</div><h2>${esc(t("before_after"))}</h2><div class="ba two">${C.before_after.map(b => `<div><div class="cmp"><img src="${esc(b.after)}" alt="${esc(t("after"))}"><img class="top" src="${esc(b.before)}" alt="${esc(t("before"))}"><span class="lb" style="inset-inline-start:10px">${esc(t("before"))}</span><span class="lb" style="inset-inline-end:10px">${esc(t("after"))}</span><input type="range" min="0" max="100" value="50" aria-label="${esc(t("before_after"))}"></div>${tx(b.caption) ? `<p class="small muted">${esc(tx(b.caption))}</p>` : ""}</div>`).join("")}</div></section>` : ""}
  ${M.reviews && (C.reviews.length || C.review_link) ? `<section id="reviews"><div class="kick">${esc(t("reviews"))}</div><h2>${esc(t("reviews"))}</h2>
    ${avg ? `<div class="avg"><b>${avg.toFixed(1)}</b><div><div class="stars">${"★".repeat(Math.round(avg))}${"☆".repeat(5 - Math.round(avg))}</div><div class="small muted">${C.reviews.length} ${esc(t("reviews")).toLowerCase()}</div></div></div>` : ""}
    <div class="rv">${C.reviews.map(r => `<div class="c"><div class="stars">${"★".repeat(r.stars)}${"☆".repeat(5 - r.stars)}</div><p>${esc(r.text)}</p><b>${esc(r.author)}</b><div class="src">${esc(r.source)}</div></div>`).join("")}</div>
    ${C.review_link ? `<p><a class="btn ghost" href="${esc(C.review_link)}" target="_blank" rel="noopener" data-hit="review_click">★ ${esc(t("leave_review"))}</a></p>` : ""}</section>` : ""}
  ${extrasHTML()}
  ${M.retail && C.products.length ? `<section id="shop"><div class="kick">${esc(t("shop"))}</div><h2>${esc(t("shop"))}</h2><div class="prod" id="prod"></div></section>` : ""}
  <section id="visit"><div class="kick">${esc(t("find_us"))}</div><h2>${esc(t("hours"))}</h2><div class="two">
    ${M.hours ? `<div><div class="hrs">${C.hours.map((h, i) => `<div class="${i === today ? "today" : ""}"><span>${esc(dayName(i))}</span><span>${h.closed ? esc(t("closed")) : esc(h.open + "–" + h.close)}</span></div>`).join("")}</div>
      ${tx(C.hours_note) ? `<p class="small muted">${esc(tx(C.hours_note))}</p>` : ""}
      ${(C.closed_dates || []).length ? `<p class="small"><b>${esc(t("closed_dates"))}:</b> ${C.closed_dates.map(esc).join(", ")}</p>` : ""}</div>` : ""}
    <div>${C.address ? `<p><b>${esc(C.address)}</b>${C.postcode ? `<br>${esc(C.postcode)}` : ""}</p>` : ""}
      ${M.map && C.lat ? `<div class="map"><iframe loading="lazy" title="Map" src="https://www.openstreetmap.org/export/embed.html?bbox=${C.lon - 0.006},${C.lat - 0.0035},${C.lon + 0.006},${C.lat + 0.0035}&layer=mapnik&marker=${C.lat},${C.lon}"></iframe></div>` : ""}
      <div class="links" style="margin-top:12px">${C.map_url ? `<a class="btn" href="${esc(C.map_url)}" target="_blank" rel="noopener" data-hit="directions">📍 ${esc(t("directions"))}</a>` : ""}
      ${C.phone ? `<a class="btn ghost" href="tel:${esc(C.phone.replace(/\s/g, ""))}" data-hit="call">📞 ${esc(C.phone)}</a>` : ""}</div>
      ${M.multi_branch && C.branches.length ? `<div class="hrs" style="margin-top:14px">${C.branches.map(b => `<div><span><b>${esc(b.name)}</b><br><span class="small muted">${esc(b.address)} ${esc(b.postcode)}</span></span>${b.phone ? `<a href="tel:${esc(b.phone)}">${esc(b.phone)}</a>` : ""}</div>`).join("")}</div>` : ""}
      ${M.accessibility && tx(C.access_info) ? `<div class="box" style="margin-top:14px"><h3>♿ ${esc(t("access"))}</h3><p>${esc(tx(C.access_info))}</p></div>` : ""}
    </div></div></section>
  ${M.policy && tx(C.policy_text) ? `<section id="policy"><h2>${esc(t("policy"))}</h2><div class="box"><p style="white-space:pre-line;margin:0">${esc(tx(C.policy_text))}</p></div></section>` : ""}
  ${(M.social_links && (C.instagram || C.tiktok)) || (M.platform_links && Object.values(C.platform_links || {}).some(Boolean)) ? `<section><div class="two">
    ${M.social_links && (C.instagram || C.tiktok) ? `<div><h3>${esc(t("follow"))}</h3><div class="links">${C.instagram ? `<a class="btn ghost sm" href="${esc(C.instagram)}" target="_blank" rel="noopener">Instagram</a>` : ""}${C.tiktok ? `<a class="btn ghost sm" href="${esc(C.tiktok)}" target="_blank" rel="noopener">TikTok</a>` : ""}</div></div>` : ""}
    ${M.platform_links && Object.values(C.platform_links || {}).some(Boolean) ? `<div><h3>${esc(t("book_elsewhere"))}</h3><div class="links">${Object.entries(C.platform_links).filter(([, v]) => v).map(([k, v]) => `<a class="btn ghost sm" href="${esc(v)}" target="_blank" rel="noopener" data-hit="platform_link">${esc({ fresha: "Fresha", treatwell: "Treatwell", booksy: "Booksy" }[k])} ↗</a>`).join("")}</div></div>` : ""}
  </div></section>` : ""}
  </main>
  <footer>${M.install ? `<p><button class="btn ghost sm" id="inst" hidden>⬇ ${esc(t("install"))}</button></p>` : ""}
    <p>${esc(C.made_with)}</p><p><a href="/admin/">${esc(t("admin"))}</a></p></footer>
  ${M.contact_bar ? `<nav class="dock">${C.phone ? `<a href="tel:${esc(C.phone.replace(/\s/g, ""))}" data-hit="call"><span class="ic">📞</span>${esc(t("call"))}</a>` : "<span></span>"}
    ${wa ? `<a href="https://wa.me/${wa}" data-hit="whatsapp"><span class="ic">💬</span>${esc(t("whatsapp"))}</a>` : "<span></span>"}
    ${C.map_url ? `<a href="${esc(C.map_url)}" target="_blank" rel="noopener" data-hit="directions"><span class="ic">📍</span>${esc(t("directions"))}</a>` : "<span></span>"}
    ${C.booking_mode ? `<a class="main" href="#book" data-hit="book_start"><span class="ic">✂</span>${esc(t("book"))}</a>` : M.walkin_queue ? `<a class="main" href="#queue"><span class="ic">✂</span>${esc(t("queue"))}</a>` : "<span></span>"}</nav>` : ""}
  ${M.accessibility ? `<div class="a11y" id="a11y"><b>${esc(t("access"))}</b><label class="tick"><input type="checkbox" data-a="big"> ${esc(t("bigger_text"))}</label><label class="tick"><input type="checkbox" data-a="hc"> ${esc(t("contrast"))}</label><label class="tick"><input type="checkbox" data-a="rm"> ${esc(t("less_motion"))}</label></div>` : ""}`;
  wire();
  if (M.services) renderServices();
  if (C.booking_mode) renderBooking();
  if (M.walkin_queue) renderQueue();
  if (M.retail) renderProducts();
}

function personCard(s) {
  const ph = s.photo ? `<div class="ph" style="background-image:url('${esc(s.photo)}')"></div>` : `<div class="ph pat"><span>${esc(initial(s.name))}</span></div>`;
  return `<div class="person">${ph}<div class="bd"><h3>${esc(s.name)}</h3><div class="role">${esc(tx(s.role))}</div>${tx(s.bio) ? `<p>${esc(tx(s.bio))}</p>` : ""}
    <div class="row">${(s.specialities || []).map(x => `<span class="tag">${esc(x)}</span>`).join("")}</div>
    ${C.booking_mode && s.bookable !== false ? `<p><a class="btn sm acc" href="#book" data-staff="${esc(s.id)}">${esc(t("book"))}</a></p>` : ""}</div></div>`;
}

function extrasHTML() {
  const M = C.modules; const parts = [];
  if (M.loyalty) parts.push(`<div class="box"><h3>★ ${esc(t("loyalty"))}</h3><p class="small muted">${C.loyalty.stamps_needed} ${esc(t("stamps"))} → ${esc(C.loyalty.reward)}</p>
    <div class="row"><input id="lcode" placeholder="${esc(t("card_code"))}" autocapitalize="characters"><button class="btn sm" id="lgo">${esc(t("check"))}</button></div><div id="lres"></div></div>`);
  if (M.vouchers) parts.push(`<div class="box"><h3>🎁 ${esc(t("vouchers"))}</h3>
    <div class="row">${(C.vouchers.amounts || []).map(a => C.vouchers.pay_link ? `<a class="btn sm acc" href="${esc(C.vouchers.pay_link)}" target="_blank" rel="noopener">£${esc(a)}</a>` : (waNum(C.whatsapp) ? `<a class="btn sm acc" href="https://wa.me/${waNum(C.whatsapp)}?text=${encodeURIComponent(t("buy_voucher") + " £" + a)}">£${esc(a)}</a>` : `<span class="tag">£${esc(a)}</span>`)).join("")}</div>
    <p class="small muted" style="margin-top:12px">${esc(t("voucher_check"))}</p><div class="row"><input id="vcode" placeholder="${esc(t("voucher_code"))}" autocapitalize="characters"><button class="btn sm" id="vgo">${esc(t("check"))}</button></div><div id="vres"></div></div>`);
  if (M.packages && C.packages.length) parts.push(`<div class="box"><h3>♻ ${esc(t("packages"))}</h3>${C.packages.map(p => `<div class="row" style="justify-content:space-between;border-top:1px solid var(--line);padding:10px 0"><span><b>${esc(tx(p.name))}</b><br><span class="small muted">${p.uses} ${esc(t("visits"))} · ${esc(t("valid_for"))} ${p.valid_days} ${esc(t("days"))}</span></span><span>${p.price ? `<b>${esc(money(p.price))}</b>` : ""} ${p.pay_link ? `<a class="btn sm acc" href="${esc(p.pay_link)}" target="_blank" rel="noopener">${esc(t("buy"))}</a>` : ""}</span></div>`).join("")}</div>`);
  return parts.length ? `<section id="extras"><div class="cards">${parts.join("")}</div></section>` : "";
}

function wire() {
  const lang = $("#lang"); if (lang) lang.onchange = e => { L = e.target.value; localStorage.setItem("lang", L); render(); };
  $$("[data-hit]").forEach(a => a.addEventListener("click", () => hit(a.dataset.hit)));
  $$("[data-staff]").forEach(a => a.addEventListener("click", () => { S.bk.staff = a.dataset.staff; if (S.bk.step < 1) S.bk.step = 0; }));
  $$(".cmp input").forEach(r => r.oninput = () => r.parentElement.querySelector(".top").style.clipPath = `inset(0 ${100 - r.value}% 0 0)`);
  const a11yb = $("#a11yb"); if (a11yb) a11yb.onclick = () => $("#a11y").classList.toggle("show");
  $$("#a11y input").forEach(i => { const on = localStorage.getItem("a11y_" + i.dataset.a) === "1"; i.checked = on; applyA11y(i.dataset.a, on); i.onchange = () => { localStorage.setItem("a11y_" + i.dataset.a, i.checked ? "1" : "0"); applyA11y(i.dataset.a, i.checked); }; });
  const lgo = $("#lgo"); if (lgo) lgo.onclick = async () => { try { const r = await api("loyalty/" + encodeURIComponent($("#lcode").value.trim())); $("#lres").innerHTML = `<div class="stamps">${Array.from({ length: r.stamps_needed }, (_, i) => `<i class="${i < r.stamps ? "on" : ""}">${i < r.stamps ? "✓" : ""}</i>`).join("")}</div>${r.rewards_ready ? `<b>🎉 ${esc(t("reward_ready"))}</b> ${esc(r.reward)}` : ""}`; } catch (e) { $("#lres").innerHTML = `<div class="err">${esc(e.message === "preview" ? "Preview only" : e.message)}</div>`; } };
  const vgo = $("#vgo"); if (vgo) vgo.onclick = async () => { try { const r = await api("voucher/" + encodeURIComponent($("#vcode").value.trim())); $("#vres").innerHTML = `<p><b>${esc(t("balance"))}: ${esc(r.balance)}</b><br><span class="small muted">${esc(t("expires"))} ${esc(r.expires)}${r.valid ? "" : " — not valid"}</span></p>`; } catch (e) { $("#vres").innerHTML = `<div class="err">${esc(e.message === "preview" ? "Preview only" : e.message)}</div>`; } };
  const heroes = C.hero_images; if (heroes.length > 1 && !document.body.classList.contains("rm")) { clearInterval(window._hero); window._hero = setInterval(() => { S.heroI = (S.heroI + 1) % heroes.length; const h = $("#heroimg"); if (!h) return; h.style.backgroundImage = `url('${heroes[S.heroI]}')`; $$(".hero .dots i").forEach((d, i) => d.classList.toggle("on", i === S.heroI)); }, 5000); }
}
function applyA11y(k, on) { if (k === "big") document.documentElement.style.setProperty("--fs", on ? "1.2" : "1"); else document.body.classList.toggle(k, on); }

/* ---------------------------------------------------------------- services */
function renderServices() {
  const cats = [...new Set(C.services.map(s => s.category).filter(Boolean))];
  const list = C.services.filter(s => (!S.cat || s.category === S.cat) && (!S.who || s.audience === S.who || s.audience === "anyone") && (!S.hair || !(s.hair_types || []).length || s.hair_types.includes(S.hair) || s.hair_types.includes("any")));
  const hairUsed = [...new Set(C.services.flatMap(s => s.hair_types || []))].filter(h => h !== "any");
  const whoUsed = [...new Set(C.services.map(s => s.audience))].filter(a => a && a !== "anyone");
  $("#svcwrap").innerHTML = `${cats.length > 1 ? `<div class="chips"><button class="chip ${S.cat ? "" : "on"}" data-c="">${esc(t("all"))}</button>${cats.map(c => `<button class="chip ${S.cat === c ? "on" : ""}" data-c="${esc(c)}">${esc(c)}</button>`).join("")}</div>` : ""}
    ${whoUsed.length || hairUsed.length ? `<div class="filters">${whoUsed.length ? `<select id="fwho" aria-label="${esc(t("who_for"))}"><option value="">${esc(t("who_for"))}: ${esc(t("all"))}</option>${whoUsed.map(w => `<option value="${w}" ${S.who === w ? "selected" : ""}>${esc(optLabel("audiences", w))}</option>`).join("")}</select>` : ""}
    ${hairUsed.length ? `<select id="fhair" aria-label="${esc(t("hair_type"))}"><option value="">${esc(t("hair_type"))}: ${esc(t("all"))}</option>${hairUsed.map(h => `<option value="${h}" ${S.hair === h ? "selected" : ""}>${esc(optLabel("hair_types", h))}</option>`).join("")}</select>` : ""}</div>` : ""}
    <div class="svc">${list.map(s => `<div class="it"><div><div class="nm">${esc(tx(s.name))}</div>${tx(s.description) ? `<div class="desc">${esc(tx(s.description))}</div>` : ""}
      <div class="meta"><span class="tag">⏱ ${s.duration_min} ${esc(t("min"))}</span>${s.audience && s.audience !== "anyone" ? `<span class="tag">${esc(optLabel("audiences", s.audience))}</span>` : ""}${(s.hair_types || []).filter(h => h !== "any").slice(0, 3).map(h => `<span class="tag">${esc(optLabel("hair_types", h))}</span>`).join("")}</div>
      ${tx(s.price_note) ? `<div class="desc">${esc(tx(s.price_note))}</div>` : ""}</div>
      <div class="pr">${s.price_from ? `<span class="f">${esc(t("from"))}</span><b>${esc(money(s.price_from))}</b>` : ""}${C.booking_mode ? `<div style="margin-top:6px"><a class="btn sm acc" href="#book" data-svc="${esc(s.id)}">${esc(t("book"))}</a></div>` : ""}</div></div>`).join("")}</div>`;
  $$("#svcwrap [data-c]").forEach(b => b.onclick = () => { S.cat = b.dataset.c; renderServices(); });
  const w = $("#fwho"); if (w) w.onchange = () => { S.who = w.value; renderServices(); };
  const h = $("#fhair"); if (h) h.onchange = () => { S.hair = h.value; renderServices(); };
  $$("#svcwrap [data-svc]").forEach(b => b.onclick = () => { S.bk = { step: 1, service: b.dataset.svc }; hit("book_start"); renderBooking(); });
}

/* ----------------------------------------------------------------- booking */
function svc() { return C.services.find(s => s.id === S.bk.service); }
function staffFor(s) { return C.staff.filter(x => x.bookable !== false && (!(s.staff_ids || []).length || s.staff_ids.includes(x.id)) && (!S.bk.branch || !x.branch || x.branch === S.bk.branch)); }
function renderBooking() {
  const el = $("#bk"); if (!el) return;
  const B = S.bk, steps = 5;
  const bar = `<div class="steps">${Array.from({ length: steps }, (_, i) => `<i class="${i <= B.step ? "on" : ""}"></i>`).join("")}</div>`;
  const summary = B.service ? `<div class="summary">✂ <b>${esc(tx(svc().name))}</b> · ${svc().duration_min} ${esc(t("min"))}${B.staff ? ` · ${esc(staffName(B.staff))}` : ""}${B.date ? ` · ${esc(new Date(B.date + "T12:00").toLocaleDateString(loc(), { weekday: "short", day: "numeric", month: "short" }))}` : ""}${B.time ? ` · ${esc(B.time)}` : ""}</div>` : "";
  if (B.outbox) {
    el.innerHTML = `<div class="okbox"><div class="big">📵</div><h3>${esc(t("not_sent"))}</h3><p>${esc(t("outbox_note"))}</p>${summary}
      <p><button class="btn ghost sm" id="bnew">${esc(t("back"))}</button></p></div>`;
    $("#bnew").onclick = () => { localStorage.removeItem("booking_outbox"); B.outbox = false; B.step = 4; renderBooking(); };
    return;
  }
  if (B.wa) {
    el.innerHTML = `<div class="okbox"><div class="big">💬</div><h3>${esc(t("wa_request_title"))}</h3><p><b>${esc(t("wa_request_note"))}</b></p>${summary}
      <div class="cta" style="justify-content:center"><a class="btn acc" href="${esc(B.wa)}" target="_blank" rel="noopener">${esc(t("wa_open"))}</a></div>
      <p><button class="btn ghost sm" id="bnew">${esc(t("book"))} +</button></p></div>`;
    $("#bnew").onclick = () => { S.bk = { step: 0 }; renderBooking(); };
    return;
  }
  if (B.done && B.done.status === "held") {
    const d = B.done, until = d.hold_until ? d.hold_until.slice(11, 16) : "";
    el.innerHTML = `<div class="okbox"><div class="big">⏳</div><h3>${esc(t("held_title"))}</h3>${summary}
      <p>${esc(t("held_until"))} <b>${esc(until)}</b>. ${esc(t("held_note"))}</p>
      <div class="small muted">${esc(t("booking_ref"))}</div><div class="ref">${esc(d.ref)}</div>
      ${d.pay_link ? `<div class="cta" style="justify-content:center;margin-top:12px"><a class="btn acc" href="${esc(d.pay_link)}" target="_blank" rel="noopener">💳 ${esc(t("pay_deposit"))}${d.deposit ? " " + esc(money(d.deposit)) : ""}</a></div>` : ""}
      ${d.pay_problem ? `<div class="err">${esc(d.pay_problem)}</div>` : ""}</div>`;
    clearTimeout(window._bt); window._bt = setTimeout(async () => {          // the server decides: confirmed, released or expired
      try { const s = await api("booking/" + d.ref); if (s.status !== "held") { B.done = Object.assign({}, d, { status: s.status }); } } catch (e) { }
      renderBooking(); }, 10000);
    return;
  }
  if (B.done && ["expired", "cancelled", "refund_due"].includes(B.done.status)) {
    el.innerHTML = `<div class="okbox"><div class="big">⌛</div><h3>${esc(t("cancelled_t"))}</h3><p>${esc(t("hold_expired"))}</p>${summary}
      <p><button class="btn ghost sm" id="bnew">${esc(t("book"))} +</button></p></div>`;
    $("#bnew").onclick = () => { S.bk = { step: 0 }; renderBooking(); };
    return;
  }
  if (B.done) {
    const d = B.done;
    el.innerHTML = `<div class="okbox"><div class="big">${d.status === "confirmed" ? "✅" : "📨"}</div><h3>${esc(d.status === "confirmed" ? t("booked") : t("request_sent"))}</h3>
      ${d.status !== "confirmed" ? `<p class="muted">${esc(t("request_note"))}</p>` : ""}${d.note ? `<p class="small">${esc(d.note)}</p>` : ""}${summary}
      <div class="small muted">${esc(t("booking_ref"))}</div><div class="ref">${esc(d.ref)}</div>
      <div class="cta" style="justify-content:center;margin-top:12px"><a class="btn" href="${esc(d.ics_url)}">📅 ${esc(t("add_calendar"))}</a>
      ${d.pay_link ? `<a class="btn acc" href="${esc(d.pay_link)}" target="_blank" rel="noopener">💳 ${esc(t("pay_deposit"))}${d.deposit ? " " + esc(money(d.deposit)) : ""}</a>` : ""}</div>
      <p><button class="btn ghost sm" id="bnew">${esc(t("book"))} +</button></p></div>`;
    $("#bnew").onclick = () => { S.bk = { step: 0 }; renderBooking(); };
    return;
  }
  let body = "";
  if (B.step === 0) {
    body = `<h3>1 · ${esc(t("step_service"))}</h3>${C.modules.multi_branch && C.branches.length ? `<div class="field"><label>${esc(t("branch"))}</label><select id="bbr">${C.branches.map(b => `<option value="${esc(b.id)}" ${B.branch === b.id ? "selected" : ""}>${esc(b.name)}</option>`).join("")}</select></div>` : ""}
      <div class="opts">${C.services.map(s => `<button class="opt ${B.service === s.id ? "on" : ""}" data-v="${esc(s.id)}"><div style="flex:1"><b>${esc(tx(s.name))}</b><div class="small muted">${s.duration_min} ${esc(t("min"))}${s.category ? " · " + esc(s.category) : ""}</div></div>${s.price_from ? `<b>${esc(money(s.price_from))}</b>` : ""}</button>`).join("")}</div>`;
  } else if (B.step === 1) {
    const st = staffFor(svc());
    body = `<h3>2 · ${esc(t("step_staff"))}</h3>${summary}<div class="opts"><button class="opt ${!B.staff || B.staff === "any" ? "on" : ""}" data-v="any"><div class="av">★</div><b>${esc(t("any_staff"))}</b></button>
      ${st.map(s => `<button class="opt ${B.staff === s.id ? "on" : ""}" data-v="${esc(s.id)}"><div class="av">${s.photo ? `<img src="${esc(s.photo)}" alt="">` : esc(initial(s.name))}</div><div><b>${esc(s.name)}</b><div class="small muted">${esc(tx(s.role))}</div></div></button>`).join("")}</div>`;
  } else if (B.step === 2) {
    if (API && C.booking_mode !== "whatsapp_request" && !S.days) {          // the shop's own calendar (its clock, its closed days)
      api("days" + (B.branch ? "?branch=" + encodeURIComponent(B.branch) : "")).then(r => { S.days = r.days; renderBooking(); })
        .catch(() => { S.days = []; renderBooking(); });
      el.innerHTML = bar + `<p class="muted">…</p>`; return;
    }
    let days = [];
    if (S.days && S.days.length) days = S.days.map(x => ({ d: new Date(x.date + "T12:00"), iso: x.date, h: x.closed ? null : { open: x.open, close: x.close } }));
    else { const now = new Date(); for (let i = 0; i < 21; i++) { const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i); days.push({ d, iso: isoDay(d), h: hoursFor(d) }); } }
    body = `<h3>3 · ${esc(t("step_day"))}</h3>${summary}<div class="daystrip">${days.map(({ d, iso, h }) => `<button class="day ${h ? "" : "shut"} ${B.date === iso ? "on" : ""}" data-v="${iso}"><small>${esc(d.toLocaleDateString(loc(), { weekday: "short" }))}</small><b>${d.getDate()}</b><small>${h ? esc(h.open + "–" + h.close) : esc(t("closed"))}</small></button>`).join("")}</div>`;
  } else if (B.step === 3) {
    body = `<h3>4 · ${esc(t("step_time"))}</h3>${summary}<div id="times"><p class="muted">…</p></div>`;
  } else if (B.step === 4) {
    body = `<h3>5 · ${esc(t("step_details"))}</h3>${summary}
      <div class="field"><label for="bn">${esc(t("name"))}</label><input id="bn" autocomplete="name" value="${esc(B.name || "")}"></div>
      <div class="field"><label for="bp">${esc(t("phone"))}</label><input id="bp" type="tel" autocomplete="tel" value="${esc(B.phone || "")}"></div>
      ${(svc().hair_types || []).length > 1 ? `<div class="field"><label for="bh">${esc(t("hair_type"))}</label><select id="bh"><option value=""></option>${svc().hair_types.filter(h => h !== "any").map(h => `<option value="${h}">${esc(optLabel("hair_types", h))}</option>`).join("")}</select></div>` : ""}
      <div class="field"><label for="bno">${esc(t("notes"))}</label><textarea id="bno">${esc(B.notes || "")}</textarea></div>
      ${C.modules.referrals ? `<div class="field"><label for="brf">${esc(t("referral"))}</label><input id="brf" autocapitalize="characters"></div>` : ""}
      <label class="tick"><input type="checkbox" id="bok" checked> ${esc(t("contact_ok"))}</label>
      ${C.policy_required ? `<label class="tick"><input type="checkbox" id="bpol"> <span>${esc(t("accept_policy"))} — <a href="#policy">${esc(t("policy"))}</a></span></label>` : ""}
      <div id="berr"></div>`;
  }
  const nextOk = [!!B.service, true, !!B.date, !!B.time, true][B.step];
  el.innerHTML = bar + body + `<div class="nav">${B.step ? `<button class="btn ghost" id="bback">${esc(t("back"))}</button>` : "<span></span>"}
    ${B.step < 4 ? `<button class="btn acc" id="bnext" ${nextOk ? "" : "disabled"}>${esc(t("next"))}</button>` : `<button class="btn acc" id="bsend">${esc(C.booking_mode === "instant" ? t("confirm_booking") : C.booking_mode === "whatsapp_request" ? t("wa_open") : t("send_request"))}</button>`}</div>`;
  const pick = (k) => $$(".opt,.day", el).forEach(b => b.onclick = () => { B[k] = b.dataset.v; if (k === "service") { B.staff = ""; } if (k === "date") B.time = ""; renderBooking(); });
  if (B.step === 0) { pick("service"); const br = $("#bbr"); if (br) { B.branch = B.branch || br.value; br.onchange = () => { B.branch = br.value; }; } }
  if (B.step === 1) pick("staff");
  if (B.step === 2) pick("date");
  if (B.step === 3) loadTimes();
  const back = $("#bback"); if (back) back.onclick = () => { B.step--; renderBooking(); };
  const nx = $("#bnext"); if (nx) nx.onclick = () => { B.step++; renderBooking(); el.scrollIntoView({ behavior: "smooth", block: "start" }); };
  const send = $("#bsend"); if (send) send.onclick = sendBooking;
}
async function loadTimes() {
  const B = S.bk, box = $("#times"), s = svc();
  let times = [];
  if (C.booking_mode === "instant" && API) {
    try { const r = await api(`slots?service=${encodeURIComponent(B.service)}&date=${B.date}&staff=${encodeURIComponent(B.staff || "any")}&branch=${encodeURIComponent(B.branch || "")}`); times = r.slots.map(x => x.time); if (!times.length) { box.innerHTML = `<p class="muted">${esc(r.note || t("no_slots"))}</p>`; return; } }
    catch (e) { API = false; }
  }
  if (!times.length) {
    const d = new Date(B.date + "T00:00"), h = hoursFor(d); if (!h) { box.innerHTML = `<p>${esc(t("closed"))}</p>`; return; }
    const now = new Date(), minStart = (isoDay(now) === B.date) ? now.getHours() * 60 + now.getMinutes() + 60 : 0;
    for (let m = tm(h.open); m + s.duration_min <= tm(h.close); m += 15) if (m >= minStart) times.push(hm(m));
    if (!times.length) { box.innerHTML = `<p class="muted">${esc(t("no_slots"))}</p>`; return; }
  }
  box.innerHTML = `${C.booking_mode !== "instant" ? `<p class="small muted">${esc(t("preferred_time"))} — ${esc(t("ask_time"))}</p>` : ""}<div class="times">${times.map(x => `<button class="time ${B.time === x ? "on" : ""}" data-v="${x}">${x}</button>`).join("")}</div>`;
  $$(".time", box).forEach(b => b.onclick = () => { B.time = b.dataset.v; $$(".time", box).forEach(x => x.classList.toggle("on", x === b)); $("#bnext").disabled = false; });
}
async function sendBooking() {
  const B = S.bk;
  B.name = $("#bn").value.trim(); B.phone = $("#bp").value.trim(); B.notes = $("#bno").value.trim();
  const body = { service_id: B.service, staff_id: B.staff || "any", date: B.date, time: B.time, name: B.name, phone: B.phone, notes: B.notes,
    hair_type: ($("#bh") || {}).value || "", referral_code: ($("#brf") || {}).value || "", contact_ok: $("#bok").checked, accept_policy: ($("#bpol") || {}).checked || false, branch: B.branch || "" };
  const err = m => $("#berr").innerHTML = `<div class="err">${esc(m)}</div>`;
  if (!B.name || !B.phone) return err(t("name") + " / " + t("phone"));
  if (C.policy_required && !body.accept_policy) return err(t("accept_policy"));
  if (!API || C.booking_mode === "whatsapp_request") return waRequest(err);
  if (!navigator.onLine) return toOutbox(body);
  try { $("#bsend").disabled = true; B.done = await api("book", body); localStorage.removeItem("booking_outbox"); renderBooking(); }
  catch (e) {
    $("#bsend").disabled = false;
    if (e.message === "preview") { API = false; return sendBooking(); }
    if (e.network) return toOutbox(body);
    if (e.alternatives) return slotGone(e, err);
    err(e.message);
  }
}
function waRequest(err) {                 // no always-on server: a WhatsApp request, clearly not a booking (B21)
  const B = S.bk, wa = waNum(C.whatsapp);
  if (!wa) return err(t("call") + ": " + (C.phone || ""));
  B.wa = `https://wa.me/${wa}?text=${encodeURIComponent(`${t("hello_book")}: ${tx(svc().name)}, ${B.date} ${B.time}, ${staffName(B.staff)}. ${B.name} (${B.phone})${B.notes ? " - " + B.notes : ""}`)}`;
  renderBooking();
}
function toOutbox(body) {                 // offline: saved on the phone, marked NOT booked (B20)
  localStorage.setItem("booking_outbox", JSON.stringify(body)); S.bk.outbox = true; renderBooking();
}
function slotGone(e, err) {
  const B = S.bk;
  err(`${t("slot_gone")} ${e.alternatives.length ? t("other_times") : ""}`);
  if (e.alternatives.length) {
    $("#berr").insertAdjacentHTML("beforeend", `<div class="times">${e.alternatives.map(x => `<button class="time" data-alt="${x}">${x}</button>`).join("")}</div>`);
    $$("[data-alt]").forEach(b => b.onclick = () => { B.time = b.dataset.alt; renderBooking(); });
  }
}
async function flushOutbox() {            // back online: send it now; the server re-checks the time like any other request
  const raw = localStorage.getItem("booking_outbox"); if (!raw || !API) return;
  const body = JSON.parse(raw), B = S.bk;
  try { B.done = await api("book", body); B.outbox = false; localStorage.removeItem("booking_outbox"); }
  catch (e) {
    if (e.network) return;
    localStorage.removeItem("booking_outbox"); B.outbox = false;
    Object.assign(B, { service: body.service_id, staff: body.staff_id, date: body.date, time: "", step: 3 });
    renderBooking(); setTimeout(() => { const box = $("#times"); if (box) box.insertAdjacentHTML("afterbegin", `<div class="err">${esc(t("slot_gone"))} ${esc(e.message)}</div>`); }, 400);
    return;
  }
  renderBooking();
}

/* ------------------------------------------------------------------- queue */
async function renderQueue() {
  const el = $("#qw"); if (!el) return;
  let board = null; try { board = await api("queue/board"); } catch (e) { API = API && e.message !== "preview"; }
  if (S.ticket) {
    let tk = null, stale = false;
    try { tk = await api("queue/ticket/" + S.ticket); localStorage.setItem("queue_last", JSON.stringify(tk)); }
    catch (e) { if (e.network) { tk = JSON.parse(localStorage.getItem("queue_last") || "null"); stale = true; } else { S.ticket = ""; localStorage.removeItem("queue_ticket"); } }
    if (tk && stale) {                    // no signal: show the last answer and when it was checked; never guess (Q8)
      el.innerHTML = `<div class="ticket"><div class="small">${esc(t("your_ticket"))}</div><div class="no">${esc(tk.no)}</div><div><b>${esc(tk.name)}</b></div>
        <p>${esc(t("position"))}: <b>${tk.position || "–"}</b>${tk.about ? ` · ${esc(t("about"))} ${esc(tk.about)}` : ""}</p>
        <p class="small"><b>${esc(t("no_signal"))}.</b> ${esc(t("last_checked"))}: ${esc((tk.checked_at || "").slice(11, 16))}</p></div>`;
      clearTimeout(window._qt); window._qt = setTimeout(renderQueue, 15000); return;
    }
    if (tk) {
      if (tk.status === "waiting" || tk.status === "called") {
        const next = tk.youre_next || tk.status === "called";
        el.innerHTML = `<div class="ticket ${next ? "next" : ""}"><div class="small">${esc(t("your_ticket"))}</div><div class="no">${esc(tk.no)}</div><div><b>${esc(tk.name)}</b></div>
          ${next ? `<h3>🔔 ${esc(t("youre_next"))}</h3>` : `<p>${esc(t("position"))}: <b>${tk.position}</b> · ${esc(t("queue_wait"))}: ~${tk.wait_minutes} ${esc(t("minutes"))}${tk.about ? ` (${esc(t("about"))} ${esc(tk.about)})` : ""}</p>`}
          <p class="small muted">${esc(t("last_checked"))}: ${esc((tk.checked_at || "").slice(11, 16))}</p>
          <button class="btn ghost sm" id="qleave">${esc(t("leave_queue"))}</button></div>`;
        if (next && navigator.vibrate && !S.vibrated) { navigator.vibrate([300, 150, 300]); S.vibrated = true; }
        $("#qleave").onclick = async () => { await api("queue/leave", { token: S.ticket }).catch(() => {}); S.ticket = ""; localStorage.removeItem("queue_ticket"); renderQueue(); };
        clearTimeout(window._qt); window._qt = setTimeout(renderQueue, 15000); return;
      }
      S.ticket = ""; localStorage.removeItem("queue_ticket"); localStorage.removeItem("queue_last");
    }
  }
  const barbers = C.staff.filter(s => s.walk_ins !== false);
  el.innerHTML = `<div class="q"><div class="row" style="justify-content:space-between"><div><div class="n">${board ? board.waiting_count : "–"}</div><div>${esc(t("queue_waiting"))}</div></div>
      <div style="text-align:end"><div class="n" style="font-size:2rem">${board ? "~" + board.estimated_wait_minutes : "–"}</div><div class="small">${esc(t("queue_wait"))} (${esc(t("minutes"))})</div></div></div>
    ${board && board.now_serving.length ? `<p class="small">${esc(t("now_serving"))}: ${board.now_serving.map(n => `<b>${esc(n.no)}</b> ${esc(n.name)}`).join(" · ")}</p>` : ""}
    ${board && !board.open ? `<p><b>${esc(t("queue_closed"))}</b></p>` : `
    <div class="field"><label for="qn">${esc(t("your_name_board"))}</label><input id="qn" maxlength="24"></div>
    <div class="field"><label for="qp">${esc(t("phone"))}</label><input id="qp" type="tel" autocomplete="tel"></div>
    <div class="field"><label for="qs">${esc(t("step_service"))}</label><select id="qs">${C.services.map(s => `<option value="${esc(s.id)}">${esc(tx(s.name))} · ${s.duration_min} ${esc(t("min"))}</option>`).join("")}</select></div>
    ${barbers.length > 1 ? `<div class="field"><label for="qb">${esc(C.staff_word)}</label><select id="qb"><option value="any">${esc(t("any_staff"))}</option>${barbers.map(b => `<option value="${esc(b.id)}">${esc(b.name)}</option>`).join("")}</select></div>` : ""}
    <button class="btn acc" id="qgo" ${API ? "" : "disabled"}>${esc(t("queue_join"))}</button><div id="qerr"></div>`}</div>`;
  const go = $("#qgo"); if (go) go.onclick = async () => {
    try { const r = await api("queue/join", { name: $("#qn").value, service_id: $("#qs").value, barber: ($("#qb") || {}).value || "any", phone: ($("#qp") || {}).value || "" }); S.ticket = r.token; localStorage.setItem("queue_ticket", r.token); renderQueue(); }
    catch (e) { $("#qerr").innerHTML = `<div class="err">${esc(e.message)}</div>`; } };
  clearTimeout(window._qt); if (board) window._qt = setTimeout(renderQueue, 30000);
}

/* ---------------------------------------------------------------- products */
async function renderProducts() {
  const el = $("#prod"); if (!el) return;
  let stock = {}; try { stock = await api("stock"); } catch (e) { }
  const wa = waNum(C.whatsapp);
  el.innerHTML = C.products.map(p => { const ok = stock[p.id] !== false; return `<div class="c"><div class="im">${p.image ? `<img loading="lazy" src="${esc(p.image)}" alt="">` : ""}</div><div class="bd">
    <b>${esc(tx(p.name))}</b><span class="small muted">${esc(p.brand || "")} ${esc(p.size || "")}</span>${p.price ? `<b>${esc(money(p.price))}</b>` : ""}
    <span class="stock ${ok ? "" : "no"}">${esc(ok ? t("in_stock") : t("out_of_stock"))}</span>
    ${ok && p.pay_link ? `<a class="btn sm acc" href="${esc(p.pay_link)}" target="_blank" rel="noopener">${esc(t("buy"))}</a>` : ok && wa ? `<a class="btn sm" href="https://wa.me/${wa}?text=${encodeURIComponent(t("reserve") + ": " + tx(p.name))}">${esc(t("reserve"))}</a>` : ""}</div></div>`; }).join("");
}

/* -------------------------------------------------------------------- boot */
let deferred = null;
window.addEventListener("beforeinstallprompt", e => { e.preventDefault(); deferred = e; const b = $("#inst"); if (b) b.hidden = false; });
document.addEventListener("click", async e => { if (e.target.id === "inst" && deferred) { deferred.prompt(); hit("install"); deferred = null; e.target.hidden = true; } });
window.addEventListener("online", () => { document.body.classList.remove("is-offline"); if (localStorage.getItem("booking_outbox")) { S.bk.outbox = false; flushOutbox(); } });
window.addEventListener("offline", () => document.body.classList.add("is-offline"));
(async function () {
  try { C = await (await fetch("content.json", { cache: "no-cache" })).json(); }
  catch (e) { $("#app").innerHTML = `<div class="boot">Can't load the shop details.</div>`; return; }
  const saved = localStorage.getItem("lang"), nav = (navigator.language || "en").slice(0, 2);
  L = C.languages.includes(saved) ? saved : C.languages.includes(nav) ? nav : C.default_language;
  if (!navigator.onLine) document.body.classList.add("is-offline");
  render(); hit("open");
  if (navigator.onLine && localStorage.getItem("booking_outbox")) flushOutbox();
  if ("serviceWorker" in navigator && location.protocol !== "file:") navigator.serviceWorker.register("sw.js").catch(() => {});
})();
