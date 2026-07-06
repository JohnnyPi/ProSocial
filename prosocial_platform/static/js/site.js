(function () {
  function initPostModal() {
    const modal = document.getElementById("post-modal");
    const openBtn = document.getElementById("post-modal-open");
    if (!modal || !openBtn) {
      return;
    }

    openBtn.addEventListener("click", () => modal.showModal());

    modal.addEventListener("click", (event) => {
      if (event.target === modal) {
        modal.close();
      }
    });

    modal.addEventListener("close", () => {
      const form = modal.querySelector("#post-composer-form");
      form?.reset();
    });

    document.body.addEventListener("click", (event) => {
      const closeTrigger = event.target.closest(".modal-close");
      if (closeTrigger && modal.contains(closeTrigger)) {
        modal.close();
      }
    });

    document.body.addEventListener("htmx:afterRequest", (event) => {
      const form = event.target.closest("#post-composer-form");
      if (form && event.detail.successful) {
        modal.close();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPostModal);
  } else {
    initPostModal();
  }
})();
