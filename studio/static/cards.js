/* HVT Foundry Studio v0.3 — Card apps: pick a card, see the 4-star preview, switch modules, build and export. */
"use strict";
const CA = { card: "", preset: "", choices: {}, detail: null, preview: "", built: null, device: "phone" };
const MS_TXT = { "working": "working", "needs-key": "needs key", "code-ready-needs-key": "code ready, needs key", "link-only": "link only", "unverified": "unverified" };
const msBadge = s => `<span class="badge ms-${esc(s)}">${esc(MS_TXT[s] || s)}</span>`;

window.renderCards = async function () {
  const list = await api("cards");
  if (!CA.card && list.length) CA.card = list[0].card_id;
  if (!CA.detail || CA.detail.card.card_id !== CA.card) {
    CA.detail = await api("cards/" + encodeURIComponent(CA.card));
    CA.preset = CA.detail.card.presets[0].id; CA.choices = {}; CA.preview = "";
  }
  const D = CA.detail, card = D.card;
  const on = id => { const m = D.modules.find(x => x.id === id); if (m.locked) return true; if (id in CA.choices) return CA.choices[id]; return m.default_on; };
  const replaced = new Set(D.modules.filter(m => on(m.id) && m.replaces).map(m => m.replaces));
  const counts = {}; D.modules.forEach(m => { if (on(m.id) && !replaced.has(m.id)) counts[m.status] = (counts[m.status] || 0) + 1; });
  const [apps, sessions] = await Promise.all([api("card-apps"), api("sessions")]);
  const pre = card.presets.find(p => p.id === CA.preset);
  const modRow = m => `<div class="cmod ${on(m.id) && !replaced.has(m.id) ? "on" : ""}"><label class="tog"><input type="checkbox" data-mod="${esc(m.id)}" ${on(m.id) ? "checked" : ""} ${m.locked ? "disabled" : ""}><span></span></label>
    <div><div class="row" style="gap:6px"><b>${esc(m.name)}</b> ${msBadge(m.status)} ${replaced.has(m.id) ? badge("replaced by automated booking", "partly") : ""}</div>
    <div class="small muted">${esc(m.description)}</div>
    ${(m.parts || []).length ? `<div class="small">${m.parts.map(p => `${esc(p[0])} ${msBadge(p[1])}`).join(" · ")}</div>` : ""}
    <div class="small cost">${m.cost_notes.map(c => `${c.connector ? `<b>${esc(c.connector)}:</b> ` : ""}${esc(c.text)}${c.checked ? ` <i>(checked ${esc(c.checked)}${c.url ? ` · <a href="${esc(c.url)}" target="_blank" rel="noopener">source</a>` : ""})</i>` : ""}`).join("<br>")}</div></div></div>`;
  view().innerHTML = `<div class="sess-row"><div><h1>Card apps</h1>
    <p class="lead">Each BusinessType card is a complete app template: a strong <b>4-star base</b> out of the box, plus every optional module a shop can switch on. Pick the look, switch modules, then build the shop's own app and export it as a zip they own.</p></div>
    <div class="row">${list.map(c => `<button class="chip ${c.card_id === CA.card ? "on" : ""}" data-card="${esc(c.card_id)}">${esc(c.title)} · ${esc(c.business_type_id)}</button>`).join("")}</div></div>
  <div class="warn">${esc(card.title)} card v${esc(card.version)} — <b>${esc(card.status)}</b> (${esc(card.authority)}). ${esc(card.record_note)}</div>
  <div class="grid cardsgrid">
    <div>
      <div class="card"><h2 style="margin-top:0">1 · Look</h2><div class="presets">${card.presets.map(p => `<button class="presetb ${p.id === CA.preset ? "on" : ""}" data-preset="${esc(p.id)}"><span class="sw4">${["primary", "accent", "bg", "text"].map(k => `<i style="background:${p.colours[k]}"></i>`).join("")}</span><b>${esc(p.label)}</b><span class="small muted">${esc(p.description)}</span></button>`).join("")}</div>
        <p class="small muted">The owner can change every colour in their admin page afterwards.</p></div>
      <div class="card"><h2 style="margin-top:0">2 · Modules</h2>
        <p class="small">Switched on now: ${Object.entries(counts).map(([k, v]) => `${msBadge(k)} ×${v}`).join(" ")}</p>
        <h3>4-star base (on out of the box)</h3>${D.modules.filter(m => m.tier === "base").map(modRow).join("")}
        <h3>Optional modules</h3>${D.modules.filter(m => m.tier === "optional").map(modRow).join("")}</div>
    </div>
    <div>
      <div class="card sticky"><div class="row" style="justify-content:space-between"><h2 style="margin:0">4-star preview</h2>
        <div class="row"><button class="chip ${CA.device === "phone" ? "on" : ""}" data-dev="phone">📱 Phone</button><button class="chip ${CA.device === "tablet" ? "on" : ""}" data-dev="tablet">📟 Tablet</button></div></div>
        <p class="small muted">${esc(pre.label)} with invented <b>(demo)</b> content. Booking, queue and stamp checks run live in the shop's own app once started.</p>
        <div class="devwrap"><div class="device ${CA.device}">${CA.preview ? `<iframe src="${esc(CA.preview)}" title="Preview"></iframe>` : `<div class="empty">Press <b>Show preview</b>.</div>`}</div></div>
        <div class="row" style="margin-top:10px"><button class="btn amber" id="cprev">👁 Show preview</button>${CA.preview ? `<a class="btn ghost small" href="${esc(CA.preview)}" target="_blank">Open in new tab ↗</a>` : ""}</div></div>
      <div class="card"><h2 style="margin-top:0">3 · Build the shop's own app</h2>
        <div class="grid g2"><div><label for="cb_name">Shop name</label><input type="text" id="cb_name" placeholder="e.g. the salon's trading name"></div>
          <div><label for="cb_sess">Link to a session (optional)</label><select id="cb_sess"><option value="">— none —</option>${sessions.map(s => `<option value="${esc(s.id)}">${esc(s.id)} · ${esc(s.business_name || "")}</option>`).join("")}</select></div>
          <div><label for="cb_phone">Phone</label><input type="text" id="cb_phone"></div><div><label for="cb_wa">WhatsApp</label><input type="text" id="cb_wa"></div>
          <div><label for="cb_addr">Address</label><input type="text" id="cb_addr"></div><div><label for="cb_pc">Postcode</label><input type="text" id="cb_pc" autocapitalize="characters"></div>
          <div><label for="cb_langs">Languages (codes, up to 4)</label><input type="text" id="cb_langs" value="en"></div>
          <div><label for="cb_pw">Owner password for their admin page</label><input type="text" id="cb_pw" placeholder="6+ characters, owner chooses"></div></div>
        <label>Colours (start from the preset)</label><div class="row">${["primary", "accent", "bg", "text"].map(k => `<label class="small" style="margin:0">${k}<br><input type="color" data-col="${k}" value="${pre.colours[k]}"></label>`).join("")}</div>
        <p class="small muted">Services, team, photos, prices and hours are added by the owner (or with them) in the app's admin page — nothing is invented for a real shop.</p>
        <div class="row"><button class="btn green" id="cbuild">🛠 Build app</button></div><div id="cbres">${CA.built ? builtHTML(CA.built) : ""}</div></div>
      <div class="card"><h2 style="margin-top:0">Built card apps</h2>${apps.length ? `<table class="tbl"><tr><th>ID</th><th>Shop</th><th>Look</th><th>Modules on</th><th></th></tr>${apps.map(a => `<tr><td>${esc(a.id)}</td><td>${esc(a.shop_name)}</td><td>${esc(a.preset)}</td><td>${Object.values(a.modules).filter(Boolean).length}</td><td class="row"><a class="small" href="${esc(a.preview_url)}" target="_blank">preview ↗</a><button class="btn small ghost" data-exp="${esc(a.id)}">⬇ zip</button></td></tr>`).join("")}</table>` : `<p class="muted">None yet.</p>`}</div>
    </div></div>`;
  document.querySelectorAll("[data-card]").forEach(b => b.onclick = () => { CA.card = b.dataset.card; CA.detail = null; renderCards(); });
  document.querySelectorAll("[data-preset]").forEach(b => b.onclick = () => { CA.preset = b.dataset.preset; CA.preview = ""; renderCards(); });
  document.querySelectorAll("[data-dev]").forEach(b => b.onclick = () => { CA.device = b.dataset.dev; renderCards(); });
  document.querySelectorAll("[data-mod]").forEach(i => i.onchange = () => { CA.choices[i.dataset.mod] = i.checked; renderCards(); });
  $("#cprev").onclick = () => act(() => api(`cards/${encodeURIComponent(CA.card)}/preview`, { preset: CA.preset, modules: CA.choices }), "Preview built", r => { CA.preview = r.result.preview_url + "?t=" + Date.now(); renderCards(); });
  $("#cbuild").onclick = () => {
    const colours = {}; document.querySelectorAll("[data-col]").forEach(i => colours[i.dataset.col] = i.value);
    const shop = { name: $("#cb_name").value, phone: $("#cb_phone").value, whatsapp: $("#cb_wa").value, address: $("#cb_addr").value, postcode: $("#cb_pc").value,
      languages: $("#cb_langs").value.split(",").map(x => x.trim()).filter(Boolean), preset: CA.preset, colours, modules: CA.choices, hours: [] };
    act(() => api(`cards/${encodeURIComponent(CA.card)}/build`, { shop, password: $("#cb_pw").value, session_id: $("#cb_sess").value }), "Shop app built", r => { CA.built = r.result; renderCards(); });
  };
  document.querySelectorAll("[data-exp]").forEach(b => b.onclick = () => act(() => api(`card-apps/${encodeURIComponent(b.dataset.exp)}/export`, {}), "Zip ready", r => { location.href = r.result.download_url; }));
};
function builtHTML(b) {
  return `<div class="ok" style="margin-top:12px"><b>${esc(b.shop_name)}</b> built (${esc(b.id)}). <a href="${esc(b.preview_url)}" target="_blank">Open preview ↗</a> · status ${badge("pending human review", "pending")}
    <div class="small">${esc(b.ownership)}</div><div class="row" style="margin-top:8px"><button class="btn small" data-exp="${esc(b.id)}">⬇ Export zip for the shop</button></div></div>`;
}
