"""The page `ogy view` fills: its style and its few lines of script, in one string with no outside file or link."""

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{title}}</title>
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--mute:#6b6b66;--line:#dcdcd5;--card:#fff;--product:#2b6cb0;--software:#2f855a;--accent:#b7791f}
@media (prefers-color-scheme:dark){:root{--bg:#161614;--fg:#ececE6;--mute:#9a9a92;--line:#33332f;--card:#1f1f1c;--product:#63a4e8;--software:#5ec58d;--accent:#e0a84a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif}
header{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--line);padding:12px 16px;z-index:2;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
header h1{font-size:18px;margin:0}header input{flex:1;min-width:160px;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
header button{padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg);cursor:pointer}
main{max-width:1000px;margin:0 auto;padding:16px}h2{margin:28px 0 10px}h3{margin:18px 0 6px;font-size:15px;color:var(--mute);text-transform:uppercase;letter-spacing:.04em}
h3 small{font-weight:400}h4{margin:10px 0 2px;font-size:13px;color:var(--mute)}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.tile{display:block;padding:12px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--product);border-radius:8px;color:inherit;text-decoration:none}
.tile[data-layer=software]{border-left-color:var(--software)}.tile:hover{border-color:var(--accent)}
.tile b{display:block}.tile span{display:block;color:var(--mute);font-size:13px;margin:4px 0}.tile em{font-style:normal;font-size:12px;color:var(--accent)}
.area{padding:8px 0 24px;border-top:1px solid var(--line)}.layer{font-size:12px;text-transform:uppercase;color:var(--product);border:1px solid currentColor;border-radius:10px;padding:1px 8px;vertical-align:middle}
.area[data-layer=software] .layer{color:var(--software)}.says{font-size:17px}.unlike,.start{color:var(--mute);font-size:14px}
.story{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px}
ul{margin:4px 0;padding-left:20px}li{margin:3px 0}details{margin:2px 0}summary{cursor:pointer}summary span{color:var(--mute)}
details[open]>summary{margin-bottom:4px}.who{color:var(--accent);font-size:13px}code{background:var(--card);border:1px solid var(--line);padding:0 4px;border-radius:4px}
.hide{display:none}
@media (max-width:600px){main{padding:12px}}
</style></head><body>
<header><h1>{{title}}</h1><input id="q" type="search" placeholder="Filter areas and entries" aria-label="Filter"><button id="all">Open all</button><button id="none">Close all</button></header>
<main><nav>{{sitemap}}</nav>{{areas}}</main>
<script>
const q=document.getElementById('q');
function filter(){const w=q.value.toLowerCase().split(/[ ]+/).filter(Boolean);
document.querySelectorAll('.area').forEach(a=>{const t=a.textContent.toLowerCase();a.classList.toggle('hide',!w.every(x=>t.includes(x)))});
document.querySelectorAll('.tile').forEach(a=>{const t=a.textContent.toLowerCase();a.classList.toggle('hide',!w.every(x=>t.includes(x)))})}
q.addEventListener('input',filter);
document.getElementById('all').onclick=()=>document.querySelectorAll('details').forEach(d=>d.open=true);
document.getElementById('none').onclick=()=>document.querySelectorAll('details').forEach(d=>d.open=false);
</script></body></html>
"""
