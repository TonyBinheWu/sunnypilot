<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Carrot Vision 사용

**메뉴:** 차량·하드웨어 \> 운전자 모니터링

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## Carrot Vision 사용

`CarrotVisionEnabled`

웹 도로 영상을 활성화합니다. 주차 중에도 시청 세션이 있을 때만 카메라와 전용 인코더를 요청하고 종료 후 해제합니다. 운전자 감시 및 외부 HUD와 독립적으로 동작합니다. 동시 영상 사용 시 기기 부하가 증가할 수 있습니다.

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="5fbb787301e91de8d19e1b45256b8852e1a5538270c374d20b04dda266f3b867" semantic="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 끄기 (`0`)
- **범위:** 끄기 (`0`) ~ 켜기 (`1`)
- **변경 단위:** `1`
- **선택지:** `0` 끄기, `1` 켜기
- **메뉴:** 차량·하드웨어 \> 운전자 모니터링
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CarrotVisionEnabled -->

<!-- CARROT:MANUAL:BEGIN CarrotVisionEnabled -->
<!-- CARROT:REVIEW reviewed-for="b2d518e8de1cb65052caf0bf8dd1cad8094210462341bdc7090b9f4156fdff5f" reviewed-at="2026-11-13T16:58:12Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

운전자 감시 및 외부 HUD와 독립적으로 주행·주차 중 도로 영상을 제공합니다. 주차 카메라와 인코더는 시청 세션이 있을 때만 요청하며 다른 카메라 사용자는 기존 조건을 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

설정을 켜고 앱 또는 웹의 Vision을 엽니다. 차량 소프트웨어 업데이트 후 한 번 재부팅하면 CarrotAssist 0.2.16을 계속 사용할 수 있고 진단 카메라 실행기는 필요하지 않습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

주차 시청은 주행 모델·제어·일반 주행 녹화를 시작하거나 이전 주행 안내를 재사용하지 않으며 녹화 재생은 기록된 데이터를 유지합니다. 배터리 종료 조건도 유지됩니다. 이전 DisableDM 영상 선택은 감시나 실험 모드를 바꾸지 않고 한 번만 이전됩니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
