const storageKey = 'formosalink-text-size';
const minimum = 75, maximum = 250;

export function textSizePreference(storage) {
  try {
    const value = Number(storage?.getItem(storageKey));
    if (Number.isInteger(value) && value >= minimum && value <= maximum) return value;
  } catch {}
  return 100;
}

export function initTextSize() {
  const dialog = document.getElementById('text-size-dialog');
  if (!dialog) return;
  const slider = document.getElementById('text-size-range');
  const output = document.getElementById('text-size-value');
  const smaller = document.getElementById('text-smaller'), larger = document.getElementById('text-larger');
  let storage;
  try { storage = localStorage; } catch {}
  function reflow() {
    const root = document.documentElement;
    const columns = root.clientWidth / parseFloat(getComputedStyle(root).fontSize);
    root.toggleAttribute('data-compact', columns < 58);
    root.toggleAttribute('data-narrow', columns < 25);
    root.toggleAttribute('data-tight', columns < 19);
  }
  window.addEventListener('resize', reflow);

  function apply(value, save = false) {
    value = Math.max(minimum, Math.min(maximum, value));
    document.documentElement.style.fontSize = value + '%';
    reflow();
    slider.value = String(value);
    output.value = value + '%';
    slider.setAttribute('aria-valuetext', output.value);
    smaller.disabled = value === minimum;
    larger.disabled = value === maximum;
    if (save) {
      try { storage?.setItem(storageKey, String(value)); } catch {}
    }
  }

  slider.min = minimum;
  slider.max = maximum;
  slider.addEventListener('input', () => apply(slider.valueAsNumber, true));
  smaller.addEventListener('click', () => apply(slider.valueAsNumber - 10, true));
  larger.addEventListener('click', () => apply(slider.valueAsNumber + 10, true));
  document.getElementById('text-size-reset').addEventListener('click', () => apply(100, true));
  for (const button of document.querySelectorAll('[data-text-size]')) {
    button.addEventListener('click', () => dialog.showModal());
  }
  window.addEventListener('storage', event => {
    if (event.key === storageKey || event.key === null) apply(textSizePreference(storage));
  });
  apply(textSizePreference(storage));
}
