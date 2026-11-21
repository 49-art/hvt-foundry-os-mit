/* HVT Foundry Studio — front end (no frameworks, no external files). */
"use strict";
const $ = (s, el = document) => el.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const view = () => $("#view");
let STATE = null;
const UI = { step: {}, sizing: {} };

async function api(path, body) {
  const opt = body === undefined ? {} : { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body) };
  const r = await fetch("/api/" + path, opt);
  const j = await r.json();
  if (r.status === 401 && j.login_required) { showLogin(); throw Object.assign(new Error(j.message), { code: 401 }); }
  if (!r.ok) { const e = new Error(j.message || "Refused"); e.code = r.status; e.body = j; throw e; }
  return j;
}
function showLogin() {
  if (document.getElementById("loginbox")) return;
  view().innerHTML = `<div class="card" id="loginbox" style="max-width:460px;margin:40px auto"><h2 style="margin-top:0">Studio login</h2>
    <p class="muted">This Studio is protected with a password.</p><label for="lpw">Password</label><input type="password" id="lpw" style="width:100%;padding:14px;border:2px solid var(--line);border-radius:12px">
    <div class="row" style="margin-top:14px"><button class="btn amber" id="lgo">Log in</button></div><div id="lmsg"></div></div>`;
  const go = async () => { const r = await fetch("/api/login", { method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({ password: $("#lpw").value }) });
    if (r.ok) location.reload(); else $("#lmsg").innerHTML = `<div class="warn">Wrong password.</div>`; };
  $("#lgo").onclick = go; $("#lpw").onkeydown = e => { if (e.key === "Enter") go(); };
}
function toast(msg, bad = false) {
  const t = document.createElement("div"); t.className = "toast" + (bad ? " bad" : ""); t.innerHTML = msg;
  $("#toasts").appendChild(t); setTimeout(() => t.remove(), bad ? 9000 : 6000);
}
function kernelToast(res, what) {
  const k = res.kernel || {};
  toast(`<b>${esc(what)}</b><br><span class="small">Kernel: authorized for ${esc(k.agent)} (${esc(k.office)}) · status <b>${esc(res.review_status)}</b></span>`);
}
function refusalToast(e) { toast(`<b>Refused${e.code ? " (" + e.code + ")" : ""}</b><br>${esc(e.message)}`, true); }
async function act(fn, what, after) {
  try { const r = await fn(); kernelToast(r, what); await refreshState(); if (after) await after(r); return r; }
  catch (e) { refusalToast(e); await refreshState(); }
}
async function refreshState() {
  STATE = await api("state");
  const k = $("#kstatus");
  k.textContent = STATE.booted ? "Kernel booted · 4 gates OK" : "Kernel NOT booted";
  k.className = "kstatus " + (STATE.booted ? "ok" : "bad");
  $("#qcount").textContent = STATE.counts.queue || "";
}
const badge = (txt, cls) => `<span class="badge b-${esc(cls || txt)}">${esc(txt)}</span>`;
const pending = () => badge("pending human review", "pending");

