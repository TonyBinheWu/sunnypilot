<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_CENTER" param="PathOffset" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차선치우침 좌우보정(0)

**메뉴:** 주행 제어 \> 차량 조향 \> 중앙 보정

---

<!-- CARROT:SETTING:BEGIN PathOffset -->
<a id="PathOffset"></a>

## 차선치우침 좌우보정(0)

`PathOffset`

(레인모드) (-)좌측 / (+)우측

<!-- CARROT:AUTO:BEGIN PathOffset -->
<!-- CARROT:AUTO:SOURCE facts="1709dfe1bdb5b9cc4e3d02a925a5108a6540afeed0a382a1140848a94aa6e502" semantic="81aef93bf00308504aceb19384c7229c79421ee80c58f4397de30e222059d1d7" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0cm`
- **범위:** `-150cm` ~ `150cm`
- **변경 단위:** `1`
- **표시 단위:** `cm`
- **메뉴:** 주행 제어 \> 차량 조향 \> 중앙 보정
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END PathOffset -->

<!-- CARROT:MANUAL:BEGIN PathOffset -->
<!-- CARROT:REVIEW reviewed-for="81aef93bf00308504aceb19384c7229c79421ee80c58f4397de30e222059d1d7" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

(레인모드) / (-)좌측 / (+)우측.

- **음수 방향:** 목표 경로를 왼쪽으로 옮깁니다.
- **양수 방향:** 목표 경로를 오른쪽으로 옮깁니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

평평하고 직선인 도로에서 일정한 속도로 확인하며, 한 단계씩 바꿔 좌우 편향이 줄어드는지 비교합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END PathOffset -->

<!-- CARROT:SETTING:END PathOffset -->
