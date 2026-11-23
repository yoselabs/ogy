// node build.mjs : builds lab29b-standalone.html from src/ (lab 28's stylesheet and data + the 29B modules, inline, no server)
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const read = (n) => fs.readFileSync(path.join(here, "src", n), "utf8");
const modules = ["data.js", "icons.js", "core.js", "model.js", "route.js", "cards.js", "detail.js", "draw.js", "ui.js"];
const head = read("head.html").replace("Product board v2 (prototype)", "Board lab 29B (prototype)");
const html = `${head}<style>${read("style.base.css")}${read("style.29b.css")}</style>\n</head><body>\n${read("body29b.html")}<script>\n${modules.map(read).join("\n")}\n</script></body></html>\n`;
fs.writeFileSync(path.join(here, "lab29b-standalone.html"), html);
console.log("lab29b-standalone.html", html.length);
