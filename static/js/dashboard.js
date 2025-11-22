document.addEventListener("DOMContentLoaded", () => {

    const sidebar = document.getElementById("sidebar");
    const main = document.getElementById("main");
    const toggle = document.getElementById("sidebarToggle");
    const themeBtn = document.getElementById("themeToggle");

    // ---------------------------
    // SIDEBAR TOGGLE
    // ---------------------------
    toggle.addEventListener("click", (e) => {
        e.stopPropagation();
        sidebar.classList.toggle("open");
        main.classList.toggle("blur");
    });

    // Click outside → close sidebar
    main.addEventListener("click", () => {
        if (sidebar.classList.contains("open")) {
            sidebar.classList.remove("open");
            main.classList.remove("blur");
        }
    });

    // ESC → close
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            sidebar.classList.remove("open");
            main.classList.remove("blur");
        }
    });

    // ---------------------------
    // THEME TOGGLE
    // ---------------------------
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark");
        themeBtn.textContent = "☀️";
    }

    themeBtn.addEventListener("click", () => {
        document.body.classList.toggle("dark");

        if (document.body.classList.contains("dark")) {
            localStorage.setItem("theme", "dark");
            themeBtn.textContent = "☀️";
        } else {
            localStorage.setItem("theme", "light");
            themeBtn.textContent = "🌙";
        }
    });

    // ---------------------------
    // NAV ACTIVE HIGHLIGHT
    // ---------------------------
    const links = document.querySelectorAll(".nav-link");
    const current = window.location.pathname;

    links.forEach(link => {
        if (link.getAttribute("href") === current) {
            link.classList.add("active-nav");
        }
    });

});
