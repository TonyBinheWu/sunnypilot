<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_CANFD" param="CanfdHDA2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 현대 CAN-FD 배선

**메뉴:** 차량·하드웨어 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdHDA2 -->
<a id="CanfdHDA2"></a>

## 현대 CAN-FD 배선

`CanfdHDA2`

다음 시작 시 적용. 자동 감지 또는 실제 배선에 맞게 선택하세요.

<!-- CARROT:AUTO:BEGIN CanfdHDA2 -->
<!-- CARROT:AUTO:SOURCE facts="deb14d09ba6573570618206dd21782fba6503fb9687d84d26b9c901b8bfc5d92" semantic="a4d30a9a469e9c7a3be9b5bb5943a92f33fce83e193ba0e774e932a8a536e295" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 자동 감지 (`2`)
- **범위:** 카메라 (HDA1) (`0`) ~ 자동 감지 (`2`)
- **변경 단위:** `1`
- **선택지:** `0` 카메라 (HDA1), `1` ADAS ECU (HDA2), `2` 자동 감지
- **메뉴:** 차량·하드웨어 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdHDA2 -->

<!-- CARROT:MANUAL:BEGIN CanfdHDA2 -->
<!-- CARROT:REVIEW reviewed-for="2cd10469d96bc08a71fdfa257929f6cf6790a84cd48e7d2bcc55c07355d65caa" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 현대·기아 CAN FD 차량을 HDA1 구성으로 처리합니다.
- `1` — HDA2 CAN 버스 구성을 사용합니다.
- `2` — 관측한 LKAS 메시지와 길이로 CAN-FD 조향 하네스를 자동 감지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량의 HDA·CAN FD 구성을 확인한 뒤 정차 상태에서 설정하고, 다음 주행에서 관련 기능과 오류 유무를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 검증되지 않은 CAN FD 설정은 차량 경고등이나 CAN 오류를 일으킬 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CanfdHDA2 -->

<!-- CARROT:SETTING:END CanfdHDA2 -->
