'use strict';
{
  const dialog = document.getElementById('vehicleDetails');
  const labels = {
    carrot: 'CarrotPlanner', upstream: 'openpilot Autospeed', inactive: '控制未介入',
    mpc: '縱向 MPC', lead0: '第一跟車目標', lead1: '第二跟車目標', lead2: '第三跟車目標', cruise: '巡航設定',
    e2e: '視覺模型', model: '模型曲率', e2eCurve: '視覺模型與彎道減速',
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
    for (const [id, key] of [['plannerProfile', 'profile'], ['speedConstraint', 'speed'], ['steeringInfluence', 'steering']]) {
      document.getElementById(id).textContent = describe(state[key]);
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
    if (dialog.open && !document.hidden) poll(generation);
  }
  new MutationObserver(refresh).observe(dialog, {attributes: true, attributeFilter: ['open']});
  document.addEventListener('visibilitychange', refresh);
}
