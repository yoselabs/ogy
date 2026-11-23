// Card renderers. A card is named by its title, else its key humanized; kind is a small word in the corner.
(() => {
  const { h, esc, by, name, human, key, out, inc, kids, decision } = B;
  const go = (a, label) => `<span class="chip go" data-go="${esc(a)}">${esc(label ?? name(a))}</span>`;
  const mark = (e) => (e.ag ? '<span class="ag" title="agreed"></span>' : "");
  const card = (e, cls, inner) => h("div", `card ${cls || ""}`, inner, { "data-a": e.a, "data-k": e.k });
  const head = (e, ic) => `<div class="hd"><span class="ic">${ic || ""}</span><b>${mark(e)}${esc(name(e))}</b><span class="kw">${e.k}</span></div>`;
  const says = (e) => (e.f.says ? `<div class="says">${esc(e.f.says)}</div>` : "");
  const tgt = (e, f) => (out.get(e.a) || []).filter((r) => r.f === f).map((r) => r.t);
  const list = (label, as) => (as.length ? `<div class="says">${label} ${as.map((a) => go(a)).join("")}</div>` : "");

  const C = {};
  C.note = (e) => card(e, `note ${e.k}`, head(e) + says(e) + list("for", tgt(e, "for")).replace(/class="says"/, 'class="says"')
    + list("realizes", tgt(e, "realizes")));
  C.rule = (e) => card(e, "rule", head(e, "§") + says(e) + list("constrains", tgt(e, "constrains")));
  C.principle = (e) => card(e, "rule", head(e, "§") + says(e) + `<div class="says">because ${esc(e.f.why || "")}</div>`);
  C.actor = (e) => card(e, "actor", head(e, e.f.nature === "human" ? "☺" : e.f.nature === "ai" ? "✦" : "⚙") + `<div class="says">${esc(e.f.says)}</div><span class="chip">${e.f.nature}</span>`);
  C.quantity = (e) => card(e, "quantity", head(e, "#") + `<div class="says">${esc(e.f.says || "")}</div><b>${esc(e.f.is)} ${esc(e.f.unit || "")}</b>`);
  C.enum = (e) => card(e, "enum", head(e, "≡") + says(e) + (e.f.members || []).map((m) => `<span class="chip mono">${esc(m)}</span>`).join(""));
  C.term = (e) => card(e, "term", head(e, "“") + `<div class="says">${esc(e.f.says || "")}</div>${list("names", tgt(e, "names"))}`
    + (e.f.avoid ? `<div class="says">avoid: ${e.f.avoid.map(esc).join(", ")}</div>` : ""));
  C.area = (e) => null;
  C.entity = (e) => {
    const attrs = kids(e.a, ["attribute"]).map((a) => `<div class="attr"><span>${esc(name(a))}</span><i>${esc(a.f.of ? name(a.f.of) : a.f.type || "")}${a.f.many ? " ×n" : ""}${a.f.optional ? " ?" : ""}</i></div>`).join("");
    const states = kids(e.a, ["state"]), trs = kids(e.a, ["transition"]);
    const st = states.length ? `<div class="st">${states.map((s) => `<span class="pill" data-a="${esc(s.a)}">${esc(name(s))}</span>`).join('<span class="tr">›</span>')}</div>` : "";
    const tr = trs.map((t) => `<div class="tr" data-a="${esc(t.a)}">${esc(name(t))}: ${t.f.from ? esc([].concat(t.f.from).map((f) => human(f)).join(", ")) : "(new)"} → ${esc(human(t.f.to))}</div>`).join("");
    return card(e, "entity", head(e, "▦") + says(e) + attrs + st + tr);
  };
  C.decision = (e) => {
    const d = decision(e.a), f = e.f, opts = kids(e.a, ["option"]), prop = kids(e.a, ["proposal"])[0];
    const status = d?.status || "waiting", chose = d?.chose;
    const stat = status === "waiting" ? '<span class="stat waiting">waiting</span>' : d.delegated ? '<span class="stat deleg">answered · delegated</span>' : '<span class="stat">answered</span>';
    const os = opts.map((o) => `<div class="opt ${o.a === chose ? "chosen" : ""}" data-a="${esc(o.a)}">${o.a === chose ? "✓" : "○"} ${esc(name(o))}</div>`).join("");
    const pr = !opts.length && prop?.f.sets ? `<div class="says">proposal sets ${Object.keys(prop.f.sets).map((a) => go(a)).join("")}</div>` : "";
    const c = card(e, `dec ${status}`, `<div class="hd"><span class="ic">◇</span><b>${esc(name(e))}</b><span class="kw">decision</span></div>`
      + `<div class="says">${esc(f.question || "")}</div><div style="margin-top:4px">${stat}</div>${os}${pr}`);
    return c;
  };
  C.screen = (e, nested) => {
    const f = e.f, inc2 = tgt(e, "includes").map((a) => by.get(a)).filter(Boolean);
    const offers = tgt(e, "offers").map((a) => `<span class="btn" data-go="${esc(a)}">${esc(name(a))}</span>`).join("");
    const body = says(e) + `<div>${f.form ? `<span class="chip">${esc(f.form)}</span>` : ""}</div>`
      + (f.invoked_as ? `<div class="cli">$ ${esc(f.invoked_as)}</div>` : "")
      + list("shows", tgt(e, "shows")) + list("accepts", tgt(e, "accepts")) + list("allows", tgt(e, "allows")) + list("serves", tgt(e, "serves")) + (offers ? `<div>${offers}</div>` : "");
    const el = h("div", `card screen${nested ? " nested" : ""}`, `<div class="bar"><i></i><i></i><i></i><b>${esc(name(e))}</b><span class="kw">interface</span></div><div class="body">${body}</div>`, { "data-a": e.a, "data-k": "interface" });
    for (const i of inc2) el.querySelector(".body").append(C.screen(i, true));
    return el;
  };
  C.handler = (e) => card(e, "handler", head(e, "⚙") + says(e) + list("performs", tgt(e, "performs")) + list("uses", tgt(e, "uses")));
  C.dependency = (e) => card(e, "handler", head(e, "⛓") + says(e) + (e.f.pin ? `<span class="chip mono">${esc(e.f.pin)}</span>` : "")
    + list("realizes", tgt(e, "realizes")) + kids(e.a, ["workaround"]).map((w) => `<div class="says" data-a="${esc(w.a)}">workaround · when ${esc(w.f.when?.text || "")}: ${esc(w.f.says)}</div>`).join(""));
  C.swrule = (e) => card(e, "rule sw-rule", head(e, "§") + says(e));
  B.cards = C;
  B.go = go;
})();
