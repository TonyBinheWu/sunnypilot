/* Read-only compact-channel liveness. No settings, camera or control writes. */
(function (target) {
  'use strict';
  function watch(ws, lost, options = {}) {
    const now = options.now || (() => performance.now());
    const schedule = options.setTimeout || target.setTimeout.bind(target);
    const cancel = options.clearTimeout || target.clearTimeout.bind(target);
    const active = options.active || (() => true);
    let timer = null, stopped = false, alive = now(), pingAt = -Infinity;
    const created = alive;
    function received() { if (!stopped) alive = now(); }
    function pong(event) {
      if (typeof event.data !== 'string' || event.data.length > 256) return;
      try { if (JSON.parse(event.data)?.type === 'pong') received(); } catch {}
    }
    function stop() {
      stopped = true; cancel(timer); timer = null;
      ws.removeEventListener('message', pong);
    }
    function fail(reason) { stop(); if (active()) lost(reason); }
    function tick() {
      if (stopped || !active()) { stop(); return; }
      const time = now();
      if (ws.readyState === 0 && time - created >= 8000) { fail('connect-timeout'); return; }
      if (ws.readyState === 1) {
        if (time - alive >= 12000) { fail('heartbeat-timeout'); return; }
        if (time - pingAt >= 5000) {
          try { ws.send('{"type":"ping"}'); pingAt = time; }
          catch { fail('send-failed'); return; }
        }
      } else if (ws.readyState >= 2) { fail('socket-closed'); return; }
      timer = schedule(tick, 1000);
    }
    ws.addEventListener('message', pong);
    timer = schedule(tick, 1000);
    return Object.freeze({received, stop});
  }
  target.CarrotCompactConnection = Object.freeze({watch});
})(window);
