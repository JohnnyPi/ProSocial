(function () {
  const MIN_LENGTH = 8;

  function bindContentReview(config) {
    const body = document.getElementById(config.bodyId);
    const target = document.getElementById(config.targetId);
    const form = body ? body.closest("form") : null;
    const submitBtn = form ? form.querySelector("[data-content-review-submit]") : null;
    if (!body || !target || !form || !submitBtn || !config.reviewUrl) {
      return;
    }

    let state = "idle";
    let reviewEventId = null;
    let reviewedText = "";

    function textValue() {
      return body.value.trim();
    }

    function reviewRequired() {
      return config.enabled && textValue().length >= MIN_LENGTH;
    }

    function setButtonReview() {
      submitBtn.type = "button";
      submitBtn.textContent = "Review";
      submitBtn.disabled = false;
    }

    function setButtonSubmit() {
      submitBtn.type = "submit";
      submitBtn.textContent = config.submitLabel;
      submitBtn.disabled = false;
    }

    function setButtonAnalyzing() {
      submitBtn.type = "button";
      submitBtn.textContent = "Analyzing…";
      submitBtn.disabled = true;
    }

    function clearReviewPanel() {
      target.innerHTML = "";
      reviewEventId = null;
      reviewedText = "";
    }

    function syncButtonState() {
      if (!config.enabled) {
        setButtonSubmit();
        return;
      }
      if (state === "analyzing") {
        return;
      }
      if (state === "reviewed" && textValue() === reviewedText) {
        setButtonSubmit();
        return;
      }
      if (state === "reviewed" && textValue() !== reviewedText) {
        state = "stale";
        clearReviewPanel();
      }
      setButtonReview();
    }

    function injectReviewEventId() {
      let hidden = form.querySelector('input[name="review_event_id"]');
      if (!hidden) {
        hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "review_event_id";
        form.appendChild(hidden);
      }
      hidden.value = reviewEventId || "";
    }

    function runReview() {
      const text = textValue();
      if (!reviewRequired()) {
        form.requestSubmit();
        return;
      }
      state = "analyzing";
      setButtonAnalyzing();
      target.innerHTML = '<p class="content-review-panel__loading">Analyzing tone…</p>';

      fetch(config.reviewUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": config.csrfToken,
        },
        body:
          "text=" +
          encodeURIComponent(text) +
          "&surface=" +
          encodeURIComponent(config.surface || "POST"),
      })
        .then(function (response) {
          return response.text().then(function (html) {
            return { ok: response.ok, html: html };
          });
        })
        .then(function (result) {
          target.innerHTML = result.html;
          const panel = target.querySelector("[data-review-event-id]");
          if (!result.ok || !panel) {
            state = "idle";
            setButtonReview();
            return;
          }
          reviewEventId = panel.getAttribute("data-review-event-id");
          reviewedText = text;
          state = "reviewed";
          setButtonSubmit();
          injectReviewEventId();
        })
        .catch(function () {
          target.innerHTML =
            '<p class="content-review-panel__error">Review unavailable. Try again.</p>';
          state = "idle";
          setButtonReview();
        });
    }

    submitBtn.addEventListener("click", function (event) {
      if (submitBtn.type === "button") {
        event.preventDefault();
        runReview();
      }
    });

    form.addEventListener("submit", function (event) {
      if (!config.enabled) {
        return;
      }
      if (reviewRequired()) {
        if (state !== "reviewed" || textValue() !== reviewedText) {
          event.preventDefault();
          setButtonReview();
          return;
        }
        injectReviewEventId();
      }
    });

    form.addEventListener("htmx:beforeRequest", function (event) {
      if (event.target !== form) {
        return;
      }
      if (!config.enabled) {
        return;
      }
      if (reviewRequired() && (state !== "reviewed" || textValue() !== reviewedText)) {
        event.preventDefault();
        setButtonReview();
      } else if (reviewEventId) {
        injectReviewEventId();
      }
    });

    body.addEventListener("input", function () {
      if (!config.enabled) {
        return;
      }
      syncButtonState();
    });

    form.addEventListener("reset", function () {
      state = "idle";
      clearReviewPanel();
      syncButtonState();
    });

    syncButtonState();
  }

  function initFromElement(el) {
    if (el.getAttribute("data-content-review-bound") === "true") {
      return;
    }
    el.setAttribute("data-content-review-bound", "true");
    bindContentReview({
      bodyId: el.getAttribute("data-content-review-body"),
      targetId: el.getAttribute("data-content-review-target"),
      reviewUrl: el.getAttribute("data-content-review-url"),
      submitLabel: el.getAttribute("data-content-review-submit-label") || "Post",
      surface: el.getAttribute("data-content-review-surface") || "POST",
      csrfToken: el.getAttribute("data-csrf-token") || "",
      enabled: el.getAttribute("data-content-review-enabled") === "true",
    });
  }

  function initAll(root) {
    (root || document).querySelectorAll("[data-content-review-body]").forEach(initFromElement);
  }

  initAll();

  document.body.addEventListener("htmx:afterSwap", function (event) {
    initAll(event.detail.target);
  });
})();
