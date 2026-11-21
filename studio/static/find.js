/* HVT Foundry Studio v0.2 — Find for my business, Shop's own app, Connectors, Settings. */
"use strict";
const CAT_ICON = { suppliers: "🚚", stock: "📦", finance: "💷", delivery: "🛵", storage: "🏬", other: "✏️" };
const F = { cat: "suppliers", community: "romanian", postcode: "", radius: 3000, text: "", sid: "", last: null };
const RTLSET = new Set(["ar", "fa", "ur", "ps", "ckb", "prs"]);
const when = s => (s || "").slice(0, 16).replace("T", " ");

/* ============================================================ FIND */
window.renderFind = async function (sid) {
  const [cat, sessions] = await Promise.all([api("communities"), api("sessions")]);
  if (sid) F.sid = sid;
  if (!F.sid && sessions.length) F.sid = sessions[0].id;
  const S = STATE.search_ready || {};
  view().innerHTML = `<div class="sess-row"><div><h1>Find for my business</h1>
    <p class="lead">Search the internet and the map, live, for what this shop needs — in English <b>and</b> in the owner's own language. Everything shown comes from a live source with its link and the time it was checked. <b>Nothing is checked by us.</b></p></div>
    <div class="row">${S.brave ? badge("Brave Search on", "pass") : badge("No Brave key — using free fallback", "partly")} <a class="small" href="#/settings">Settings</a></div></div>
  <div class="card find-form">
    <div class="grid g2"><div><label for="fsid">Which shop (session)? Results are saved to it.</label>
      <select id="fsid"><option value="">— just looking, don't save —</option>${sessions.map(s => `<option value="${esc(s.id)}" ${s.id === F.sid ? "selected" : ""}>${esc(s.id)} · ${esc(s.business_name || s.classification.business_type_name)}</option>`).join("")}</select></div>
      <div><label for="fpc">Shop postcode (for the map)</label><input type="text" id="fpc" value="${esc(F.postcode)}" placeholder="e.g. HA3 5AA" autocapitalize="characters"></div></div>
    <label>What does the owner need?</label>
    <div class="chips big" id="fcat">${Object.entries(cat.categories).map(([k, v]) => `<button class="chip ${k === F.cat ? "on" : ""}" data-v="${k}">${CAT_ICON[k]} ${esc(v)}</button>`).join("")}</div>
    <label>The owner's community / heritage</label>
    <div class="chips" id="fcom">${cat.communities.map(c => `<button class="chip ${c.id === F.community ? "on" : ""}" data-v="${c.id}">${esc(c.label)}</button>`).join("")}</div>
    <div class="grid g2"><div><label for="ftx">Anything else? Type it (any language)</label><input type="text" id="ftx" value="${esc(F.text)}" placeholder="e.g. halal meat, baklava boxes, chest freezer"></div>
      <div><label>How far (map)</label><div class="chips" id="frad">${[1000, 3000, 5000, 10000].map(r => `<button class="chip ${r === F.radius ? "on" : ""}" data-v="${r}">${r / 1000} km</button>`).join("")}</div></div></div>
    <details open><summary>Search phrases we'll use (<span id="qn">…</span>)</summary><div id="qprev" class="qprev"></div></details>
    <div class="row" style="margin-top:12px"><button class="btn amber" id="fgo">🔎 Search live now</button><span class="small muted">Results are kept for 24 hours so we don't overload the free services.</span></div>
  </div>
  <div id="fres">${F.last ? "" : `<div class="empty">Pick what the owner needs and press <b>Search live now</b>.</div>`}</div>
  <div id="fsaved"></div>`;
  const pick = (id, key, cast = x => x) => document.querySelectorAll(`#${id} .chip`).forEach(b => b.onclick = () => {
    document.querySelectorAll(`#${id} .chip`).forEach(x => x.classList.remove("on")); b.classList.add("on"); F[key] = cast(b.dataset.v); previewQ(); });
  pick("fcat", "cat"); pick("fcom", "community"); pick("frad", "radius", Number);
  $("#ftx").oninput = () => { F.text = $("#ftx").value; clearTimeout(window._qt); window._qt = setTimeout(previewQ, 300); };
  $("#fpc").onchange = () => { F.postcode = $("#fpc").value; };
  $("#fsid").onchange = () => { F.sid = $("#fsid").value; showSaved(); };
  $("#fgo").onclick = doSearch;
  previewQ(); showSaved();
  if (F.last) showResults(F.last);
};

