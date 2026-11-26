let screen = document.querySelector("#display");
// A cached pairing page can still contain the previous image element after an OTA update.
if (screen.tagName === "IMG") {
  const canvas = document.createElement("canvas");
  canvas.id = screen.id;
  canvas.className = screen.className;
  canvas.hidden = true;
  canvas.setAttribute("role", "img");
  canvas.setAttribute("aria-label", screen.alt);
  screen.replaceWith(canvas);
  screen = canvas;
}
const pair = document.querySelector("#pair");
const status = document.querySelector("#status");
const end = document.querySelector("#disconnect");

const context = screen.getContext("2d", {alpha: false});
const probe = document.createElement("canvas");
const probeContext = probe.getContext("2d", {alpha: false, willReadFrequently: true});
const maxFrameAge = 1400;
const waiting = "畫面暫停 · 等待車機影像恢復，遠端觸控已停用";
let socket, heartbeat, watchdog, pendingMove;
let decoding = false;
let nextFrame = null;
let revision = 0;
let pointer = null;
let epoch = -1;
let lastFrame = 0;
let displayedAt = 0;

function disconnect(message) {
  const previous = socket;
  socket = null;
  previous?.close();
  clearInterval(heartbeat);
  clearInterval(watchdog);
  cancelAnimationFrame(pendingMove);
  epoch = -1;
  invalidateDisplay();
  screen.hidden = true;
  context?.clearRect(0, 0, screen.width, screen.height);
  pair.hidden = false;
  end.hidden = true;
  status.textContent = message;
}

function sendTouch(type, point) {
  if (socket?.readyState !== WebSocket.OPEN || screen.hidden || !displayedAt || performance.now() - displayedAt > maxFrameAge || epoch % 4 === 2) return false;
  const rect = screen.getBoundingClientRect();
  if (!rect.width || !rect.height) return false;
  const clip = value => Math.max(0, Math.min(1, value));
  socket.send(JSON.stringify({type, epoch, x: clip((point.clientX - rect.left) / rect.width), y: clip((point.clientY - rect.top) / rect.height)}));
  return true;
}

function sendCancel() {
  // Cancel a held gesture without converting it to a click on the last known screen.
  if (pointer && socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({type: "cancel", epoch, x: 0, y: 0}));
  }
  pointer = null;
}

function invalidateDisplay() {
  sendCancel();
  displayedAt = 0;
  nextFrame = null;
  revision++;
}

function hasVisiblePixels(image, width, height) {
  if (probe.width !== width) probe.width = width;
  if (probe.height !== height) probe.height = height;
  probeContext.globalCompositeOperation = "copy";
  probeContext.drawImage(image, 0, 0, width, height);
  const pixels = probeContext.getImageData(0, 0, width, height).data;
  for (let i = 0; i < pixels.length; i += 4) {
    if (pixels[i] || pixels[i + 1] || pixels[i + 2]) return true;
  }
  return false;
}

async function drawFrames() {
  if (decoding) return;
  decoding = true;
  try {
    while (nextFrame) {
      const job = nextFrame;
      nextFrame = null;
      const url = URL.createObjectURL(new Blob([job.data.slice(4)], {type: "image/png"}));
      let timeout;
      try {
        const image = new Image();
        await new Promise((resolve, reject) => {
          image.onload = resolve;
          image.onerror = reject;
          timeout = setTimeout(() => reject(new Error("image decode timeout")), maxFrameAge);
          image.src = url;
        });
        if (job.revision !== revision || performance.now() - job.at > maxFrameAge) continue;
        if (!context || context.isContextLost?.()) throw new Error("canvas unavailable");
        // During a rolling update an older producer can still send opaque black PNGs.
        // Check a thumbnail first, then confirm at full size to preserve sparse dark detail.
        if (!hasVisiblePixels(image, 16, 8) && !hasVisiblePixels(image, image.naturalWidth, image.naturalHeight)) {
          throw new Error("empty screen capture");
        }
        if (screen.width !== image.naturalWidth) screen.width = image.naturalWidth;
        if (screen.height !== image.naturalHeight) screen.height = image.naturalHeight;
        context.drawImage(image, 0, 0);
        displayedAt = job.at;
        screen.hidden = false;
        status.textContent = [
          "停車 · 可操作車機選單",
          "行駛 · 可點按、滑動車機當下開放的介面",
          "車況切換、警示或訊號未就緒 · 暫停遠端觸控",
        ][epoch % 4];
      } catch {
        if (job.revision === revision) {
          // Keep any newer queued image. Only a successful draw enables touch again.
          sendCancel();
          displayedAt = 0;
          status.textContent = waiting;
        }
      } finally {
        clearTimeout(timeout);
        URL.revokeObjectURL(url);
      }
    }
  } finally {
    decoding = false;
  }
}

