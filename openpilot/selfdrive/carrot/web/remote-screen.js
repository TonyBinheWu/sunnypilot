const img = document.querySelector("#display");
const pair = document.querySelector("#pair");
const status = document.querySelector("#status");
const end = document.querySelector("#disconnect");

let socket, heartbeat, watchdog, frameUrl, pendingMove;
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
  pointer = null;
  epoch = -1;
  displayedAt = 0;
  img.hidden = true;
  img.onload = null;
  img.removeAttribute("src");
  if (frameUrl) URL.revokeObjectURL(frameUrl);
  frameUrl = null;
  pair.hidden = false;
  end.hidden = true;
  status.textContent = message;
}

function sendTouch(type, point) {
  if (socket?.readyState !== WebSocket.OPEN || img.hidden || !displayedAt || performance.now() - displayedAt > 1400 || epoch % 4 === 2) return false;
  const rect = img.getBoundingClientRect();
  if (!rect.width || !rect.height) return false;
  const clip = value => Math.max(0, Math.min(1, value));
  socket.send(JSON.stringify({type, epoch, x: clip((point.clientX - rect.left) / rect.width), y: clip((point.clientY - rect.top) / rect.height)}));
  return true;
}

function receiveFrame(ws, data) {
  if (!(data instanceof ArrayBuffer) || data.byteLength <= 4) return;
  const receivedAt = performance.now();
  lastFrame = receivedAt;
  const nextEpoch = new DataView(data).getUint32(0);
  if (epoch !== nextEpoch) {
    pointer = null;
    displayedAt = 0;
    img.hidden = true;
  }
  const previous = frameUrl;
  const url = URL.createObjectURL(new Blob([data.slice(4)], {type: "image/png"}));
  frameUrl = url;
  img.onload = () => {
    if (socket !== ws || frameUrl !== url) return;
    epoch = nextEpoch;
    displayedAt = receivedAt;
    img.hidden = false;
    status.textContent = [
      "停車 · 可操作車機選單",
      "行駛 · 可點按、滑動車機當下開放的介面",
      "車況切換、警示或訊號未就緒 · 暫停遠端觸控",
    ][epoch % 4];
  };
  img.src = url;
  if (previous) URL.revokeObjectURL(previous);
}

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
      receiveFrame(ws, event.data);
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
      if (performance.now() - lastFrame > 2500) disconnect("畫面逾時，連線已結束");
    }, 400);
  };
  ws.onerror = ws.onclose = () => {
    if (socket === ws) disconnect("連線已結束。重新配對時請使用車機上顯示的當次配對碼。");
  };
};

img.onpointerdown = event => {
  if (pointer || event.button !== 0 || !sendTouch("down", event)) return;
  pointer = event;
  img.setPointerCapture(event.pointerId);
};
img.onpointermove = event => {
  if (pointer?.pointerId !== event.pointerId) return;
  pointer = event;
  cancelAnimationFrame(pendingMove);
  pendingMove = requestAnimationFrame(() => { if (pointer) sendTouch("move", pointer); });
};
function release(event) {
  if (pointer?.pointerId !== event.pointerId) return;
  cancelAnimationFrame(pendingMove);
  sendTouch(event.type === "pointerup" ? "up" : "cancel", event);
  pointer = null;
}
img.onpointerup = img.onpointercancel = img.onlostpointercapture = release;
end.onclick = () => disconnect("已結束連線");
window.addEventListener("pagehide", () => disconnect("已離開"));
document.addEventListener("visibilitychange", () => { if (document.hidden) disconnect("切換背景，已中斷連線"); });
