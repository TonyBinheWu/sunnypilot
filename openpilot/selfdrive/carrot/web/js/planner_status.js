'use strict';
{
  const dialog = document.getElementById('vehicleDetails');
  const labels = {
    visionE2e: '純視覺端到端（實驗）', visionLead: '鏡頭辨識前車', stockLong: '原廠巡航控制加減速',
    cruiseOnly: '僅巡航，轉向由駕駛操作', sunny: '模型與跟車協同', mapCurve: '地圖彎速', speedLimit: '導航道路速限', blinkerPause: '低速方向燈暫停轉向',
    carrot: 'CarrotPlanner', upstream: 'openpilot Autospeed', inactive: '控制未介入',
    mpc: '縱向 MPC', lead0: '第一跟車目標', lead1: '第二跟車目標', lead2: '第三跟車目標', cruise: '巡航設定',
    e2e: '視覺模型', openingLead: '前車拉遠，平順恢復巡航', model: '模型曲率', e2eCurve: '視覺模型與彎道減速',
    hkgCurve: 'HKG 彎道限速', forceDecel: '系統要求減速', softHold: '停車保持',
    signalPrepare: '號誌預備減速', signalHold: '號誌起步等待', modelFilter: '模型曲率平滑',
    hkgFilter: 'HKG 曲率平滑', laneLines: '車道線規劃', holdCurvature: '維持目前曲率',
  };
  function describe(value) {
    if (!value) return '等待資料';
    if (value.startsWith('carrot/')) {
      const source = value.slice('carrot/'.length);
      const names = {atc: '前方轉向', atc2: '下一個轉向', cam: '測速照相', section: '區間測速',
        police: '警示點', bump: '減速丘', hda: '原車速限', hda_bump: '原車減速丘',
        school: '學校區域', hda_section: '原車區間測速', road: '道路速限', vturn: '彎道', route: '導航路線'};
      return 'Carrot · ' + (names[source] || source || '限速');
    }
    if (value.endsWith('+limit')) return describe(value.slice(0, -6)) + ' · 曲率受限';
    return labels[value] || value;
  }
  let timer, generation = 0;
  function render(state) {
    const setup = {native: '視覺縱橫向', alpha: '視覺縱橫向（Alpha）', stock: '視覺轉向／原廠巡航', passive: '僅行車記錄'};
    const providers = {native: 'openpilot 縱向', alpha: 'Alpha 縱向', stock: '原廠巡航', passive: '僅行車記錄'};
    let profile = describe(state.profile);
    if (state.profile === 'sunny' && providers[state.setup]) profile += ' · ' + providers[state.setup];
    if (state.profile === 'visionE2e' && setup[state.setup]) profile = '純視覺自動適配 · ' + setup[state.setup];
    const ceiling = state.cruiseCeilingKph;
    document.getElementById('plannerCeiling').textContent = Number.isFinite(ceiling) ? ceiling + ' km/h' : '—';
    document.getElementById('visionSetSpeed').textContent = Number.isFinite(ceiling) ? ceiling : '—';
    for (const [id, key] of [['plannerProfile', 'profile'], ['speedConstraint', 'speed'], ['steeringInfluence', 'steering']]) {
      document.getElementById(id).textContent = key === 'profile' ? profile : describe(state[key]);
    }
  }
  async function poll(current) {
    let state = {};
    try {
      const response = await fetch('/api/planner/status', {cache: 'no-store', signal: AbortSignal.timeout(1500)});
      if (response.ok) state = await response.json();
    } catch {}
    if (current !== generation) return;
    render(state);
    timer = setTimeout(() => poll(current), 750);
  }
  function refresh() {
    clearTimeout(timer);
    generation++;
    render({});
    if ((dialog.open || document.body.dataset.panel === 'vision') && !document.hidden) poll(generation);
  }
  new MutationObserver(refresh).observe(dialog, {attributes: true, attributeFilter: ['open']});
  new MutationObserver(refresh).observe(document.body, {attributes: true, attributeFilter: ['data-panel']});
  document.addEventListener('visibilitychange', refresh);
  refresh();
}
