document.addEventListener("DOMContentLoaded", () => {
  const themeToggle =
    document.getElementById("themeToggle");

  const savedTheme =
    localStorage.getItem("aeroopt-help-theme");

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
      "aeroopt-help-theme",
      nextTheme
    );
  });


  const faqItems =
    document.querySelectorAll(".faq-item");

  faqItems.forEach((item) => {
    const button =
      item.querySelector(".faq-question");

    button?.addEventListener("click", () => {
      const wasOpen =
        item.classList.contains("open");

      faqItems.forEach((faq) => {
        faq.classList.remove("open");
      });

      if (!wasOpen) {
        item.classList.add("open");
      }
    });
  });


  const searchInput =
    document.getElementById("helpSearch");

  searchInput?.addEventListener("input", (event) => {
    const query =
      event.target.value
        .toLowerCase()
        .trim();

    const searchableItems =
      document.querySelectorAll(
        ".help-card, .faq-item, .trouble-card"
      );

    searchableItems.forEach((item) => {
      const text =
        item.textContent
          .toLowerCase();

      const matches =
        text.includes(query);

      item.classList.toggle(
        "hidden",
        query !== "" && !matches
      );
    });
  });
});