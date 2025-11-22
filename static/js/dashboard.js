// dashboard.js - Global helpers + UI logic (load first)

(function () {
  function onReady(fn) {
    if (document.readyState === "complete" || document.readyState === "interactive") {
      setTimeout(fn, 1);
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  function setRiskBox(boxEl, value) {
    if (!boxEl) return;
    const pct = Math.round(Number(value) || 0);
    boxEl.innerText = pct + "%";
    if (pct < 40) {
      boxEl.style.background = "#d8ffd9";
      boxEl.style.color = "#005500";
    } else if (pct < 75) {
      boxEl.style.background = "#fff7d0";
      boxEl.style.color = "#7a5a00";
    } else {
      boxEl.style.background = "#ffe3e3";
      boxEl.style.color = "#7a0000";
    }
    boxEl.style.transform = "scale(1.05)";
    setTimeout(() => (boxEl.style.transform = "scale(1)"), 220);
  }

  function pushAndCap(arr, item, cap = 60) {
    arr.push(item);
    while (arr.length > cap) arr.shift();
  }

  window.LS_helpers = {
    setRiskBox,
    pushAndCap,
  };

  onReady(() => {
    const sidebar = document.querySelector(".sidebar");
    const main = document.querySelector(".main");
    const toggle = document.getElementById("sidebarToggle");
    const themeBtn = document.getElementById("themeToggle");

    if (toggle && sidebar && main) {
      toggle.addEventListener("click", (ev) => {
        ev.stopPropagation();
        sidebar.classList.toggle("open");
        main.classList.toggle("blur");
      });
      main.addEventListener("click", () => {
        if (sidebar.classList.contains("open")) {
          sidebar.classList.remove("open");
          main.classList.remove("blur");
        }
      });
      document.addEventListener("keydown", (ev) => {
        if (ev.key === "Escape") {
          sidebar.classList.remove("open");
          main.classList.remove("blur");
        }
      });
    }

    if (themeBtn) {
      if (localStorage.getItem("ls_theme") === "dark") {
        document.body.classList.add("dark");
        themeBtn.textContent = "☀️";
      } else {
        themeBtn.textContent = "🌙";
      }

      themeBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark");
        const dark = document.body.classList.contains("dark");
        localStorage.setItem("ls_theme", dark ? "dark" : "light");
        themeBtn.textContent = dark ? "☀️" : "🌙";
      });
    }

    try {
      const links = document.querySelectorAll(".nav-link");
      const current = window.location.pathname.replace(/\/+$/, "") || "/";
      links.forEach((lnk) => {
        const href = new URL(lnk.href, window.location.origin)
          .pathname.replace(/\/+$/, "") || "/";
        if (href === current) {
          lnk.classList.add("active-nav");
        } else {
          lnk.classList.remove("active-nav");
        }
      });
    } catch (e) {
      console.warn("Navigation highlighting skipped:", e);
    }
  });
})();
