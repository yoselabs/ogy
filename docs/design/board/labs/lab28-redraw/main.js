// Camera (pan, zoom, pinch), semantic zoom, selection and the panel.
(() => {
  const { by, name, esc, h, decision, parent, route, place, out, inc, data, human } = B;
  const stage = document.getElementById("stage"), world = document.getElementById("world");
  const cam = { x: 0, y: 0, s: 0.4 }, MIN = 0.12, MAX = 2.5;
  let sel = null;
  const lodOf = (s) => (s < 0.5 ? "areas" : s < 0.95 ? "flows" : "detail");

  function apply(animate) {
    world.classList.toggle("anim", !!animate);
    world.style.transform = `translate(${cam.x}px,${cam.y}px) scale(${cam.s})`;
    world.style.setProperty("--inv", String(1 / cam.s));
    // a selection needs names on the cards it touches, so it never zooms out to the area level
    const lod = sel && cam.s < 0.5 ? "flows" : lodOf(cam.s); world.dataset.lod = lod;
    document.getElementById("zoom").textContent = Math.round(cam.s * 100) + "%";
    document.querySelectorAll("[data-lod-btn]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lodBtn === lod)));
    if (animate) setTimeout(() => world.classList.remove("anim"), 400);
  }
  function zoomAt(cx, cy, k) {
    const s = Math.min(MAX, Math.max(MIN, cam.s * k)), r = s / cam.s;
    cam.x = cx - (cx - cam.x) * r; cam.y = cy - (cy - cam.y) * r; cam.s = s; apply();
  }
  function fitRect(r, pad = 60, max = 1.4, right = 0) {
    const W = stage.clientWidth - right, H = stage.clientHeight;
    const s = Math.min(max, Math.max(MIN, Math.min((W - pad * 2) / r.w, (H - pad * 2) / r.h)));
    cam.s = s; cam.x = (W - r.w * s) / 2 - r.x * s; cam.y = (H - r.h * s) / 2 - r.y * s; apply(true);
  }
  const rectOf = (el) => B.worldRect(el);
  const union = (rs) => { const x = Math.min(...rs.map((r) => r.x)), y = Math.min(...rs.map((r) => r.y)); return { x, y, w: Math.max(...rs.map((r) => r.x + r.w)) - x, h: Math.max(...rs.map((r) => r.y + r.h)) - y }; };

  // ---- pointer: drag pans, wheel zooms, two fingers pinch
  const ptrs = new Map(); let drag = null, pinch = null;
  stage.addEventListener("pointerdown", (e) => {
    if (e.button !== 0 && e.pointerType === "mouse") return;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (ptrs.size === 2) { const [a, b] = [...ptrs.values()]; pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), s: cam.s }; drag = null; }
    else drag = { x: e.clientX, y: e.clientY, cx: cam.x, cy: cam.y, moved: false };
  });
  stage.addEventListener("pointermove", (e) => {
    if (!ptrs.has(e.pointerId)) return;
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pinch && ptrs.size === 2) {
      const [a, b] = [...ptrs.values()], d = Math.hypot(a.x - b.x, a.y - b.y), r = stage.getBoundingClientRect();
      zoomAt((a.x + b.x) / 2 - r.left, (a.y + b.y) / 2 - r.top, (pinch.s * d / pinch.d) / cam.s); return;
    }
    if (!drag) return;
    const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
    if (!drag.moved && Math.hypot(dx, dy) > 4) { drag.moved = true; stage.classList.add("panning"); stage.setPointerCapture(e.pointerId); }
    if (drag.moved) { cam.x = drag.cx + dx; cam.y = drag.cy + dy; apply(); }
  });
  const up = (e) => {
    const was = drag; ptrs.delete(e.pointerId); if (ptrs.size < 2) pinch = null;
    stage.classList.remove("panning"); drag = null;
    if (was && !was.moved && e.type === "pointerup") click(document.elementFromPoint(e.clientX, e.clientY));
  };
  stage.addEventListener("pointerup", up); stage.addEventListener("pointercancel", up);
  stage.addEventListener("wheel", (e) => {
    e.preventDefault(); const r = stage.getBoundingClientRect();
    if (e.shiftKey || e.altKey) { cam.x -= e.deltaY; cam.y -= e.deltaX; apply(); return; }
    zoomAt(e.clientX - r.left, e.clientY - r.top, Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)));
  }, { passive: false });
  addEventListener("keydown", (e) => {
    if (e.target.closest?.("input,textarea")) return;
    const cx = stage.clientWidth / 2, cy = stage.clientHeight / 2;
    if (e.key === "+" || e.key === "=") zoomAt(cx, cy, 1.25); else if (e.key === "-") zoomAt(cx, cy, 0.8);
    else if (e.key === "0") fit(); else if (e.key === "Escape") select(null);
    else if (e.key.startsWith("Arrow")) { const d = { ArrowLeft: [60, 0], ArrowRight: [-60, 0], ArrowUp: [0, 60], ArrowDown: [0, -60] }[e.key]; cam.x += d[0]; cam.y += d[1]; apply(); }
  });

  function click(el) {
    if (!el || !stage.contains(el) && el !== stage) return;
    const g = el.closest("[data-go]"); if (g) return select(g.dataset.go, true);
    const t = el.closest(".row[data-a], .step[data-a], .card[data-a], .end[data-a], .frame[data-a]");
    if (world.dataset.lod === "areas") { // at area level a click opens what you clicked
      const f = el.closest(".frame"), r = el.closest(".region");
      if (f) return fitRect(rectOf(f), 70, 1.2, panelWidth());
      if (r) return fitRect(rectOf(r), 40, 0.5);
    }
    if (!t) return select(null);
    select(t.dataset.a, false);
  }
  const panelWidth = () => (document.getElementById("panel").classList.contains("open") ? 380 : 0);
  const fit = () => { select(null); fitRect(B.bounds, 40, 0.6); };

  // ---- selection
  function impactOf(a) {
    const d = decision(a); if (!d) return null;
    const reach = new Set(); for (const o of Object.values(d.options)) o.reach.forEach((x) => reach.add(x));
    const sets = new Set(); for (const o of Object.values(d.options)) o.sets.forEach((x) => sets.add(x));
    const prop = (B.kids(a, ["proposal"])[0]?.f.sets) || {}; Object.keys(prop).forEach((x) => by.has(x) && sets.add(x));
    let derived = false;
    if (!reach.size) { // no ogy impact data: what links to what the options set
      derived = true;
      for (const s of sets) { for (const r of out.get(s) || []) reach.add(r.t); for (const r of inc.get(s) || []) if (r.o !== a && !r.o.startsWith(a + "/")) reach.add(r.o); }
      reach.delete(a);
    }
    return { reach: [...reach].filter((x) => by.has(x)).sort(), sets: [...sets], derived, count: reach.size };
  }
  function related(a) {
    const map = new Map();
    const add = (x, f) => { if (x && x !== a && by.has(x)) (map.get(x) || map.set(x, new Set()).get(x)).add(f); };
    const prefix = a + "/";
    for (const r of data.relations) {
      if (r.o === a || r.o.startsWith(prefix)) add(r.t, r.f);
      if (r.t === a || r.t.startsWith(prefix)) add(r.o, "← " + r.f);
    }
    return map;
  }
  function select(a, pan) {
    for (const c of ["sel", "rel", "impact", "rowhit", "keep"]) world.querySelectorAll("." + c).forEach((n) => n.classList.remove(c));
    world.querySelectorAll(".tag").forEach((n) => n.remove());
    document.getElementById("overlay").innerHTML = ""; sel = a;
    world.classList.toggle("has-sel", !!a);
    const panel = document.getElementById("panel");
    if (!a) { panel.classList.remove("open"); return; }
    const el = B.elFor(a); if (!el) return;
    const imp = impactOf(a), ids = imp ? imp.reach : [...related(a).keys()], cls = imp ? "impact" : "rel";
    const top = (x) => { const n = B.elFor(x); return n && (n.matches(".row,.opt,.tr,.pill") ? n.closest(".step,.card,.end") : n); };
    const targets = [];
    for (const x of ids) { const n = B.els.get(x) || B.elFor(x); const t = top(x); if (!t) continue;
      t.classList.add(cls); if (n && n.matches(".row")) n.classList.add("rowhit"); if (!targets.includes(t)) targets.push(t); }
    const own = top(a) || el; own.classList.add("sel"); if (el.matches(".row")) el.classList.add("rowhit");
    own.querySelectorAll("[data-a]").forEach((x) => x.classList.add("keep")); own.closest(".frame")?.querySelector(".frame-bg")?.classList.add("keep");
    const names = new Map();
    for (const x of ids) { const t = top(x); if (!t) continue; const e = by.get(x), r = route(x); (names.get(t) || names.set(t, []).get(t)).push(name(x)); }
    targets.forEach((t) => { t.closest(".frame")?.querySelector(".frame-bg")?.classList.add("keep");
      const l = [...new Set(names.get(t) || [])]; t.insertAdjacentHTML("beforeend", `<span class="tag ${cls === "impact" ? "" : "rel"}">${esc(l.slice(0, 1).join("") + (l.length > 1 ? " +" + (l.length - 1) : ""))}</span>`); });
    // lines from the selection to each target
    const ov = document.getElementById("overlay"), A = rectOf(own); let d = "";
    for (const t of targets) { if (t === own) continue; const R = rectOf(t);
      const x1 = A.x + A.w / 2, y1 = A.y + A.h / 2, x2 = R.x + R.w / 2, y2 = R.y + R.h / 2, vert = Math.abs(y2 - y1) > Math.abs(x2 - x1);
      const p1 = vert ? [x1, y2 > y1 ? A.y + A.h : A.y] : [x2 > x1 ? A.x + A.w : A.x, y1], p2 = vert ? [x2, y2 > y1 ? R.y : R.y + R.h] : [x2 > x1 ? R.x : R.x + R.w, y2];
      d += `<path class="x ${cls}" d="M${p1[0]},${p1[1]} C${vert ? `${p1[0]},${(p1[1] + p2[1]) / 2} ${p2[0]},${(p1[1] + p2[1]) / 2}` : `${(p1[0] + p2[0]) / 2},${p1[1]} ${(p1[0] + p2[0]) / 2},${p2[1]}`} ${p2[0]},${p2[1]}" marker-end="url(#ah-${cls === "impact" ? "impact" : "x"})"/>`; }
    ov.innerHTML = `<defs>${["x", "impact"].map((c) => `<marker id="ah-${c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="ah ${c}" d="M0,0L10,5L0,10z"/></marker>`).join("")}</defs>` + d;
    B.panel(a, imp, related(a));
    panel.classList.add("open");
    if (pan !== false || imp) fitRect(union([A, ...targets.map(rectOf)]), 80, 1.1, 380);
  }
  B.select = select; B.cam = cam; B.fitRect = fitRect; B.stage = stage;

  // ---- header
  function header() {
    const w = B.waiting();
    document.getElementById("wait").innerHTML = w.length ? `<span class="mark" id="waitmark" style="cursor:pointer">${w.length} waiting</span>` : "";
    document.getElementById("wait").onclick = () => w[0] && select(w[0].a, true);
    document.querySelectorAll("[data-lod-btn]").forEach((b) => b.addEventListener("click", () => {
      const s = { areas: 0.38, flows: 0.7, detail: 1.15 }[b.dataset.lodBtn], cx = stage.clientWidth / 2, cy = stage.clientHeight / 2; zoomAt(cx, cy, s / cam.s); }));
    document.getElementById("fit").onclick = fit;
    document.getElementById("theme").onclick = () => { const r = document.documentElement, d = r.dataset.theme === "dark" || (!r.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches); r.dataset.theme = d ? "light" : "dark"; };
  }
  const bounds = B.build(); header(); fit();
  addEventListener("resize", () => !sel && fitRect(B.bounds, 40, 0.6));
})();
