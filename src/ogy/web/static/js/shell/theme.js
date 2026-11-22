// Old canvas rules select on data-theme; the tokens follow the system setting on their own.
export function followSystemTheme() {
  const query = matchMedia("(prefers-color-scheme: dark)");
  const apply = () => {
    document.documentElement.dataset.theme = query.matches ? "dark" : "light";
  };
  query.addEventListener("change", apply);
  apply();
}
