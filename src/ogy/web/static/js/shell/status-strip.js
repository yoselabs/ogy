import { glyph, h } from "../ui/dom.js";
import { words } from "../ui/words.js";

// Standing facts, each a count and, once its list exists, a link. Colour only where the fact is a status.
const ITEMS = [
  ["waiting", words.waitingCount, "waiting", "is-waiting"],
  ["owed", words.owed, "owed", "is-owed"],
  ["unagreed", words.unagreed, "unagreed", ""],
  ["changed", words.changed, "changed", ""],
  ["dropped", words.dropped, "dropped", ""],
  ["findings", words.findings, "findings", "is-failure"],
];

export function mountStatusStrip(root, { router, live }) {
  const render = ({ data, error }) => {
    if (!data)
      return root.replaceChildren(
        h(
          "p",
          { role: "status", class: "strip-error" },
          error ? (error.status === 401 ? `${words.countsUnavailable} ${words.signedOut}` : words.countsUnavailable) : words.loading,
        ),
      );
    root.replaceChildren(
      ...ITEMS.map(([key, label, path, status]) => {
        const count = data.totals[key];
        const props = { class: `stat ${count > 0 ? status : ""}`, "data-stat": key };
        const body = [glyph(key), h("b", {}, String(count)), h("span", {}, label)];
        return router.has(path) ? h("a", { ...props, href: `#/${path}` }, body) : h("span", props, body);
      }),
    );
  };
  live.subscribe(render);
}
