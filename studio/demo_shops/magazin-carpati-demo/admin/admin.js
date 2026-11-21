/* Shop owner admin page. Plain JavaScript. Talks only to this shop's own server. */
"use strict";
const $ = s => document.querySelector(s);
const esc = v => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const DAYS = ["mon","tue","wed","thu","fri","sat","sun"], DAYN = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
const LANGS = {en:"English",ro:"Romanian",pl:"Polish",ar:"Arabic",tr:"Turkish",kmr:"Kurdish (Kurmanji)",ckb:"Kurdish (Sorani)",hi:"Hindi",ur:"Urdu",bn:"Bengali",ta:"Tamil",pa:"Punjabi",fr:"French",so:"Somali",am:"Amharic",zh:"Chinese",pt:"Portuguese",bg:"Bulgarian",lt:"Lithuanian",uk:"Ukrainian",el:"Greek",fa:"Farsi",prs:"Dari",ps:"Pashto"};
const RTL = new Set(["ar","fa","ur","ps","ckb","prs"]);
let S = null, TAB = "shop";

async function api(path, body) {
  const r = await fetch("/api/" + path, body === undefined ? {} : { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body) });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { const e = new Error(j.message || "Something went wrong"); e.code = r.status; throw e; }
  return j;
}
function toast(m) { const t = document.createElement("div"); t.className = "toast"; t.textContent = m; document.body.appendChild(t); setTimeout(() => t.remove(), 5000); }

async function start() {
  const me = await api("admin/me");
  if (!me.logged_in) return loginView();
  S = await api("admin/shop");
  document.documentElement.style.setProperty("--p", S.colours.primary); document.documentElement.style.setProperty("--a", S.colours.accent);
  frame();
}
function loginView() {
  $("#root").innerHTML = `<div class="card login"><h2>Owner login</h2><p class="muted">Only the shop owner can change the app.</p>
   <label for="pw">Password</label><input type="password" id="pw" autocomplete="current-password"><p><button class="btn" id="go">Log in</button></p><div id="msg"></div></div>`;
  const go = async () => { try { await api("login", { password: $("#pw").value }); start(); } catch (e) { $("#msg").innerHTML = `<div class="note bad">${esc(e.message)}</div>`; } };
  $("#go").onclick = go; $("#pw").onkeydown = e => { if (e.key === "Enter") go(); };
}
function frame() {
  $("#root").innerHTML = `<header><h1>${esc(S.name)} — owner admin${S.demo ? " (demo)" : ""}</h1><a href="/" target="_blank">See the app</a><button class="btn g s" id="out">Log out</button></header>
   <nav>${[["shop","Shop details"],["products","Products & prices"],["suppliers","My suppliers (private)"],["connectors","Connectors"],["account","Password & publishing"]].map(([k,n]) => `<button data-t="${k}" class="${k === TAB ? "on" : ""}">${n}</button>`).join("")}</nav><main id="m"></main>`;
  document.querySelectorAll("nav button").forEach(b => b.onclick = () => { TAB = b.dataset.t; frame(); });
  $("#out").onclick = async () => { await api("logout", {}); location.reload(); };
  ({shop: tabShop, products: tabProducts, suppliers: tabSuppliers, connectors: tabConnectors, account: tabAccount})[TAB]();
}
function ml(field, lang) { return (S[field] || {})[lang] || ""; }
async function save(msg) { try { const r = await api("admin/shop", S); S = r.shop; toast(msg || "Saved. The app is updated."); } catch (e) { toast("Not saved: " + e.message); } }

