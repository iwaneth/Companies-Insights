// Applies the saved theme before first paint. Load in <head>.
// "light" | "dark" — defaults to the OS preference when nothing is saved.
(function () {
  var stored = null;
  try {
    stored = localStorage.getItem("theme");
  } catch (e) {}
  var prefersDark = window.matchMedia
    ? window.matchMedia("(prefers-color-scheme: dark)").matches
    : false;
  if (stored ? stored === "dark" : prefersDark) {
    document.documentElement.classList.add("dark-theme");
  }
})();