function receiveFrame(data) {
  if (!(data instanceof ArrayBuffer) || data.byteLength < 4) return;
  lastFrame = performance.now();
  const nextEpoch = new DataView(data).getUint32(0);
  if (epoch !== nextEpoch || data.byteLength === 4) {
    invalidateDisplay();
    epoch = nextEpoch;
    status.textContent = waiting;
  }
  if (data.byteLength > 4) {
    nextFrame = {data, at: lastFrame, revision};
    void drawFrames();
  }
}

screen.addEventListener("contextlost", event => {
  event.preventDefault();
  invalidateDisplay();
  if (socket) status.textContent = waiting;
});

pair.querySelector("form").onsubmit = event => {
  event.preventDefault();
  disconnect("配對中…");
  const input = pair.querySelector("input");
  const pin = input.value;
  input.value = "";
  const scheme = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(scheme + "//" + location.host + "/ws/device-screen");
  socket = ws;
  ws.binaryType = "arraybuffer";
  ws.onopen = () => { if (socket === ws) ws.send(JSON.stringify({pin})); };
  ws.onmessage = event => {
    if (socket !== ws) return;
    if (event.data !== "ready") {
      receiveFrame(event.data);
      return;
    }
    pair.hidden = true;
    end.hidden = false;
    lastFrame = performance.now();
    status.textContent = "已配對 · 等待畫面";
    heartbeat = setInterval(() => {
      if (ws.readyState !== WebSocket.OPEN) return;
      ws.send(JSON.stringify({type: "ping"}));
      if (pointer) sendTouch("move", pointer);
    }, 900);
    watchdog = setInterval(() => {
      if (performance.now() - lastFrame > 6000) {
        disconnect("車機連線逾時，請重新配對");
      } else if (displayedAt && performance.now() - displayedAt > maxFrameAge) {
        sendCancel();
        displayedAt = 0;
        status.textContent = waiting;
      }
    }, 400);
  };
  ws.onerror = ws.onclose = () => {
    if (socket === ws) disconnect("連線已結束。重新配對時請使用車機上顯示的當次配對碼。");
  };
};

screen.onpointerdown = event => {
  if (pointer || event.button !== 0 || !sendTouch("down", event)) return;
  pointer = event;
  screen.setPointerCapture(event.pointerId);
};
screen.onpointermove = event => {
  if (pointer?.pointerId !== event.pointerId) return;
  pointer = event;
  cancelAnimationFrame(pendingMove);
  pendingMove = requestAnimationFrame(() => { if (pointer) sendTouch("move", pointer); });
};
function release(event) {
  if (pointer?.pointerId !== event.pointerId) return;
  cancelAnimationFrame(pendingMove);
  if (!sendTouch(event.type === "pointerup" ? "up" : "cancel", event)) sendCancel();
  pointer = null;
}
screen.onpointerup = screen.onpointercancel = screen.onlostpointercapture = release;
end.onclick = () => disconnect("已結束連線");
window.addEventListener("pagehide", () => disconnect("已離開"));
document.addEventListener("visibilitychange", () => { if (document.hidden) disconnect("切換背景，已中斷連線"); });
