<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_BASIC" param="ClusterHud" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 활성화(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 기본

---

<!-- CARROT:SETTING:BEGIN ClusterHud -->
<a id="ClusterHud"></a>

## 외부 HUD 활성화(0)

`ClusterHud`

0: 끄기 1: TURZX 9.2인치 본체 USB에 연결한 HUD에 적용됩니다. Jetson USB에 연결한 HUD는 이 설정과 무관하게 자동 실행됩니다. 시동 OFF 시 화면을 끄며, 항상 켜기는 HUD 디버그 설정을 따릅니다. Jetson은 지원 런타임에서 추론 중 USB로 HUD·지도·신호등 정보를 받습니다. 구형 수신기는 업데이트 전까지 기존 Wi-Fi 경로를 사용합니다. 본체 출력은 10 FPS, eGPU 활성 시 5 FPS이며 Jetson 목표 출력은 10 FPS입니다.

<!-- CARROT:AUTO:BEGIN ClusterHud -->
<!-- CARROT:AUTO:SOURCE facts="deec0b8e3dd2913fc6d794b12e2e6ecfef9c6c6089dd33202fb70a9fb3598890" semantic="9edf824457ea89ad8d62580c7ca4d5e4fc5c4e9c21e0b81860547c9d4b2bb10e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 화면 표시 \> 외부 HUD \> 기본
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHud -->

<!-- CARROT:MANUAL:BEGIN ClusterHud -->
<!-- CARROT:REVIEW reviewed-for="17e8e51b49d27978d564c982b7216d47db6b18c9d4a636e239f4306d3b9cdf96" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

본체 USB 또는 등록된 S3 HUD를 켜고 끕니다. Jetson에 연결한 HUD는 이 설정과 무관하게 자동 실행됩니다.

최신 C4와 S3 1.2.0은 H.264를 자동 사용하고, 이전 펌웨어 또는 기능 확인 응답이 없으면 JPEG를 사용합니다. 목표 15 FPS, eGPU 활성 시 최대 10 FPS이며 실제 속도는 화면 내용과 무선 상태에 따라 달라집니다.

[설치·펌웨어·등록 안내](https://upload.shind0.synology.me/models/carrot-s3/index.html)에 따라 기존 S3를 1.2.0으로 한 번 업데이트하세요. Wi-Fi·C4 등록은 유지되며 같은 2.4GHz 네트워크에서 자동 재연결합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

기본적으로 시동 OFF 시 화면을 끕니다. 시동 OFF에도 표시하려면 HUD 디버그의 항상 켜기를 사용하며, 밝기와 화면 구성은 기존 HUD 설정에서 조정합니다.

Jetson HUD는 Jetson 온도를 표시하고 장치의 온도 한계에 가까워지면 경고합니다. 경고 시 팬과 통풍 상태를 확인하세요.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHud -->

<!-- CARROT:SETTING:END ClusterHud -->