async function previewQ() {
  const qs = await api(`queries?community=${encodeURIComponent(F.community)}&category=${F.cat}&area=${encodeURIComponent("your area")}&free_text=${encodeURIComponent(F.text)}`).catch(() => []);
  $("#qn").textContent = qs.length + " phrases, " + new Set(qs.map(q => q.lang)).size + " language(s)";
  $("#qprev").innerHTML = qs.map(q => `<div class="qline"><span class="badge b-pending">${esc(q.lang_name)}</span> <span dir="${q.dir}" lang="${esc(q.lang)}">${esc(q.q)}</span>
    ${q.checked_by_native_speaker === false ? `<span class="badge b-unknown" title="Written carefully, not yet checked by a native speaker">not yet checked by a native speaker</span>` : ""}</div>`).join("")
    || `<div class="muted">Type what the owner needs.</div>`;
}

async function doSearch() {
  F.postcode = $("#fpc").value.trim(); F.text = $("#ftx").value.trim(); F.sid = $("#fsid").value;
  $("#fres").innerHTML = `<div class="card searching"><div class="spinner"></div><b>Searching live…</b> postcodes.io → OpenStreetMap → web search in ${esc(F.community)} phrases. This can take 10–40 seconds on free services.</div>`;
  try {
    const r = await api("search", { category: F.cat, community: F.community, postcode: F.postcode, radius_m: F.radius, free_text: F.text, session_id: F.sid || null });
    F.last = r; showResults(r);
  } catch (e) { $("#fres").innerHTML = `<div class="warn"><b>Search didn't run.</b> ${esc(e.message)}</div>`; }
}

function resultCard(x, i, kind) {
  const rtl = RTLSET.has(x.query_lang);
  return `<div class="res ${kind}"><div class="res-head"><a href="${esc(x.url)}" target="_blank" rel="noopener" class="res-title">${esc(x.title)}</a>
    ${F.sid ? `<button class="btn small green" data-save="${kind}:${i}">＋ Save to this shop</button>` : ""}</div>
    ${kind === "map" ? `<div class="res-meta"><b>${esc(x.distance_text)}</b> · ${esc(x.kind)} ${x.community_match ? badge("community name match", "pass") : ""}</div><div>${esc(x.address)}</div>
      ${x.phone ? `<div class="small">📞 ${esc(x.phone)}</div>` : ""}${x.website ? `<div class="small"><a href="${esc(x.website)}" target="_blank" rel="noopener">${esc(x.website)}</a></div>` : ""}`
      : `<div class="res-snip">${esc(x.snippet)}</div>`}
    <div class="res-url">${esc(x.url)}</div>
    <div class="res-foot">${badge(x.source, "pending")} ${badge("search language: " + (x.query_lang_name || x.query_lang), "grey")} ${x.query ? `<span class="small muted" dir="${rtl ? "rtl" : "ltr"}">“${esc(x.query)}”</span>` : ""}
      <span class="small muted">checked ${esc(when(x.checked_at))}</span> ${badge("found live, not checked by us", "unknown")}</div></div>`;
}

