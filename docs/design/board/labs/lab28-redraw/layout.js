// Places every region, card and frame on the world, then draws the links between Product and Software.
(() => {
  const { h, esc, by, name, data, parent, out, inc, key, waiting, human } = B;
  const C = B.cards, world = document.getElementById("world");
  const at = (el, x, y, w) => { el.style.left = x + "px"; el.style.top = y + "px"; if (w) el.style.width = w + "px"; world.append(el); return el; };
  const group = (x, y, w, label, cls, items) => {
    const g = h("div", "grp " + (cls || ""), ""); g.style.width = w + "px";
    items.filter(Boolean).forEach((i) => g.append(i));
    if (label) at(h("div", "gl", label), x, y - 20);
    return at(g, x, y);
  };
  const entries = (k, ly, ar) => data.entries.filter((e) => e.k === k && e.ly === ly && e.ar === ar && !parent(e.a));
  const region = (id, cls, layer, title, says, x, y, w, hgt) => {
    const r = h("div", "region " + cls, `<div class="rhead"><div class="layer">${layer}</div><h2>${esc(title)}</h2><p>${esc(says)}</p><div class="rsum"></div></div>`, { "data-region": id });
    r.style.height = hgt + "px"; at(r, x, y, w); return r;
  };
  const worldRect = (el) => { let x = 0, y = 0; for (let n = el; n && n !== world; n = n.offsetParent) { x += n.offsetLeft; y += n.offsetTop; } return { x, y, w: el.offsetWidth, h: el.offsetHeight }; };
  B.worldRect = worldRect;

  // Geometry must not change with the zoom level: a card is as tall as the taller of its detail and its (larger-type) workflow-level look.
  const probe = (els, lod, inv) => { const l0 = world.dataset.lod, i0 = world.style.getPropertyValue("--inv"); if (lod) { world.dataset.lod = lod; world.style.setProperty("--inv", inv); }
    const r = els.map((e) => e.offsetHeight); if (lod) { l0 ? (world.dataset.lod = l0) : delete world.dataset.lod; world.style.setProperty("--inv", i0 || "1"); } return r; };
  const fix = (els) => { const a = probe(els), b = probe(els, "flows", "3"); els.forEach((e, i) => { if (b[i] > a[i]) e.style.minHeight = b[i] + "px"; }); };
  const fixIn = (g) => fix([...g.querySelectorAll(".card, .end")]);

  B.build = () => {
    const rects = {}, regionEls = {};
    const area = (ly, ar) => by.get(`${ly}/${ar}/area/${ar}`);
    const PLx = 760, x0 = PLx + 40;
    // ---- Product lending, context band
    const pl = (k) => entries(k, "product", "lending");
    const A = 170;
    const decs = pl("decision").sort((p, q) => (B.decision(q.a)?.status === "waiting") - (B.decision(p.a)?.status === "waiting")).map(C.decision);
    decs.forEach((c) => (c.style.width = "260px"));
    const g5 = group(x0, A, 1090, "Decisions, waiting first", "wrap", decs);
    const g1 = group(x0 + 1130, A, 300, "Goal and capability", "", [...pl("goal"), ...pl("capability")].map(C.note));
    const g2 = group(x0 + 1470, A, 780, "Rules", "grid", pl("rule").map(C.rule));
    const ent = [...pl("entity"), ...pl("enum")].map((e) => (e.k === "enum" ? C.enum(e) : C.entity(e)));
    const g3 = group(x0 + 2290, A, 800, "Entities", "wrap", ent); ent.forEach((c, i) => (c.style.width = i === 0 ? "300px" : "250px"));
    [g5, g1, g2, g3].forEach(fixIn);
    const row2 = Math.max(...[g5, g1, g2, g3].map((g) => g.offsetTop + g.offsetHeight)) + 50;
    const act = pl("actor").map(C.actor); act.forEach((c) => (c.style.width = "250px"));
    const g4 = group(x0, row2, 3060, "Actors and settings", "wrap", [...act, ...pl("quantity").map(C.quantity)]);
    g4.querySelectorAll(".quantity").forEach((c) => (c.style.width = "250px"));
    fixIn(g4);
    const bandBottom = Math.max(...[g1, g2, g3, g4, g5].map((g) => g.offsetTop + g.offsetHeight));
    // ---- workflows
    const fy = bandBottom + 90; let fx = x0; const frames = [];
    for (const wf of pl("workflow").sort((a, b) => (a.a.endsWith("borrow") ? -1 : 0) - (b.a.endsWith("borrow") ? -1 : 0))) {
      const f = B.workflow(wf); at(f.el, fx, fy); fixIn(f.el); let H = f.finish();
      frameSummary(wf, f); H = Math.max(H, areaNeed(f.el)); f.el.style.height = H + "px";
      frames.push({ wf, f, x: fx, y: fy, H, W: f.width }); fx += f.width + 50;
    }
    const PW = fx - 50 + 40 - PLx, fBottom = fy + Math.max(...frames.map((f) => f.H));
    const PLh = fBottom + 40;
    rects["product/lending"] = { x: PLx, y: 0, w: PW, h: PLh };
    regionEls["product/lending"] = region("product/lending", "p", "Product", "Lending", area("product", "lending").f.says, PLx, 0, PW, PLh);
    // ---- Software lending
    const SWy = PLh + 420, borrow = frames.find((f) => f.wf.a.endsWith("borrow")), rest = frames.filter((f) => f !== borrow);
    const sw = (k) => entries(k, "software", "lending");
    const ifs = sw("interface").filter((e) => !(B.inc.get(e.a) || []).some((r) => r.f === "includes"));
    const sA = SWy + 170;
    const gi = group(borrow.x, sA, borrow.W, "Interfaces", "wrap", ifs.map((e) => C.screen(e)));
    gi.style.gap = "30px"; gi.children.length && [...gi.children].forEach((c, i) => (c.style.width = i === 0 ? "340px" : "300px"));
    const lend = group(borrow.x, sA + gi.offsetHeight + 50, 320, "Handlers", "wrap", [sw("handler").find((e) => e.a.endsWith("lend"))].map(C.handler));
    const rx = rest[0].x, rw = fx - 50 - rx;
    const sgrp = group(rx, sA, rw, "Handlers, dependency and rule", "wrap", [
      C.handler(sw("handler").find((e) => e.a.endsWith("send-reminder"))), ...sw("dependency").map(C.dependency), ...sw("rule").map(C.swrule), ...sw("decision").map(C.decision)]);
    [...sgrp.children].forEach((c) => (c.style.width = "290px")); sgrp.style.gap = "20px";
    [gi, lend, sgrp].forEach(fixIn);
    const SWb = Math.max(...[gi, lend, sgrp].map((g) => g.offsetTop + g.offsetHeight)) + 40, SWh = SWb - SWy;
    rects["software/lending"] = { x: PLx, y: SWy, w: PW, h: SWh };
    regionEls["software/lending"] = region("software/lending", "s", "Software", "Lending", area("software", "lending").f.says, PLx, SWy, PW, SWh);
    // ---- Constitution and shared, to the left
    const cons = data.entries.filter((e) => e.k === "principle");
    group(40, 170, 380, "Principles", "", cons.map(C.principle));
    rects["constitution"] = { x: 0, y: 0, w: 460, h: 360 };
    regionEls.constitution = region("constitution", "x", "Constitution", "Principles", "What every decision is judged against.", 0, 0, 460, 360);
    const terms = group(40, 590, 380, "Terms", "", entries("term", "product", "shared").map(C.term));
    rects["product/shared"] = { x: 0, y: 420, w: 460, h: Math.max(380, terms.offsetTop + terms.offsetHeight - 420 + 40) };
    regionEls["product/shared"] = region("product/shared", "p", "Product", "Shared", area("product", "shared").f.says, 0, 420, 460, rects["product/shared"].h);
    for (const id in regionEls) world.insertBefore(regionEls[id], world.firstChild);
    summaries(regionEls);
    // ---- element map and links
    const els = new Map();
    world.querySelectorAll("[data-a]").forEach((el) => { if (!els.has(el.dataset.a)) els.set(el.dataset.a, el); });
    B.els = els; B.rects = rects; B.frames = frames;
    B.elFor = (a) => { for (let p = a; p; p = parent(p)) if (els.has(p)) return els.get(p); return null; };
    crossLinks(); bundles();
    const all = Object.values(rects);
    B.bounds = { x: 0, y: 0, w: Math.max(...all.map((r) => r.x + r.w)), h: Math.max(...all.map((r) => r.y + r.h)) };
    return B.bounds;
  };

  const areaNeed = (frame) => { const l0 = world.dataset.lod, i0 = world.style.getPropertyValue("--inv"); world.dataset.lod = "areas"; world.style.setProperty("--inv", "3");
    const s = frame.querySelector(".fsum"); const n = s ? s.offsetTop + s.offsetHeight + 24 : 0; l0 ? (world.dataset.lod = l0) : delete world.dataset.lod; world.style.setProperty("--inv", i0 || "1"); return n; };
  function summaries(regionEls) {
    for (const id in regionEls) {
      const [ly, ar] = id.split("/"); const rs = regionEls[id].querySelector(".rsum");
      const list = id === "constitution" ? data.entries.filter((e) => !e.ly) : data.entries.filter((e) => e.ly === ly && e.ar === ar && !parent(e.a));
      const n = {}; list.forEach((e) => { if (e.k !== "area") n[e.k] = (n[e.k] || 0) + 1; });
            rs.innerHTML = list.filter((e) => e.k === "goal" || e.k === "capability").map((e) => `<span class="n ${e.k}">${e.k === "goal" ? "Goal" : "Capability"}: ${esc(B.name(e))}</span>`).join("") + Object.entries(n).map(([k, c]) => `<span>${c} ${c > 1 ? (k.endsWith("y") ? k.slice(0, -1) + "ies" : k + "s") : k}</span>`).join("") + list.filter((e) => e.k === "decision" && B.decision(e.a)?.status === "waiting").map((e) => `<span class="w">Waiting: ${esc(B.name(e))}</span>`).join("");
    }
  }

  function frameSummary(wf, f) {
    {
      const steps = B.kids(wf.a, ["step"]), ends = B.kids(wf.a, ["end"]);
      const ifs = new Set(), hs = new Set(), under = (a) => a === wf.a || a.startsWith(wf.a + "/");
      for (const r of data.relations) { if (!under(r.t)) continue; if (r.f === "serves") ifs.add(r.o); if (r.f === "performs") hs.add(r.o); }
      const flow = steps.sort((a, b) => f.steps.get(a.a).offsetLeft - f.steps.get(b.a).offsetLeft).map((s) => esc(name(s))).join(" › ");
      const chip = (n, w, c) => (n ? `<span class="fchip ${c || ""}">${n} ${n > 1 ? w + "s" : w}</span>` : "");
      f.el.insertAdjacentHTML("beforeend", `<div class="fsum"><div class="fsays">${esc(wf.f.says)}</div><div class="flow">${flow}</div><div>${chip(steps.length, "step")}${chip(ends.length, "end")}</div>`
        + `<div>${chip(ifs.size, "interface", "sw")}${ifs.size ? '<span class="fl">serve it</span>' : ""} ${chip(hs.size, "handler", "sw")}${hs.size ? '<span class="fl">perform it</span>' : ""}</div></div>`);
    }
  }
  function crossLinks() {
    const svg = document.getElementById("links"); let html = "", lbl = "";
    const seen = new Set();
    for (const r of data.relations) {
      if (r.f !== "serves" && r.f !== "performs") continue;
      const own = B.elFor(r.o);
      let t = r.t; while (t && by.get(t)?.k !== "step") t = parent(t);
      const te = t && B.els.get(t); if (!own || !te) continue;
      const id = r.o + ">" + t + r.f; if (seen.has(id)) continue; seen.add(id);
      const a = worldRect(own), b = worldRect(te), n = seen.size;
      const x1 = a.x + a.w / 2, y1 = a.y, x2 = b.x + 40 + ((n * 53) % (b.w - 80)), y2 = b.y + b.h + 8; // end just below the step box
      const my = (y1 + y2) / 2;
      html += `<path class="x" d="M${x1},${y1} C${x1},${y1 - 120} ${x2},${y2 + 160} ${x2},${y2}" marker-end="url(#ah-x)"/>`;
      const u = 0.3, bx = (1 - u) ** 3 * x1 + 3 * (1 - u) ** 2 * u * x1 + 3 * (1 - u) * u * u * x2 + u ** 3 * x2, by2 = (1 - u) ** 3 * y1 + 3 * (1 - u) ** 2 * u * (y1 - 120) + 3 * (1 - u) * u * u * (y2 + 160) + u ** 3 * y2;
      lbl += `<div class="lk" style="left:${bx}px;top:${by2}px">${r.f}</div>`;
    }
    svg.innerHTML = `<defs><marker id="ah-x" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="ah x" d="M0,0L10,5L0,10z"/></marker></defs>` + html;
    world.insertAdjacentHTML("beforeend", lbl);
    // a call: arrow from the call chip to the called workflow
    const cs = document.getElementById("links");
    for (const r of data.relations.filter((r) => r.f === "calls")) {
      const own = B.els.get(r.o), tgt = B.els.get(r.t); if (!own || !tgt) continue;
      const a = worldRect(own), b = worldRect(tgt);
      cs.insertAdjacentHTML("beforeend", `<path class="e call" d="M${a.x + a.w / 2},${a.y + a.h} L${b.x + b.w / 2},${b.y}" marker-end="url(#ah-call)"/>`);
    }
  }

  function bundles() {
    const svg = document.getElementById("bundles"), pairs = new Map();
    const reg = (a) => { const e = by.get(a); return e ? (e.ly ? `${e.ly}/${e.ar}` : "constitution") : null; };
    for (const r of data.relations) {
      const a = reg(r.o), b = reg(r.t); if (!a || !b || a === b) continue;
      const k = [a, b].sort().join("|"); const m = pairs.get(k) || pairs.set(k, { a, b, f: {} }).get(k);
      m.f[r.f] = (m.f[r.f] || 0) + 1;
    }
    let html = "", labels = "";
    for (const { a, b, f } of pairs.values()) {
      const A = B.rects[a], Bt = B.rects[b]; if (!A || !Bt) continue;
      let p1, p2;
      if (Math.abs(A.x - Bt.x) < 5) { const top = A.y < Bt.y ? A : Bt, low = top === A ? Bt : A; p1 = [Math.max(top.x, low.x) + 900, top.y + top.h]; p2 = [p1[0], low.y]; }
      else { const left = A.x < Bt.x ? A : Bt, right = left === A ? Bt : A; const y = Math.max(left.y, right.y) + 130; p1 = [left.x + left.w, y]; p2 = [right.x, y]; }
      const tot = Object.values(f).reduce((s, n) => s + n, 0), words = Object.entries(f).sort((x, y) => y[1] - x[1]).map(([k, n]) => `${k} ${n}`).join(" · ");
      html += `<path class="bundle-line" d="M${p1[0]},${p1[1]} L${p2[0]},${p2[1]}"/>`;
      const title = (id) => (id === "constitution" ? "Constitution" : human(id.split("/")[0]) + " " + id.split("/")[1]);
      labels += `<div class="bundle ${tot > 3 ? "big" : ""}" style="left:${(p1[0] + p2[0]) / 2}px;top:${(p1[1] + p2[1]) / 2}px">${tot > 3 ? `<b>${esc(title(a))} ↔ ${esc(title(b))}</b>` : ""}<small>${esc(words)}</small></div>`;
    }
    svg.innerHTML = html; world.insertAdjacentHTML("beforeend", labels);
  }
})();
