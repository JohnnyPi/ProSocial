(function () {
  const btn = document.getElementById("clip-selection-btn");
  const form = document.getElementById("clip-selection-form");
  if (!btn || !form) return;
  btn.addEventListener("click", function () {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || !selection.toString().trim()) {
      alert("Select text in the post to clip.");
      return;
    }
    const text = selection.toString().trim();
    document.getElementById("clip-quoted-text").value = text.slice(0, 5000);
    document.getElementById("clip-selection-start").value = "0";
    document.getElementById("clip-selection-end").value = String(text.length);
    form.submit();
  });
})();
