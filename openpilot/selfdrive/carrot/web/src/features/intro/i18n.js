"use strict";

/* 인트로 문구
 *
 * 웹 UI 언어는 ko/en/zh/zh-tw 4종 (web_settings.py: WEB_LANGUAGES).
 * 줄바꿈(\n)은 언어마다 자연스러운 지점에 직접 넣는다.
 * 한 문장을 3개 언어에 기계적으로 맞추지 않는다.
 *
 * 설명은 한 줄로 끝낸다. 선택 화면에서 문단을 읽게 하지 않는다 —
 * 각 선택지가 답해야 하는 건 두 가지뿐이다: 하네스가 어디에 붙었나,
 * 가감속은 누가 하나.
 *
 * 예외는 legalBody 하나다. 이건 훑는 글이 아니라 읽는 글이라
 * 문단 배열로 둔다 (한 문자열에 \n\n 을 넣지 않는다 — 구조가 곧 문단). */

globalThis.CarrotIntroI18n = {
  ko: {
    restore: "기존 설정 불러오기",
    back: "이전",
    preview: "미리보기 · 저장되지 않음",
    previewClose: "닫기",

    carTitle: "차량을 선택하세요",
    carBackToList: "목록으로",
    carEmpty: "지원 차량 목록을 불러오지 못했어요.",

    hdaTitle: "HDA 종류",
    hda1: "HDA1",
    hda1d: "대부분의 CAN 차량",
    hda2: "HDA2",
    hda2d: "CAN-FD 차량",

    ctrlTitle: "주행제어 방식",
    ctrlSub: "하네스를 어디에 연결하셨나요?",

    /* ① 하네스가 ADAS/레이더에 있으면 코너레이더까지 쓴다 */
    p1: "ADAS · 레이더 롱컨",
    p1d: "ADAS·레이더에 연결 · 코너레이더까지",

    /* ② 당근파일럿 전용.
       근거 — opendbc/car/hyundai/interface.py:179 의 `# carrot` 분기:
       순정 openpilot 은 alpha_long 이 켜져야만 롱컨을 하는데,
       당근파일럿은 CAMERA_SCC 가 켜지면 그 게이트를 무시하고
       openpilotLongitudinalControl 을 강제로 True 로 만든다.
       SCC 메시지는 카메라 버스에서 읽는다 (carstate.py:228). */
    p2: "카메라 롱컨",
    p2d: "SCC 신호가 카메라로 가는 차량",

    /* ③ HyundaiCameraSCC=0 이라 롱컨 강제가 없고,
       SpeedFromPCM=2 로 커브/카메라 감속만 버튼으로 넣는다. */
    p3: "순정",
    p3d: "가감속은 순정 SCC · 조향만",

    legalTitle: "법적 고지",
    legalBody: [
      "대한민국 자동차관리법 개정안에 따라, 본 소프트웨어를 실제 차량에 장착하거나 주행에 사용하는 것은 법률에 위배될 수 있습니다.",
      "이 저장소에 있는 모든 소프트웨어는 연구, 실험, 시뮬레이션 목적으로만 제공됩니다.",
      "개발자는 본 소프트웨어의 실제 사용으로 인해 발생하는 모든 법적 책임을 지지 않습니다.",
    ],
    legalAck: "확인했습니다",

    outTitle: "준비됐어요",
    outSub: "궁금한 점은 언제든\n당근서버에 물어보세요.",
    start: "시작하기",
    previewDone: "미리보기 닫기",

    rsTitle: "설정 불러오기",
    rsSub: "이전 기기의 백업에서 그대로.",
    rsFile: "백업 파일 선택",
    rsFiled: "params_backup.json",
    rsDone: "설정을 가져왔어요.",
  },

  en: {
    restore: "Restore my settings",
    back: "Back",
    preview: "Preview · Not saved",
    previewClose: "Close",

    carTitle: "Choose your car",
    carBackToList: "Back to list",
    carEmpty: "Could not load the supported car list.",

    hdaTitle: "HDA generation",
    hda1: "HDA1",
    hda1d: "Most CAN cars",
    hda2: "HDA2",
    hda2d: "CAN-FD cars",

    ctrlTitle: "Driving control",
    ctrlSub: "Where is your harness connected?",

    p1: "ADAS · radar long",
    p1d: "On ADAS or radar · corner radar too",

    p2: "Camera long",
    p2d: "On the camera only · CarrotPilot drives accel",

    p3: "Stock",
    p3d: "Stock SCC drives accel · steering only",

    legalTitle: "Legal notice",
    legalBody: [
      "Under the amended Motor Vehicle Management Act of the Republic of Korea, installing this software in an actual vehicle or using it while driving may violate the law.",
      "All software in this repository is provided for research, experimentation, and simulation purposes only.",
      "The developers accept no legal liability whatsoever arising from actual use of this software.",
    ],
    legalAck: "I understand",

    outTitle: "You're all set",
    outSub: "Questions? Just ask\non the Carrot server.",
    start: "Start",
    previewDone: "Close preview",

    rsTitle: "Restore settings",
    rsSub: "Straight from a previous device.",
    rsFile: "Choose backup file",
    rsFiled: "params_backup.json",
    rsDone: "Settings restored.",
  },

  zh: {
    restore: "导入已有设置",
    back: "返回",
    preview: "预览 · 不保存",
    previewClose: "关闭",

    carTitle: "请选择车辆",
    carBackToList: "返回列表",
    carEmpty: "无法加载支持的车辆列表。",

    hdaTitle: "HDA 代次",
    hda1: "HDA1",
    hda1d: "多数 CAN 车型",
    hda2: "HDA2",
    hda2d: "CAN-FD 车型",

    ctrlTitle: "驾驶控制方式",
    ctrlSub: "线束连接在哪里？",

    p1: "ADAS · 雷达纵向",
    p1d: "接至 ADAS 或雷达 · 含角雷达",

    p2: "摄像头纵向",
    p2d: "仅接至摄像头 · 当根领航负责加减速",

    p3: "原厂",
    p3d: "加减速交给原厂 SCC · 仅转向",

    legalTitle: "法律声明",
    legalBody: [
      "根据大韩民国《汽车管理法》修正案，将本软件安装于实际车辆或用于行驶可能违反法律。",
      "本仓库中的所有软件仅供研究、实验与仿真用途。",
      "开发者对因实际使用本软件而产生的一切法律责任概不负责。",
    ],
    legalAck: "我已知悉",

    outTitle: "准备就绪",
    outSub: "有任何疑问\n欢迎在当根服务器提问。",
    start: "开始",
    previewDone: "关闭预览",

    rsTitle: "导入设置",
    rsSub: "直接从旧设备的备份导入。",
    rsFile: "选择备份文件",
    rsFiled: "params_backup.json",
    rsDone: "设置已导入。",
  },
  "zh-tw": {
    restore: "匯入已有設定",
    back: "返回",
    preview: "預覽 · 不儲存",
    previewClose: "關閉",

    carTitle: "請選擇車輛",
    carBackToList: "返回列表",
    carEmpty: "無法載入支援的車輛列表。",

    hdaTitle: "HDA 代次",
    hda1: "HDA1",
    hda1d: "多數 CAN 車型",
    hda2: "HDA2",
    hda2d: "CAN-FD 車型",

    ctrlTitle: "駕駛控制方式",
    ctrlSub: "線束連線在哪裡？",

    p1: "ADAS · 雷達縱向",
    p1d: "接至 ADAS 或雷達 · 含角雷達",

    p2: "攝影機縱向",
    p2d: "僅接至攝影機 · 當根領航負責加減速",

    p3: "原廠",
    p3d: "加減速交給原廠 SCC · 僅轉向",

    legalTitle: "法律宣告",
    legalBody: [
      "根據大韓民國《汽車管理法》修正案，將本軟體安裝於實際車輛或用於行駛可能違反法律。",
      "本倉庫中的所有軟體僅供研究、實驗與模擬用途。",
      "開發者對因實際使用本軟體而產生的一切法律責任概不負責。",
    ],
    legalAck: "我已知悉",

    outTitle: "準備就緒",
    outSub: "有任何疑問\n歡迎在當根伺服器提問。",
    start: "開始",
    previewDone: "關閉預覽",

    rsTitle: "匯入設定",
    rsSub: "直接從舊裝置的備份匯入。",
    rsFile: "選擇備份檔案",
    rsFiled: "params_backup.json",
    rsDone: "設定已匯入。",
  },
};

