// The tokens follow the system setting; data-theme lets a check force one.
export function followSystemTheme() {
  const query = matchMedia("(prefers-color-scheme: dark)");
  const apply = () => {
    document.documentElement.dataset.theme = query.matches ? "dark" : "light";
  };
  query.addEventListener("change", apply);
  apply();
}
