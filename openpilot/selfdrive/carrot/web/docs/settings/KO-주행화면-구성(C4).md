<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_BRIGHT" param="ShowModelView" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 주행화면 구성(C4)

**메뉴:** 화면 표시 \> 밝기·주행화면

---

<!-- CARROT:SETTING:BEGIN ShowModelView -->
<a id="ShowModelView"></a>

## 주행화면 구성(C4)

`ShowModelView`

C4 주행화면에서 카메라 영상과 차선·주행 경로 그림을 선택합니다. 차선·경로에는 앞차 표시도 포함됩니다. 밝기 설정과 관계없이 적용되며, 주행 중 변경하면 약 5초 안에 반영됩니다. 둘 다 숨겨도 속도와 경고는 계속 표시됩니다. 외부 HUD 연결 시에는 ‘외부 HUD 연결 시 본체 카메라’ 설정이 우선합니다.

<!-- CARROT:AUTO:BEGIN ShowModelView -->
<!-- CARROT:AUTO:SOURCE facts="f1e1f9435e4970970876593698a49e79bf790bf6fd5d2c7257f1546f467fe63a" semantic="0fbb289950310b907ca1e85a973172fac18f0381fcd7718d1a6f3ebf584a61ce" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 0 카메라 + 차선·경로 (`0`)
- **범위:** 0 카메라 + 차선·경로 (`0`) ~ 3 둘 다 숨김 (`3`)
- **변경 단위:** `1`
- **선택지:** `0` 0 카메라 + 차선·경로, `1` 1 카메라만, `2` 2 차선·경로만, `3` 3 둘 다 숨김
- **메뉴:** 화면 표시 \> 밝기·주행화면
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ShowModelView -->

<!-- CARROT:MANUAL:BEGIN ShowModelView -->
<!-- CARROT:REVIEW reviewed-for="c8040075196baa91f6b37ffa483d6e1197e44f8bd97dd6bfca9c50ab762b41de" reviewed-at="2026-10-08T09:28:59.208385+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

C4 주행화면의 영상과 그림을 선택합니다. 차선·경로 그림에는 앞차 표시도 포함됩니다.

- `0` — 카메라 영상 위에 차선·경로를 표시합니다.
- `1` — 카메라 영상만 표시합니다.
- `2` — 검은 배경에 차선·경로만 표시합니다.
- `3` — 카메라와 차선·경로를 모두 숨깁니다. 속도·경고·운전자 상태는 계속 표시됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

밝기 설정과 관계없이 적용되며 주행 시작 후 별도 대기는 없습니다. 주행 중 값을 바꾸면 재부팅 없이 약 5초 안에 반영됩니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

C3/C3X에는 적용되지 않습니다. 외부 HUD 연결 중 `ShowCameraWithCluster=0`이면 이 선택과 관계없이 본체의 카메라와 차선·경로를 모두 숨깁니다.

카메라 촬영·주행 판단·차량 제어는 바뀌지 않습니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ShowModelView -->

<!-- CARROT:SETTING:END ShowModelView -->
