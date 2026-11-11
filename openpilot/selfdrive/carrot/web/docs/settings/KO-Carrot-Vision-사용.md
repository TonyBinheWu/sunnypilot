<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DM" param="CarrotVisionEnabled" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# Carrot Vision 사용

**메뉴:** 차량·하드웨어 \> 운전자 모니터링

---

<!-- CARROT:SETTING:BEGIN CarrotVisionEnabled -->
<a id="CarrotVisionEnabled"></a>

## Carrot Vision 사용

`CarrotVisionEnabled`

웹 도로 영상 스트리밍을 활성화합니다. 운전자 감시와 독립적으로 동작하며 외부 HUD와 함께 사용할 수 있습니다. 동시 영상 사용 시 기기 부하가 증가할 수 있습니다.

<!-- CARROT:AUTO:BEGIN CarrotVisionEnabled -->
<!-- CARROT:AUTO:SOURCE facts="3f52883d1e149378f0655716f9c3d050f9db5b7ec9babbb1b1cb4840a76b4505" semantic="06ceb617dbe739cddd0239009397024736b16a64f730822966da6da92c24437d" review="needs_review" -->
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
<!-- CARROT:REVIEW reviewed-for="196e1f296cc743239e491c11d519cea88fbf7bde06ad6f1fe40b377fe6758e07" reviewed-at="2026-09-28T07:45:02.991356+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 웹 도로 영상 스트리밍을 사용할 수 있고 끄면 중지합니다. 운전자 감시 모드와 독립적입니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

웹 도로 영상을 사용할 때 켜세요. USB 계기판 사용 중에는 Carrot Vision을 사용할 수 없습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

기존 DisableDM의 영상 활성화 값은 최초 전환 시 이 설정으로 옮깁니다. 이 승계로 운전자 감시가 꺼지거나 실험 모드가 켜지지 않습니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END CarrotVisionEnabled -->

<!-- CARROT:SETTING:END CarrotVisionEnabled -->
