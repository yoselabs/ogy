import { h } from "../ui/dom.js";
import { words } from "../ui/words.js";

export function mountNotFound(main, { route }) {
  main.replaceChildren(
    h(
      "section",
      { class: "page notice" },
      h("h1", {}, words.notFound),
      h("p", {}, `${words.noPage} `, h("code", { "data-authored": true }, `#/${route.path}`), "."),
      h("p", {}, h("a", { href: "#/" }, words.board)),
    ),
  );
}
