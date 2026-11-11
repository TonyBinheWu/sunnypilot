<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_CARROT" param="CruiseCoastingPercent" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 크루즈 코스팅 여유

**메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈

---

<!-- CARROT:SETTING:BEGIN CruiseCoastingPercent -->
<a id="CruiseCoastingPercent"></a>

## 크루즈 코스팅 여유

`CruiseCoastingPercent`

0%는 기존 제어를 유지합니다. 설정속도 초과 구간에서 크루즈 감속만 완화하고, 여유 상한에 가까워지면 감속을 복원합니다. 설정속도를 높이거나 SCC를 끄지 않습니다. 앞차·정지·외부 속도제어가 없는 일반 크루즈에서만 적용됩니다.

<!-- CARROT:AUTO:BEGIN CruiseCoastingPercent -->
<!-- CARROT:AUTO:SOURCE facts="94ad6fda8bf2b23bb8b124e52df359b017b3f03c16215bbee4a47d319f43f6dd" semantic="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0%`
- **범위:** `0%` ~ `10%`
- **변경 단위:** `1`
- **표시 단위:** `%`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 당근 크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CruiseCoastingPercent -->

<!-- CARROT:MANUAL:BEGIN CruiseCoastingPercent -->
<!-- CARROT:REVIEW reviewed-for="9e7ec0cc19d4be87699aad493790df42abd5125510f4ee68a4722b620c403b7a" reviewed-at="2026-09-25T08:35:39+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

설정속도를 초과한 일반 크루즈에서 감속 명령만 완화합니다. 값을 높이면 허용하는 초과속도 구간이 넓어지고, 낮추면 일반 감속이 더 일찍 복원됩니다.

- 여유 구간의 처음 10%에서 완화를 늘리고 마지막 40%에서 감속을 점차 복원합니다. 설정속도와 MPC 목표를 높이거나 SCC를 끄지 않습니다.
- 기준속도 10km/h 초과, 설정속도·여유 설정과 조건의 1초 유지가 필요합니다. 허용 조건에 진입할 때 환산한 기준속도를 고정하며, 이후 속도 보정비율 변화로 대기시간이나 기준을 다시 잡지 않습니다.
- 앞차·끼어들기 후보·정지·커브 제한·외부 속도제어·차선 변경·실험모드에서는 적용하지 않습니다. 설정속도·여유 설정 변경이나 조건 해제 후에는 기준을 다시 잡고 1초를 기다립니다.
- 연비 제어의 목표속도 증가나 기존 당근크루즈 가속 제한 모드가 활성화된 동안에는 적용하지 않습니다. 내비 제한이 코스팅 상한 이하인 경우에도 적용하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

변경은 실행 중 약 1초 주기로 반영됩니다. 기존 크루즈 감속으로 돌아가려면 꺼짐 값으로 설정합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

설정속도 100km/h에 여유 5%라면 103~105km/h에서 일반 감속이 복원됩니다. 105km/h까지 가속시키거나 실제 속도가 상한을 넘지 않도록 보장하는 기능은 아닙니다.

SCC 가속도 0 명령에서도 차종에 따라 회생이 발생할 수 있습니다. 차량 주행 검증은 아직 완료되지 않았습니다.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END CruiseCoastingPercent -->

<!-- CARROT:SETTING:END CruiseCoastingPercent -->
