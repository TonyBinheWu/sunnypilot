<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_SCREEN" param="ClusterHudScreenMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 화면 모드(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 화면·카메라

---

<!-- CARROT:SETTING:BEGIN ClusterHudScreenMode -->
<a id="ClusterHudScreenMode"></a>

## 외부 HUD 화면 모드(0)

`ClusterHudScreenMode`

-1: 3D 전체화면 0: 기본(내비/주행 리포트) 1: 디버그 2: 디버그(시스템) 3: 디버그(그래프1) 4: 디버그(그래프2) 5: 주행 리포트 6: 외부 내비 전체화면 7: 주행화면 + 오른쪽 Nav 지도 Onroad P에서는 주차 화면, R에서는 EV6 제원의 후진 참고 화면을 우선 표시합니다. 다른 기어 또는 offroad에서는 기존 화면 모드로 돌아갑니다.

<!-- CARROT:AUTO:BEGIN ClusterHudScreenMode -->
<!-- CARROT:AUTO:SOURCE facts="a2ad8adce229b5c5c9e2f5b76ff97b4b0c00fafd71130984a33c62308cb53ce4" semantic="4454f6bc7bf3c1b0d27dc7adfae91475bc67670dc85dee7fee357a165b54433d" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** `0`
- **범위:** `-1` ~ `7`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 외부 HUD \> 화면·카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudScreenMode -->

<!-- CARROT:MANUAL:BEGIN ClusterHudScreenMode -->
<!-- CARROT:REVIEW reviewed-for="627a973ecafa1b31a96e570c3d02499497c8b6d45ab1e2366aa65ab21435fe93" reviewed-at="2026-07-31T23:37:31+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `-1` — 3D 카메라 뷰 `0`, `1`에서 정보 패널 없이 전체 폭을 사용합니다. 좌측 표시는 기존 여백을 유지하고 우측 게이지·TPMS는 화면 오른쪽에 맞추며, 시계·월드·방향지시등은 전체 화면 중앙축에 맞춥니다. 로드카메라 뷰 `2`에서는 내비/주행 리포트 자동 전환과 좌우 패널 배치까지 `0`과 동일합니다.
- `0` — 내비가 수신되면 내비 패널을, 수신되지 않으면 주행 리포트를 자동으로 표시하는 기본 화면입니다.
- `1` — 라이브 지연·토크·조향·횡방향 계획을 표시하는 일반 디버그 화면입니다.
- `2` — 기준 시스템 화면입니다. `0`의 자동 주행 리포트 전환 없이 내비 또는 `NAVI DISCONNECTED` 상태를 유지하고, 내비 소스가 없을 때만 경로 오버레이로 전환합니다.
- `3` — 주행 장면을 끄고 `ShowPlotMode` 그래프를 크게 표시합니다.
- `4` — 주행 장면과 정보 패널 그래프를 함께 표시합니다. 가속·조향·연료·요소수 게이지는 그래프 바로 왼쪽에 붙고 좌우 패널 전환도 따라가며, TPMS는 주행 화면에 남습니다.
- `5` — 주행 리포트를 항상 표시합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

일반 사용은 `0`, 3D 장면을 넓게 볼 때는 `-1`, 그래프와 주행 장면을 함께 비교할 때는 `4`를 선택합니다. 원래 자동 내비/리포트 화면으로 돌아가려면 `0`으로 복구합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudScreenMode -->

<!-- CARROT:SETTING:END ClusterHudScreenMode -->
