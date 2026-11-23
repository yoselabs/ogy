// The panel: what the selected entry is, what it connects to, and for a decision what it impacts and where.
(() => {
  const { by, name, esc, decision, route, place, kids, human } = B;
  const item = (a, extra) => { const e = by.get(a); return `<li><div class="it" data-pick="${esc(a)}"><span class="k">${e ? e.k : ""}</span><span><b>${esc(name(a))}</b>`
    + `<div class="w">${esc(place(a))}${B.parent(a) ? " › " + esc(route(a).slice(0, -1).join(" › ")) : ""}</div>${extra || ""}</span></div></li>`; };
  const group = (as, extra) => { // grouped by area, as the owner reads them: where in the system
    const by2 = new Map(); as.forEach((a) => { const p = place(a); (by2.get(p) || by2.set(p, []).get(p)).push(a); });
    return [...by2].map(([p, l]) => `<h4>${esc(p)}</h4><ul>${l.map((a) => item(a, extra?.(a))).join("")}</ul>`).join("");
  };
  const setLine = (o, sets) => Object.entries(sets || {}).map(([a, v]) => v == null ? `removes ${esc(name(a))}` : `sets ${esc(name(a))}${v && typeof v === "object" ? " " + esc(Object.entries(v).map(([k, x]) => `${k} ${x}`).join(", ")) : ""}`).join("; ");

  B.panel = (a, imp, rel) => {
    const e = by.get(a), f = e.f, p = document.getElementById("panel");
    let html = `<button class="close" id="closep" aria-label="Close">Close</button><div class="kw" style="text-align:left">${e.k} · ${esc(place(a))}</div><h3>${esc(name(a))}</h3>`;
    if (route(a).length > 1) html += `<div class="w" style="color:var(--mute)">${esc(route(a).join(" › "))}</div>`;
    if (f.says) html += `<p>${esc(f.says)}</p>`;
    if (e.k === "decision") {
      const d = decision(a), opts = kids(a, ["option"]), prop = kids(a, ["proposal"])[0];
      html += `<div class="q">${esc(f.question)}</div>`;
      if (f.context) html += `<div class="note2">${esc(f.context)}</div>`;
      html += `<div>${d.status === "waiting" ? '<span class="stat waiting">waiting for the owner</span>' : '<span class="stat">answered</span>'}${d.delegated ? ' <span class="stat deleg">delegated</span>' : ""}</div>`;
      html += "<h4>Options</h4>" + (opts.length ? opts.map((o) => `<div class="opt ${o.a === d.chose ? "chosen" : ""}"><b>${o.a === d.chose ? "✓ " : ""}${esc(name(o))}</b><div class="w" style="color:var(--mute)">${setLine(o, o.f.sets)}</div></div>`).join("")
        : `<div class="note2">No options yet.${prop ? " Proposal: " + esc(prop.f.why || "") : ""}</div>`);
      const ans = (f.answers || [])[0]; if (ans) html += `<div class="note2">Answered: “${esc(ans.said)}” (${esc(ans.at.slice(0, 10))})${ans.delegated ? ", under a delegation" : ""}</div>`;
      if (prop && opts.length) html += `<div class="note2">Proposal: ${esc(prop.f.why)}</div>`;
      html += `<h4>Impacts ${imp.count} ${imp.count === 1 ? "entry" : "entries"}</h4>`;
      if (imp.sets.length) html += `<div class="note2">Sets ${imp.sets.map((s) => esc(name(s))).join(", ")}.</div>`;
      html += imp.derived ? `<div class="note2">${imp.count ? "ogy impact lists nothing for these options yet; these are the entries that link to what they set." : "Nothing links to what these options set yet."}</div>`
        : `<div class="note2">From ogy impact: the same for every option.</div>`;
      html += group(imp.reach);
    } else {
      const fe = Object.entries(f).filter(([k, v]) => k !== "says" && v !== null && typeof v !== "object");
      if (fe.length) html += `<h4>Fields</h4><ul>${fe.map(([k, v]) => `<li><span class="w" style="color:var(--mute)">${esc(k)}</span> ${esc(v)}</li>`).join("")}</ul>`;
      const groups = new Map(); for (const [x, fs] of rel) { const k = [...fs].join(", "); (groups.get(k) || groups.set(k, []).get(k)).push(x); }
      for (const [k, l] of groups) html += `<h4>${esc(k)}</h4><ul>${l.map((x) => item(x)).join("")}</ul>`;
      if (!groups.size) html += '<div class="note2">Nothing links to or from this entry.</div>';
    }
    p.innerHTML = html;
    p.querySelectorAll("[data-pick]").forEach((n) => n.addEventListener("click", () => B.select(n.dataset.pick, true)));
    p.querySelector("#closep").onclick = () => B.select(null);
  };
})();
