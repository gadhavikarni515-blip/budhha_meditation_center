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
  }

  function initSidebar() {
    const toggleBtn = qs("[data-admin-sidebar-toggle]");
    const backdrop = qs("[data-admin-sidebar-backdrop]");
    if (toggleBtn) toggleBtn.addEventListener("click", () => toggleSidebar());
    if (backdrop) backdrop.addEventListener("click", () => toggleSidebar(false));

    // Close sidebar after clicking a nav link on mobile
    qsa(".admin-nav a").forEach((a) => {
      a.addEventListener("click", () => {
        if (window.matchMedia("(max-width: 980px)").matches) toggleSidebar(false);
      });
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

  document.addEventListener("DOMContentLoaded", () => {
    initSidebar();
    initToggles();
    initProgramTimeAutoFill();
  });
})();