function showResults(r) {
  const loc = r.location;
  const errs = r.errors || [];
  $("#fres").innerHTML = `
  ${loc ? `<div class="pill-note">📍 <b>${esc(loc.postcode)}</b> is in ${esc(loc.ward)}, ${esc(loc.area)} (${esc(loc.region)}). Source: <a href="${esc(loc.source_url)}" target="_blank" rel="noopener">postcodes.io</a>, checked ${esc(when(loc.checked_at))}.</div>` : ""}
  ${errs.length ? `<div class="warn"><b>Some sources didn't answer:</b><ul>${[...new Map(errs.map(e => [e.provider + e.message, e])).values()].map(e => `<li><b>${esc(e.provider)}</b>: ${esc(e.message)}</li>`).join("")}</ul></div>` : ""}
  ${(r.notes || []).map(n => `<div class="pill-note">${esc(n)}</div>`).join("")}
  <div class="grid g2 results">
    <div class="card"><h2 style="margin-top:0">🗺️ On the map near the shop (${r.map.length})</h2>
      ${loc && r.map.length ? radar(r.map, loc) : ""}
      ${r.map.length ? r.map.map((x, i) => resultCard(x, i, "map")).join("") : `<div class="empty">No map results.</div>`}
      <p class="small muted">Map data © OpenStreetMap contributors (ODbL). Not every business is on OpenStreetMap.</p></div>
    <div class="card"><h2 style="margin-top:0">🌐 On the web (${r.web.length})</h2>
      ${r.web.length ? r.web.map((x, i) => resultCard(x, i, "web")).join("") : `<div class="empty">No web results this time. ${STATE.search_ready && STATE.search_ready.brave ? "" : "Tip: add a Brave Search key in <a href='#/settings'>Settings</a> for reliable web results."}</div>`}</div>
  </div>
  <p class="small muted">Search started ${esc(when(r.started_at))} · kernel: ${esc((r.kernel || {}).agent || "")} — ${esc((r.kernel || {}).action || "")} · status ${esc(r.review_status || "")}</p>`;
  document.querySelectorAll("[data-save]").forEach(b => b.onclick = async () => {
    const [kind, i] = b.dataset.save.split(":"); const x = (kind === "map" ? r.map : r.web)[+i];
    try { const res = await api(`sessions/${F.sid}/save-result`, { result: Object.assign({ category: r.category, community: r.community }, x) });
      kernelToast(res, "Saved to " + F.sid); b.textContent = "✓ Saved"; b.disabled = true; showSaved(); } catch (e) { refusalToast(e); }
  });
}

function radar(items, loc) {
  const W = 320, R = 140, maxD = Math.max(...items.map(x => x.distance_m), 500);
  const pts = items.slice(0, 40).map((x, i) => {
    const dy = (x.lat - loc.lat) * 111320, dx = (x.lon - loc.lon) * 111320 * Math.cos(loc.lat * Math.PI / 180);
    const s = R / maxD; return `<circle cx="${W / 2 + dx * s}" cy="${W / 2 - dy * s}" r="${x.community_match ? 7 : 5}" class="${x.community_match ? "pt c" : "pt"}"><title>${esc(x.title)} — ${esc(x.distance_text)}</title></circle>`; }).join("");
  return `<svg viewBox="0 0 ${W} ${W}" class="radar" role="img" aria-label="Places around the shop">
    <circle cx="${W / 2}" cy="${W / 2}" r="${R}" class="ring"/><circle cx="${W / 2}" cy="${W / 2}" r="${R / 2}" class="ring"/>
    <text x="${W / 2 + 4}" y="${W / 2 - R + 12}" class="lbl">${(maxD / 1609.344).toFixed(1)} mi</text>${pts}
    <circle cx="${W / 2}" cy="${W / 2}" r="8" class="me"/><text x="${W / 2 + 10}" y="${W / 2 + 4}" class="lbl b">the shop</text></svg>`;
}

async function showSaved() {
  const box = $("#fsaved"); if (!box) return;
  if (!F.sid) { box.innerHTML = ""; return; }
  const d = await api("sessions/" + F.sid).catch(() => null); if (!d) return;
  box.innerHTML = `<div class="card"><div class="sess-row"><h2 style="margin:0">Saved to ${esc(F.sid)} (${d.saved_results.length})</h2>
    <a class="btn small" href="#/shopapp/${esc(F.sid)}">📱 Put these in the shop's own app →</a></div>
    ${d.saved_results.length ? `<div class="scroll"><table><tr><th>Name</th><th>Where from</th><th>Link</th><th>Checked</th><th>Saved</th></tr>${d.saved_results.map(x => `<tr><td><b>${esc(x.title)}</b><div class="small muted">${esc(x.address || x.snippet || "")}</div></td><td>${esc(x.source)}<div class="small muted">${esc(x.query_lang_name || x.query_lang || "")}</div></td><td class="small"><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.url)}</a></td><td class="small">${esc(when(x.checked_at))}</td><td class="small">${esc(when(x.saved_at))}</td></tr>`).join("")}</table></div>
      <p class="small muted">All labelled “found live, not checked by us”. They appear in the owner's summary and in the owner-only part of their app.</p>` : `<div class="empty">Nothing saved yet. Press “Save to this shop” on a result.</div>`}</div>`;
}

/* ============================================================ SHOP APP */
const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"], DAYN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
window.renderShopApp = async function (sid) {
  if (!sid) { location.hash = "#/sessions"; return; }
  const d = await api(`sessions/${sid}/shop-app`);
  const sh = d.shop, L = d.languages;
  sh.languages = sh.languages && sh.languages.length ? sh.languages : ["en"];
  sh.colours = sh.colours || { primary: "#3D2C8D", accent: "#F29E4C", bg: "#FAF6F0", text: "#1C1433" };
  sh.hours = sh.hours && sh.hours.length ? sh.hours : DAYS.map((day, i) => ({ day, open: "09:00", close: i === 6 ? "16:00" : "20:00", closed: false }));
  sh.products = sh.products || []; sh.tagline = sh.tagline || {}; sh.announcement = sh.announcement || {};
  sh.features = sh.features || { whatsapp_order: true, pay_links: true, barcode_lookup: true };
  const rec = d.record;
  view().innerHTML = `<div class="sess-row"><div><h1>The shop's own app</h1><p class="lead">Build a real app for <b>${esc(sh.name || sid)}</b>: their name, their colours, their language, their prices. It installs on a phone, works offline, and the owner keeps it — no lock-in.</p></div>
    <div class="row"><a class="btn small ghost" href="#/session/${esc(sid)}">← Back to ${esc(sid)}</a></div></div>
  <div class="appgen">
   <div class="appform">
    <div class="card"><h2 style="margin-top:0">1 · Name and languages</h2>
      <label>Shop name</label><input type="text" id="an" value="${esc(sh.name)}" placeholder="the name on the sign">
      <label>Languages (tap up to 4 — the first one you tap is the main one)</label><div class="small muted" id="lorder"></div>
      <div class="chips" id="alangs">${Object.entries(L).map(([k, v]) => `<button class="chip ${sh.languages.includes(k) ? "on" : ""}" data-v="${k}">${esc(v)}${RTLSET.has(k) ? " ⇐" : ""}</button>`).join("")}</div>
      <div id="altxt"></div></div>
    <div class="card"><h2 style="margin-top:0">2 · Colours (the owner chooses)</h2>
      <p class="small muted">Ideas inspired by each community — or pick any colours. No plain white shops.</p>
      <div class="palettes">${d.palettes.map((p, i) => `<button class="pal" data-p="${i}" title="${esc(p.label)}"><span style="background:${p.primary}"></span><span style="background:${p.accent}"></span><span style="background:${p.bg}"></span><small>${esc(p.name)}</small></button>`).join("")}</div>
      <div class="grid g4">${[["primary", "Main"], ["accent", "Second"], ["bg", "Background"], ["text", "Text"]].map(([k, n]) => `<div><label>${n}</label><input type="color" data-col="${k}" value="${esc(sh.colours[k])}"></div>`).join("")}</div>
      <label>Logo (optional)</label><input type="file" id="alogo" accept="image/png,image/jpeg,image/webp,image/svg+xml"> ${sh.logo ? `<img src="${sh.logo}" style="height:48px;border-radius:10px;vertical-align:middle">` : ""}</div>
    <div class="card"><h2 style="margin-top:0">3 · Contact, address, hours</h2>
      <div class="grid g2"><div><label>Phone</label><input type="text" id="aph" value="${esc(sh.phone || "")}" inputmode="tel"></div><div><label>WhatsApp</label><input type="text" id="awa" value="${esc(sh.whatsapp || "")}" inputmode="tel"></div></div>
      <div class="grid g2"><div><label>Address</label><input type="text" id="aad" value="${esc(sh.address || "")}"></div><div><label>Postcode</label><input type="text" id="apc" value="${esc(sh.postcode || "")}"></div></div>
      <table class="hours-edit">${sh.hours.map((h, i) => `<tr><td>${DAYN[i]}</td><td><input type="time" data-h="${i}" data-k="open" value="${esc(h.open)}"></td><td><input type="time" data-h="${i}" data-k="close" value="${esc(h.close)}"></td><td><label class="chip" style="margin:0"><input type="checkbox" data-h="${i}" data-k="closed" ${h.closed ? "checked" : ""}> closed</label></td></tr>`).join("")}</table>
      <button class="btn small ghost" id="acopy">Copy Monday to every day</button></div>
    <div class="card"><h2 style="margin-top:0">4 · Products and prices (the owner's own prices)</h2><div id="aprods"></div><button class="btn small ghost" id="aadd">+ Add a product</button></div>
    <div class="card"><h2 style="margin-top:0">5 · Switches and password</h2>
      <div class="chips"><label class="chip"><input type="checkbox" id="fwa" ${sh.features.whatsapp_order ? "checked" : ""}> WhatsApp order button</label>
      <label class="chip"><input type="checkbox" id="fpay" ${sh.features.pay_links ? "checked" : ""}> Pay buttons (payment links)</label>
      <label class="chip"><input type="checkbox" id="fbc" ${sh.features.barcode_lookup ? "checked" : ""}> Barcode lookup in admin (Open Food Facts)</label>
      <label class="chip"><input type="checkbox" id="aann" ${sh.announcement_on !== false ? "checked" : ""}> Show offer banner</label></div>
      <p class="small">🔒 ${sh.suppliers_count || 0} saved supplier(s) go into the owner-only admin page. Customers never see them.</p>
      <label>Owner's admin password ${rec ? "(leave empty to keep the current one)" : "(owner types it, 6+ characters)"}</label><input type="password" id="apw" autocomplete="new-password" style="width:100%;padding:14px;border:2px solid var(--line);border-radius:12px">
      <p class="small muted">Only a scrambled (hashed) copy is stored.</p></div>
    <div class="row sticky-actions"><button class="btn amber" id="abuild">📱 ${rec ? "Update the app" : "Build the app"}</button>
      ${rec ? `<button class="btn green" id="aexp">⬇ Download the owner's app (zip)</button><a class="btn ghost" href="${esc(rec.preview_url)}" target="_blank" rel="noopener">Open full screen</a>` : ""}</div>
    <div id="aexpres"></div>
   </div>
   <div class="appprev"><div class="phone">${rec ? `<iframe id="aframe" src="${esc(rec.preview_url)}?v=${Date.now()}" title="Shop app preview"></iframe>` : `<div class="phone-empty">The app preview appears here after you press <b>Build the app</b>.</div>`}</div>
     <p class="small muted" style="text-align:center">Phone preview · ${rec ? "built " + esc(when(rec.recorded_at)) : "not built yet"}</p></div>
  </div>`;
  const SEL = [...sh.languages];                      // keeps the order the owner chose (first = main language)
  const langsNow = () => SEL.slice();
  const mlText = () => { const ls = langsNow(); $("#lorder").textContent = "Main language first: " + ls.map(l => L[l]).join(" → "); $("#altxt").innerHTML = ls.map(l => `<div class="grid g2"><div><label>Short line under the name (${esc(L[l])})</label><input type="text" dir="${RTLSET.has(l) ? "rtl" : "ltr"}" data-ml="tagline" data-l="${l}" value="${esc(sh.tagline[l] || "")}"></div>
     <div><label>Offer banner (${esc(L[l])})</label><input type="text" dir="${RTLSET.has(l) ? "rtl" : "ltr"}" data-ml="announcement" data-l="${l}" value="${esc(sh.announcement[l] || "")}"></div></div>`).join(""); };
  const prods = () => { const ls = langsNow(); $("#aprods").innerHTML = `<div class="scroll"><table><tr>${ls.map(l => `<th>Name (${esc(L[l])})</th>`).join("")}<th>£</th><th>Unit</th><th>Group</th><th></th></tr>
     ${sh.products.map((p, i) => `<tr>${ls.map(l => `<td><input type="text" dir="${RTLSET.has(l) ? "rtl" : "ltr"}" data-pi="${i}" data-k="name" data-l="${l}" value="${esc((p.name || {})[l] || "")}"></td>`).join("")}
       <td><input type="text" data-pi="${i}" data-k="price" value="${esc(p.price || "")}" inputmode="decimal" style="width:80px"></td><td><input type="text" data-pi="${i}" data-k="unit" value="${esc(p.unit || "")}" style="width:70px"></td>
       <td><input type="text" data-pi="${i}" data-k="category" value="${esc(p.category || "")}"></td><td><button class="btn small red" data-pd="${i}">✕</button></td></tr>`).join("")}</table></div>`;
    document.querySelectorAll("[data-pd]").forEach(b => b.onclick = () => { collect(); sh.products.splice(+b.dataset.pd, 1); prods(); }); };
  const collect = () => {
    sh.name = $("#an").value; sh.languages = langsNow().length ? langsNow() : ["en"]; sh.default_language = sh.languages[0];
    document.querySelectorAll("[data-col]").forEach(i => sh.colours[i.dataset.col] = i.value);
    document.querySelectorAll("[data-ml]").forEach(i => sh[i.dataset.ml][i.dataset.l] = i.value);
    document.querySelectorAll("[data-h]").forEach(i => { const h = sh.hours[+i.dataset.h]; h[i.dataset.k] = i.type === "checkbox" ? i.checked : i.value; });
    document.querySelectorAll("[data-pi]").forEach(i => { const p = sh.products[+i.dataset.pi]; if (i.dataset.k === "name") { p.name = p.name || {}; p.name[i.dataset.l] = i.value; } else p[i.dataset.k] = i.value; });
    Object.assign(sh, { phone: $("#aph").value, whatsapp: $("#awa").value, address: $("#aad").value, postcode: $("#apc").value, announcement_on: $("#aann").checked,
      features: { whatsapp_order: $("#fwa").checked, pay_links: $("#fpay").checked, barcode_lookup: $("#fbc").checked } });
  };
  document.querySelectorAll("#alangs .chip").forEach(b => b.onclick = () => { collect(); if (!b.classList.contains("on") && langsNow().length >= 4) return toast("Up to 4 languages.", true); const i = SEL.indexOf(b.dataset.v); if (i >= 0) { if (SEL.length > 1) SEL.splice(i, 1); } else SEL.push(b.dataset.v);
    b.classList.toggle("on", SEL.includes(b.dataset.v)); mlText(); prods(); });
  document.querySelectorAll(".pal").forEach(b => b.onclick = () => { const p = d.palettes[+b.dataset.p]; ["primary", "accent", "bg", "text"].forEach(k => $(`[data-col=${k}]`).value = p[k]); });
  $("#acopy").onclick = () => { collect(); sh.hours.forEach((h, i) => { if (i) Object.assign(h, { open: sh.hours[0].open, close: sh.hours[0].close, closed: sh.hours[0].closed }); }); renderShopAppKeep(); };
  $("#aadd").onclick = () => { collect(); sh.products.push({ name: {}, price: "", unit: "", category: "" }); prods(); };
  $("#alogo").onchange = e => { const f = e.target.files[0]; if (!f) return; const rd = new FileReader(); rd.onload = () => { sh.logo = rd.result; toast("Logo added — press Build/Update."); }; rd.readAsDataURL(f); };
  const renderShopAppKeep = () => { document.querySelectorAll("[data-h]").forEach(i => { const h = sh.hours[+i.dataset.h]; if (i.type === "checkbox") i.checked = h.closed; else i.value = h[i.dataset.k]; }); };
  $("#abuild").onclick = async () => { collect(); try { const r = await api(`sessions/${sid}/shop-app`, { shop: sh, password: $("#apw").value });
      kernelToast(r, "Shop app built"); window.renderShopApp(sid); } catch (e) { refusalToast(e); } };
  const ex = $("#aexp"); if (ex) ex.onclick = async () => { try { const r = await api(`sessions/${sid}/shop-app/export`, {}); kernelToast(r, "Zip ready");
      $("#aexpres").innerHTML = `<div class="pill-note">✅ <b>${esc(r.result.top_folder)}.zip</b> — ${r.result.files} files. Keys and secrets left out: ${r.result.skipped_secrets.length ? esc(r.result.skipped_secrets.join(", ")) : "none were present"}.<br><a class="btn small green" href="${esc(r.result.download_url)}">Download zip</a></div>`; } catch (e) { refusalToast(e); } };
  mlText(); prods();
};

/* ============================================================ CONNECTORS */
const CONN = { cat: "All" };
window.renderConnectors = async function (scope) {
  scope = scope || "studio";
  const [d, sessions] = await Promise.all([api("connectors?scope=" + encodeURIComponent(scope)), api("sessions")]);
  const cats = ["All", ...new Set(d.items.map(c => c.category))];
  const items = d.items.filter(c => c.id !== "custom_api" && (CONN.cat === "All" || c.category === CONN.cat));
  const legend = { "working-tested": "we called the real service and it worked", "code-ready-needs-key": "written from the vendor's official docs; works once the owner adds a key", "unverified": "docs not readable today, or needs a partner account — a starting point only" };
  view().innerHTML = `<div class="sess-row"><div><h1>Connectors</h1><p class="lead">Plug the Studio or a shop into free, open-source and paid services. Keys stay on this computer (never in a zip or git) and show masked.</p></div>
    <div><label for="cscope" style="margin-top:0">Keys and switches for</label><select id="cscope"><option value="studio">The Studio (my own keys)</option>${sessions.map(s => `<option value="${esc(s.id)}" ${s.id === scope ? "selected" : ""}>${esc(s.id)} · ${esc(s.business_name || s.classification.business_type_name)}</option>`).join("")}</select></div></div>
  <div class="grid g3">${d.statuses.map(s => `<div class="card stat"><div class="big">${d.counts[s] || 0}</div>${badge(s, s)}<div class="small muted">${esc(legend[s])}</div></div>`).join("")}</div>
  <div class="chips" style="margin:10px 0">${cats.map(c => `<button class="chip ${c === CONN.cat ? "on" : ""}" data-cc="${esc(c)}">${esc(c)}</button>`).join("")}</div>
  <div class="grid g2">${items.map(c => `<div class="card conn"><div class="sess-row"><div><b>${esc(c.name)}</b><div class="small muted">${esc(c.category)} · ${esc(c.cost_type)}</div></div><div>${badge(c.status, c.status)} ${c.enabled ? badge("on", "pass") : ""}</div></div>
     <p style="margin:.4em 0">${esc(c.what_it_does)}</p>
     ${c.status_note ? `<div class="small muted">${esc(c.status_note)}</div>` : ""}
     <div class="small">${c.pricing ? `Cost: ${esc(c.pricing.text)} ${c.pricing.checked ? `(checked ${esc(c.pricing.checked)})` : ""} <a href="${esc(c.pricing.url)}" target="_blank" rel="noopener">vendor page</a>` : ""} · <a href="${esc(c.docs_url)}" target="_blank" rel="noopener">official docs</a> (${esc(c.docs_checked || "")})</div>
     <details><summary>Keys, test and actions</summary>
      ${(c.credentials || []).map(k => `<label>${esc(k.label)}</label><input type="${k.secret ? "password" : "text"}" data-cid="${esc(c.id)}" data-k="${esc(k.key)}" value="${esc((c.saved_credentials || {})[k.key] || "")}" placeholder="${esc(k.help || "")}" autocomplete="off">`).join("")}
      <div class="row" style="margin-top:8px">${(c.credentials || []).length ? `<button class="btn small ghost" data-csave="${esc(c.id)}">Save keys</button>` : ""}<button class="btn small" data-ctest="${esc(c.id)}">Test</button>
       <button class="btn small ghost" data-cen="${esc(c.id)}" data-on="${c.enabled ? 0 : 1}">${c.enabled ? "Switch off" : "Switch on"}</button></div>
      ${Object.entries(c.actions || {}).map(([a, ad]) => `<div class="row" style="margin-top:8px">${(ad.params || []).map(p => `<input type="text" style="flex:1 1 140px;padding:10px;border:2px solid var(--line);border-radius:10px" data-cap="${esc(c.id)}|${esc(a)}" data-k="${esc(p.key)}" placeholder="${esc(p.label)}${p.example ? " e.g. " + esc(p.example) : ""}">`).join("")}<button class="btn small amber" data-crun="${esc(c.id)}|${esc(a)}">${esc(ad.label)}</button></div>`).join("")}
      <div class="cout" id="co-${esc(c.id.replace(/[^a-z0-9]/gi, "_"))}"></div></details></div>`).join("")}</div>
  <div class="card"><h2 style="margin-top:0">➕ Add any other service (Custom API)</h2><p class="small muted">For any open-source or paid service with a web API. No code needed.</p>
    <div class="grid g2"><div><label>Short name</label><input type="text" id="xs" placeholder="e.g. my_stock_system"></div><div><label>Base address</label><input type="text" id="xb" placeholder="https://api.example.com/v1"></div></div>
    <div class="grid g2"><div><label>Login type</label><select id="xa"><option value="none">No login</option><option value="api_key_header">API key in a header</option><option value="bearer">Bearer token</option><option value="basic">Username + password</option></select></div><div><label>Header name (API key)</label><input type="text" id="xh" value="X-API-Key"></div></div>
    <label>Actions, one per line: name, METHOD, /path/{placeholder}</label><textarea id="xx" placeholder="latest, GET, /latest"></textarea>
    <label>…or paste an OpenAPI (Swagger) JSON file</label><textarea id="xo" placeholder='{"openapi": "3.0.0", ...}'></textarea>
    <div class="row" style="margin-top:10px"><button class="btn ghost" id="xoi">Read the OpenAPI file</button><button class="btn amber" id="xsv">Save custom API</button></div><div id="xres"></div></div>`;
  $("#cscope").onchange = () => { location.hash = "#/connectors/" + $("#cscope").value; };
  document.querySelectorAll("[data-cc]").forEach(b => b.onclick = () => { CONN.cat = b.dataset.cc; window.renderConnectors(scope); });
  const out = (id, html) => { const el = $("#co-" + id.replace(/[^a-z0-9]/gi, "_")); if (el) el.innerHTML = html; };
  const op = (id, o, body) => api(`connectors/${encodeURIComponent(id)}/${o}`, Object.assign({ scope }, body || {}));
  document.querySelectorAll("[data-csave]").forEach(b => b.onclick = async () => { const id = b.dataset.csave, v = {}; document.querySelectorAll(`[data-cid="${id}"]`).forEach(i => v[i.dataset.k] = i.value);
    try { const r = await op(id, "credentials", { values: v }); kernelToast(r, "Keys saved (masked)"); window.renderConnectors(scope); } catch (e) { refusalToast(e); } });
  document.querySelectorAll("[data-ctest]").forEach(b => b.onclick = async () => { const id = b.dataset.ctest; out(id, "Testing live…");
    try { const r = (await op(id, "test")).result; out(id, `<div class="${r.ok ? "pill-note" : "warn"}">${r.ok ? "✅" : "⚠️"} ${esc(r.message)}</div>`); } catch (e) { out(id, `<div class="warn">${esc(e.message)}</div>`); } });
  document.querySelectorAll("[data-cen]").forEach(b => b.onclick = async () => { try { await op(b.dataset.cen, "enable", { on: b.dataset.on === "1" }); window.renderConnectors(scope); } catch (e) { refusalToast(e); } });
  document.querySelectorAll("[data-crun]").forEach(b => b.onclick = async () => { const [id, a] = b.dataset.crun.split("|"), p = {}; document.querySelectorAll(`[data-cap="${b.dataset.crun}"]`).forEach(i => { if (i.value) p[i.dataset.k] = i.value; }); out(id, "Working…");
    try { const r = (await op(id, "run", { action: a, params: p })).result; out(id, r.ok ? `<pre>${esc(JSON.stringify(r.result, null, 1))}</pre>` : `<div class="warn">${esc(r.message)}</div>`); } catch (e) { out(id, `<div class="warn">${esc(e.message)}</div>`); } });
  $("#xoi").onclick = async () => { try { const o = (await op("custom_api", "openapi", { spec: $("#xo").value })).result; $("#xb").value = o.base_url; $("#xa").value = o.auth_type; $("#xh").value = o.header_name;
      $("#xx").value = o.endpoints.slice(0, 30).map(e => `${e.name}, ${e.method}, ${e.path}`).join("\n"); if (!$("#xs").value) $("#xs").value = o.title.toLowerCase().replace(/[^a-z0-9]+/g, "_").slice(0, 30);
      $("#xres").innerHTML = `<div class="pill-note">${esc(o.title)} ${esc(o.version)} — ${o.endpoints.length} endpoints. First 30 filled in; delete what you don't need.</div>`; } catch (e) { $("#xres").innerHTML = `<div class="warn">${esc(e.message)}</div>`; } };
  $("#xsv").onclick = async () => { const actions = $("#xx").value.split("\n").map(l => l.split(",").map(s => s.trim())).filter(a => a.length >= 3).map(([name, method, path]) => ({ name, method, path, label: name }));
    try { await op("custom_api", "custom", { slug: $("#xs").value, definition: { label: $("#xs").value, base_url: $("#xb").value, auth_type: $("#xa").value, header_name: $("#xh").value, actions } }); toast("Custom API saved."); window.renderConnectors(scope); } catch (e) { refusalToast(e); } };
};

