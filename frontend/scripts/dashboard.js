// ── Safe Initialization Helper ──
function initDashboard() {
  console.log("Dashboard JS initialized successfully!");

  // ── Search ──
  const searchInput = document.getElementById("search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll(".company-card").forEach((card) => {
        const text = (card.dataset.search || "").toLowerCase();
        card.style.display = text.includes(q) ? "" : "none";
      });
    });
  }

  // ── Theme Switcher (light / dark, persisted) ──
  const html = document.documentElement;
  const radios = document.getElementsByName("themes");

  // Reflect the saved theme in the switcher UI
  const saved = localStorage.getItem("theme");
  const isDark = saved ? saved === "dark" : html.classList.contains("dark-theme");
  const checked = document.getElementById(isDark ? "dark-theme" : "light-theme");
  if (checked) checked.checked = true;

  for (let i = 0; i < radios.length; i++) {
    radios[i].addEventListener("change", function () {
      html.classList.toggle("dark-theme", this.id === "dark-theme");
      try {
        localStorage.setItem(
          "theme",
          this.id === "dark-theme" ? "dark" : "light",
        );
      } catch (e) {}
      console.log("Theme switched to:", this.id);
    });
  }
}

// Attach safely whether DOM is ready or still loading
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initDashboard);
} else {
  initDashboard();
}

function formatPubDate(value) {
  const dt = new Date(value);
  if (Number.isNaN(dt.getTime())) return String(value);
  const dd = String(dt.getDate()).padStart(2, "0");
  const mm = String(dt.getMonth() + 1).padStart(2, "0");
  const yy = String(dt.getFullYear()).slice(-2);
  return `${dd}/${mm}/${yy}`;
}

// ── News Modal ──
function openNewsModal(el) {
  const record = JSON.parse(el.dataset.record || "{}");
  const modalTitle = document.getElementById("modalTitle");
  const modalMeta = document.getElementById("modalMeta");
  const modalDl = document.getElementById("modalDl");

  modalTitle.textContent = record.title || "News item";
  modalMeta.textContent = record.pubDate
    ? `Date: ${formatPubDate(record.pubDate)}`
    : "";
  modalDl.replaceChildren();

  if (record.newsArticle) {
    const dt = document.createElement("dt");
    dt.textContent = "Article";
    const dd = document.createElement("dd");
    dd.textContent = record.newsArticle;
    modalDl.append(dt, dd);
  }

  document.getElementById("newsModal").classList.add("active");
}

function closeNewsModal(e) {
  if (e && e.target !== e.currentTarget) return;
  document.getElementById("newsModal").classList.remove("active");
}

// ── Company Modal (all attributes & properties) ──
function openCompanyModal(card) {
  const source = card.querySelector(".company-modal-source");
  const body = document.getElementById("companyModalBody");
  body.replaceChildren();
  if (source) {
    source.childNodes.forEach((node) => {
      body.appendChild(node.cloneNode(true));
    });
  }
  document.getElementById("companyModal").classList.add("active");
}

function closeCompanyModal(e) {
  if (e && e.target !== e.currentTarget) return;
  document.getElementById("companyModal").classList.remove("active");
}
