// Keep the native catalog name as the value written to the device. The reported
// 2025 HEV used this exact ccNC selection, which the catalog lists by HDA package.
function sorentoHev(name, platform) {
  return platform === 'KIA_SORENTO_2024' && name === 'Kia Sorento (without HDA II) 2024-25';
}

function vehicleLabel(name, vehicles, t) {
  return sorentoHev(name, vehicles[name]) ? t('sorentoHevLabel') : name;
}

export function matchingVehicles(vehicles, query) {
  const terms = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return Object.keys(vehicles).filter(name => {
    if (!terms.length) return true;
    const years = [];
    for (const [, first, last] of name.matchAll(/\b(\d{4})[-–](\d{2,4})\b/g)) {
      const end = last.length === 2 ? Number(first.slice(0, 2) + last) : Number(last);
      for (let year = Number(first); year <= Math.min(end, Number(first) + 99); year++) years.push(year);
    }
    const aliases = sorentoHev(name, vehicles[name]) || /\bhybrid\b/i.test(name) && !/plug-in/i.test(name)
      ? ' HEV Hybrid 油電 ハイブリッド' : '';
    const text = [name, vehicles[name], ...years, aliases].join(' ').toLowerCase();
    return terms.every(term => text.includes(term));
  }).sort();
}

export function vehiclePicker(editor, entry, initialValue, filter, {el, t, disabled, onFilter, onChoose}) {
  const vehicles = entry.vehicles;
  const search = el('input');
  search.type = 'search';
  search.dataset.field = 'vehicle-search';
  search.value = filter;
  search.placeholder = t('vehicleSearch');
  search.setAttribute('aria-label', t('vehicleSearch'));
  const select = el('select');
  select.dataset.field = 'value';
  select.setAttribute('aria-label', t('vehicleChoice'));
  select.disabled = disabled;
  const noMatches = el('small', t('noSearchResults'), 'workspace-muted');
  const preview = el('output');
  let value = initialValue;

  function renderChoices() {
    const matches = matchingVehicles(vehicles, search.value);
    select.replaceChildren(new Option(t('vehicleAutomatic'), ''));
    // Keep the saved choice or draft selected when a search filters it out.
    if (value && !matches.includes(value)) {
      const current = new Option(vehicleLabel(value, vehicles, t), value);
      current.disabled = !Object.hasOwn(vehicles, value);
      select.add(current);
    }
    for (const name of matches) select.add(new Option(vehicleLabel(name, vehicles, t), name));
    select.value = value;
    noMatches.hidden = matches.length > 0;
  }
  function showChoice() {
    preview.hidden = !value;
    preview.textContent = value ? [vehicleLabel(value, vehicles, t), vehicles[value]].filter(Boolean).join(' · ') : '';
  }
  search.addEventListener('input', () => {
    onFilter(search.value);
    renderChoices();
  });
  select.addEventListener('change', () => {
    value = select.value;
    onChoose(value);
    showChoice();
  });
  editor.classList.add('vehicle-picker');
  editor.append(search, select, noMatches, preview);
  renderChoices();
  showChoice();
}
