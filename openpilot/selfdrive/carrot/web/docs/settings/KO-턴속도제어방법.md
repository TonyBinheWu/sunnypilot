<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CURVE" param="TurnSpeedControlMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 턴속도제어방법

**메뉴:** 주행 제어 \> 속도·감속 \> 커브·턴

---

<!-- CARROT:SETTING:BEGIN TurnSpeedControlMode -->
<a id="TurnSpeedControlMode"></a>

## 턴속도제어방법

`TurnSpeedControlMode`

0: 속도제어안함 1: 비젼 2: 비젼+경로(TBT) 3: 경로(항상)

<!-- CARROT:AUTO:BEGIN TurnSpeedControlMode -->
<!-- CARROT:AUTO:SOURCE facts="e0d18053fe490a4ddc6f916fc11280bc1c6b0e3861c86f3d0af13609f86f1b27" semantic="0e0a5e58e9061594b9a41986ec433b7b6680c5f6ce99da897cd9b4e52ded8e38" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `1`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 커브·턴
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TurnSpeedControlMode -->

<!-- CARROT:MANUAL:BEGIN TurnSpeedControlMode -->
<!-- CARROT:REVIEW reviewed-for="0e0a5e58e9061594b9a41986ec433b7b6680c5f6ce99da897cd9b4e52ded8e38" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 속도제어안함
- `1` — 비젼
- `2` — 비젼+경로(TBT)
- `3` — 경로(항상)
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 커브와 경로 안내 조건에서 한 항목씩 조정하고, 진입 전 목표 속도와 커브 통과 속도를 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TurnSpeedControlMode -->

<!-- CARROT:SETTING:END TurnSpeedControlMode -->