/* ---------------------------------------------------------------- tiny markdown */
function md(src) {
  if (!src) return "<p class='muted'>No document.</p>";
  const lines = src.split("\n"); let out = [], inList = false, inCode = false, table = [];
  const inline = s => esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`(.+?)`/g, "<code>$1</code>");
  const flushTable = () => { if (!table.length) return; const rows = table.filter(r => !/^\|\s*-/.test(r));
    out.push("<div class='scroll'><table>" + rows.map((r, i) => "<tr>" + r.replace(/^\||\|$/g, "").split("|").map(c => i ? `<td>${inline(c.trim())}</td>` : `<th>${inline(c.trim())}</th>`).join("") + "</tr>").join("") + "</table></div>"); table = []; };
  for (const l of lines) {
    if (l.startsWith("```")) { if (inCode) { out.push("</pre>"); inCode = false; } else { out.push("<pre>"); inCode = true; } continue; }
    if (inCode) { out.push(esc(l) + "\n"); continue; }
    if (l.startsWith("|")) { table.push(l); continue; } else flushTable();
    const m = l.match(/^(#{1,4})\s+(.*)/);
    if (/^\s*[-*]\s+/.test(l)) { if (!inList) { out.push("<ul>"); inList = true; } out.push("<li>" + inline(l.replace(/^\s*[-*]\s+/, "")) + "</li>"); continue; }
    if (inList) { out.push("</ul>"); inList = false; }
    if (m) out.push(`<h${m[1].length + 1}>${inline(m[2])}</h${m[1].length + 1}>`);
    else if (l.trim() === "---") out.push("<hr>");
    else if (l.trim()) out.push("<p>" + inline(l) + "</p>");
  }
  flushTable(); if (inList) out.push("</ul>"); if (inCode) out.push("</pre>");
  return "<div class='md'>" + out.join("") + "</div>";
}

/* ---------------------------------------------------------------- router */
const routes = { boot: renderBoot, sessions: renderSessions, session: renderSession, queue: renderQueue, audit: renderAudit, about: renderAbout,
  find: (a) => window.renderFind(a), shopapp: (a) => window.renderShopApp(a), connectors: (a) => window.renderConnectors(a), settings: () => window.renderSettings(), cards: (a) => window.renderCards(a) };
async function route() {
  const [, name = "boot", arg, stepArg] = (location.hash || "#/boot").split("/");
  if (name === "session" && stepArg !== undefined && /^[0-5]$/.test(stepArg)) UI.step[arg] = +stepArg;
  document.querySelectorAll("#tabs a").forEach(a => a.classList.toggle("active", a.dataset.tab === ({session: "sessions", shopapp: "sessions"}[name] || name)));
  try { await refreshState(); await (routes[name] || renderBoot)(arg); }
  catch (e) { view().innerHTML = `<div class="card"><h2>Something went wrong</h2><p>${esc(e.message)}</p></div>`; }
  view().focus({ preventScroll: true });
}
window.addEventListener("hashchange", route);

/* ---------------------------------------------------------------- boot */
async function renderBoot(_, fresh) {
  view().innerHTML = `<h1>Boot the Foundry Kernel</h1>
  <p class="lead">Before anything else, the kernel checks four things in order. It must also say <b>no</b> when it should — a kernel that only shows success hasn't proved it enforces anything.</p>
  <div class="card"><div class="row" style="justify-content:space-between"><h2 style="margin:0">Boot sequence</h2>
  <button class="btn amber" id="reboot">Run the boot again</button></div><ul class="steps" id="steps"></ul><div id="bootsum"></div></div>
  <div class="card"><h2>What happens next</h2><p>Open a <a href="#/sessions">session</a> with a business owner. Every action you take is checked by the kernel first and saved as <b>pending human review</b>.</p>
  ${STATE.banners.map(b => `<div class="warn">${esc(b)}</div>`).join("")}</div>`;
  const data = fresh || { steps: STATE.boot_steps, ok: STATE.booted };
  const ul = $("#steps");
  data.steps.forEach((s, i) => {
    const li = document.createElement("li");
    li.innerHTML = `<div class="gate ${s.outcome}">${esc(s.gate)}</div><div style="flex:1"><div class="row"><b>${esc(s.title)}</b>
      ${badge(s.outcome === "pass" ? "PASS" : "REFUSED", s.outcome)} ${s.expected === "refused" ? badge("refusal expected", "pending") : ""}
      ${s.as_expected ? "" : badge("NOT AS EXPECTED", "refused")}</div><div class="muted small">${esc(s.detail)} · ${s.ms} ms</div></div>`;
    ul.appendChild(li); setTimeout(() => li.classList.add("show"), 250 * i + 50);
  });
  setTimeout(() => { $("#bootsum").innerHTML = data.ok
    ? `<div class="pill-note"><b>Kernel booted.</b> All gates passed and all three refusal checks refused, as they should.</div>`
    : `<div class="warn"><b>Kernel did not boot.</b> No actions can run until it does.</div>`; }, 250 * data.steps.length + 100);
  $("#reboot").onclick = async () => { const r = await api("boot", {}); await refreshState(); renderBoot(null, r); };
}

/* ---------------------------------------------------------------- sessions */
async function renderSessions() {
  const [types, sessions] = await Promise.all([api("business-types"), api("sessions")]);
  view().innerHTML = `<h1>Customer Sessions</h1>
  <p class="lead">Step 1 of the loop: open a session (SES-####) for the kind of business you are sitting with.</p>
  <div class="card"><h2 style="margin-top:0">Open a new session</h2>
    <label>What kind of business is it?</label><div class="grid g3" id="types">${types.map(t => `
      <button class="chip" data-id="${t.id}" style="text-align:left;border-radius:14px;padding:14px">
        <b>${esc(t.name)}</b><br><span class="small muted">${esc(t.id)} · ${t.data_level === "full" ? "full data" : "card summary only"}</span><br>
        <span class="small">${esc(t.card_status)}</span></button>`).join("")}</div>
    <div id="typeinfo"></div>
    <div class="grid g2"><div><label for="bname">Business name (optional, as the owner gives it)</label><input type="text" id="bname" placeholder="e.g. the name on the shop sign"></div>
    <div><label for="loc">Where (optional)</label><input type="text" id="loc" placeholder="e.g. in the shop"></div></div>
    <label for="runby">Who is running this session (optional)</label><input type="text" id="runby" placeholder="your own name">
    <div class="row" style="margin-top:16px"><button class="btn amber" id="open" disabled>Open session</button><span class="muted small">Acts as: ${esc(STATE.acting_agent)}</span></div>
  </div>
  <h2>All sessions</h2>
  ${sessions.length ? sessions.map(s => `<div class="card sess-row"><div><b>${esc(s.id)}</b> · ${esc(s.classification.business_type_name)} ${s.business_name ? "· " + esc(s.business_name) : ""}
    <div class="small muted">${esc(s.date)} · ${s.linked_wishes.length} wish(es) ${s.follow_up_of ? "· follow-up of " + esc(s.follow_up_of) : ""}</div></div>
    <div class="row">${badge(s.status, s.status === "Open" ? "pending" : "pass")}<a class="btn small ghost" href="#/session/${s.id}">Open</a></div></div>`).join("")
    : `<div class="empty">No sessions yet.</div>`}`;
  let chosen = null;
  document.querySelectorAll("#types .chip").forEach(b => b.onclick = async () => {
    document.querySelectorAll("#types .chip").forEach(x => x.classList.remove("on")); b.classList.add("on"); chosen = b.dataset.id; $("#open").disabled = false;
    const t = types.find(x => x.id === chosen);
    $("#typeinfo").innerHTML = `<div class="card" style="background:#fbfaf7"><dl class="kv"><dt>Sector</dt><dd>${esc(t.sector)}</dd><dt>Market industry</dt><dd>${esc(t.market_industry)}</dd><dt>Card</dt><dd>${esc(t.doc_path)}</dd></dl>
      <h3>Known gaps (shown honestly)</h3><ul>${t.gaps.map(g => `<li>${esc(g)}</li>`).join("")}</ul></div>`;
  });
  $("#open").onclick = () => act(() => api("sessions", { business_type_id: chosen, business_name: $("#bname").value, location: $("#loc").value, run_by: $("#runby").value }),
    "Session opened", r => { location.hash = "#/session/" + r.result.id; });
}

/* ---------------------------------------------------------------- one session */
const STEPS = ["Session", "Classify", "Configure", "Owner review", "Wishes", "Close"];
async function renderSession(sid) {
  const d = await api("sessions/" + sid);
  const s = d.session, open = s.status === "Open";
  const cur = UI.step[sid] ?? (open ? (d.proposals.length ? 3 : 1) : 5);
  const done = [true, s.classification.source !== "graph" || d.proposals.length > 0, d.proposals.length > 0, d.responses.length > 0, d.wishes.length > 0, !open];
  view().innerHTML = `<div class="sess-row"><div><h1>${esc(s.id)} · ${esc(s.classification.business_type_name)}</h1>
    <p class="lead">${s.business_name ? esc(s.business_name) + " · " : ""}${esc(s.date)} ${s.follow_up_of ? "· follow-up of <a href='#/session/" + esc(s.follow_up_of) + "'>" + esc(s.follow_up_of) + "</a>" : ""}</p></div>
    <div class="row">${badge(s.status, open ? "pending" : "pass")} ${pending()}</div></div>
    <div class="row" style="margin:-4px 0 12px"><a class="btn small amber" href="#/find/${esc(s.id)}">🔎 Find for this shop (live)</a>
      <a class="btn small" href="#/shopapp/${esc(s.id)}">📱 Build the shop's own app</a>
      <a class="btn small ghost" href="#/connectors/${esc(s.id)}">🔌 Connectors for this shop</a>
      <span class="small muted">${d.saved_results.length} saved find(s)${d.shop_app ? " · app built" : ""}</span></div>
    <div class="stepper">${STEPS.map((n, i) => `<button data-i="${i}" class="${i === cur ? "active" : ""} ${done[i] ? "done" : ""}"><b>Step ${i + 1}</b>${n}</button>`).join("")}</div>
    <div id="panel"></div>`;
  document.querySelectorAll(".stepper button").forEach(b => b.onclick = () => { UI.step[sid] = +b.dataset.i; renderSession(sid); });
  const P = $("#panel");
  const reload = () => renderSession(sid);
  if (!open && cur !== 0 && cur !== 5) P.innerHTML = `<div class="warn">This session is ${esc(s.status)}. Its records are permanent and can't be changed — only superseded by a follow-up session.</div>`;
  const panels = [panelSession, panelClassify, panelConfigure, panelReview, panelWishes, panelClose];
  await panels[cur](P, d, open, reload);
}

function panelSession(P, d) {
  const s = d.session;
  P.innerHTML += `<div class="card"><h2 style="margin-top:0">Session record</h2><dl class="kv">
    <dt>ID</dt><dd>${esc(s.id)} (rev ${s.rev})</dd><dt>Business type</dt><dd>${esc(s.project_id_or_business_type_id || "not listed")}</dd>
    <dt>Status</dt><dd>${esc(s.status)} <span class="muted small">(Open → Closed → Actioned, HVT-0006 §9.1)</span></dd>
    <dt>Owner</dt><dd>${esc(s.owner)}</dd><dt>Run by</dt><dd>${esc(s.run_by || "—")}</dd><dt>Location</dt><dd>${esc(s.location || "—")}</dd>
    <dt>Record</dt><dd>${esc(s.record_note)}</dd></dl>
    ${d.carried_wishes.length ? `<h3>Wishes carried into this follow-up</h3>${d.carried_wishes.map(w => `<div class="quote">${esc(w.description)} <span class="small muted">${esc(w.id)} · ${esc(w.status)}</span></div>`).join("")}` : ""}
    <details><summary>Revision history (${d.history.length}) — nothing deleted</summary><div class="scroll"><table><tr><th>Rev</th><th>Recorded</th><th>Status</th><th>Supersedes</th></tr>
    ${d.history.map(h => `<tr><td>${h.rev}</td><td>${esc(h.recorded_at)}</td><td>${esc(h.status)}</td><td>${esc(h.supersedes || "—")}</td></tr>`).join("")}</table></div></details>
    <div class="row" style="margin-top:12px"><button class="btn" onclick="UI.step['${s.id}']=1;renderSession('${s.id}')">Next: classify →</button></div></div>`;
}

async function panelClassify(P, d, open, reload) {
  const s = d.session, c = s.classification;
  const types = await api("business-types");
  const card = c.business_type_id ? await api("card/" + c.business_type_id) : { markdown: null };
  P.innerHTML += `<div class="grid g2"><div class="card"><h2 style="margin-top:0">Current classification</h2><dl class="kv">
    <dt>Business type</dt><dd>${esc(c.business_type_name)} ${c.business_type_id ? "(" + esc(c.business_type_id) + ")" : ""}</dd>
    <dt>Sector</dt><dd>${esc(c.sector)}</dd><dt>Market industry</dt><dd>${esc(c.market_industry)}</dd>
    <dt>Source</dt><dd>${c.source === "graph" ? badge("from the Foundry graph", "pending") : badge("corrected by owner", "partly")}</dd></dl>
    ${c.owner_corrections.length ? `<h3>Owner corrections</h3>${c.owner_corrections.map(o => `<div class="quote">${esc(o.owner_words || "(no words given)")}<div class="small muted">${esc(o.at)}</div></div>`).join("")}` : ""}
    <div class="pill-note">The customer's stated reality overrides any earlier classification (DOC-0005).</div></div>
    <div class="card"><h2 style="margin-top:0">Owner says it's different?</h2>
    <label for="cbt">Business type</label><select id="cbt" ${open ? "" : "disabled"}><option value="">— keep —</option>
      ${types.map(t => `<option value="${t.id}">${esc(t.id)} · ${esc(t.name)}</option>`).join("")}<option value="UNLISTED">Not listed — none of these</option></select>
    <label for="csec">Sector, in the owner's words (optional)</label><input type="text" id="csec" ${open ? "" : "disabled"}>
    <label for="cind">Industry, in the owner's words (optional)</label><input type="text" id="cind" ${open ? "" : "disabled"}>
    <label for="cwords">What the owner said</label><textarea id="cwords" placeholder="Type exactly what the owner said" ${open ? "" : "disabled"}></textarea>
    <div class="row" style="margin-top:12px"><button class="btn amber" id="csave" ${open ? "" : "disabled"}>Save owner's correction</button>
    <button class="btn ghost" onclick="UI.step['${s.id}']=2;renderSession('${s.id}')">Looks right → configure</button></div></div></div>
    <div class="card"><details><summary>What the BusinessType card says (from the record)</summary>${md(card.markdown)}</details></div>`;
  const b = $("#csave"); if (b) b.onclick = () => act(() => api(`sessions/${s.id}/classify`, { business_type_id: $("#cbt").value || null, sector: $("#csec").value || null, market_industry: $("#cind").value || null, owner_words: $("#cwords").value }), "Classification updated", reload);
}

function chipGroup(id, opts, val) { return `<div class="chips" data-group="${id}">${opts.map(o => `<button class="chip ${o === val ? "on" : ""}" data-v="${esc(o)}">${esc(o)}</button>`).join("")}</div>`; }
function bindChips(root, onChange) {
  root.querySelectorAll(".chips[data-group]").forEach(g => g.querySelectorAll(".chip").forEach(c => c.onclick = () => {
    const on = c.classList.contains("on"); g.querySelectorAll(".chip").forEach(x => x.classList.remove("on")); if (!on) c.classList.add("on");
    onChange && onChange(g.dataset.group, on ? null : c.dataset.v); }));
}
const chipVal = (root, g) => { const c = root.querySelector(`.chips[data-group="${g}"] .chip.on`); return c ? c.dataset.v : null; };

function renderConfig(cfg) {
  if (!cfg.known) return `<div class="warn">${cfg.flags.map(esc).join("<br>")}</div>`;
  const f = cfg.filters;
  const comp = c => { const fc = c.factcheck;
    return `<div class="card" style="margin:0"><div class="sess-row"><b>${esc(c.name)}</b>${badge(fc ? fc.overall : "unverified", fc ? fc.overall : "unverified")}</div>
    <div class="small muted">${esc(c.id)} · ${esc(c.category)} · Tier ${esc(c.tier)} · partner status: ${esc(c.partner_status)}</div>
    <p style="margin:.5em 0">${esc(fc ? fc.plain_price : "No fact-check.")}</p>
    <div class="row small">${f.budget.value ? badge(c.budget_fit === "fits" ? "fits budget" : c.budget_fit === "over" ? "over budget" : "price unverified", c.budget_fit) : ""}
      <span class="muted">works with ${c.compatible_engines.map(esc).join(", ")}</span></div>
    ${/inferred|PROVISIONAL/.test(c.id_provenance || "") ? `<div class="small muted">ID note: ${esc(c.id_provenance)}</div>` : ""}
    <details><summary class="small">Fact-check detail (${esc(fc ? fc.checked_on : "")})</summary><table>${(fc ? fc.fields : []).map(x => `<tr><td>${esc(x.field)}</td><td>${badge(x.result, x.result)}</td><td>${esc(x.note)}${x.source ? `<div class="muted small">${esc(x.source)}</div>` : ""}</td></tr>`).join("")}</table></details></div>`; };
  return `<div class="warn">${cfg.flags.map(esc).join("<br>")}</div>
  <h3>Filters</h3><ul class="small">${["size", "budget", "tech"].map(k => `<li><b>${k === "tech" ? "Technical ability" : k[0].toUpperCase() + k.slice(1)}: ${esc(f[k].value || "not set")}</b> — ${esc(f[k].note)}</li>`).join("")}</ul>
  <h3>Recommended Foundry engines</h3><div class="grid g3">${cfg.engines.map(e => `<div class="card" style="margin:0"><b>${esc(e.name)}</b><div class="small muted">${esc(e.id)}</div><p style="margin:.4em 0">${esc(e.plain)}</p>${badge(e.status, e.status === "Reusable Asset" ? "pass" : "partly")} <span class="small muted">${esc(e.status_plain)}</span></div>`).join("") || "<div class='empty'>None on the card.</div>"}</div>
  ${cfg.capabilities.length ? `<h3>Capabilities</h3><div class="scroll"><table><tr><th>Capability</th><th>Needed?</th><th>Covered by</th></tr>${cfg.capabilities.map(c => `<tr><td>${esc(c.name)}</td><td>${c.required ? "required" : "optional"}</td><td>${c.covered_by ? esc(c.covered_by) : badge("gap — no engine", "gap") + (c.overlay ? `<div class="small">${esc(c.overlay.search_result)} (${esc(c.overlay.search)}) → ${esc(c.overlay.procedure)}</div>` : `<div class="small muted">${esc(c.note || "")}</div>`)}</td></tr>`).join("")}</table></div>` : ""}
  <h3>Problems</h3><ul>${cfg.problems.map(p => `<li>${esc(p.id)} ${esc(p.name || "(name only in the card document)")} ${p.solved_by.length ? "— solved by " + p.solved_by.map(esc).join(", ") : badge("no engine", "gap")}</li>`).join("")}</ul>
  <h3>Solution Components (tools from other companies)</h3>${cfg.components.length ? `<div class="grid g2">${cfg.components.map(comp).join("")}</div>` : `<div class="empty">No Solution Components are linked to this business type in the graph.</div>`}`;
}

async function panelConfigure(P, d, open, reload) {
  const s = d.session, z = s.sizing || {}, V = STATE.vocab;
  const last = d.proposals[d.proposals.length - 1];
  P.innerHTML += `<div class="card"><h2 style="margin-top:0">Run the Configurator</h2>
    <p class="muted">Pick what fits the owner (HVT-0006 §4). Leave any blank if unsure.</p>
    <label>Business size</label>${chipGroup("size", V.sizes, z.size)}
    <label>Monthly budget for tools</label>${chipGroup("budget", V.budgets, z.budget)}
    <label>Technical ability</label>${chipGroup("tech", V.tech, z.tech)}
    <div class="row" style="margin-top:16px"><button class="btn amber" id="run" ${open ? "" : "disabled"}>Run Configurator</button><span class="muted small">Makes proposal ${esc(s.id)}/P${d.proposals.length + 1}</span></div></div>
    <div class="card" id="cfgout">${last ? `<div class="sess-row"><h2 style="margin:0">Proposal ${esc(last.id)}</h2>${pending()}</div>` + renderConfig(last.configuration)
      + `<div class="row" style="margin-top:14px"><button class="btn" onclick="UI.step['${s.id}']=3;renderSession('${s.id}')">Show the owner →</button></div>` : "<div class='empty'>No proposal yet. Run the Configurator.</div>"}</div>`;
  bindChips(P);
  const b = $("#run"); if (b) b.onclick = () => act(() => api(`sessions/${s.id}/configure`, { size: chipVal(P, "size"), budget: chipVal(P, "budget"), tech: chipVal(P, "tech") }), "Configurator run — proposal saved", reload);
}

function panelReview(P, d, open, reload) {
  const s = d.session, last = d.proposals[d.proposals.length - 1];
  if (!last) { P.innerHTML += `<div class="empty">Run the Configurator first.</div>`; return; }
  P.innerHTML += `<div class="card"><div class="sess-row"><h2 style="margin-top:0">Here's what we'd suggest for your business</h2>${badge(last.status, /Accepted/.test(last.status) ? "pass" : /Rejected/.test(last.status) ? "refused" : "pending")}</div>
    <ul class="plain">${last.plain.map(l => `<li><b>${esc(l.head)}</b>${esc(l.body)}</li>`).join("")}</ul>
    ${d.saved_results.length ? `<h3>What we found for you today</h3><p class="small muted">Found live on the internet and on OpenStreetMap, <b>not checked by us</b>. Please check any supplier yourself before paying.</p>
      <ul class="plain">${d.saved_results.map(x => `<li><b>${esc(x.title)}</b>${esc(x.snippet || x.address || "")} <span class="small"><a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.url)}</a> · ${esc(x.source)} · checked ${esc((x.checked_at || "").slice(0, 16).replace("T", " "))}</span></li>`).join("")}</ul>` : ""}
    <div class="pill-note">Nothing here is final. The Foundry team reviews everything before anything is built or set up.</div>
    <label for="ow">Anything the owner wants to say (their own words)</label><textarea id="ow" ${open ? "" : "disabled"}></textarea>
    <div class="row" style="margin-top:12px"><button class="btn green" id="acc" ${open ? "" : "disabled"}>Owner is happy with this</button>
    <button class="btn red" id="rej" ${open ? "" : "disabled"}>Owner says no</button>
    <button class="btn ghost" onclick="UI.step['${s.id}']=4;renderSession('${s.id}')">Owner has a wish →</button></div>
    ${d.responses.length ? `<h3>Owner responses so far</h3>${d.responses.map(r => `<div class="quote">${badge(r.decision === "accept" ? "happy" : "said no", r.decision === "accept" ? "pass" : "refused")} ${esc(r.owner_words || "")}<div class="small muted">${esc(r.id)} · ${esc(r.meaning)}</div></div>`).join("")}` : ""}</div>`;
  const send = dec => act(() => api(`sessions/${s.id}/response`, { proposal_id: last.id, decision: dec, owner_words: $("#ow").value }), "Owner's answer recorded", reload);
  const a = $("#acc"), r = $("#rej"); if (a) a.onclick = () => send("accept"); if (r) r.onclick = () => send("reject");
}

function panelWishes(P, d, open, reload) {
  const s = d.session;
  P.innerHTML += `<div class="grid g2"><div class="card"><h2 style="margin-top:0">Capture a wish</h2>
    <label for="wd">In the owner's own words</label><textarea id="wd" placeholder="Type exactly what they said — don't tidy it up" ${open ? "" : "disabled"}></textarea>
    <label>How much does the owner want it? (their words, optional)</label>${chipGroup("prio", STATE.vocab.priorities, null)}
    ${d.problems.length ? `<label>Linked problems (optional)</label><div class="chips">${d.problems.map(p => `<label class="chip" style="margin:0;font-weight:600"><input type="checkbox" value="${esc(p.id)}" class="wp"> ${esc(p.id)} ${esc(p.name || "")}</label>`).join("")}</div>` : ""}
    <label for="wc">Which capability is this about? (optional)</label><input type="text" id="wc" ${open ? "" : "disabled"}>
    <label class="chip" style="display:inline-flex;gap:10px;margin-top:14px"><input type="checkbox" id="wa"> This touches the owner's own data, branding or content (Article VIII)</label>
    <div class="row" style="margin-top:14px"><button class="btn amber" id="wsave" ${open ? "" : "disabled"}>Save wish</button></div></div>
    <div class="card"><h2 style="margin-top:0">Wishes in this session (${d.wishes.length})</h2>
    ${d.wishes.length ? d.wishes.map(w => `<div class="quote">${esc(w.description)}<div class="small muted">${esc(w.id)} · ${esc(w.status)} ${w.priority ? "· " + esc(w.priority) : ""} ${w.customer_asset_flag ? "· customer asset" : ""}</div></div>`).join("") : "<div class='empty'>No wishes yet.</div>"}
    <div class="row" style="margin-top:12px"><button class="btn ghost" onclick="UI.step['${s.id}']=5;renderSession('${s.id}')">Finished → close session</button></div></div></div>`;
  bindChips(P);
  const b = $("#wsave"); if (b) b.onclick = () => act(() => api(`sessions/${s.id}/wishes`, { description: $("#wd").value, priority: chipVal(P, "prio"),
    linked_problems: [...P.querySelectorAll(".wp:checked")].map(x => x.value), linked_capabilities: $("#wc").value, customer_asset_flag: $("#wa").checked }), "Wish saved", reload);
}

function panelClose(P, d, open, reload) {
  const s = d.session;
  P.innerHTML += `<div class="card"><h2 style="margin-top:0">${open ? "Close the session" : "Session " + esc(s.status)}</h2>
    ${open ? `<p>When you close, the session and its ${d.wishes.length} wish(es) become permanent records. Open wishes go straight to the <a href="#/queue">review queue</a>.</p>
      <button class="btn amber" id="close">Close session</button>`
    : `<p>Closed ${esc(s.closed_at || "")}. ${d.wishes.length} wish(es) recorded. ${s.status === "Actioned" ? "All wishes have been resolved." : "Open wishes are in the review queue."}</p>
      <div class="row"><a class="btn" href="#/queue">Go to review queue</a>
      <button class="btn ghost" id="fup">Offer an updated configuration (new follow-up session)</button></div>`}</div>`;
  const c = $("#close"); if (c) c.onclick = () => { if (confirm("Close " + s.id + "? This can't be undone — records become permanent.")) act(() => api(`sessions/${s.id}/close`, {}), "Session closed", reload); };
  const f = $("#fup"); if (f) f.onclick = () => act(() => api(`sessions/${s.id}/follow-up`, {}), "Follow-up session opened", r => { location.hash = "#/session/" + r.result.id; });
}

/* ---------------------------------------------------------------- review queue */
async function renderQueue() {
  const [q, sessions] = await Promise.all([api("queue"), api("sessions")]);
  const resolvedSessions = sessions.filter(s => s.status !== "Open");
  view().innerHTML = `<h1>Review queue</h1>
  <p class="lead">Step 7, the return path. Each open wish is looked at under Article XIV (model first) and Article II (Engine Search), then resolved one of three ways. Nothing is deleted — a resolution adds a new revision.</p>
  ${q.length ? q.map(w => `<div class="card" data-w="${esc(w.id)}"><div class="sess-row"><div><b>${esc(w.id)}</b> · ${esc(w.business_type || "")} ${w.business_name ? "· " + esc(w.business_name) : ""} · from <a href="#/session/${esc(w.session_id)}">${esc(w.session_id)}</a></div>
    <div class="row">${badge(w.status, "pending")} ${w.priority ? badge(w.priority) : ""} ${w.customer_asset_flag ? badge("customer asset", "partly") : ""}</div></div>
    <div class="quote">${esc(w.description)}</div>
    ${w.session_status === "Open" ? `<div class="warn">Session still open — close it first (the return path starts after leaving the tablet).</div>` : ""}
    <div class="chips" data-group="o-${esc(w.id)}"><button class="chip" data-v="reconfigure">a. Re-configure with existing engines</button><button class="chip" data-v="engine_search">b. Log a formal Engine Search</button><button class="chip" data-v="out_of_scope">c. Out of scope for now</button></div>
    <label>Reason (required — it is logged)</label><textarea class="rs" style="min-height:70px"></textarea>
    <label>Capability (for an Engine Search)</label><input type="text" class="cap" value="${esc(w.linked_capabilities || "")}">
    <div class="row" style="margin-top:10px"><button class="btn amber res" ${w.session_status === "Open" ? "disabled" : ""}>Record resolution</button></div></div>`).join("")
    : `<div class="empty">No open wishes. 🎉</div>`}
  <h2>Closed sessions</h2>${resolvedSessions.length ? resolvedSessions.map(s => `<div class="card sess-row"><div><b>${esc(s.id)}</b> · ${esc(s.classification.business_type_name)} · ${s.linked_wishes.length} wish(es)</div><div class="row">${badge(s.status, "pass")}<a class="btn small ghost" href="#/session/${s.id}">Open</a></div></div>`).join("") : "<div class='empty'>None yet.</div>"}`;
  bindChips(view());
  view().querySelectorAll("[data-w]").forEach(card => { const b = card.querySelector(".res"); b.onclick = () => {
    const outcome = chipVal(card, "o-" + card.dataset.w);
    if (!outcome) return toast("Choose a, b or c first.", true);
    act(() => api(`wishes/${card.dataset.w}/resolve`, { outcome, reason: card.querySelector(".rs").value, capability: card.querySelector(".cap").value }), "Wish resolved", renderQueue);
  }; });
}

/* ---------------------------------------------------------------- audit */
async function renderAudit() {
  const a = await api("audit");
  view().innerHTML = `<h1>Audit log</h1><p class="lead">Every kernel check and every Studio action, newest first. Nothing is removed from this log.</p>
  <div class="card"><h2 style="margin-top:0">Test the authority check</h2><p class="muted">These deliberately try things that must be refused.</p>
  <div class="row"><button class="btn ghost" data-case="ceo_captures_wish">CEO Agent tries to capture a wish</button>
  <button class="btn ghost" data-case="architect_amends_constitution">Chief Architect tries to amend the Constitution</button>
  <button class="btn ghost" data-case="architect_approves_governance_doc">Chief Architect tries to approve a governance doc</button></div><div id="atres"></div></div>
  <div class="card"><h2 style="margin-top:0">Studio actions (${a.studio_events.length})</h2><div class="scroll"><table><tr><th>#</th><th>When</th><th>Action</th><th>Subject</th><th>Outcome</th><th>Authorized by / reason</th></tr>
  ${a.studio_events.map(e => `<tr><td>${e.n}</td><td class="small">${esc(e.timestamp)}</td><td>${esc(e.action)}</td><td>${esc(e.subject || "")}</td><td>${e.outcome === "ok" ? badge("ok") + " " + pending() : badge("refused", "refused")}</td><td class="small">${esc(e.kernel ? e.kernel.agent + " — " + e.kernel.authorized_by : e.refusal)}</td></tr>`).join("")}</table></div></div>
  <div class="card"><h2 style="margin-top:0">Kernel audit (${a.kernel_audit.length})</h2><div class="scroll"><table><tr><th>When (UTC)</th><th>Gate</th><th>Outcome</th><th>Detail</th></tr>
  ${a.kernel_audit.map(e => `<tr><td class="small">${esc(e.timestamp)}</td><td>${esc(e.gate)}</td><td>${badge(e.outcome === "ok" ? "ok" : "refused", e.outcome === "ok" ? "pass" : "refused")}</td><td class="small">${esc(e.detail)}</td></tr>`).join("")}</table></div></div>`;
  view().querySelectorAll("[data-case]").forEach(b => b.onclick = async () => {
    try { const r = await api("authority-test", { case: b.dataset.case });
      $("#atres").innerHTML = `<div class="${r.refused ? "pill-note" : "warn"}"><b>${r.refused ? "Refused, as it should be." : "NOT refused — defect"}</b><br>${esc(r.message)}</div>`;
      setTimeout(renderAudit, 1800);
    } catch (e) { refusalToast(e); } });
}

/* ---------------------------------------------------------------- about */
async function renderAbout() {
  const ov = await api("overlay");
  view().innerHTML = `<h1>About HVT Foundry Studio</h1>
  <div class="card"><h2 style="margin-top:0">What this is</h2><p>A tablet app for sitting with a high-street business owner and working through the <b>DOC-0005 High-Street Tablet Design Loop</b>: open a session, check what kind of business it is, see which Foundry engines and outside tools could fit, show the owner in plain words, write down their wishes in their own words, then review those wishes back at base.</p>
  <p>It runs on the Foundry Kernel. Every action is checked by the kernel first and saved as <b>pending human review</b>.</p></div>
  <div class="card"><h2 style="margin-top:0">Rules it follows</h2><ul>
   <li>Nothing is ever deleted. Changes add a new revision.</li><li>Nothing is marked Approved. An owner saying "yes" is their own choice, not a Foundry approval.</li>
   <li>Only data from the HVT Foundry record is shown. Vendor facts carry the 25 Sept 2026 fact-check (DR-2026-09-25-04); anything unverified is labelled.</li>
   <li>No new Engines. Stock and review gaps follow DR-2026-09-04-10 (Approved): no Foundry engine; use DOC-0006 / DOC-0007 paths.</li>
   <li>Customer data stays the customer's (Article VIII).</li></ul>
   ${STATE.banners.map(b => `<div class="warn">${esc(b)}</div>`).join("")}
   <p class="small muted">Saving to: ${esc(STATE.state_file)}</p></div>
  <div class="card"><details><summary>BUT-0001 capability overlay (HVT-0006-OVL-0001, Draft, pending Raj)</summary>${md(ov.markdown)}</details></div>`;
}

route();
