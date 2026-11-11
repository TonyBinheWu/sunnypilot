<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="TFollowGap2" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(2): 차량간격시간2x0.01s(120)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN TFollowGap2 -->
<a id="TFollowGap2"></a>

## TF(2): 차량간격시간2x0.01s(120)

`TFollowGap2`

크루즈갭 2단계의 기본 차간시간입니다. 50=0.50초. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.

<!-- CARROT:AUTO:BEGIN TFollowGap2 -->
<!-- CARROT:AUTO:SOURCE facts="3c8ffa320c7c2e612e7e783040e8e1866f31a54060797c610602d490f4eb1ca5" semantic="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `120`
- **범위:** `40` ~ `300`
- **변경 단위:** `5`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap2 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap2 -->
<!-- CARROT:REVIEW reviewed-for="4352d22a167ac26fa0a74811c302d3a719e21aaf91e7e7767b23e77fec61b555" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

크루즈갭 2단계에서 사용하는 기본 차간시간입니다. 높이면 기본 간격이 길어지고 낮추면 짧아집니다. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

저장값 50은 0.50초입니다. 기본 TF가 같아도 단계별 앞차 가속 반응을 다르게 설정할 수 있습니다. 주행 경로의 바와 m 숫자는 동적 보정이 반영된 추종 목표거리입니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap2 -->

<!-- CARROT:SETTING:END TFollowGap2 -->
