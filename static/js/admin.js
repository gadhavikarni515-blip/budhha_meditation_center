(() => {
    function qs(sel, root = document) {
        return root.querySelector(sel);
    }

    function qsa(sel, root = document) {
        return Array.from(root.querySelectorAll(sel));
    }

    function toggleSidebar(open) {
        const body = document.body;
        const isOpen = body.classList.contains("sidebar-open");
        const next = typeof open === "boolean" ? open : !isOpen;
        body.classList.toggle("sidebar-open", next);

        // Prevent body scroll when sidebar is open on mobile
        if (next) {
            body.style.overflow = "hidden";
        } else {
            body.style.overflow = "";
        }
    }

    function initSidebar() {
        const toggleBtn = qs("[data-admin-sidebar-toggle]");
        const backdrop = qs("[data-admin-sidebar-backdrop]");
        const closeBtn = qs("[data-admin-sidebar-close]");

        if (toggleBtn) toggleBtn.addEventListener("click", () => toggleSidebar());
        if (backdrop) backdrop.addEventListener("click", () => toggleSidebar(false));
        if (closeBtn) closeBtn.addEventListener("click", () => toggleSidebar(false));

        // Close sidebar after clicking a nav link on mobile
        qsa(".admin-nav a").forEach((a) => {
            a.addEventListener("click", () => {
                if (window.matchMedia("(max-width: 980px)").matches) toggleSidebar(false);
            });
        });

        // Close sidebar on escape key
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && document.body.classList.contains("sidebar-open")) {
                toggleSidebar(false);
            }
        });

        // Handle window resize - close sidebar if resizing to desktop
        let resizeTimer;
        window.addEventListener("resize", () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth > 980 && document.body.classList.contains("sidebar-open")) {
                    toggleSidebar(false);
                }
            }, 100);
        });
    }

    function initToggles() {
        qsa("[data-admin-toggle]").forEach((btn) => {
            const targetSel = btn.getAttribute("data-admin-toggle");
            const target = targetSel ? qs(targetSel) : null;
            if (!target) return;

            btn.addEventListener("click", () => {
                target.classList.toggle("is-hidden");
                const expanded = !target.classList.contains("is-hidden");
                btn.setAttribute("aria-expanded", expanded ? "true" : "false");

                // Scroll to panel when opened on mobile
                if (expanded && window.innerWidth <= 768) {
                    setTimeout(() => {
                        target.scrollIntoView({ behavior: "smooth", block: "start" });
                    }, 100);
                }
            });
        });
    }

    function formatTimeTo12h(value24) {
        try {
            const d = new Date("2000-01-01T" + value24);
            return d.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit", hour12: true });
        } catch {
            return value24;
        }
    }

    function initProgramTimeAutoFill() {
        const start = qs("#start_time");
        const end = qs("#end_time");
        const display = qs("#time");

        if (!start || !display) return;

        const update = () => {
            const s = start.value;
            const e = end ? end.value : "";
            if (s && e) display.value = `${formatTimeTo12h(s)} - ${formatTimeTo12h(e)}`;
            else if (s) display.value = formatTimeTo12h(s);
        };

        start.addEventListener("change", update);
        if (end) end.addEventListener("change", update);
        update();
    }

    // Add data-label attributes to table cells for mobile card view
    function initResponsiveTables() {
        qsa(".admin-table").forEach((table) => {
            const headers = qsa("th", table);
            const headerTexts = headers.map((th) => th.textContent.trim());

            qsa("tbody tr", table).forEach((row) => {
                qsa("td", row).forEach((cell, index) => {
                    if (headerTexts[index]) {
                        cell.setAttribute("data-label", headerTexts[index]);
                    }
                });
            });
        });
    }

    // Handle touch events for better mobile experience
    function initTouchHandlers() {
        // Swipe to close sidebar
        let touchStartX = 0;
        let touchEndX = 0;
        const sidebar = qs(".admin-sidebar");

        if (sidebar) {
            sidebar.addEventListener("touchstart", (e) => {
                touchStartX = e.changedTouches[0].screenX;
            }, { passive: true });

            sidebar.addEventListener("touchend", (e) => {
                touchEndX = e.changedTouches[0].screenX;
                const swipeDistance = touchStartX - touchEndX;

                // Swipe left to close (threshold of 50px)
                if (swipeDistance > 50 && document.body.classList.contains("sidebar-open")) {
                    toggleSidebar(false);
                }
            }, { passive: true });
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        initSidebar();
        initToggles();
        initProgramTimeAutoFill();
        initResponsiveTables();
        initTouchHandlers();
    });
})();