function tabShop() {
  const L = S.languages;
  $("#m").innerHTML = `<div class="card"><h2>Name and look</h2>
   <label>Shop name</label><input id="name" value="${esc(S.name)}">
   ${L.map(l => `<label>Short line under the name (${LANGS[l] || l})</label><input dir="${RTL.has(l) ? "rtl" : "ltr"}" data-ml="tagline" data-l="${l}" value="${esc(ml("tagline", l))}">`).join("")}
   <label>Languages in the app (first one is the main language, up to 4)</label>
   <div class="row">${[0,1,2,3].map(i => `<select data-lang="${i}"><option value="">—</option>${Object.entries(LANGS).map(([k,n]) => `<option value="${k}" ${L[i] === k ? "selected" : ""}>${n}</option>`).join("")}</select>`).join("")}</div>
   <div class="row">${[["primary","Main colour"],["accent","Second colour"],["bg","Background"],["text","Text"]].map(([k,n]) => `<div><label>${n}</label><input type="color" data-col="${k}" value="${S.colours[k]}"></div>`).join("")}</div>
   <label>Logo (optional, under 600 KB)</label><input type="file" id="logo" accept="image/png,image/jpeg,image/webp,image/svg+xml">
   ${S.logo ? `<p><img src="${S.logo}" style="height:64px;border-radius:12px"> <button class="btn g s" id="nologo">Remove logo</button></p>` : ""}</div>
   <div class="card"><h2>Contact and address</h2><div class="row"><div><label>Phone</label><input id="phone" value="${esc(S.phone)}" inputmode="tel"></div>
   <div><label>WhatsApp number</label><input id="wa" value="${esc(S.whatsapp)}" inputmode="tel"></div></div>
   <label>Address</label><input id="addr" value="${esc(S.address)}"><label>Postcode</label><input id="pc" value="${esc(S.postcode)}"></div>
   <div class="card"><h2>Opening hours</h2><table>${S.hours.map((h, i) => `<tr><td>${DAYN[i]}</td><td><input type="time" data-h="${i}" data-k="open" value="${esc(h.open)}"></td><td><input type="time" data-h="${i}" data-k="close" value="${esc(h.close)}"></td><td><label style="margin:0"><input type="checkbox" data-h="${i}" data-k="closed" ${h.closed ? "checked" : ""} style="width:auto;min-height:0"> closed</label></td></tr>`).join("")}</table></div>
   <div class="card"><h2>Offer / announcement banner</h2><label><input type="checkbox" id="annon" ${S.announcement_on ? "checked" : ""} style="width:auto;min-height:0"> Show the banner</label>
   ${L.map(l => `<label>Banner text (${LANGS[l] || l})</label><input dir="${RTL.has(l) ? "rtl" : "ltr"}" data-ml="announcement" data-l="${l}" value="${esc(ml("announcement", l))}">`).join("")}</div>
   <p><button class="btn a" id="sv">Save changes</button></p>`;
  const f = () => {
    S.name = $("#name").value; S.phone = $("#phone").value; S.whatsapp = $("#wa").value; S.address = $("#addr").value; S.postcode = $("#pc").value;
    S.announcement_on = $("#annon").checked;
    document.querySelectorAll("[data-ml]").forEach(i => { S[i.dataset.ml] = S[i.dataset.ml] || {}; S[i.dataset.ml][i.dataset.l] = i.value; });
    document.querySelectorAll("[data-col]").forEach(i => S.colours[i.dataset.col] = i.value);
    document.querySelectorAll("[data-h]").forEach(i => { const h = S.hours[+i.dataset.h]; h[i.dataset.k] = i.type === "checkbox" ? i.checked : i.value; });
    const langs = [...document.querySelectorAll("[data-lang]")].map(s => s.value).filter(Boolean); if (langs.length) { S.languages = [...new Set(langs)]; S.default_language = S.languages[0]; }
  };
  $("#sv").onclick = () => { f(); save().then(frame); };
  const nl = $("#nologo"); if (nl) nl.onclick = () => { f(); S.logo = ""; save().then(frame); };
  $("#logo").onchange = e => { const file = e.target.files[0]; if (!file) return; const rd = new FileReader(); rd.onload = () => { f(); S.logo = rd.result; save("Logo saved.").then(frame); }; rd.readAsDataURL(file); };
}

