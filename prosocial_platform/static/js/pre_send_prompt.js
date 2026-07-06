(function () {
  function bindPreSendPrompt(bodyId, targetId, checkUrl, csrfToken) {
    const body = document.getElementById(bodyId);
    const target = document.getElementById(targetId);
    if (!body || !target || !checkUrl) return;
    let timer;
    body.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        const text = body.value.trim();
        if (text.length < 12) {
          target.innerHTML = "";
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
          .then((r) => r.text())
          .then((html) => {
            target.innerHTML = html;
          })
          .catch(() => {});
      }, 400);
    });
  }

  document.querySelectorAll("[data-pre-send-body]").forEach(function (el) {
    bindPreSendPrompt(
      el.getAttribute("data-pre-send-body"),
      el.getAttribute("data-pre-send-target"),
      el.getAttribute("data-pre-send-url"),
      el.getAttribute("data-csrf-token")
    );
  });
})();
