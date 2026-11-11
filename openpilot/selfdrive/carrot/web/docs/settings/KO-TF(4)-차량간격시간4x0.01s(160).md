<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="TFollowGap4" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(4): 차량간격시간4x0.01s(160)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN TFollowGap4 -->
<a id="TFollowGap4"></a>

## TF(4): 차량간격시간4x0.01s(160)

`TFollowGap4`

크루즈갭 4단계의 기본 차간시간입니다. 50=0.50초. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.

<!-- CARROT:AUTO:BEGIN TFollowGap4 -->
<!-- CARROT:AUTO:SOURCE facts="af2cc59094403b55f0399183066f91e938787d2eeee5ca6d3902e21c4cf3a7a3" semantic="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `160`
- **범위:** `40` ~ `300`
- **변경 단위:** `5`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap4 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap4 -->
<!-- CARROT:REVIEW reviewed-for="a772a1a64ce8b511e296150a40a883a31e7950a6c45ae92c5a364b37c775e817" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

크루즈갭 4단계에서 사용하는 기본 차간시간입니다. 높이면 기본 간격이 길어지고 낮추면 짧아집니다. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

저장값 50은 0.50초입니다. 기본 TF가 같아도 단계별 앞차 가속 반응을 다르게 설정할 수 있습니다. 주행 경로의 바와 m 숫자는 동적 보정이 반영된 추종 목표거리입니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap4 -->

<!-- CARROT:SETTING:END TFollowGap4 -->
