(function () {
  "use strict";

  function revert(label, original) {
    setTimeout(function () {
      label.textContent = original;
    }, 2000);
  }

  document.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-share-url]");
    if (!btn) {
      return;
    }
    var url = btn.getAttribute("data-share-url") || window.location.href;
    var original = btn.textContent;
    function done(message) {
      btn.textContent = message;
      revert(btn, original);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(function () {
        done("Ссылка скопирована!");
      }, function () {
        window.prompt("Скопируйте ссылку:", url);
      });
    } else {
      window.prompt("Скопируйте ссылку:", url);
    }
  });
})();
