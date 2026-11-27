export const isModelSlot = key => /^DrivingModel(?:Small|Big)(?:Page\d+)?$/.test(key);

export function modelStatus(parent, snapshot, {el, t}) {
  const box = el('section', undefined, 'workspace-card model-status');
  box.append(el('h2', t('modelConfigured')));
  let info;
  try { info = JSON.parse(snapshot.info?.model_manager); } catch {}
  if (!Array.isArray(info?.configured)) {
    box.append(el('p', t('modelUpgrade')));
  } else {
    const list = el('dl', undefined, 'device-details');
    for (const [i, title] of ['modelSmall','modelBig'].entries()) {
      list.append(el('dt', t(title)), el('dd', String(info.configured[i] || '—')));
    }
    box.append(list);
    if(snapshot.info.egpu_status==='not_installed') box.append(el('p', t('modelChestnutHardware'), 'workspace-muted'));
    const status = el('p', [t('modelState_' + info.status), info.name].filter(Boolean).join(' · '));
    status.setAttribute('role', 'status');
    box.append(status);
    if (Number.isFinite(info.percent) && ['downloading','verifying'].includes(info.status)) {
      const bar = el('progress');
      bar.max = 100;
      bar.value = info.percent;
      bar.setAttribute('aria-label', t('modelProgress'));
      status.append(' ' + info.percent + '%', bar);
    }
    if (!snapshot.catalog.some(e => isModelSlot(e.key) && e.options?.length > 1)) box.append(el('p', t('modelNoCatalog')));
  }
  const current = parent.querySelector('.model-status');
  if (current) current.replaceWith(box);
  else parent.append(box);
}

export function modelPicker(editor, entry, value, blocked, filter, {el, label, t, change, setFilter}) {
  editor.classList.add('vehicle-picker');
  const search = el('input'), select = el('select'), count = el('output');
  search.type = 'search';
  search.placeholder = t('modelSearch');
  search.setAttribute('aria-label', search.placeholder + ' · ' + label(entry.title));
  search.dataset.field = 'model-filter';
  search.value = filter;
  select.dataset.field = 'value';
  select.setAttribute('aria-label', label(entry.title));
  function render() {
    const query = search.value.trim().toLocaleLowerCase();
    const matches = entry.options.filter(o => !query || label(o.label).toLocaleLowerCase().includes(query));
    select.replaceChildren();
    if (!matches.some(o => o.value === value)) {
      const prompt = el('option', t('modelChoose'));
      prompt.value = '-';
      prompt.disabled = prompt.selected = true;
      select.append(prompt);
    }
    for (const option of matches) {
      const node = el('option', label(option.label));
      node.value = option.value;
      node.selected = value === option.value;
      node.disabled = !option.enabled;
      select.append(node);
    }
    select.disabled = blocked || !matches.length;
    count.textContent = matches.length ? t('modelMatches') + ' ' + matches.length : t('noSearchResults');
  }
  search.addEventListener('input', () => { setFilter(search.value); render(); });
  select.addEventListener('change', () => { value = select.value; change(value); });
  editor.append(search, select, count);
  render();
}
