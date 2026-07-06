(function () {
  function bindPreSendPrompt(bodyId, targetId, checkUrl, recordUrl, csrfToken) {
    const body = document.getElementById(bodyId);
    const target = document.getElementById(targetId);
    const form = body ? body.closest("form") : null;
    if (!body || !target || !checkUrl) return;
    let timer;
    let civilityEventId = null;
    let blockSubmit = false;

    function recordAction(action, text) {
      if (!recordUrl || !civilityEventId) return;
      fetch(recordUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
        },
        body:
          "event_id=" +
          encodeURIComponent(civilityEventId) +
          "&user_action=" +
          encodeURIComponent(action) +
          "&text=" +
          encodeURIComponent(text || ""),
      }).catch(function () {});
    }

    target.addEventListener("click", function (e) {
      const btn = e.target.closest("[data-civility-action]");
      if (!btn) return;
      const action = btn.getAttribute("data-civility-action");
      if (action === "EDITED") {
        recordAction("EDITED", body.value);
        blockSubmit = false;
        target.innerHTML = "";
        body.focus();
        return;
      }
      if (action === "CANCELLED") {
        recordAction("CANCELLED", body.value);
        blockSubmit = true;
        target.innerHTML = "";
        return;
      }
      if (action === "POSTED_ANYWAY") {
        recordAction("POSTED_ANYWAY", body.value);
        blockSubmit = false;
        target.innerHTML = "";
        if (form) form.requestSubmit();
      }
    });

    if (form) {
      form.addEventListener("submit", function (e) {
        if (blockSubmit) {
          e.preventDefault();
          return;
        }
        let hidden = form.querySelector('input[name="civility_event_id"]');
        if (!hidden && civilityEventId) {
          hidden = document.createElement("input");
          hidden.type = "hidden";
          hidden.name = "civility_event_id";
          form.appendChild(hidden);
        }
        if (hidden && civilityEventId) {
          hidden.value = civilityEventId;
        }
      });
    }

    body.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        const text = body.value.trim();
        if (text.length < 12) {
          target.innerHTML = "";
          civilityEventId = null;
          blockSubmit = false;
          return;
        }
        fetch(checkUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": csrfToken,
          },
          body: "text=" + encodeURIComponent(text),
        })
          .then(function (r) {
            return r.text();
          })
          .then(function (html) {
            target.innerHTML = html;
            const promptEl = target.querySelector("[data-civility-event-id]");
            if (promptEl) {
              civilityEventId = promptEl.getAttribute("data-civility-event-id");
              blockSubmit = true;
            } else {
              civilityEventId = null;
              blockSubmit = false;
            }
          })
          .catch(function () {});
      }, 400);
    });
  }

  document.querySelectorAll("[data-pre-send-body]").forEach(function (el) {
    bindPreSendPrompt(
      el.getAttribute("data-pre-send-body"),
      el.getAttribute("data-pre-send-target"),
      el.getAttribute("data-pre-send-url"),
      el.getAttribute("data-pre-send-record-url"),
      el.getAttribute("data-csrf-token")
    );
  });
})();
