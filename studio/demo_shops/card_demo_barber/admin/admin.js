/* Owner admin for a card app. Everything saves to this shop's own computer. */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"];
const DAYN = { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday", sat: "Saturday", sun: "Sunday" };
const STATUS_TXT = { "working": "working", "needs-key": "needs key", "code-ready-needs-key": "code ready, needs key", "link-only": "link only", "unverified": "unverified" };
let SHOP = null, CARD = null, MODS = [], ON = {}, TAB = location.hash.slice(1) || "today";

async function api(path, body) {
  const r = await fetch("/api/" + path, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const ct = r.headers.get("content-type") || ""; const j = ct.includes("json") ? await r.json() : {};
  if (r.status === 401) { showLogin(); throw new Error("Please log in."); }
  if (!r.ok) throw new Error(j.message || "Refused");
  return j;
}
function toast(m, bad) { const t = $("#toast"); t.textContent = m; t.className = "show" + (bad ? " bad" : ""); clearTimeout(t._h); t._h = setTimeout(() => t.className = "", bad ? 7000 : 3500); }
async function guard(fn, okMsg) { try { const r = await fn(); if (okMsg) toast(okMsg); return r; } catch (e) { toast(e.message, true); throw e; } }
const L0 = () => SHOP.languages[0];
const ml = o => !o ? "" : typeof o === "string" ? o : (o[SHOP.default_language] || Object.values(o)[0] || "");
let SHOP_TODAY = "";   // the shop's own date (Europe/London), sent by the shop's app
const today = () => SHOP_TODAY || new Date().toLocaleDateString("en-CA");
const badge = (s, txt) => `<span class="b b-${esc(s)}">${esc(txt || STATUS_TXT[s] || s)}</span>`;

function showLogin() {
  $("#root").innerHTML = `<div class="card login"><h1>Owner login</h1><p class="lead">This page is for the shop owner only.</p>
    <label for="pw">Password</label><input type="password" id="pw" autofocus><div class="row" style="margin-top:12px"><button class="btn" id="go">Log in</button></div><div id="lm"></div></div>`;
  const go = async () => { const r = await fetch("/api/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password: $("#pw").value }) });
    if (r.ok) boot(); else $("#lm").innerHTML = `<div class="bad">${esc((await r.json()).message)}</div>`; };
  $("#go").onclick = go; $("#pw").onkeydown = e => { if (e.key === "Enter") go(); };
}

async function boot() {
  const me = await (await fetch("/api/admin/me")).json();
  if (!me.logged_in) return showLogin();
  const [shop, card] = await Promise.all([api("admin/shop"), api("admin/card")]);
  SHOP = shop; CARD = card.card; MODS = card.modules; ON = card.on; SHOP_TODAY = card.today || "";
  document.documentElement.style.setProperty("--p", SHOP.colours.primary); document.documentElement.style.setProperty("--a", SHOP.colours.accent);
  frame();
}

function tabs() {
  const has = id => ON[id];
  const t = [["Daily", [["today", "📋 Today"], ["bookings", "📅 Bookings"], has("walkin_queue") && ["queue", "💈 Walk-in queue"], (has("reminders") || has("review_requests")) && ["reminders", "💬 Reminders & reviews"]]],
    ["Your app", [["details", "🏠 Shop details"], ["look", "🎨 Look & photos"], ["services", "✂ Services & prices"], ["staff", "👤 " + (SHOP.staff_word_plural || "Team")], ["gallery", "🖼 Gallery"], ["reviews", "★ Reviews"], has("multi_branch") && ["branches", "🏬 Branches"], ["modules", "🧩 Modules (switch on/off)"]]],
    ["Extras", [has("loyalty") && ["loyalty", "🎟 Loyalty cards"], has("vouchers") && ["vouchers", "🎁 Gift vouchers"], has("packages") && ["packages", "♻ Packages"], has("retail") && ["products", "🧴 Products & stock"], has("client_records") && ["clients", "🔒 Client records"], has("rota") && ["rota", "🗓 Rota & commission"], has("referrals") && ["referrals", "🤝 Referrals"], has("analytics") && ["analytics", "📈 Analytics"], has("supplier_finder") && ["suppliers", "🔎 Supplier finder"]]],
    ["Settings", [["connectors", "🔌 Connectors & keys"], ["password", "🔑 Password"]]]];
  return t.map(([g, items]) => [g, items.filter(Boolean)]).filter(([, i]) => i.length);
}
function frame() {
  $("#root").innerHTML = `${SHOP.demo ? `<div class="demo">DEMO SHOP — invented business for illustration only</div>` : ""}
  <div class="top"><b>${esc(SHOP.name)} · Owner admin</b><a href="/" target="_blank">View app ↗</a>${ON.walkin_queue ? `<a href="/queue" target="_blank">Queue board ↗</a>` : ""}<button id="out">Log out</button></div>
  <div class="wrap"><nav id="nav">${tabs().map(([g, items]) => `<div class="grp">${esc(g)}</div>${items.map(([id, lab]) => `<button data-t="${id}" class="${TAB === id ? "on" : ""}">${esc(lab)}</button>`).join("")}`).join("")}</nav><main id="main"></main></div>`;
  $("#out").onclick = async () => { await fetch("/api/logout", { method: "POST" }); location.reload(); };
  $$("#nav button").forEach(b => b.onclick = () => { TAB = b.dataset.t; location.hash = TAB; $$("#nav button").forEach(x => x.classList.toggle("on", x === b)); show(); });
  show();
}
async function show() {
  const m = $("#main"); m.innerHTML = "<p class='muted'>Loading…</p>";
  try { await (VIEWS[TAB] || VIEWS.today)(m); } catch (e) { m.innerHTML = `<div class="bad">${esc(e.message)}</div>`; }
}
async function saveShop(msg = "Saved. Your app is updated.") {
  const r = await guard(() => api("admin/shop", SHOP), msg); SHOP = r.shop; return r;
}
function fileToData(f) { return new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(r.result); r.onerror = no; r.readAsDataURL(f); }); }
async function upload(input) { const f = input.files[0]; if (!f) return ""; if (f.size > 1.8e6) { toast("Please use a picture under 1.8 MB.", true); return ""; } const data = await fileToData(f); return (await guard(() => api("admin/image", { data }))).path; }

/* ------------------------------------------------------ generic list editor */
function fieldHTML(f, v, idx) {
  const id = `f_${idx}_${f.key}`, lab = `<label for="${id}">${esc(f.label)}${f.required ? " *" : ""}</label>`;
  const opts = (CARD.service_options[f.options_from] || []).map(o => Array.isArray(o) ? o : [o, o]);
  switch (f.type) {
    case "ml_text": return `<div>${SHOP.languages.map(l => `<label for="${id}_${l}">${esc(f.label)} (${esc(l)})${f.required && l === L0() ? " *" : ""}</label><input type="text" id="${id}_${l}" data-k="${f.key}" data-l="${l}" value="${esc((v || {})[l] || "")}" dir="auto">`).join("")}</div>`;
    case "text_long": return `<div>${lab}<textarea id="${id}" data-k="${f.key}">${esc(v || "")}</textarea></div>`;
    case "int": return `<div>${lab}<input type="number" id="${id}" data-k="${f.key}" min="${f.min ?? ""}" max="${f.max ?? ""}" value="${esc(v ?? f.default ?? "")}"></div>`;
    case "money": return `<div>${lab}<input type="text" inputmode="decimal" id="${id}" data-k="${f.key}" value="${esc(v || "")}" placeholder="e.g. 35"></div>`;
    case "choice": return `<div>${lab}<select id="${id}" data-k="${f.key}">${opts.map(([k, t]) => `<option value="${esc(k)}" ${v === k ? "selected" : ""}>${esc(t)}</option>`).join("")}</select></div>`;
    case "choice_or_text": return `<div>${lab}<input type="text" id="${id}" data-k="${f.key}" list="${id}_l" value="${esc(v || "")}"><datalist id="${id}_l">${opts.map(([k]) => `<option value="${esc(k)}">`).join("")}</datalist></div>`;
    case "multichoice": return `<div><label>${esc(f.label)}</label><div class="pills" data-k="${f.key}" data-multi="1">${opts.map(([k, t]) => `<label><input type="checkbox" value="${esc(k)}" ${(v || []).includes(k) ? "checked" : ""}> ${esc(t)}</label>`).join("")}</div></div>`;
    case "staff_refs": return `<div><label>${esc(f.label)}</label><div class="pills" data-k="${f.key}" data-multi="1">${SHOP.staff.map(s => `<label><input type="checkbox" value="${esc(s.id)}" ${(v || []).includes(s.id) ? "checked" : ""}> ${esc(s.name)}</label>`).join("") || "<span class='muted small'>Add team members first.</span>"}</div></div>`;
    case "bool": return `<label class="chk"><input type="checkbox" data-k="${f.key}" ${v ? "checked" : ""}> ${esc(f.label)}</label>`;
    case "image": return `<div><label>${esc(f.label)}${f.required ? " *" : ""}</label><div class="row">${v ? `<img class="thumb" src="/${esc(v)}" alt="">` : ""}<input type="file" accept="image/png,image/jpeg,image/webp" data-img="${f.key}"><input type="hidden" data-k="${f.key}" value="${esc(v || "")}"></div></div>`;
    case "url": return `<div>${lab}<input type="url" id="${id}" data-k="${f.key}" value="${esc(v || "")}" placeholder="https://"></div>`;
    case "tags": return `<div>${lab}<input type="text" id="${id}" data-k="${f.key}" data-tags="1" value="${esc((v || []).join(", "))}"></div>`;
    case "barcode": return `<div>${lab}<div class="row"><input type="text" inputmode="numeric" id="${id}" data-k="${f.key}" value="${esc(v || "")}" style="flex:1">${ON.retail ? `<button class="btn sm ghost" data-lookup="${id}" type="button">Look up</button>` : ""}</div></div>`;
    case "commission": return `<div><label>${esc(f.label)}</label><div class="row"><input type="number" min="0" max="100" data-k="${f.key}" data-sub="service_percent" value="${esc((v || {}).service_percent ?? 0)}" style="width:90px"> % service <input type="number" min="0" max="100" data-k="${f.key}" data-sub="retail_percent" value="${esc((v || {}).retail_percent ?? 0)}" style="width:90px"> % retail</div></div>`;
    case "breaks": return `<div>${lab}<input type="text" id="${id}" data-k="${f.key}" value="${esc(Array.isArray(v) ? v.map(b => b.start + "-" + b.end).join(", ") : (v || ""))}" placeholder="13:00-13:30"></div>`;
    default: return `<div>${lab}<input type="text" id="${id}" data-k="${f.key}" value="${esc(v || "")}"></div>`;
  }
}
function readItem(el, schema, old) {
  const o = { id: old.id };
  if (old.days) o.days = old.days;
  schema.forEach(f => {
    const nodes = $$(`[data-k="${f.key}"]`, el);
    if (f.type === "ml_text") { o[f.key] = {}; nodes.forEach(n => { if (n.value.trim()) o[f.key][n.dataset.l] = n.value.trim(); }); }
    else if (f.type === "multichoice" || f.type === "staff_refs") o[f.key] = $$("input:checked", nodes[0]).map(i => i.value);
    else if (f.type === "bool") o[f.key] = nodes[0].checked;
    else if (f.type === "tags") o[f.key] = nodes[0].value.split(",").map(s => s.trim()).filter(Boolean);
    else if (f.type === "commission") { o[f.key] = {}; nodes.forEach(n => o[f.key][n.dataset.sub] = n.value); }
    else o[f.key] = nodes[0] ? nodes[0].value : "";
  });
  return o;
}
function listEditor(m, key, title, lead, labelFn) {
  const schema = CARD.content_schema[key];
  const items = SHOP[key] || [];
  m.innerHTML = `<h1>${esc(title)}</h1><p class="lead">${lead}</p><div id="items">${items.map((it, i) => `<details class="item" ${items.length < 3 ? "open" : ""} data-i="${i}"><summary>${esc(labelFn(it) || "(new)")}</summary><div class="body"><div class="grid">${schema.map(f => fieldHTML(f, it[f.key], i)).join("")}</div>
    <div class="row" style="margin-top:12px"><button class="btn sm ghost" data-up="${i}">↑ Move up</button><button class="btn sm red" data-del="${i}">Remove</button></div></div></details>`).join("") || "<p class='muted'>Nothing here yet.</p>"}</div>
    <div class="row"><button class="btn ghost" id="add">+ Add</button><button class="btn" id="save">Save</button></div>`;
  const collect = () => $$("#items .item").map(el => readItem(el, schema, items[+el.dataset.i]));
  $("#add").onclick = () => { SHOP[key] = collect().concat([{}]); listEditor(m, key, title, lead, labelFn); };
  $$("[data-del]", m).forEach(b => b.onclick = () => { if (!confirm("Remove this?")) return; const c = collect(); c.splice(+b.dataset.del, 1); SHOP[key] = c; listEditor(m, key, title, lead, labelFn); });
  $$("[data-up]", m).forEach(b => b.onclick = () => { const c = collect(), i = +b.dataset.up; if (i > 0) [c[i - 1], c[i]] = [c[i], c[i - 1]]; SHOP[key] = c; listEditor(m, key, title, lead, labelFn); });
  $$("[data-img]", m).forEach(inp => inp.onchange = async () => { const p = await upload(inp); if (p) { inp.nextElementSibling.value = p; const im = inp.parentElement.querySelector("img") || Object.assign(document.createElement("img"), { className: "thumb" }); im.src = "/" + p; inp.parentElement.prepend(im); } });
  $$("[data-lookup]", m).forEach(b => b.onclick = async () => { const code = $("#" + b.dataset.lookup).value; const r = await guard(() => api("admin/products/barcode", { barcode: code }));
    if (!r.found) return toast(r.message || "Not found — type the details in.");
    const it = b.closest(".item"); const nm = $(`[data-k="name"][data-l="${L0()}"]`, it); if (nm && !nm.value) nm.value = r.product_name || ""; const br = $(`[data-k="brand"]`, it); if (br && !br.value) br.value = r.brands || ""; const sz = $(`[data-k="size"]`, it); if (sz && !sz.value) sz.value = r.quantity || "";
    toast(`Found: ${r.brands || ""} ${r.product_name || ""} (from ${r.source_url})`); });
  $("#save").onclick = async () => { SHOP[key] = collect(); await saveShop(); listEditor(m, key, title, lead, labelFn); };
}

/* ------------------------------------------------------------------- views */
const VIEWS = {
  async today(m) {
    const d = await api(`admin/bookings?from=${today()}`);
    const req = d.bookings.filter(b => b.status === "requested"), up = d.bookings.filter(b => b.status === "confirmed");
    const held = d.bookings.filter(b => b.status === "held");
    const td = up.filter(b => b.date === today());
    m.innerHTML = `<h1>Today</h1><p class="lead">${new Date(today() + "T12:00:00").toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long" })}</p>
      ${d.clashes.length ? `<div class="bad">Double booking found: ${esc(d.clashes.join(", "))}. Move one of them.</div>` : ""}
      <div class="grid"><div class="stat"><b>${td.length}</b>confirmed today</div><div class="stat"><b>${req.length}</b>requests waiting for you</div><div class="stat"><b>${up.length}</b>confirmed from today on</div></div>
      ${alertBox(d.alerts)}
      ${held.length ? `<h2>Waiting for a deposit</h2><p class="small muted">These times are held for a few minutes while the client pays. If no payment comes, the time is released by itself.</p>${bookingTable(held)}` : ""}
      <h2>Requests to confirm</h2>${bookingTable(req)}<h2>Today's appointments</h2>${bookingTable(td)}`;
    wireBookings(m);
  },
  async bookings(m) {
    const d = await api(`admin/bookings`);
    m.innerHTML = `<h1>Bookings</h1><p class="lead">Mode: <b>${ON.auto_booking ? "Automated (customers get confirmed free slots)" : "Requests (you confirm each one)"}</b>. A stylist can never be double-booked: the app refuses any clash.</p>
      ${d.clashes.length ? `<div class="bad">Clash: ${esc(d.clashes.join(", "))}</div>` : `<div class="ok">No double bookings.</div>`}
      ${alertBox(d.alerts)}
      ${ON.deposits ? `<p class="small">Deposits: ${d.pay_provider ? `taken online through <b>${esc(d.pay_provider)}</b>` : "<b>no payment firm connected</b> - bookings that need a deposit come in as requests, and you take the deposit yourself (then press <i>Deposit paid</i>)"}.</p>` : ""}
      <details class="card"><summary><b>+ Add a booking yourself (phone or walk-in)</b></summary>${addBookingForm()}</details>${bookingTable(d.bookings)}`;
    wireBookings(m);
    const f = $("#nb"); if (f) f.onclick = async () => { await guard(() => api("admin/bookings", { service_id: $("#nb_s").value, staff_id: $("#nb_st").value, date: $("#nb_d").value, time: $("#nb_t").value, name: $("#nb_n").value, phone: $("#nb_p").value, notes: "Added by the shop" }), "Booking added."); show(); };
  },
  async queue(m) {
    const d = await api("admin/queue");
    const barbers = SHOP.staff.filter(s => s.walk_ins !== false);
    m.innerHTML = `<h1>Walk-in queue</h1><p class="lead">Put <a href="/queue" target="_blank">/queue</a> on a TV or tablet in the shop. Customers join from the app or you add them here.</p>
      <div class="row"><span>Queue is <b>${d.board.open ? "open" : "closed"}</b></span><button class="btn sm ${d.board.open ? "red" : "green"}" id="qo">${d.board.open ? "Close queue" : "Open queue"}</button></div>
      <h2>Call the next customer</h2><div class="row">${barbers.map(b => `<button class="btn acc" data-call="${esc(b.id)}">Next for ${esc(b.name)}</button>`).join("")}</div>
      <h2>Add a walk-in</h2><div class="row"><input type="text" id="qn" placeholder="First name / initials" style="max-width:220px"><select id="qs" style="max-width:260px">${SHOP.services.map(s => `<option value="${esc(s.id)}">${esc(ml(s.name))}</option>`).join("")}</select><select id="qb" style="max-width:200px"><option value="any">Any</option>${barbers.map(b => `<option value="${esc(b.id)}">${esc(b.name)}</option>`).join("")}</select><button class="btn" id="qadd">Add</button></div>
      <h2>Today's tickets</h2><table><tr><th>No.</th><th>Name</th><th>Wants</th><th>Status</th><th></th></tr>${d.tickets.map(t => `<tr><td><b>${esc(t.no)}</b></td><td>${esc(t.name)}</td><td>${esc(t.barber === "any" ? "Any" : (SHOP.staff.find(s => s.id === t.barber) || {}).name)}</td><td>${esc(t.status)}${t.chair ? " · " + esc((SHOP.staff.find(s => s.id === t.chair) || {}).name || "") : ""}</td>
        <td class="row">${t.status === "called" ? `<button class="btn sm" data-st="${t.no}|in_chair">In chair</button>` : ""}${["called", "in_chair"].includes(t.status) ? `<button class="btn sm green" data-st="${t.no}|done">Done</button>` : ""}${t.status === "called" ? `<button class="btn sm ghost" data-skip="${t.no}" title="Called but not here: first time back 2 places, second time off the list">Not here (skip)</button>` : ""}${t.status === "waiting" || t.status === "called" ? `<button class="btn sm ghost" data-st="${t.no}|left">Left</button>` : ""}</td></tr>`).join("")}</table>
      <p class="small muted">Waits use each person's own service time and any booked appointments in the same chairs. Board checked at ${esc((d.board.checked_at || "").slice(11, 16))}.</p>`;
    $("#qo").onclick = async () => { await guard(() => api("admin/queue/open", { on: !d.board.open })); show(); };
    $$("[data-call]").forEach(b => b.onclick = async () => { const r = await guard(() => api("admin/queue/call", { chair: b.dataset.call })); toast(`Calling ${r.no} ${r.name}`); show(); });
    $$("[data-st]").forEach(b => b.onclick = async () => { const [no, st] = b.dataset.st.split("|"); await guard(() => api("admin/queue/status", { no, status: st })); show(); });
    $$("[data-skip]").forEach(b => b.onclick = async () => { const r = await guard(() => api("admin/queue/skip", { no: b.dataset.skip })); toast(r.removed ? `${r.no} skipped twice - taken off the list.` : `${r.no} moved back to place ${r.new_position}.`); show(); });
    $("#qadd").onclick = async () => { await guard(() => api("admin/queue/add", { name: $("#qn").value, service_id: $("#qs").value, barber: $("#qb").value }), "Added to the queue."); show(); };
  },
  async reminders(m) {
    let html = `<h1>Reminders & review requests</h1><p class="lead">Nothing is sent automatically. Tap a WhatsApp button to open the message ready to send from your own WhatsApp, or send an SMS if you've added a Twilio key.</p>`;
    if (ON.reminders) { const r = await api("admin/reminders"); html += `<h2>Reminders for ${esc(r.date)}</h2>${r.items.length ? `<table><tr><th>Who</th><th>When</th><th>Message</th><th></th></tr>${r.items.map(i => `<tr><td>${esc(i.name)}${i.contact_ok ? "" : "<br><span class='small muted'>didn't tick 'may message me'</span>"}</td><td>${esc(i.time)}</td><td class="small">${esc(i.text)}</td><td class="row"><a class="btn sm green" href="${esc(i.whatsapp_link)}" target="_blank">WhatsApp</a><button class="btn sm ghost" data-sms="${esc(JSON.stringify({ to: i.whatsapp_link.split("/")[3].split("?")[0], text: i.text }))}">SMS (Twilio)</button></td></tr>`).join("")}</table>` : "<p class='muted'>No confirmed bookings for tomorrow.</p>"}`; }
    if (ON.review_requests) { const r = await api("admin/review-requests"); html += `<h2>Ask for a review (visits in the last 7 days)</h2>${r.review_link ? `<p class="small">Review link: <a href="${esc(r.review_link)}" target="_blank">${esc(r.review_link)}</a></p>` : `<div class="warn">Add the shop's Google place ID in Shop details so the message contains the review link.</div>`}
      ${r.items.length ? `<table>${r.items.map(i => `<tr><td>${esc(i.name)}</td><td class="small">${esc(i.text)}</td><td><a class="btn sm green" href="${esc(i.whatsapp_link)}" target="_blank">WhatsApp</a></td></tr>`).join("")}</table>` : "<p class='muted'>Mark bookings as done to see them here.</p>"}`; }
    m.innerHTML = html;
    $$("[data-sms]").forEach(b => b.onclick = async () => { const d = JSON.parse(b.dataset.sms); await guard(() => api("admin/sms", { to: "+" + d.to, text: d.text }), "SMS sent."); });
  },
  async details(m) {
    const s = SHOP, langs = s.languages;
    const mlIn = (k, lab, area) => langs.map(l => `<label>${esc(lab)} (${esc(l)})</label>${area ? `<textarea data-ml="${k}" data-l="${l}" dir="auto">${esc((s[k] || {})[l] || "")}</textarea>` : `<input type="text" data-ml="${k}" data-l="${l}" value="${esc((s[k] || {})[l] || "")}" dir="auto">`}`).join("");
    m.innerHTML = `<h1>Shop details</h1><p class="lead">What customers see. Press Save at the bottom.</p>
    <div class="card"><div class="grid"><div><label>Shop name</label><input type="text" id="d_name" value="${esc(s.name)}"></div><div>${mlIn("tagline", "Tagline")}</div></div>
      <div class="grid"><div><label>Phone</label><input type="tel" id="d_phone" value="${esc(s.phone)}"></div><div><label>WhatsApp number</label><input type="tel" id="d_wa" value="${esc(s.whatsapp)}"></div><div><label>Email (optional)</label><input type="text" id="d_email" value="${esc(s.email || "")}"></div></div>
      <div class="grid"><div><label>Address</label><input type="text" id="d_addr" value="${esc(s.address)}"></div><div><label>Postcode</label><input type="text" id="d_pc" value="${esc(s.postcode)}"></div><div><label>Google place ID (for the review button)</label><input type="text" id="d_place" value="${esc(s.google_place_id)}" placeholder="e.g. ChIJ…"><span class="small muted">Find it with Google's Place ID finder.</span></div></div></div>
    <div class="card"><h2 style="margin-top:0">Languages</h2><p class="small muted">Up to 4. The first is the main one.</p><input type="text" id="d_langs" value="${esc(langs.join(", "))}"><p class="small muted">Codes, e.g. en, ro, pl, ar, tr, ur, fr, bn, so, pt</p></div>
    <div class="card"><h2 style="margin-top:0">Opening hours</h2>${DAYS.map((d, i) => { const h = s.hours[i]; return `<div class="row" style="margin:6px 0"><b style="width:110px">${DAYN[d]}</b><input type="time" data-h="${d}" data-w="open" value="${esc(h.open)}" style="width:130px"> – <input type="time" data-h="${d}" data-w="close" value="${esc(h.close)}" style="width:130px"><label class="chk"><input type="checkbox" data-h="${d}" data-w="closed" ${h.closed ? "checked" : ""}> Closed</label></div>`; }).join("")}
      <label>Special closed dates (YYYY-MM-DD, comma separated)</label><input type="text" id="d_closed" value="${esc((s.closed_dates || []).join(", "))}">${mlIn("hours_note", "Hours note")}</div>
    <div class="card"><h2 style="margin-top:0">Offer banner</h2><label class="chk"><input type="checkbox" id="d_offon" ${s.offer_on ? "checked" : ""}> Show the offer</label>${mlIn("offer", "Offer text")}</div>
    ${ON.policy ? `<div class="card"><h2 style="margin-top:0">Cancellation policy / no-show fee</h2>${mlIn("policy_text", "Policy", true)}<label>Short version for reminders</label><input type="text" id="d_pshort" value="${esc(s.policy_short || "")}"><p class="small muted">This is text only. To actually take a fee, switch on Deposits.</p></div>` : ""}
    ${ON.accessibility ? `<div class="card"><h2 style="margin-top:0">Accessibility information</h2>${mlIn("access_info", "Access info", true)}</div>` : ""}
    ${ON.social_links || ON.platform_links ? `<div class="card"><h2 style="margin-top:0">Links</h2><div class="grid">${ON.social_links ? `<div><label>Instagram</label><input type="url" id="d_ig" value="${esc(s.instagram)}"></div><div><label>TikTok</label><input type="url" id="d_tt" value="${esc(s.tiktok)}"></div>` : ""}
      ${ON.platform_links ? ["fresha", "treatwell", "booksy"].map(k => `<div><label>${k[0].toUpperCase() + k.slice(1)} page</label><input type="url" data-pl="${k}" value="${esc((s.platform_links || {})[k] || "")}"></div>`).join("") : ""}</div></div>` : ""}
    ${ON.loyalty || ON.vouchers ? `<div class="card"><div class="grid">${ON.loyalty ? `<div><h2 style="margin-top:0">Loyalty</h2><label>Stamps needed</label><input type="number" id="d_ln" min="2" max="30" value="${s.loyalty.stamps_needed}"><label>Reward</label><input type="text" id="d_lr" value="${esc(s.loyalty.reward)}"></div>` : ""}
      ${ON.vouchers ? `<div><h2 style="margin-top:0">Vouchers</h2><label>Valid for (months)</label><input type="number" id="d_vm" min="1" max="60" value="${s.vouchers.valid_months}"><label>Amounts offered (£, comma separated)</label><input type="text" id="d_va" value="${esc((s.vouchers.amounts || []).join(", "))}"><label>Pay link for vouchers (Deposits module)</label><input type="url" id="d_vl" value="${esc(s.vouchers.pay_link || "")}"></div>` : ""}</div></div>` : ""}
    <div class="card"><h2 style="margin-top:0">Booking settings</h2><div class="grid"><div><label>Slot step (minutes)</label><input type="number" id="b_slot" value="${s.booking.slot_minutes}"></div><div><label>Gap between appointments (min)</label><input type="number" id="b_buf" value="${s.booking.buffer_minutes}"></div><div><label>Minimum notice (min)</label><input type="number" id="b_min" value="${s.booking.min_notice_minutes}"></div><div><label>Days ahead customers can book</label><input type="number" id="b_max" value="${s.booking.max_days_ahead}"></div></div></div>
    <div class="card"><h2 style="margin-top:0">Message wording</h2><p class="small muted">Use {first}, {service}, {shop}, {date}, {time}, {policy}, {review_link}. Leave empty for the standard wording.</p><label>Reminder</label><textarea id="m_rem">${esc(s.messages.reminder || "")}</textarea><label>Review request</label><textarea id="m_rev">${esc(s.messages.review || "")}</textarea></div>
    <button class="btn" id="save">Save</button>`;
    $("#save").onclick = async () => {
      s.name = $("#d_name").value; s.phone = $("#d_phone").value; s.whatsapp = $("#d_wa").value; s.email = $("#d_email").value; s.address = $("#d_addr").value; s.postcode = $("#d_pc").value; s.google_place_id = $("#d_place").value;
      s.languages = $("#d_langs").value.split(",").map(x => x.trim()).filter(Boolean);
      $$("[data-ml]").forEach(n => { s[n.dataset.ml] = s[n.dataset.ml] || {}; if (typeof s[n.dataset.ml] === "string") s[n.dataset.ml] = {}; s[n.dataset.ml][n.dataset.l] = n.value.trim(); });
      s.hours = DAYS.map(d => ({ day: d, open: $(`[data-h="${d}"][data-w="open"]`).value, close: $(`[data-h="${d}"][data-w="close"]`).value, closed: $(`[data-h="${d}"][data-w="closed"]`).checked }));
      s.closed_dates = $("#d_closed").value.split(",").map(x => x.trim()).filter(Boolean); s.offer_on = $("#d_offon").checked;
      if ($("#d_pshort")) s.policy_short = $("#d_pshort").value;
      if ($("#d_ig")) { s.instagram = $("#d_ig").value; s.tiktok = $("#d_tt").value; }
      $$("[data-pl]").forEach(n => { s.platform_links[n.dataset.pl] = n.value; });
      if ($("#d_ln")) s.loyalty = { stamps_needed: +$("#d_ln").value, reward: $("#d_lr").value };
      if ($("#d_vm")) s.vouchers = { valid_months: +$("#d_vm").value, amounts: $("#d_va").value.split(",").map(x => x.trim()).filter(Boolean), pay_link: $("#d_vl").value };
      s.booking = { slot_minutes: +$("#b_slot").value, buffer_minutes: +$("#b_buf").value, min_notice_minutes: +$("#b_min").value, max_days_ahead: +$("#b_max").value };
      s.messages = { reminder: $("#m_rem").value, review: $("#m_rev").value };
      await saveShop(); show();
    };
  },
  async look(m) {
    const s = SHOP;
    m.innerHTML = `<h1>Look & photos</h1><p class="lead">Pick a style, then change any colour. Photos: use your own (no photos of clients without their permission).</p>
      <div class="swatch">${CARD.presets.map(p => `<button class="preset ${s.preset === p.id ? "on" : ""}" data-p="${p.id}"><div class="sw4">${["primary", "accent", "bg", "text"].map(k => `<i style="background:${p.colours[k]}"></i>`).join("")}</div><b>${esc(p.label)}</b><div class="small muted">${esc(p.description)}</div></button>`).join("")}</div>
      <div class="card"><h2 style="margin-top:0">Colours</h2><div class="grid">${["primary", "accent", "bg", "text", "surface"].map(k => `<div><label>${{ primary: "Main colour", accent: "Highlight colour", bg: "Background", text: "Text", surface: "Cards" }[k]}</label><input type="color" data-c="${k}" value="${esc(s.colours[k] || "#ffffff")}" style="width:100%;height:46px"></div>`).join("")}</div></div>
      <div class="card"><h2 style="margin-top:0">Hero photos (up to 5, they rotate)</h2><div class="row">${s.hero_images.map((h, i) => `<div><img class="thumb" src="/${esc(h)}" alt=""><br><button class="btn sm ghost" data-rm="${i}">Remove</button></div>`).join("") || "<span class='muted'>None yet — a pattern in your colours is shown.</span>"}</div><p><input type="file" accept="image/png,image/jpeg,image/webp" id="hero"></p>
        <h2>Logo</h2><div class="row">${s.logo ? `<img class="thumb" src="/${esc(s.logo)}" alt="">` : ""}<input type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" id="logo"></div></div>
      <button class="btn" id="save">Save</button>`;
    $$("[data-p]").forEach(b => b.onclick = () => { const p = CARD.presets.find(x => x.id === b.dataset.p); s.preset = p.id; s.variant = p.variant; s.colours = { ...p.colours }; VIEWS.look(m); });
    $$("[data-rm]").forEach(b => b.onclick = () => { s.hero_images.splice(+b.dataset.rm, 1); VIEWS.look(m); });
    $("#hero").onchange = async e => { const p = await upload(e.target); if (p) { s.hero_images.push(p); VIEWS.look(m); } };
    $("#logo").onchange = async e => { const p = await upload(e.target); if (p) { s.logo = p; VIEWS.look(m); } };
    $("#save").onclick = async () => { $$("[data-c]").forEach(i => s.colours[i.dataset.c] = i.value); await saveShop(); boot(); };
  },
  services(m) { listEditor(m, "services", "Services & prices", "Each service: category, minutes, 'from' price, who it's for and hair types. 'From' prices are what customers see.", it => ml(it.name) + (it.price_from ? ` · £${it.price_from}` : "") + (it.duration_min ? ` · ${it.duration_min} min` : "")); },
  staff(m) { listEditor(m, "staff", SHOP.staff_word_plural || "Team", "Profiles customers see. Commission rates are private (admin only).", it => it.name + (ml(it.role) ? " · " + ml(it.role) : "")); },
  gallery(m) {
    listEditor(m, "gallery", "Gallery", "Photos of your work and your salon.", it => ml(it.caption) || "Photo");
    if (ON.before_after) { const d = document.createElement("div"); d.innerHTML = `<hr style="margin:26px 0"><p><button class="btn ghost" id="ba">Edit before / after photos →</button></p>`; m.appendChild(d); $("#ba").onclick = () => listEditor(m, "before_after", "Before / after", "Tick that the client agreed before showing their photos.", it => ml(it.caption) || "Before / after"); }
  },
  reviews(m) { listEditor(m, "reviews", "Reviews", "Copy in real reviews only, with where and when they were left (e.g. 'Google, 2026-09-01'). Never write reviews yourself.", it => `${it.author || ""} ${"★".repeat(it.stars || 0)}`); },
  branches(m) { listEditor(m, "branches", "Branches", "Give each branch an id (shown in the list) and put that id on each team member who works there.", it => it.name); },
  async modules(m) {
    const d = await api("admin/card"); MODS = d.modules; ON = d.on;
    const sect = tier => MODS.filter(x => x.tier === tier).map(x => `<div class="mod"><label class="sw"><input type="checkbox" data-m="${esc(x.id)}" ${ON[x.id] ? "checked" : ""} ${x.locked ? "disabled" : ""}><span></span></label>
      <div><h3>${esc(x.name)} ${badge(x.status)} ${x.replaces ? `<span class="small muted">replaces ${esc(MODS.find(y => y.id === x.replaces).name)}</span>` : ""}</h3><p>${esc(x.description)}</p>
      ${(x.parts || []).length ? `<div class="row">${x.parts.map(p => `<span class="small">${esc(p[0])}: ${badge(p[1])}</span>`).join(" ")}</div>` : ""}
      <div class="cost">${x.cost_notes.map(c => `${c.connector ? `<b>${esc(c.connector)}:</b> ` : ""}${esc(c.text)}${c.checked ? ` <i>(checked ${esc(c.checked)}${c.url ? `, <a href="${esc(c.url)}" target="_blank" rel="noopener">source</a>` : ""})</i>` : ""}`).join("<br>")}</div></div></div>`).join("");
    m.innerHTML = `<h1>Modules</h1><p class="lead">${esc(CARD.title)} card v${esc(CARD.version)} (${esc(CARD.status)}). The <b>4-star base</b> is on out of the box; extras switch on when the shop wants them. Badges: ${badge("working")} works now, no key · ${badge("needs-key")} needs your own account key · ${badge("link-only")} a link to another service · ${badge("unverified")} not verified.</p>
      <div class="card"><h2 style="margin-top:0">4-star base</h2>${sect("base")}</div><div class="card"><h2 style="margin-top:0">Optional modules</h2>${sect("optional")}</div>`;
    $$("[data-m]").forEach(i => i.onchange = async () => { const r = await guard(() => api("admin/modules", { modules: { [i.dataset.m]: i.checked } }), (i.checked ? "Switched on: " : "Switched off: ") + MODS.find(x => x.id === i.dataset.m).name); ON = r.on; SHOP = await api("admin/shop"); frame(); });
  },
  async loyalty(m) {
    const d = await api("admin/loyalty");
    m.innerHTML = `<h1>Loyalty cards</h1><p class="lead">${d.rules.stamps_needed} stamps → ${esc(d.rules.reward)}. Give the customer their card code; they can check stamps in the app.</p>
      <div class="card row"><input type="text" id="ln" placeholder="Customer name (optional)" style="max-width:260px"><input type="tel" id="lp" placeholder="Phone (optional)" style="max-width:200px"><button class="btn" id="lnew">New card</button></div>
      <table><tr><th>Code</th><th>Name</th><th>Stamps</th><th>Rewards ready</th><th></th></tr>${d.cards.map(c => `<tr><td><b>${esc(c.code)}</b></td><td>${esc(c.name)}</td><td>${c.stamps} / ${d.rules.stamps_needed}</td><td>${c.rewards_ready}</td><td class="row"><button class="btn sm" data-s="${c.code}">+1 stamp</button>${c.rewards_ready ? `<button class="btn sm acc" data-r="${c.code}">Use reward</button>` : ""}</td></tr>`).join("")}</table>`;
    $("#lnew").onclick = async () => { const c = await guard(() => api("admin/loyalty/new", { name: $("#ln").value, phone: $("#lp").value })); toast("New card: " + c.code); show(); };
    $$("[data-s]").forEach(b => b.onclick = async () => { await guard(() => api("admin/loyalty/stamp", { code: b.dataset.s })); show(); });
    $$("[data-r]").forEach(b => b.onclick = async () => { await guard(() => api("admin/loyalty/redeem", { code: b.dataset.r }), "Reward used."); show(); });
  },
  async vouchers(m) {
    const d = await api("admin/vouchers");
    m.innerHTML = `<h1>Gift vouchers</h1><p class="lead">Issue a voucher when it's paid for. Customers can check the balance in the app.</p>
      <div class="card row"><input type="text" id="va" placeholder="Amount £" style="max-width:120px"><input type="text" id="vb" placeholder="Bought by" style="max-width:200px"><input type="text" id="vf" placeholder="For" style="max-width:200px"><button class="btn" id="vnew">Issue voucher</button></div>
      <div class="card row"><input type="text" id="rc" placeholder="Voucher code" style="max-width:200px"><input type="text" id="ra" placeholder="Amount to spend £" style="max-width:160px"><button class="btn acc" id="vred">Spend from voucher</button></div>
      <table><tr><th>Code</th><th>Value</th><th>Balance</th><th>For</th><th>Expires</th><th></th></tr>${d.vouchers.map(v => `<tr><td><b>${esc(v.code)}</b>${v.void ? " (cancelled)" : ""}</td><td>£${(v.value / 100).toFixed(2)}</td><td>£${(v.balance / 100).toFixed(2)}</td><td>${esc(v.for)}</td><td>${esc(v.expires)}</td><td>${v.void ? "" : `<button class="btn sm ghost" data-v="${v.code}">Cancel</button>`}</td></tr>`).join("")}</table>`;
    $("#vnew").onclick = async () => { const v = await guard(() => api("admin/vouchers/issue", { amount: $("#va").value, buyer: $("#vb").value, for: $("#vf").value })); toast("Voucher code: " + v.code); show(); };
    $("#vred").onclick = async () => { const v = await guard(() => api("admin/vouchers/redeem", { code: $("#rc").value, amount: $("#ra").value })); toast(`Done. £${(v.balance / 100).toFixed(2)} left.`); show(); };
    $$("[data-v]").forEach(b => b.onclick = async () => { if (confirm("Cancel this voucher?")) { await guard(() => api("admin/vouchers/void", { code: b.dataset.v })); show(); } });
  },
  async packages(m) {
    const d = await api("admin/packages");
    m.innerHTML = `<h1>Memberships & packages</h1><p class="lead">Define packages below, then sell them and count visits down.</p>
      <div class="card row"><select id="pp" style="max-width:260px">${d.plans.map(p => `<option value="${esc(p.id)}">${esc(ml(p.name))} (${p.uses} visits)</option>`).join("")}</select><input type="text" id="pc" placeholder="Client name" style="max-width:220px"><button class="btn" id="psell">Sell package</button></div>
      <table><tr><th>Code</th><th>Package</th><th>Client</th><th>Visits left</th><th>Ends</th><th></th></tr>${d.sold.map(p => `<tr><td><b>${esc(p.code)}</b></td><td>${esc(ml(p.plan_name))}</td><td>${esc(p.client)}</td><td>${p.uses_left} / ${p.uses_total}</td><td>${esc(p.expires)}</td><td><button class="btn sm" data-u="${p.code}">Use a visit</button></td></tr>`).join("")}</table>
      <div id="pedit"></div>`;
    $("#psell").onclick = async () => { const p = await guard(() => api("admin/packages/sell", { plan_id: $("#pp").value, client: $("#pc").value })); toast("Package code: " + p.code); show(); };
    $$("[data-u]").forEach(b => b.onclick = async () => { await guard(() => api("admin/packages/use", { code: b.dataset.u })); show(); });
    const pe = $("#pedit"); const inner = document.createElement("div"); pe.appendChild(inner); listEditor(inner, "packages", "Package types", "What you offer.", it => ml(it.name));
  },
  async products(m) {
    const d = await api("admin/products");
    m.innerHTML = `<h1>Products & stock</h1><p class="lead">Customers see only "in stock" or "out of stock", never your counts.</p>
      <table><tr><th>Product</th><th>Price</th><th>In stock</th><th></th></tr>${d.products.map(p => `<tr><td><b>${esc(ml(p.name))}</b><br><span class="small muted">${esc(p.brand || "")} ${esc(p.size || "")} ${p.barcode ? "· " + esc(p.barcode) : ""}</span></td><td>${p.price ? "£" + esc(p.price) : ""}</td><td>${p.qty}${p.low ? ` <span class="b b-needs-key">low</span>` : ""}</td>
        <td class="row"><button class="btn sm" data-sell="${esc(p.id)}">Sold 1</button><button class="btn sm ghost" data-rec="${esc(p.id)}">Received…</button><button class="btn sm ghost" data-cnt="${esc(p.id)}">Count…</button></td></tr>`).join("")}</table><div id="pe"></div>`;
    $$("[data-sell]").forEach(b => b.onclick = async () => { await guard(() => api("admin/products/sell", { id: b.dataset.sell, qty: 1 })); show(); });
    $$("[data-rec]").forEach(b => b.onclick = async () => { const q = prompt("How many arrived?"); if (q) { await guard(() => api("admin/products/receive", { id: b.dataset.rec, qty: +q })); show(); } });
    $$("[data-cnt]").forEach(b => b.onclick = async () => { const q = prompt("How many are on the shelf now?"); if (q !== null) { await guard(() => api("admin/products/count", { id: b.dataset.cnt, qty: +q })); show(); } });
    const inner = document.createElement("div"); $("#pe").appendChild(inner); listEditor(inner, "products", "Product list", "Type a barcode and press Look up to fill in name, brand and size from Open Beauty Facts (free, open database).", it => ml(it.name));
  },
  async clients(m) {
    const d = await api("admin/clients");
    m.innerHTML = `<h1>Client records</h1><div class="warn"><b>Private.</b> Stored only on this computer, never on the public app, never in an exported zip. Allergy and patch-test details are health data under UK GDPR: only record them with the client's consent (the tick box below records when and the exact wording). You can export or erase a client's record if they ask.</div>
      ${d.due.length ? `<div class="bad">Patch test due or not clear: ${d.due.map(x => esc(x.name)).join(", ")}</div>` : ""}
      <details class="card"><summary><b>+ New client</b></summary><div class="grid"><div><label>Name</label><input type="text" id="cn"></div><div><label>Phone</label><input type="tel" id="cp"></div></div>
        <label>Hair notes (colour formulas, preferences)</label><textarea id="ch"></textarea><label>Allergies</label><input type="text" id="ca">
        <label class="chk"><input type="checkbox" id="cc"> The client agreed: “${esc(d.consent_text)}”</label><button class="btn" id="csave">Save client</button></details>
      <table><tr><th>Client</th><th>Notes</th><th>Allergies</th><th>Last patch test</th><th></th></tr>${d.clients.map(c => { const pt = c.patch_tests[c.patch_tests.length - 1]; return `<tr><td><b>${esc(c.name)}</b><br><span class="small muted">${esc(c.phone)} ${c.consent && c.consent.given ? "· consent " + esc(c.consent.at.slice(0, 10)) : "· no consent"}</span></td><td class="small">${esc(c.hair_notes)}</td><td>${esc(c.allergies)}</td><td class="small">${pt ? `${esc(pt.product)}: ${esc(pt.result)} (${esc(pt.tested_on)}, retest by ${esc(pt.retest_by)})` : "—"}</td>
        <td class="row"><button class="btn sm" data-pt="${c.id}">+ Patch test</button><a class="btn sm ghost" href="/api/admin/clients/export/${c.id}" target="_blank">Export</a><button class="btn sm red" data-er="${c.id}">Erase</button></td></tr>`; }).join("")}</table>`;
    $("#csave").onclick = async () => { await guard(() => api("admin/clients/save", { name: $("#cn").value, phone: $("#cp").value, hair_notes: $("#ch").value, allergies: $("#ca").value, consent: $("#cc").checked }), "Client saved."); show(); };
    $$("[data-pt]").forEach(b => b.onclick = async () => { const product = prompt("Product tested (e.g. colour brand/shade)"); if (!product) return; const result = prompt("Result: clear, reaction, or not read yet", "not read yet"); if (!result) return; await guard(() => api("admin/clients/patch-test", { id: b.dataset.pt, product, result })); show(); });
    $$("[data-er]").forEach(b => b.onclick = async () => { if (confirm("Erase this client's record for good? (Use this when a client asks you to delete their data.)")) { await guard(() => api("admin/clients/erase/" + b.dataset.er, {}), "Erased."); show(); } });
  },
  async rota(m) {
    const d = await api("admin/rota");
    m.innerHTML = `<h1>Rota & commission</h1><p class="lead">Week ${esc(d.from)} to ${esc(d.to)}. Takings are added when you mark a booking done with the amount paid, or by hand below.</p>
      <div class="card row"><select id="rs" style="max-width:200px">${SHOP.staff.map(s => `<option value="${esc(s.id)}">${esc(s.name)}</option>`).join("")}</select><input type="date" id="rd" value="${today()}" style="max-width:170px"><input type="time" id="r1" value="09:00" style="max-width:120px"><input type="time" id="r2" value="17:30" style="max-width:120px"><button class="btn" id="radd">Add shift</button></div>
      <table><tr><th>Date</th><th>Who</th><th>Shift</th><th></th></tr>${d.shifts.map(s => `<tr><td>${esc(s.date)}</td><td>${esc((SHOP.staff.find(x => x.id === s.staff_id) || {}).name)}</td><td>${esc(s.start)}–${esc(s.end)}</td><td><button class="btn sm ghost" data-rm="${s.id}">Remove</button></td></tr>`).join("")}</table>
      <h2>Commission this week</h2><table><tr><th>Who</th><th>Service takings</th><th>Retail takings</th><th>Rates</th><th>Commission</th></tr>${d.commission.map(c => `<tr><td>${esc(c.name)}</td><td>${esc(c.service_takings)}</td><td>${esc(c.retail_takings)}</td><td>${c.service_percent}% / ${c.retail_percent}%</td><td><b>${esc(c.commission)}</b></td></tr>`).join("")}</table>
      <div class="card row"><select id="ts" style="max-width:200px">${SHOP.staff.map(s => `<option value="${esc(s.id)}">${esc(s.name)}</option>`).join("")}</select><input type="text" id="ta" placeholder="Amount £" style="max-width:120px"><select id="tk" style="max-width:140px"><option value="service">Service</option><option value="retail">Retail</option></select><button class="btn ghost" id="tadd">Add takings</button></div>`;
    $("#radd").onclick = async () => { await guard(() => api("admin/rota/shift", { staff_id: $("#rs").value, date: $("#rd").value, start: $("#r1").value, end: $("#r2").value })); show(); };
    $$("[data-rm]").forEach(b => b.onclick = async () => { await guard(() => api("admin/rota/remove", { id: b.dataset.rm })); show(); });
    $("#tadd").onclick = async () => { await guard(() => api("admin/rota/takings", { staff_id: $("#ts").value, date: today(), amount: $("#ta").value, kind: $("#tk").value })); show(); };
  },
  async referrals(m) {
    const d = await api("admin/referrals");
    m.innerHTML = `<h1>Referral codes</h1><p class="lead">Give a client a code to share. New clients type it when booking; you decide the reward.</p>
      <div class="card row"><input type="text" id="rn" placeholder="Client name" style="max-width:240px"><button class="btn" id="rnew">Create code</button></div>
      <table><tr><th>Code</th><th>Client</th><th>Used by</th></tr>${d.codes.map(c => `<tr><td><b>${esc(c.code)}</b></td><td>${esc(c.owner)}</td><td>${c.uses.map(u => esc(u.new_client) + " (" + esc(u.at.slice(0, 10)) + ")").join(", ") || "—"}</td></tr>`).join("")}</table>`;
    $("#rnew").onclick = async () => { const c = await guard(() => api("admin/referrals/new", { owner: $("#rn").value })); toast("Code: " + c.code); show(); };
  },
  async analytics(m) {
    const d = await api("admin/analytics");
    const lab = { open: "App opened", book_start: "Started booking", book_sent: "Bookings sent", call: "Call taps", whatsapp: "WhatsApp taps", directions: "Directions taps", review_click: "Review button", install: "Installed", queue_join: "Joined queue", voucher_check: "Voucher checks", loyalty_check: "Stamp checks", platform_link: "Platform links" };
    m.innerHTML = `<h1>Analytics (last 30 days)</h1><p class="lead">${esc(d.note)}</p><div class="grid">${Object.entries(lab).map(([k, v]) => `<div class="stat"><b>${d.totals[k] || 0}</b>${esc(v)}</div>`).join("")}</div>
      <h2>By day</h2><table><tr><th>Day</th>${Object.values(lab).slice(0, 6).map(v => `<th>${esc(v)}</th>`).join("")}</tr>${Object.entries(d.days).reverse().map(([day, e]) => `<tr><td>${esc(day)}</td>${Object.keys(lab).slice(0, 6).map(k => `<td>${e[k] || 0}</td>`).join("")}</tr>`).join("")}</table>`;
  },
  async suppliers(m) {
    m.innerHTML = `<h1>Supplier finder</h1><p class="lead">Live search of the web and OpenStreetMap for hair and beauty wholesalers. Every result is <b>found live, not checked by us</b> — call them before relying on it.</p>
      <div class="card row"><input type="text" id="sp" value="${esc(SHOP.postcode)}" placeholder="Postcode" style="max-width:150px"><input type="text" id="st" placeholder="Anything specific? e.g. Afro hair products" style="max-width:320px"><select id="sr" style="max-width:120px"><option value="3000">3 km</option><option value="5000" selected>5 km</option><option value="10000">10 km</option></select><button class="btn" id="sgo">Search live</button></div>
      <div id="sres"></div><h2>Saved suppliers (private)</h2><table>${(SHOP.suppliers || []).map(s => `<tr><td><b>${esc(s.title)}</b><br><a class="small" href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a></td><td class="small">${esc(s.address || "")}</td><td class="small muted">${esc(s.label || "")} ${esc((s.checked_at || "").slice(0, 16))}</td></tr>`).join("") || "<tr><td class='muted'>None saved yet.</td></tr>"}</table>`;
    $("#sgo").onclick = async () => {
      $("#sres").innerHTML = "<p class='muted'>Searching live…</p>";
      const r = await guard(() => api("admin/suppliers/search", { postcode: $("#sp").value, text: $("#st").value, radius_m: +$("#sr").value }));
      const row = x => `<tr><td><b>${esc(x.title)}</b><br><a class="small" href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.url)}</a><div class="small muted">${esc(x.snippet || x.address || "")}</div></td><td class="small muted">${esc(x.source)} · ${esc((x.checked_at || "").slice(0, 16))}</td><td><button class="btn sm" data-save='${esc(JSON.stringify(x))}'>Save</button></td></tr>`;
      $("#sres").innerHTML = `${r.errors.map(e => `<div class="warn">${esc(e.provider)}: ${esc(e.message)}</div>`).join("")}${r.notes.map(n => `<p class="small muted">${esc(n)}</p>`).join("")}
        <h2>On the map (${r.map.length})</h2><table>${r.map.map(row).join("") || "<tr><td class='muted'>Nothing tagged nearby.</td></tr>"}</table><h2>On the web (${r.web.length})</h2><table>${r.web.map(row).join("") || "<tr><td class='muted'>No web results.</td></tr>"}</table>`;
      $$("[data-save]").forEach(b => b.onclick = async () => { await guard(() => api("admin/suppliers/save", { result: JSON.parse(b.dataset.save) }), "Saved."); SHOP = await api("admin/shop"); });
    };
  },
  async connectors(m) {
    const list = await api("admin/connectors");
    const used = new Set(MODS.filter(x => ON[x.id]).flatMap(x => x.connectors || []));
    m.innerHTML = `<h1>Connectors & keys</h1><p class="lead">Keys are saved only on this computer (data/shop.secrets.json), shown masked, and never included in an exported zip.</p>
      ${list.filter(c => used.has(c.id)).map(c => `<div class="card"><h2 style="margin-top:0">${esc(c.name)} <span class="b b-${c.status === "working-tested" ? "working" : c.status === "code-ready-needs-key" ? "needs-key" : "unverified"}">${esc(c.status)}</span></h2><p class="small">${esc(c.what_it_does)}</p>
        ${(c.credentials || []).map(k => `<label>${esc(k.label)}</label><input type="${k.secret ? "password" : "text"}" data-cred="${esc(c.id)}" data-key="${esc(k.key)}" value="${esc((c.saved || {})[k.key] || "")}" placeholder="${esc(k.help || "")}">`).join("")}
        <div class="row" style="margin-top:10px">${(c.credentials || []).length ? `<button class="btn sm" data-savec="${esc(c.id)}">Save keys</button>` : ""}<button class="btn sm ghost" data-test="${esc(c.id)}">Test</button><a class="small" href="${esc(c.docs_url)}" target="_blank" rel="noopener">Official docs</a></div><div id="t_${esc(c.id)}"></div></div>`).join("") || "<p class='muted'>No switched-on module uses an outside service.</p>"}`;
    $$("[data-savec]").forEach(b => b.onclick = async () => { const values = {}; $$(`[data-cred="${b.dataset.savec}"]`).forEach(i => values[i.dataset.key] = i.value); await guard(() => api(`admin/connectors/${b.dataset.savec}/credentials`, { values }), "Keys saved on this computer."); });
    $$("[data-test]").forEach(b => b.onclick = async () => { const r = await guard(() => api(`admin/connectors/${b.dataset.test}/test`, {})); $("#t_" + b.dataset.test).innerHTML = `<div class="${r.ok ? "ok" : "bad"}">${esc(r.message)}</div>`; });
  },
  password(m) {
    m.innerHTML = `<h1>Change password</h1><div class="card" style="max-width:420px"><label>Current password</label><input type="password" id="po"><label>New password (6+ characters)</label><input type="password" id="pn"><p><button class="btn" id="pgo">Change</button></p></div>`;
    $("#pgo").onclick = async () => { await guard(() => api("admin/password", { old: $("#po").value, new: $("#pn").value }), "Password changed. Please log in again."); setTimeout(() => location.reload(), 1200); };
  },
};

function staffOpts(sel) { return `<option value="any">Anyone</option>` + SHOP.staff.map(s => `<option value="${esc(s.id)}" ${sel === s.id ? "selected" : ""}>${esc(s.name)}</option>`).join(""); }
function addBookingForm() {
  return `<div class="grid"><div><label>Service</label><select id="nb_s">${SHOP.services.map(s => `<option value="${esc(s.id)}">${esc(ml(s.name))}</option>`).join("")}</select></div><div><label>${esc(SHOP.staff_word)}</label><select id="nb_st">${staffOpts()}</select></div>
    <div><label>Date</label><input type="date" id="nb_d" value="${today()}"></div><div><label>Time</label><input type="time" id="nb_t" step="900"></div><div><label>Client name</label><input type="text" id="nb_n"></div><div><label>Phone</label><input type="tel" id="nb_p"></div></div><p><button class="btn" id="nb">Add booking</button></p>`;
}
function alertBox(alerts) {
  if (!alerts || !alerts.length) return "";
  return `<div class="bad"><b>Needs you:</b><ul>${alerts.map(a => `<li>${esc(a.text)}</li>`).join("")}</ul></div>`;
}
function bookingTable(list) {
  if (!list.length) return "<p class='muted'>None.</p>";
  return `<table><tr><th>When</th><th>Client</th><th>Service</th><th>${esc(SHOP.staff_word)}</th><th>Status</th><th></th></tr>${list.map(b => `<tr><td><b>${esc(b.date)}</b><br>${esc(b.start)}–${esc(b.end)}</td>
    <td>${esc(b.name)}<br><a class="small" href="tel:${esc(b.phone)}">${esc(b.phone)}</a>${b.notes ? `<div class="small muted">${esc(b.notes)}</div>` : ""}${b.referral_code ? `<div class="small">Referral: ${esc(b.referral_code)}</div>` : ""}</td>
    <td>${esc(ml(b.service_name))}${b.price_from ? `<div class="small muted">from £${esc(b.price_from)}</div>` : ""}</td><td>${b.staff_id ? esc((SHOP.staff.find(s => s.id === b.staff_id) || {}).name || b.staff_id) : `<select data-pick="${b.id}">${staffOpts()}</select>`}</td>
    <td>${badge(b.status, b.status === "held" ? "held for deposit" : b.status === "refund_due" ? "refund due" : b.status === "no_show" ? "no-show" : "")}<div class="small muted">ref ${esc(b.ref)}</div>
      ${b.status === "held" && b.hold_until ? `<div class="small">until ${esc(b.hold_until.slice(11, 16))}</div>` : ""}
      ${b.deposit && b.deposit.amount ? `<div class="small">deposit £${esc(b.deposit.amount)}: ${esc(({ due: "not paid yet", paid: "paid", failed: "failed", refund_due: "REFUND DUE", none: "-" })[b.deposit.state] || b.deposit.state)}</div>` : ""}
      ${(b.flags || []).map(f => `<div class="small warn-t">⚠ ${esc(f)}</div>`).join("")}</td>
    <td class="row">${b.status === "requested" ? `<button class="btn sm green" data-act="${b.id}|confirm">Confirm</button><button class="btn sm ghost" data-act="${b.id}|declined">Decline</button>` : ""}
      ${(b.status === "held" || (b.deposit && b.deposit.state === "due")) && ["held", "requested", "confirmed"].includes(b.status) ? `<button class="btn sm green" data-act="${b.id}|paid">Deposit paid</button>` : ""}
      ${b.status === "held" ? `<button class="btn sm ghost" data-act="${b.id}|payment-failed">Release time</button>` : ""}
      ${b.status === "refund_due" ? `<button class="btn sm" data-act="${b.id}|alert-done">Refund done</button>` : ""}
      ${b.status === "confirmed" ? `<button class="btn sm" data-act="${b.id}|done">Done</button><button class="btn sm ghost" data-act="${b.id}|move">Move</button><button class="btn sm ghost" data-act="${b.id}|no_show">No-show</button><button class="btn sm red" data-act="${b.id}|cancelled">Cancel</button>${ON.gcal ? `<button class="btn sm ghost" data-act="${b.id}|gcal">→ Google Calendar</button>` : ""}` : ""}
      <a class="btn sm ghost" href="/api/booking/${esc(b.ref)}.ics">.ics</a></td></tr>`).join("")}</table>`;
}
function wireBookings(m) {
  $$("[data-act]", m).forEach(b => b.onclick = async () => {
    const [id, act] = b.dataset.act.split("|"); let body = {};
    if (act === "confirm") { const p = $(`[data-pick="${id}"]`, m); body.staff_id = p && p.value !== "any" ? p.value : ""; }
    if (act === "done") { const v = prompt("Amount paid (£) — optional, used for commission", ""); if (v === null) return; body.price_paid = v; }
    if (act === "move") { const d = prompt("New date (YYYY-MM-DD)"); if (!d) return; const t = prompt("New time (HH:MM)"); if (!t) return; body = { date: d, time: t }; }
    if (act === "cancelled" && !confirm("Cancel this booking?")) return;
    if (act === "paid" && !confirm("Mark the deposit as paid? Only do this once you have the money (cash, card reader or bank).")) return;
    if (act === "alert-done" && !confirm("Have you refunded the client? This clears the alert.")) return;
    await guard(() => api(`admin/bookings/${id}/${act}`, body), act === "gcal" ? "Sent to Google Calendar." : "Updated.");
    show();
  });
}
boot();
