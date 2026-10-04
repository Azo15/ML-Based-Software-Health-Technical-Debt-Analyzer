"use strict";

// Decorative sample code only: no repository content or network traffic is used.
(() => {
  const root = document.documentElement;
  const toggle = document.getElementById("motion-toggle");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = matchMedia("(hover: hover) and (pointer: fine)");
  let paused = reduced.matches;
  try {
    paused ||= localStorage.getItem("codescope-motion") === "paused";
  } catch {
    /* Storage can be unavailable in privacy modes. */
  }
  let frame = 0;
  let x = 0;
  let y = 0;
  function clearLight() {
    cancelAnimationFrame(frame);
    frame = 0;
    root.classList.remove("pointer-active");
  }
  function sync() {
    root.classList.toggle("motion-paused", paused || reduced.matches);
    toggle.setAttribute("aria-pressed", String(paused || reduced.matches));
    toggle.textContent =
      paused || reduced.matches ? "Hareketi aç" : "Hareketi durdur";
    // Respect the operating-system preference even when the local button is used.
    toggle.disabled = reduced.matches;
    toggle.title = reduced.matches
      ? "Sistem hareket azaltma tercihi etkin"
      : "Arka plan hareketini aç veya kapat";
    clearLight();
  }
  toggle.addEventListener("click", () => {
    paused = !paused;
    try {
      localStorage.setItem("codescope-motion", paused ? "paused" : "enabled");
    } catch {}
    sync();
  });
  reduced.addEventListener("change", sync);
  finePointer.addEventListener("change", clearLight);
  document.addEventListener(
    "pointermove",
    (event) => {
      if (
        paused ||
        reduced.matches ||
        !finePointer.matches ||
        event.pointerType === "touch"
      )
        return;
      x = event.clientX;
      y = event.clientY;
      if (!frame)
        frame = requestAnimationFrame(() => {
          root.style.setProperty("--pointer-x", `${x}px`);
          root.style.setProperty("--pointer-y", `${y}px`);
          root.classList.add("pointer-active");
          frame = 0;
        });
    },
    { passive: true },
  );
  document.documentElement.addEventListener("pointerleave", clearLight);
  window.addEventListener("blur", clearLight);
  document.addEventListener("visibilitychange", () => {
    root.classList.toggle("page-hidden", document.hidden);
    if (document.hidden) clearLight();
  });
  sync();
})();