function tabProducts() {
  const L = S.languages;
  $("#m").innerHTML = `<div class="card"><h2>Products and prices</h2><p class="muted small">You set the prices. Leave price empty if you'd rather not show one. A pay link (from Stripe/Square) shows a Pay button.</p>
   <div class="row"><input id="bc" placeholder="Barcode (e.g. 5900259128843)" inputmode="numeric"><button class="btn g" id="bcgo" style="flex:0 0 auto">Look up barcode</button></div><div id="bcres"></div>
   <div style="overflow-x:auto"><table><tr>${L.map(l => `<th>Name (${LANGS[l] || l})</th>`).join("")}<th>Price £</th><th>Unit</th><th>Group</th><th>In stock</th><th>Pay link</th><th></th></tr>
   ${S.products.map((p, i) => `<tr>${L.map(l => `<td><input dir="${RTL.has(l) ? "rtl" : "ltr"}" data-p="${i}" data-k="name" data-l="${l}" value="${esc((p.name || {})[l] || "")}"></td>`).join("")}
     <td><input data-p="${i}" data-k="price" value="${esc(p.price)}" inputmode="decimal" style="width:90px"></td><td><input data-p="${i}" data-k="unit" value="${esc(p.unit)}" style="width:80px"></td>
     <td><input data-p="${i}" data-k="category" value="${esc(p.category)}"></td><td><input type="checkbox" data-p="${i}" data-k="in_stock" ${p.in_stock ? "checked" : ""} style="width:auto;min-height:0"></td>
     <td><input data-p="${i}" data-k="pay_link" value="${esc(p.pay_link)}" placeholder="https://…"></td><td><button class="btn r s" data-del="${i}">✕</button></td></tr>`).join("")}</table></div>
   <p class="row"><button class="btn g" id="add">+ Add a product</button><button class="btn a" id="sv">Save products</button></p></div>`;
  const f = () => document.querySelectorAll("[data-p]").forEach(i => { const p = S.products[+i.dataset.p];
    if (i.dataset.k === "name") { p.name = p.name || {}; p.name[i.dataset.l] = i.value; } else p[i.dataset.k] = i.type === "checkbox" ? i.checked : i.value; });
  $("#add").onclick = () => { f(); S.products.push({ name: {}, price: "", unit: "", category: "", in_stock: true, pay_link: "" }); tabProducts(); };
  document.querySelectorAll("[data-del]").forEach(b => b.onclick = () => { f(); S.products.splice(+b.dataset.del, 1); tabProducts(); });
  $("#sv").onclick = () => { f(); save("Products saved.").then(tabProducts); };
  $("#bcgo").onclick = async () => {
    try { const r = await api("admin/connectors/open_food_facts/run", { action: "barcode", params: { barcode: $("#bc").value } });
      if (!r.ok) throw new Error(r.message); const x = r.result;
      $("#bcres").innerHTML = x.found ? `<div class="note ok">${esc(x.brands || "")} ${esc(x.product_name || "")} ${esc(x.quantity || "")} <button class="btn s" id="bcadd">Add to my products</button><div class="small">From Open Food Facts (${esc(x.source_url)}). Check it's right; you set the price.</div></div>` : `<div class="note">${esc(x.message)}</div>`;
      const b = $("#bcadd"); if (b) b.onclick = () => { f(); const nm = {}; nm[S.default_language] = [x.brands, x.product_name, x.quantity].filter(Boolean).join(" "); S.products.push({ name: nm, price: "", unit: "", category: "", in_stock: true, pay_link: "", barcode: x.barcode }); tabProducts(); };
    } catch (e) { $("#bcres").innerHTML = `<div class="note bad">${esc(e.message)}</div>`; } };
}

function tabSuppliers() {
  $("#m").innerHTML = `<div class="card"><h2>My suppliers (only you see this)</h2><p class="muted small">Found with HVT Foundry Studio's live search. <b>Found live, not checked by us</b> — always check a supplier yourself before paying.</p>
   ${(S.suppliers || []).length ? S.suppliers.map(s => `<div class="card" style="margin:8px 0;border:1px solid #0001"><b>${esc(s.title)}</b> <span class="badge">${esc(s.source || "")}</span>
     <div class="small">${esc(s.snippet || s.address || "")}</div><div class="small"><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a></div>
     <div class="small muted">Found ${esc(s.checked_at || "")} · saved ${esc(s.saved_at || "")}${s.query ? " · search: " + esc(s.query) : ""}</div></div>`).join("") : `<p class="muted">None saved yet.</p>`}</div>`;
}

