<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_DRIVE_MODE" param="MyDrivingModeAuto" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 드라이브모드: 자동

**메뉴:** 주행 제어 \> 크루즈·차간 \> 가속 성향 \> 드라이브 모드

---

<!-- CARROT:SETTING:BEGIN MyDrivingModeAuto -->
<a id="MyDrivingModeAuto"></a>

## 드라이브모드: 자동

`MyDrivingModeAuto`

0:수동, 1:일반↔안전, 2:에코↔안전. 정지차 접근은 빠르게 안전으로 전환하고 지속 서행도 안전으로 판단합니다. 정지 접근이 아닐 때 앞차 가속도가 1.0m/s²를 초과하는 상태가 약 0.5초 이어지면 복귀합니다. 그 외에는 3초간 흐름 회복이나 주행 중 앞차 없는 상태를 확인한 뒤 복귀합니다. 고속은 자동 선택하지 않습니다.

<!-- CARROT:AUTO:BEGIN MyDrivingModeAuto -->
<!-- CARROT:AUTO:SOURCE facts="e6ce6ced8552ad27a25a01c23aa27dca37e4bb5a942a1b9ce1d4a28ff9d34f43" semantic="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 가속 성향 \> 드라이브 모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingModeAuto -->

<!-- CARROT:MANUAL:BEGIN MyDrivingModeAuto -->
<!-- CARROT:REVIEW reviewed-for="0704a17d228794f4dfa2ce01cffbcaf023b513a0993d4106e62db6057ef8b025" reviewed-at="2026-09-27T14:30:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

`0`은 수동, `1`은 일반↔안전, `2`는 연비↔안전입니다. 정지차 접근은 약 0.3초, 지속 서행 추종은 8초 확인 후 안전을 선택합니다. 정지 접근이 아니며 앞차 가속도가 1.0m/s² 초과로 약 0.5초 유지되면 일반/연비로 복귀합니다. 그 외에는 흐름 회복 3초 또는 앞차 없이 15km/h 이상 주행 4초를 확인합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 속도와 선행차 조건에서 모드별 가속·감속 반응을 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> 주행 중 저장된 드라이브모드를 직접 바꾸면 플래너 재시작까지 자동전환을 중지합니다. 고속은 자동 선택하지 않으며 정지 중 앞차 소실만으로 기본 모드에 복귀하지 않습니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MyDrivingModeAuto -->

<!-- CARROT:SETTING:END MyDrivingModeAuto -->
