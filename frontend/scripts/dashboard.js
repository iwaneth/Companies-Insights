// ── Safe Initialization Helper ิ──
function initDashboard() {
  console.log("Dashboard JS initialized successfully!");

  // ── Search ──
  const searchInput = document.getElementById("search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll(".company-card").forEach((card) => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(q) ? "" : "none";
      });
    });
  }

  // ── Theme Switcher ──
  const html = document.documentElement;
  const radios = document.getElementsByName("themes");

  for (let i = 0; i < radios.length; i++) {
    radios[i].addEventListener("change", function () {
      html.classList.remove("light-theme", "dark-theme", "black-theme");
      html.classList.add(this.id);
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
  modalMeta.textContent = record.pubDate ? `Date: ${formatPubDate(record.pubDate)}` : "";
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