/* ============================================================ SETTINGS */
window.renderSettings = async function () {
  const s = await api("settings");
  view().innerHTML = `<h1>Settings</h1><p class="lead">Keys are saved in <code>${esc(s.saved_to)}</code> on this computer only. That file is never put in git or in any zip.</p>
  <div class="card"><h2 style="margin-top:0">Web search</h2>
    <label>Brave Search API key ${s.brave_from_env ? badge("set by BRAVE_SEARCH_API_KEY", "pass") : ""}</label><input type="password" id="sb" value="${esc(s.brave_api_key)}" placeholder="paste the key from api-dashboard.search.brave.com" autocomplete="off" style="width:100%;padding:14px;border:2px solid var(--line);border-radius:12px">
    <p class="small muted">Brave's plans page (checked 26 Sept 2026): Search costs $5 per 1,000 requests, prepaid; a card is needed even for free credit. See REAL_LIFE_GUIDE.md.</p>
    <label>SerpAPI key (optional, uses the Bing engine)</label><input type="password" id="ss" value="${esc(s.serpapi_key)}" autocomplete="off" style="width:100%;padding:14px;border:2px solid var(--line);border-radius:12px">
    <label>Order to try (first that works wins)</label><input type="text" id="so" value="${esc(s.provider_order.join(", "))}">
    <label>Most web searches per button press (1–12)</label><input type="text" id="sm" value="${esc(s.max_web_queries)}">
    <label>Your contact email (sent politely to free services so they can reach you; optional)</label><input type="text" id="se" value="${esc(s.contact_email)}"></div>
  <div class="card"><h2 style="margin-top:0">Studio password (for when it's online)</h2><p class="small">${s.studio_password_set ? "A password is set." : "No password yet. Set one before putting the Studio on the internet."}</p>
    <input type="password" id="sp" placeholder="new Studio password (6+ characters)" autocomplete="new-password" style="width:100%;padding:14px;border:2px solid var(--line);border-radius:12px">
    ${s.studio_password_set ? `<label class="chip" style="margin-top:10px"><input type="checkbox" id="spc"> Remove the password</label>` : ""}</div>
  <button class="btn amber" id="ssv">Save settings</button>`;
  $("#ssv").onclick = async () => { const body = { brave_api_key: $("#sb").value, serpapi_key: $("#ss").value, contact_email: $("#se").value,
      provider_order: $("#so").value.split(",").map(x => x.trim()).filter(Boolean), max_web_queries: +$("#sm").value || 6 };
    if ($("#sp").value) body.studio_password = $("#sp").value; if ($("#spc") && $("#spc").checked) body.clear_studio_password = true;
    try { const r = await api("settings", body); kernelToast(r, "Settings saved"); await refreshState(); window.renderSettings(); } catch (e) { refusalToast(e); } };
};
