(function () {
  "use strict";
  const DEFAULT_ATTEMPT_TIME_LIMIT_MS = 60000;
  const page = document.querySelector("main[data-attempt-time-limit-ms]");
  const timer = document.getElementById("timer");
  const status = document.getElementById("timer-status");
  const keyAction = document.getElementById("key-action");
  const button = document.getElementById("timer-button");
  const limitLabel = document.getElementById("attempt-limit");
  const modal = document.getElementById("submission-modal");
  const form = document.getElementById("submission-form");
  const durationLabel = document.getElementById("result-duration");
  const durationInput = document.getElementById("duration-ms");
  const submit = document.getElementById("submit-button");

  let state = "ready";
  let startedAt = 0;
  let durationMs = 0;
  let frame;

  const configuredLimit = Number(page && page.dataset.attemptTimeLimitMs);
  const attemptTimeLimitMs =
    Number.isFinite(configuredLimit) && configuredLimit > 0
      ? configuredLimit
      : DEFAULT_ATTEMPT_TIME_LIMIT_MS;

  function format(ms) {
    const cs = Math.floor(ms / 10) % 100;
    const sec = Math.floor(ms / 1000) % 60;
    const min = Math.floor(ms / 60000);
    return (
      String(min).padStart(2, "0") +
      ":" +
      String(sec).padStart(2, "0") +
      "." +
      String(cs).padStart(2, "0")
    );
  }

  function paint(ms) {
    timer.textContent = format(ms);
  }

  function tick() {
    const elapsed = performance.now() - startedAt;
    if (elapsed >= attemptTimeLimitMs) {
      reset();
      return;
    }
    durationMs = elapsed;
    paint(durationMs);
    frame = requestAnimationFrame(tick);
  }

  function start() {
    state = "running";
    startedAt = performance.now();
    status.textContent = "In progress";
    status.className =
      "mb-7 text-xs font-medium uppercase tracking-[0.32em] text-lime";
    keyAction.textContent = "to stop";
    button.textContent = "Stop timer";
    frame = requestAnimationFrame(tick);
  }

  function stop(recordedDuration, reachedLimit) {
    cancelAnimationFrame(frame);
    durationMs = Math.min(
      recordedDuration === undefined
        ? performance.now() - startedAt
        : recordedDuration,
      attemptTimeLimitMs,
    );
    paint(durationMs);
    durationInput.value = String(Math.round(durationMs));
    state = "stopped";
    status.textContent = reachedLimit ? "Time limit reached" : "Time recorded";
    status.className =
      "mb-7 text-xs font-medium uppercase tracking-[0.32em] text-zinc-500";
    keyAction.textContent = "to save";
    button.textContent = "Save result";
    durationLabel.textContent = format(durationMs);
    openModal();
  }

  function openModal() {
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    document.getElementById("password").focus();
  }

  function reset() {
    form.reset();
    modal.classList.add("hidden");
    modal.classList.remove("flex");
    state = "ready";
    durationMs = 0;
    paint(0);
    status.textContent = "Ready when you are";
    status.className =
      "mb-7 text-xs font-medium uppercase tracking-[0.32em] text-zinc-500";
    keyAction.textContent = "to start";
    button.textContent = "Start timer";
    submit.disabled = false;
    submit.textContent = "Save result";
  }

  limitLabel.textContent = `Maximum attempt: ${format(attemptTimeLimitMs)}`;
  button.addEventListener("click", function () {
    if (state === "ready") start();
    else if (state === "running") stop();
    else openModal();
  });

  document.getElementById("close-modal").addEventListener("click", reset);
  modal.addEventListener("click", function (event) {
    if (event.target === modal) reset();
  });

  document.addEventListener("keydown", function (event) {
    const active = document.activeElement;
    const typing =
      active &&
      (["INPUT", "TEXTAREA", "SELECT"].includes(active.tagName) ||
        active.isContentEditable);
    if (
      event.code === "Space" &&
      !typing &&
      modal.classList.contains("hidden")
    ) {
      event.preventDefault();
      if (state === "ready") start();
      else if (state === "running") stop();
    }
  });

  form.addEventListener("submit", function () {
    durationInput.value = String(Math.round(durationMs));
    submit.disabled = true;
    submit.textContent = "Saving…";
  });
})();
