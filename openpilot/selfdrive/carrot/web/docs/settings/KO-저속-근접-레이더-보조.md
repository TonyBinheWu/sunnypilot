<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_FEEL" param="LowSpeedRadarGuard" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 저속 근접 레이더 보조

**메뉴:** 주행 제어 \> 차량 조향 \> 조향감

---

<!-- CARROT:SETTING:BEGIN LowSpeedRadarGuard -->
<a id="LowSpeedRadarGuard"></a>

## 저속 근접 레이더 보조

`LowSpeedRadarGuard`

15 km/h 이하에서 접근 중인 전방 레이더 차량이 연속 확인되면 양의 가속을 제한하고, 점유된 쪽으로 새 자동 회전 요청을 보류합니다. 벽 거리나 사각 전체를 측정하지 않습니다.

<!-- CARROT:AUTO:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:AUTO:SOURCE facts="ce709578268a9bcccd3ac5cc176a64afb8de07d75c8390561b151ad922293665" semantic="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 조향감
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LowSpeedRadarGuard -->

<!-- CARROT:MANUAL:BEGIN LowSpeedRadarGuard -->
<!-- CARROT:REVIEW reviewed-for="2daf7c8d9946d5aba8152c1a68abb9c8ea0a70692d3a23d8a390eb3222389f13" reviewed-at="2026-11-27T22:32:00+08:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

7 m 이내의 같은 전방 표적이 0.5 m/s보다 빠르게 접근하고 접촉 예상 시간이 2초 이하인 상황을 세 번의 서로 다른 레이더 샘플에서 확인합니다. 양의 가속을 제한하며 더 강한 감속 요구를 유지합니다. 측면 물체가 없을 때 차단을 해제하려면 현대·기아 0x180 또는 0x235의 완전하고 최신인 코너 스캔이 필요합니다. 벽이나 연석은 감지 범위를 벗어날 수 있습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END LowSpeedRadarGuard -->

<!-- CARROT:SETTING:END LowSpeedRadarGuard -->
