const finite = (value) => value != null && value !== "" && Number.isFinite(Number(value)) ? Number(value) : null;

// Observe the existing presentation channel. An open socket or fresh HUD data
// cannot prove that a camera picture was actually drawn.
export function createLiveFrameHealth() {
  let frames = [], sequence = null, source = null;
  function reset() { frames = []; sequence = null; source = null; }
  function observe(frame, now) {
    if (!frame || frame.reason === "late-rtp-mapping" || !Number.isFinite(now)) return;
    if (frame.sequence === sequence && frame.source === source) return;
    if (frame.source !== source || (frames.length && now < frames.at(-1))) reset();
    source = frame.source;
    sequence = frame.sequence;
    frames.push(now);
    while (frames.length > 240 || now - frames[0] > 2000) frames.shift();
  }
  function snapshot({ now, wallNow, replay = false, perf = {} } = {}) {
    perf = perf || {};
    const last = frames.at(-1);
    const age = last == null || !Number.isFinite(now) || now < last ? null : now - last;
    const fresh = age != null && age <= 2000;
    const sampleAge = finite(perf.collectedAtMs) == null ? null : wallNow - perf.collectedAtMs;
    const statsFresh = !replay && sampleAge != null && sampleAge >= 0 && sampleAge <= 6000;
    const recent = frames.filter(t => now >= t && now - t <= 2000);
    const span = recent.length > 1 ? recent.at(-1) - recent[0] : 0;
    const fps = fresh && span > 0 ? (recent.length - 1) * 1000 / span : null;
    const reconnecting = statsFresh && ["connecting", "disconnected", "failed"].includes(perf.connectionState);
    return {
      state: replay ? "replay" : fresh && source === "live" ? "playing" : reconnecting ? "reconnecting" : age == null ? "waiting" : "stalled",
      fps: replay ? null : fps,
      ageMs: replay ? null : age,
      resolution: statsFresh ? String(perf.network?.resolutionLabel || "—") : "—",
      rttMs: statsFresh ? finite(perf.network?.rttMs) : null,
      bitrateMbps: statsFresh ? finite(perf.network?.bitrateMbps) : null,
    };
  }
  return { reset, observe, snapshot };
}
