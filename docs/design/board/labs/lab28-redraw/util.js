// Data access and small helpers. Plain script: no modules, so the page opens by file.
window.B = (() => {
  const data = JSON.parse(document.getElementById("data").textContent);
  const by = new Map(data.entries.map((e) => [e.a, e]));
  const out = new Map(), inc = new Map();
  for (const r of data.relations) {
    (out.get(r.o) || out.set(r.o, []).get(r.o)).push(r);
    (inc.get(r.t) || inc.set(r.t, []).get(r.t)).push(r);
  }
  const key = (a) => a.split("/").pop();
  const human = (k) => { const s = k.replace(/[-_]+/g, " "); return s[0].toUpperCase() + s.slice(1); };
  const depth = (a) => (a.startsWith("constitution/") ? 3 : 4);
  // address = layer/area/kind/id then (kind/id)* then optionally a lone kind for a single part (timeout, proposal)
  const parent = (a) => { const p = a.split("/"), extra = p.length - depth(a); return extra <= 0 ? null : p.slice(0, extra % 2 ? -1 : -2).join("/"); };
  const kids = (a, kinds) => data.entries.filter((e) => parent(e.a) === a && (!kinds || kinds.includes(e.k)));
  const name = (e) => {
    if (typeof e === "string") e = by.get(e) || { a: e, k: "?", f: {} };
    const f = e.f || {};
    return f.title || f.word || (e.k === "decision" && f.question) || f.label || human(key(e.a));
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const h = (tag, cls, html, attrs) => {
    const el = document.createElement(tag);
    if (cls) el.className = cls;
    if (html != null) el.innerHTML = html;
    for (const k in attrs || {}) el.setAttribute(k, attrs[k]);
    return el;
  };
  const place = (a) => { const e = by.get(a); return e ? (e.ly ? `${e.ly[0].toUpperCase() + e.ly.slice(1)} · ${e.ar}` : "Constitution") : ""; };
  const route = (a) => { // workflow > step > case, as names
    const out = []; for (let p = a; p; p = parent(p)) out.unshift(name(p)); return out;
  };
  const decision = (a) => data.decisions[a];
  const waiting = () => data.entries.filter((e) => e.k === "decision" && decision(e.a)?.status === "waiting");
  const kindWord = (e) => e.k;
  return { data, by, out, inc, key, human, parent, kids, name, esc, h, place, route, decision, waiting, kindWord };
})();
