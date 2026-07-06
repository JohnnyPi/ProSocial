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
    let civilityEventId = null;
    let civilityResolved = false;
    let blockSubmit = false;

    function textValue() {
      return body.value.trim();
    }

    function reviewRequired() {
      return config.enabled && textValue().length >= MIN_LENGTH;
    }

    function civilityRequired() {
      return Boolean(civilityEventId) && !civilityResolved;
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
      civilityEventId = null;
      civilityResolved = false;
      blockSubmit = false;
    }

    function syncButtonState() {
      if (!config.enabled) {
        setButtonSubmit();
        return;
      }
      if (state === "analyzing") {
        return;
      }
      if (blockSubmit || civilityRequired()) {
        setButtonReview();
        submitBtn.disabled = true;
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

    function injectCivilityEventId() {
      let hidden = form.querySelector('input[name="civility_event_id"]');
      if (!hidden) {
        hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "civility_event_id";
        form.appendChild(hidden);
      }
      hidden.value = civilityEventId || "";
    }

    function recordCivilityAction(action) {
      if (!config.civilityRecordUrl || !civilityEventId) {
        return Promise.resolve();
      }
      return fetch(config.civilityRecordUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": config.csrfToken,
        },
        body:
          "event_id=" +
          encodeURIComponent(civilityEventId) +
          "&user_action=" +
          encodeURIComponent(action) +
          "&text=" +
          encodeURIComponent(textValue()),
      }).catch(function () {});
    }

    function bindCivilityPrompt(panel) {
      const promptEl = panel.querySelector("[data-civility-event-id]");
      if (!promptEl) {
        civilityEventId = null;
        civilityResolved = true;
        blockSubmit = false;
        return;
      }
      civilityEventId = promptEl.getAttribute("data-civility-event-id");
      civilityResolved = false;
      blockSubmit = true;
      syncButtonState();
    }

    target.addEventListener("click", function (event) {
      const btn = event.target.closest("[data-civility-action]");
      if (!btn) {
        return;
      }
      const action = btn.getAttribute("data-civility-action");
      if (action === "EDITED") {
        recordCivilityAction("EDITED").then(function () {
          blockSubmit = false;
          civilityResolved = true;
          const prompt = target.querySelector(".content-review-panel__civility");
          if (prompt) {
            prompt.remove();
          }
          body.focus();
          syncButtonState();
        });
        return;
      }
      if (action === "CANCELLED") {
        recordCivilityAction("CANCELLED").then(function () {
          blockSubmit = true;
          civilityResolved = false;
          syncButtonState();
        });
        return;
      }
      if (action === "POSTED_ANYWAY") {
        recordCivilityAction("POSTED_ANYWAY").then(function () {
          blockSubmit = false;
          civilityResolved = true;
          const prompt = target.querySelector(".content-review-panel__civility");
          if (prompt) {
            prompt.remove();
          }
          syncButtonState();
        });
      }
    });

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
          bindCivilityPrompt(panel);
          injectReviewEventId();
          syncButtonState();
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
      if (blockSubmit) {
        event.preventDefault();
        return;
      }
      if (!config.enabled) {
        return;
      }
      if (reviewRequired()) {
        if (state !== "reviewed" || textValue() !== reviewedText) {
          event.preventDefault();
          setButtonReview();
          return;
        }
        if (civilityRequired()) {
          event.preventDefault();
          syncButtonState();
          return;
        }
        injectReviewEventId();
        injectCivilityEventId();
      }
    });

    form.addEventListener("htmx:beforeRequest", function (event) {
      if (event.target !== form) {
        return;
      }
      if (blockSubmit) {
        event.preventDefault();
        return;
      }
      if (!config.enabled) {
        return;
      }
      if (reviewRequired() && (state !== "reviewed" || textValue() !== reviewedText)) {
        event.preventDefault();
        setButtonReview();
      } else if (civilityRequired()) {
        event.preventDefault();
        syncButtonState();
      } else {
        if (reviewEventId) {
          injectReviewEventId();
        }
        if (civilityEventId) {
          injectCivilityEventId();
        }
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
      civilityRecordUrl: el.getAttribute("data-civility-record-url"),
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
