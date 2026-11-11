<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_SCREEN" param="ClusterHudCameraViewMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 카메라 뷰 모드(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 화면·카메라

---

<!-- CARROT:SETTING:BEGIN ClusterHudCameraViewMode -->
<a id="ClusterHudCameraViewMode"></a>

## 외부 HUD 카메라 뷰 모드(0)

`ClusterHudCameraViewMode`

0: 기본 1: 모드1(하단뷰) 2: 일반 전방 카메라 3: 광각 전방 카메라 4: 속도에 따라 일반/광각 자동 전환

<!-- CARROT:AUTO:BEGIN ClusterHudCameraViewMode -->
<!-- CARROT:AUTO:SOURCE facts="24e8d1fc9968ae1fb566600079fd0d032977a15c12a0e90fbc05363c1b3b01ee" semantic="af3b40d3730a153e0c5d95a63e09da0dd2f8fe994a2a77fcbd201478e1a2773f" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 기본 (`0`)
- **범위:** 기본 (`0`) ~ 속도 자동 (`4`)
- **변경 단위:** `1`
- **선택지:** `0` 기본, `1` 하단 뷰, `2` 일반 카메라, `3` 광각 카메라, `4` 속도 자동
- **메뉴:** 화면 표시 \> 외부 HUD \> 화면·카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudCameraViewMode -->

<!-- CARROT:MANUAL:BEGIN ClusterHudCameraViewMode -->
<!-- CARROT:REVIEW reviewed-for="51f165f147cfa0802afd9fc04c05b0e2a5dbfbeb17f955788f4c25e38081161a" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 기본
- `1` — 모드1(하단뷰)
- `2` — 전방 카메라 배경
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD에서 화면 지연·선명도·CPU 사용량을 함께 확인하며 모드를 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudCameraViewMode -->

<!-- CARROT:SETTING:END ClusterHudCameraViewMode -->
