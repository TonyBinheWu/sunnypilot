<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="TFollowGap1" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(1): 차량간격시간1x0.01s(110)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN TFollowGap1 -->
<a id="TFollowGap1"></a>

## TF(1): 차량간격시간1x0.01s(110)

`TFollowGap1`

크루즈갭 1단계의 기본 차간시간입니다. 50=0.50초. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.

<!-- CARROT:AUTO:BEGIN TFollowGap1 -->
<!-- CARROT:AUTO:SOURCE facts="38388be7e517e3105411bb0441e5d7be5b8285b9994bb285d753696502bad653" semantic="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `110`
- **범위:** `40` ~ `300`
- **변경 단위:** `5`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap1 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap1 -->
<!-- CARROT:REVIEW reviewed-for="ed3db450ac23993e30fe62a41b6390389aef7f0343a5afe4ff667f18b0fc589a" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

크루즈갭 1단계에서 사용하는 기본 차간시간입니다. 높이면 기본 간격이 길어지고 낮추면 짧아집니다. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

저장값 50은 0.50초입니다. 기본 TF가 같아도 단계별 앞차 가속 반응을 다르게 설정할 수 있습니다. 주행 경로의 바와 m 숫자는 동적 보정이 반영된 추종 목표거리입니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap1 -->

<!-- CARROT:SETTING:END TFollowGap1 -->