// Repeat setup shares the original steps; writes remain staged until final apply.
Object.assign(CarrotIntroI18n["en"], {
  "againError_apply_unconfirmed": "Could not confirm whether settings were saved. Stay parked, cancel and reopen the guide to check current values before trying again.",
  "againTitle": "Run setup again",
  "againNote": "Setup draft · nothing saved yet",
  "againCancel": "Cancel setup",
  "againDraft": "Choose language, vehicle, HDA and control mode again. Choices stay in this draft until Apply. Cancel returns to Tools without changing settings.",
  "againRestore": "To import a backup, cancel this guide and use Restore Settings in Tools. Backup import is a separate operation.",
  "againKeepCar": "Keep current vehicle",
  "againKeepHda": "Keep current HDA configuration",
  "againKeepControl": "Keep current driving-control settings",
  "againReview": "Review changes",
  "againReviewHelp": "Only the listed items will change. Selecting a control preset replaces its listed values, including custom tuning. Apply while parked and disengaged, or with the vehicle switched off.",
  "againApply": "Apply these changes",
  "againNoChanges": "No changes selected.",
  "againSaved": "Settings saved",
  "againSavedHelp": "Setup is complete. Return to Tools.",
  "againRestart": "Vehicle configuration changed. Keep the vehicle parked and restart the device before using driving assistance. No automatic reboot is performed.",
  "againReturn": "Return to Tools",
  "againVehicle": "Vehicle",
  "againLanguage": "Web / APK language",
  "againError_settings_changed": "Settings changed while this guide was open. Cancel and reopen the guide to read current values.",
  "againError_write_failed": "Could not apply settings. Previous values were restored where necessary. You can retry while parked.",
  "againError_rollback_incomplete": "Some settings could not be restored. Keep driving assistance off and review vehicle settings while parked.",
  "againError_vehicle_unavailable": "Fresh vehicle/device state is unavailable. Park and disengage, or switch off the vehicle, then try again.",
  "againError_park_required": "Shift to Park and stop the vehicle, or switch off the vehicle, before applying.",
  "againError_controls_active": "Disengage steering and cruise control before applying.",
  "againError_controls_unavailable": "Control status is unavailable. Switch off the vehicle and wait for fresh device state.",
  "againError_moving": "Stop and shift to Park before applying.",
  "againError_invalid_selection": "Invalid choices. Cancel and reopen the guide.",
  "againError_unknown_car": "This vehicle is not in the supported list. Choose a listed vehicle.",
  "againError_invalid_hda": "HDA selection is invalid for this vehicle.",
  "againError_invalid_preset": "Choose an available control mode.",
  "againError_params_unavailable": "Device settings are unavailable. Update the vehicle and reopen the guide."
});
Object.assign(CarrotIntroI18n["zh-tw"], {
  "againError_apply_unconfirmed": "無法確認設定是否已儲存。請保持停車，取消並重新開啟引導，核對目前數值後再操作。",
  "againTitle": "重新執行設定引導",
  "againNote": "重新設定 · 套用前不會儲存",
  "againCancel": "取消設定",
  "againDraft": "可重新選擇語言、車型、HDA 與駕駛控制方式。選項先暫存，最後確認才套用；取消會回到工具並保留原設定。",
  "againRestore": "若要匯入備份，請先取消此引導，再使用工具的「還原設定」。備份匯入屬於獨立操作。",
  "againKeepCar": "保留目前車型",
  "againKeepHda": "保留目前 HDA 設定",
  "againKeepControl": "保留目前駕駛控制設定",
  "againReview": "確認要變更的設定",
  "againReviewHelp": "只會變更下列項目。選擇控制預設組合會覆蓋列出的原值，包括自行調校過的值。請停車排 P 檔並關閉轉向／巡航控制，或停車熄火後套用。",
  "againApply": "確認並套用",
  "againNoChanges": "沒有選擇任何變更。",
  "againSaved": "設定已儲存",
  "againSavedHelp": "重新設定已完成，可返回工具。",
  "againRestart": "車輛配置已變更。請保持停車，完整重新啟動車機後再使用駕駛輔助；本引導不會自動重新啟動。",
  "againReturn": "返回工具",
  "againVehicle": "車型",
  "againLanguage": "網頁／APK 語言",
  "againError_settings_changed": "引導開啟後，設定已由其他來源變更。請取消並重新開啟引導，讀取目前數值。",
  "againError_write_failed": "無法套用設定，已盡可能還原原值。保持停車後可重試。",
  "againError_rollback_incomplete": "部分設定未能還原。請先保持駕駛輔助關閉，停車檢查車輛設定後再使用。",
  "againError_vehicle_unavailable": "尚無新鮮的車輛／裝置狀態。請停車並關閉控制，或停車熄火後等待裝置連線，再重試。",
  "againError_park_required": "請停車排 P 檔，或停車熄火後再套用。",
  "againError_controls_active": "請先關閉轉向與巡航控制，再套用設定。",
  "againError_controls_unavailable": "無法確認控制狀態。請停車熄火，等待新的裝置狀態後再套用。",
  "againError_moving": "請完全停車並排 P 檔，再套用設定。",
  "againError_invalid_selection": "選項無效，請取消並重新開啟引導。",
  "againError_unknown_car": "此車型不在支援列表內，請重新選擇列表中的車型。",
  "againError_invalid_hda": "此車型的 HDA 選項無效，請重新選擇。",
  "againError_invalid_preset": "請重新選擇可用的控制方式。",
  "againError_params_unavailable": "無法讀取車機設定。請更新車機並重新開啟引導。"
});
Object.assign(CarrotIntroI18n["zh"], {
  "againError_apply_unconfirmed": "无法确认设置是否已保存。请保持停车，取消并重新打开引导，核对当前数值后再操作。",
  "againTitle": "重新执行设定引导",
  "againNote": "重新设定 · 套用前不会储存",
  "againCancel": "取消设定",
  "againDraft": "可重新选择语言、车型、HDA 与驾驶控制方式。选项先暂存，最后确认才套用；取消会回到工具并保留原设定。",
  "againRestore": "若要汇入备份，请先取消此引导，再使用工具的「还原设定」。备份汇入属于独立操作。",
  "againKeepCar": "保留目前车型",
  "againKeepHda": "保留目前 HDA 设定",
  "againKeepControl": "保留目前驾驶控制设定",
  "againReview": "确认要变更的设定",
  "againReviewHelp": "只会变更下列项目。选择控制预设组合会覆盖列出的原值，包括自行调校过的值。请停车排 P 档并关闭转向／巡航控制，或停车熄火后套用。",
  "againApply": "确认并套用",
  "againNoChanges": "没有选择任何变更。",
  "againSaved": "设定已储存",
  "againSavedHelp": "重新设定已完成，可返回工具。",
  "againRestart": "车辆配置已变更。请保持停车，完整重新启动车机后再使用驾驶辅助；本引导不会自动重新启动。",
  "againReturn": "返回工具",
  "againVehicle": "车型",
  "againLanguage": "网页／APK 语言",
  "againError_settings_changed": "引导开启后，设定已由其他来源变更。请取消并重新开启引导，读取目前数值。",
  "againError_write_failed": "无法套用设定，已尽可能还原原值。保持停车后可重试。",
  "againError_rollback_incomplete": "部分设定未能还原。请先保持驾驶辅助关闭，停车检查车辆设定后再使用。",
  "againError_vehicle_unavailable": "尚无新鲜的车辆／装置状态。请停车并关闭控制，或停车熄火后等待装置连线，再重试。",
  "againError_park_required": "请停车排 P 档，或停车熄火后再套用。",
  "againError_controls_active": "请先关闭转向与巡航控制，再套用设定。",
  "againError_controls_unavailable": "无法确认控制状态。请停车熄火，等待新的装置状态后再套用。",
  "againError_moving": "请完全停车并排 P 档，再套用设定。",
  "againError_invalid_selection": "选项无效，请取消并重新开启引导。",
  "againError_unknown_car": "此车型不在支援列表内，请重新选择列表中的车型。",
  "againError_invalid_hda": "此车型的 HDA 选项无效，请重新选择。",
  "againError_invalid_preset": "请重新选择可用的控制方式。",
  "againError_params_unavailable": "无法读取车机设定。请更新车机并重新开启引导。"
});
Object.assign(CarrotIntroI18n["ko"], {
  "againError_apply_unconfirmed": "설정 저장 여부를 확인하지 못했습니다. 정차 상태에서 취소 후 안내를 다시 열어 현재 값을 확인한 뒤 다시 시도하세요.",
  "againTitle": "설정 마법사 다시 실행",
  "againNote": "설정 초안 · 아직 저장하지 않음",
  "againCancel": "설정 취소",
  "againDraft": "언어, 차량, HDA와 주행제어 방식을 다시 선택합니다. 적용하기 전에는 초안이며 취소하면 기존 설정을 유지합니다.",
  "againRestore": "백업을 가져오려면 안내를 취소하고 도구의 설정 복원을 사용하세요. 백업 복원은 별도 작업입니다.",
  "againKeepCar": "현재 차량 유지",
  "againKeepHda": "현재 HDA 설정 유지",
  "againKeepControl": "현재 주행제어 설정 유지",
  "againReview": "변경 확인",
  "againReviewHelp": "목록의 항목만 변경됩니다. 제어 프리셋을 선택하면 사용자 조정값도 덮어씁니다. P단 정차 및 제어 해제 상태나 시동을 끈 상태에서 적용하세요.",
  "againApply": "확인 후 적용",
  "againNoChanges": "선택한 변경 사항이 없습니다.",
  "againSaved": "설정 저장 완료",
  "againSavedHelp": "설정이 완료되었습니다. 도구로 돌아가세요.",
  "againRestart": "차량 구성이 변경되었습니다. 정차 상태에서 장치를 완전히 재부팅한 뒤 운전 보조를 사용하세요. 자동으로 재부팅하지 않습니다.",
  "againReturn": "도구로 돌아가기",
  "againVehicle": "차량",
  "againLanguage": "웹 / APK 언어",
  "againError_settings_changed": "안내가 열린 동안 다른 곳에서 설정이 변경되었습니다. 취소 후 다시 열어 현재 값을 확인하세요.",
  "againError_write_failed": "설정을 적용하지 못해 이전 값으로 복원했습니다. 정차 상태에서 다시 시도하세요.",
  "againError_rollback_incomplete": "일부 설정을 복원하지 못했습니다. 운전 보조를 끄고 정차 상태에서 차량 설정을 확인하세요.",
  "againError_vehicle_unavailable": "최신 차량·장치 상태를 확인할 수 없습니다. 정차 및 제어 해제 또는 시동을 끈 후 다시 시도하세요.",
  "againError_park_required": "P단으로 정차하거나 정차 후 시동을 끄고 적용하세요.",
  "againError_controls_active": "조향과 크루즈 제어를 해제한 뒤 적용하세요.",
  "againError_controls_unavailable": "제어 상태를 확인할 수 없습니다. 정차 후 시동을 끄고 최신 장치 상태를 기다리세요.",
  "againError_moving": "완전히 정차하고 P단에서 적용하세요.",
  "againError_invalid_selection": "선택이 잘못되었습니다. 취소 후 안내를 다시 여세요.",
  "againError_unknown_car": "지원 목록에 없는 차량입니다. 목록의 차량을 선택하세요.",
  "againError_invalid_hda": "이 차량에 유효하지 않은 HDA 선택입니다.",
  "againError_invalid_preset": "사용 가능한 제어 방식을 선택하세요.",
  "againError_params_unavailable": "장치 설정을 읽을 수 없습니다. 장치를 업데이트하고 안내를 다시 여세요."
});

