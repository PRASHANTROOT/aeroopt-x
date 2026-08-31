document.addEventListener("DOMContentLoaded", () => {
  const themeToggle =
    document.getElementById("themeToggle");

  const savedTheme =
    localStorage.getItem("aeroopt-doc-theme");

  if (savedTheme) {
    document.documentElement.setAttribute(
      "data-theme",
      savedTheme
    );
  }

  themeToggle?.addEventListener("click", () => {
    const currentTheme =
      document.documentElement.getAttribute("data-theme");

    const nextTheme =
      currentTheme === "dark"
        ? "light"
        : "dark";

    document.documentElement.setAttribute(
      "data-theme",
      nextTheme
    );

    localStorage.setItem(
      "aeroopt-doc-theme",
      nextTheme
    );
  });


  const links =
    document.querySelectorAll(".docs-nav-link");

  const sections =
    document.querySelectorAll(".docs-section");

  const observer =
    new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) {
            return;
          }

          const id =
            entry.target.getAttribute("id");

          links.forEach((link) => {
            link.classList.toggle(
              "active",
              link.getAttribute("href") === `#${id}`
            );
          });
        });
      },
      {
        rootMargin: "-20% 0px -70% 0px",
      }
    );

  sections.forEach((section) => {
    observer.observe(section);
  });
});