async function tabConnectors() {
  $("#m").innerHTML = `<div class="card"><h2>Connectors</h2><p class="muted small">Link your shop to other services. Keys are saved only on this computer (data/shop.secrets.json), shown masked, and never included in the public app or in a zip.</p><div id="cl">Loading…</div></div>
   <div class="card"><h2>Add any other service (Custom API)</h2>
   <div class="row"><div><label>Name (letters/numbers)</label><input id="cs"></div><div><label>Base address</label><input id="cb" placeholder="https://api.example.com/v1"></div></div>
   <div class="row"><div><label>Login type</label><select id="ca"><option value="none">No login</option><option value="api_key_header">API key in a header</option><option value="bearer">Bearer token</option><option value="basic">Username + password</option></select></div><div><label>Header name (for API key)</label><input id="ch" value="X-API-Key"></div></div>
   <label>Actions — one per line: name, GET or POST, path (use {placeholders})</label><textarea id="cx" placeholder="latest, GET, /latest&#10;product, GET, /products/{id}"></textarea>
   <label>…or paste an OpenAPI JSON file to list its endpoints</label><textarea id="co"></textarea><p class="row"><button class="btn g" id="coi">Read OpenAPI</button><button class="btn a" id="csv">Save custom API</button></p><div id="cor"></div></div>`;
  const list = await api("admin/connectors");
  $("#cl").innerHTML = list.filter(c => c.id !== "custom_api").map(c => `<details class="card" style="margin:8px 0;border:1px solid #0001"><summary><b>${esc(c.name)}</b> <span class="badge">${esc(c.category)}</span> <span class="badge">${esc(c.cost_type)}</span> <span class="badge b-${esc(c.status)}">${esc(c.status)}</span> ${c.enabled ? '<span class="badge ok">on</span>' : ""}</summary>
    <p>${esc(c.what_it_does)}</p>${c.status_note ? `<div class="note small">${esc(c.status_note)}</div>` : ""}
    ${c.pricing ? `<div class="small muted">Cost: ${esc(c.pricing.text)} ${c.pricing.checked ? "(checked " + esc(c.pricing.checked) + ")" : ""} <a href="${esc(c.pricing.url)}" target="_blank" rel="noopener">vendor page</a></div>` : ""}
    ${(c.credentials || []).map(k => `<label>${esc(k.label)}</label><input data-c="${esc(c.id)}" data-k="${esc(k.key)}" ${k.secret ? 'type="password" autocomplete="off"' : ""} value="${esc((c.saved_credentials || {})[k.key] || "")}" placeholder="${esc(k.help || "")}">`).join("")}
    <p class="row">${(c.credentials || []).length ? `<button class="btn g s" data-save="${esc(c.id)}">Save keys</button>` : ""}<button class="btn s" data-test="${esc(c.id)}">Test</button>
     <button class="btn g s" data-en="${esc(c.id)}" data-on="${c.enabled ? 0 : 1}">${c.enabled ? "Switch off" : "Switch on for my shop"}</button></p>
    ${Object.entries(c.actions || {}).map(([a, d]) => `<div class="row">${(d.params || []).map(p => `<input data-ap="${esc(c.id)}:${esc(a)}" data-k="${esc(p.key)}" placeholder="${esc(p.label)}${p.example ? " e.g. " + esc(p.example) : ""}">`).join("")}<button class="btn a s" data-run="${esc(c.id)}:${esc(a)}" style="flex:0 0 auto">${esc(d.label)}</button></div>`).join("")}
    <div id="r-${esc(c.id.replace(":", "_"))}"></div></details>`).join("");
  const out = (id, html) => { $("#r-" + id.replace(":", "_")).innerHTML = html; };
  document.querySelectorAll("[data-save]").forEach(b => b.onclick = async () => { const id = b.dataset.save, v = {};
    document.querySelectorAll(`[data-c="${id}"]`).forEach(i => v[i.dataset.k] = i.value);
    try { await api(`admin/connectors/${id}/credentials`, { values: v }); toast("Keys saved on this computer."); tabConnectors(); } catch (e) { toast(e.message); } });
  document.querySelectorAll("[data-test]").forEach(b => b.onclick = async () => { const id = b.dataset.test; out(id, "Testing…");
    try { const r = await api(`admin/connectors/${id}/test`, {}); out(id, `<div class="note ${r.ok ? "ok" : "bad"}">${esc(r.message)}</div>`); } catch (e) { out(id, `<div class="note bad">${esc(e.message)}</div>`); } });
  document.querySelectorAll("[data-en]").forEach(b => b.onclick = async () => { await api(`admin/connectors/${b.dataset.en}/enable`, { on: b.dataset.on === "1" }); tabConnectors(); });
  document.querySelectorAll("[data-run]").forEach(b => b.onclick = async () => { const [id, a] = b.dataset.run.split(/:(?=[^:]+$)/), p = {};
    document.querySelectorAll(`[data-ap="${b.dataset.run}"]`).forEach(i => p[i.dataset.k] = i.value); out(id, "Working…");
    try { const r = await api(`admin/connectors/${id}/run`, { action: a, params: p }); out(id, r.ok ? `<pre>${esc(JSON.stringify(r.result, null, 1))}</pre>` : `<div class="note bad">${esc(r.message)}</div>`); } catch (e) { out(id, `<div class="note bad">${esc(e.message)}</div>`); } });
  $("#coi").onclick = async () => { try { const o = await api("admin/openapi", { spec: $("#co").value }); $("#cb").value = o.base_url; $("#ca").value = o.auth_type; $("#ch").value = o.header_name;
      $("#cx").value = o.endpoints.slice(0, 30).map(e => `${e.name}, ${e.method}, ${e.path}`).join("\n");
      $("#cor").innerHTML = `<div class="note ok">${esc(o.title)} ${esc(o.version)}: ${o.endpoints.length} endpoints found. The first 30 are filled in above — delete the ones you don't need.</div>`; } catch (e) { $("#cor").innerHTML = `<div class="note bad">${esc(e.message)}</div>`; } };
  $("#csv").onclick = async () => { const actions = $("#cx").value.split("\n").map(l => l.split(",").map(x => x.trim())).filter(a => a.length >= 3).map(([name, method, path]) => ({ name, method, path }));
    try { await api("admin/custom-api", { slug: $("#cs").value, definition: { label: $("#cs").value, base_url: $("#cb").value, auth_type: $("#ca").value, header_name: $("#ch").value, actions } }); toast("Custom API saved. Add its key above and press Test."); tabConnectors(); } catch (e) { toast(e.message); } };
}

function tabAccount() {
  $("#m").innerHTML = `<div class="card"><h2>Change password</h2><label>Current password</label><input type="password" id="o"><label>New password (6+ characters)</label><input type="password" id="n"><p><button class="btn" id="cp">Change password</button></p></div>
   <div class="card"><h2>Put your app online</h2><p>Your public app is the <b>site</b> folder next to this program. Every time you press Save here, it is updated.</p>
   <ol><li>Upload the <b>site</b> folder to a free static host (the README explains Cloudflare Pages step by step).</li><li>Send customers the link, or print it as a QR code in the window.</li><li>On their phone they open the link and choose <b>Add to Home Screen</b>.</li></ol>
   <p class="muted small">Your private data (password, suppliers, keys) is in the <b>data</b> folder and is never uploaded.</p></div>`;
  $("#cp").onclick = async () => { try { const r = await api("admin/password", { old: $("#o").value, new: $("#n").value }); toast(r.message); setTimeout(() => location.reload(), 1500); } catch (e) { toast(e.message); } };
}
start();
