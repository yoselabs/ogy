// A workflow frame as in lab 28: orange header, step boxes in columns, ends on the right, arrows leave the row that causes them.
(() => {
  const { h, esc, by, name, human, key, out, kids, go } = B;
  const SW = 250, GAP = 84, X0 = 24, Y0 = 124;
  const tgt = (a, f) => (out.get(a) || []).filter((r) => r.f === f).map((r) => r.t);
  const val = (a) => { const e = by.get(a); return e ? `${e.f.is ?? ""} ${e.f.unit ?? ""}`.trim() : ""; };

  function effectHTML(fx) {
    const t = fx.on, e = by.get(t), op = fx.do;
    const ic = { create: "+", delete: "−", write: "✎", transition: "⇄", tell: "✉" }[op] || "•";
    let body = go(t);
    if (op === "transition" && e) {
      const owner = by.get(B.parent(t)), to = e.f.to;
      body = `${go(owner.a)}: ${go(t, name(e))} <span class="tr">→</span> <span class="pill">${esc(human(to))}</span>`;
    }
    return `<div class="fx ${op}"><span>${ic}</span><span class="op">${op}</span>${body}</div>`;
  }
  function rowHTML(r, wfAddr) {
    const f = r.f, to = f.then ? `${wfAddr}/${by.has(`${wfAddr}/end/${f.then}`) ? "end" : "step"}/${f.then}` : null;
    const toE = to && by.get(to), res = toE?.k === "end" ? toE.f.result : "";
    let label;
    if (r.k === "choice") label = esc(f.label);
    else if (r.k === "timeout") label = `after ${go(f.after, `${name(f.after)} (${val(f.after)})`)}`;
    else if (f.covers_ends) label = `when ${esc(name(B.parent(f.covers_ends[0])))} ends: ${f.covers_ends.map((a) => esc(name(a))).join(", ")}`;
    else label = f.when ? esc(f.when.text.replace(/^./, (c) => c.toUpperCase())) : "Otherwise";
    const perf = (B.inc.get(r.a) || []).filter((x) => x.f === "performs").map((x) => `<span class="by" data-go="${esc(x.o)}">⚙ performed by ${esc(name(x.o))}</span>`).join("");
    return `<div class="row" data-a="${esc(r.a)}" data-to="${esc(to || "")}" data-res="${res}"><div class="rt"><span class="rl">${label}</span><span class="rk">${r.k}</span>`
      + `<span class="to ${res}">${to ? "→ " + esc(name(toE)) : ""}</span></div>`
      + (r.k === "choice" && f.when ? `<div class="when">when ${esc(f.when.text)}</div>` : "")
      + (f.effects || []).map(effectHTML).join("") + perf + `</div>`;
  }
  function stepEl(s, wf) {
    const f = s.f, calls = f.calls, rows = kids(s.a, ["choice", "case", "timeout"]);
    const who = f.actor ? `<div class="who">${go(f.actor)}</div>` : "";
    const el = h("div", "step card", `<div class="hd"><span class="ic">▢</span><b>${esc(name(s))}</b><span class="kw">step</span></div>`
      + (f.says ? `<div class="says">${esc(f.says)}</div>` : "") + who
      + (calls ? `<div class="sec">Calls</div><span class="callchip" data-go="${esc(calls)}">▷ ${esc(name(calls))}</span><div class="sec">Then, by how it ended</div>` : "")
      + rows.sort((a, b) => (a.f.order ?? 99) - (b.f.order ?? 99)).map((r) => rowHTML(r, wf.a)).join(""), { "data-a": s.a, "data-k": "step" });
    return el;
  }
  function endEl(e) {
    return h("div", `end ${e.f.result}`, `<b>${esc(name(e))}</b><small>${esc(e.f.says || "")}</small>`, { "data-a": e.a, "data-k": "end", "data-res": e.f.result });
  }
  const path = (x1, y1, x2, y2, lane, ox, oy) => {
    if (lane == null) { const d = Math.max(30, (x2 - x1) / 2); return `M${x1},${y1} C${x1 + d},${y1} ${x2 - d},${y2} ${x2},${y2}`; }
    const a = x1 + ox, b = x2 - oy;
    return `M${x1},${y1} L${a - 8},${y1} Q${a},${y1} ${a},${y1 + 8} L${a},${lane - 8} Q${a},${lane} ${a + 8},${lane} L${b - 8},${lane} Q${b},${lane} ${b},${lane - 8} L${b},${y2 + 8} Q${b},${y2} ${b + 8},${y2} L${x2},${y2}`;
  };
  const pos = (el, up) => { let x = 0, y = 0; for (let n = el; n && n !== up; n = n.offsetParent) { x += n.offsetLeft; y += n.offsetTop; } return { x, y }; };

  B.workflow = (wf) => {
    const steps = kids(wf.a, ["step"]), ends = kids(wf.a, ["end"]), sub = new Map();
    const start = wf.f.start;
    // columns by breadth from the start step
    const col = new Map(), stepOf = (k) => steps.find((s) => key(s.a) === k);
    const q = [[start, 0]];
    while (q.length) { const [k, c] = q.shift(); const s = stepOf(k); if (!s || col.has(k)) continue; col.set(k, c);
      for (const r of kids(s.a, ["choice", "case", "timeout"])) if (r.f.then) q.push([r.f.then, c + 1]); }
    steps.forEach((s) => { if (!col.has(key(s.a))) col.set(key(s.a), 0); });
    const maxc = Math.max(...col.values());
    const f = h("div", "frame", "", { "data-a": wf.a, "data-k": "workflow" });
    const trig = [];
    if (wf.f.event) trig.push("starts when " + name(wf.f.event) + " (" + name(B.parent(wf.f.event)) + ")");
    if (wf.f.schedule) trig.push("every " + val(wf.f.schedule));
    if (!trig.length) trig.push("starts at " + name(by.get(`${wf.a}/step/${start}`)));
    f.innerHTML = `<div class="frame-bg"></div><div class="frame-hd"><b>${esc(name(wf))}</b><span class="kw">workflow</span><p>${esc(wf.f.says || "")}</p></div><div class="trigger">${esc(trig.join(" · "))}</div>`
      + `<svg class="links"><defs>${["", "success", "failure", "call"].map((c) => `<marker id="ah-${wf.a.split("/").pop()}-${c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="ah ${c}" d="M0,0L10,5L0,10z"/></marker>`).join("")}</defs></svg>`;
    const width = X0 * 2 + (maxc + 1) * (SW + GAP) + 190;
    const sid = wf.a.split("/").pop();
    const els = [];
    steps.forEach((s) => { const el = stepEl(s, wf); el.style.left = X0 + col.get(key(s.a)) * (SW + GAP) + "px"; el.style.top = Y0 + "px"; f.append(el); sub.set(s.a, el); });
    ends.forEach((e) => { const el = endEl(e); el.style.left = X0 + (maxc + 1) * (SW + GAP) + "px"; f.append(el); sub.set(e.a, el); els.push(el); });
    return { el: f, steps: sub, width, finish() {
      // measure, stack ends, route arrows
      let y = Y0;
      ends.forEach((e) => { const el = sub.get(e.a); el.style.top = y + "px"; y += el.offsetHeight + 22; });
      let bottom = Math.max(y - 22, ...steps.map((s) => Y0 + sub.get(s.a).offsetHeight));
      const edges = [];
      steps.forEach((s) => {
        const sEl = sub.get(s.a); let n = 0;
        sEl.querySelectorAll(".row").forEach((row) => {
          const to = row.dataset.to; if (!to) return; const tEl = sub.get(to); if (!tEl) return;
          const x1 = sEl.offsetLeft + sEl.offsetWidth, y1 = sEl.offsetTop + row.offsetTop + 16;
          const x2 = tEl.offsetLeft, y2 = tEl.offsetTop + Math.min(24, tEl.offsetHeight / 2);
          const adj = x2 - x1 <= GAP + 2 && x2 > x1;
          edges.push({ x1, y1, x2, y2, adj, res: row.dataset.res, n: n++ });
        });
      });
      const longs = edges.filter((e) => !e.adj), lane0 = bottom + 26;
      let k = 0; const svg = f.querySelector("svg"), sidx = sid;
      edges.forEach((e) => {
        const cls = e.res || "";
        const lane = e.adj ? null : lane0 + 12 * k++;
        const d = path(e.x1, e.y1, e.x2, e.y2, lane, 14 + 7 * e.n, 14 + 7 * e.n);
        svg.insertAdjacentHTML("beforeend", `<path class="e ${cls}" d="${d}" marker-end="url(#ah-${sidx}-${cls})"/>`);
      });
      const H = lane0 + 12 * longs.length + 24;
      f.style.width = width + "px"; f.style.height = H + "px";
      return H;
    }, anchors(addr) { const el = sub.get(addr); return el ? { x: el.offsetLeft, y: el.offsetTop, w: el.offsetWidth, h: el.offsetHeight } : null; } };
  };
})();