/* 0단계에서 순환하며 보여주고, 그대로 선택지가 되는 목록 */
globalThis.CarrotIntroLangs = [
  ["en", "English", "Welcome!"],
  ["ko", "한국어",  "오셨군요!"],
  ["zh", "简体中文", "欢迎!"],
  ["zh-tw", "繁體中文", "歡迎！"],
];

/* 브라우저 언어 감지 → 기본값. 못 알아보면 영어.
 * navigator.languages 를 순서대로 훑어 처음 맞는 것을 쓴다.
 *   ko, ko-KR        → ko
 *   zh, zh-CN → zh; zh-TW, zh-Hant → zh-tw
 *   그 외             → en  */
globalThis.detectCarrotIntroLang = function detectCarrotIntroLang() {
  const supported = new Set(CarrotIntroLangs.map(([code]) => code));
  const tags = [
    ...(Array.isArray(navigator.languages) ? navigator.languages : []),
    navigator.language || "",
  ];
  for (const tag of tags) {
    const normalized = String(tag).toLowerCase().replaceAll("_", "-");
    if (/^zh-(?:tw|hk|mo|hant|cht)(?:-|$)/.test(normalized)) return "zh-tw";
    const base = normalized.split("-")[0];
    if (supported.has(base)) return base;
  }
  return "en";
};
