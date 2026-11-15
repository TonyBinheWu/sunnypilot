<!-- CARROT:GENERATED schema="1" locale="ko" group="DISP_PATH" param="RainbowMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 무지개 도로 (SP 스타일)

**메뉴:** 화면 표시 \> 경로 표시

---

<!-- CARROT:SETTING:BEGIN RainbowMode -->
<a id="RainbowMode"></a>

## 무지개 도로 (SP 스타일)

`RainbowMode`

횡방향 제어가 활성화되면 예측 경로에 SP 스타일의 움직이는 무지개를 표시합니다. 0:끄기, 1:켜기. 표시만 바꾸며 조향·속도·경로 계산은 바뀌지 않습니다. 재시작 없이 적용됩니다.

<!-- CARROT:AUTO:BEGIN RainbowMode -->
<!-- CARROT:AUTO:SOURCE facts="bec59155d8a40345836bde7e3cfe70fbf041eee24186b1c2aad4518430fd529b" semantic="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 화면 표시 \> 경로 표시
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END RainbowMode -->

<!-- CARROT:MANUAL:BEGIN RainbowMode -->
<!-- CARROT:REVIEW reviewed-for="1aba7ed0cb53ca634c206d22650345f906fe8d15486d15e502ccfad140063cfd" reviewed-at="2026-11-15T15:32:10.973445+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 횡방향 제어가 활성화된 동안 기기 예측 경로를 SP 스타일의 움직이는 무지개로 표시합니다. 끄거나 횡방향 제어가 비활성화되면 기존 경로 모양으로 돌아갑니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

기기 토글 화면 또는 Carrot Web / CarrotAssist에서 `RainbowMode`를 검색합니다. C3/C3X와 C4에서 재시작 없이 적용됩니다. 끄면 기존 경로 모양과 색상을 사용합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

경로의 채움만 바꾸며 조향, 순항 속도, 모델 출력과 경고는 바뀌지 않습니다. 웹 / APK의 무지개 표시는 별도 `vision_rainbow_lane` 설정입니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END RainbowMode -->

<!-- CARROT:SETTING:END RainbowMode -->
