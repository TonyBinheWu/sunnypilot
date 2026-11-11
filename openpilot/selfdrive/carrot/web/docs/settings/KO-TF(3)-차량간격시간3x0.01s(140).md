<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="TFollowGap3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF(3): 차량간격시간3x0.01s(140)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN TFollowGap3 -->
<a id="TFollowGap3"></a>

## TF(3): 차량간격시간3x0.01s(140)

`TFollowGap3`

크루즈갭 3단계의 기본 차간시간입니다. 50=0.50초. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.

<!-- CARROT:AUTO:BEGIN TFollowGap3 -->
<!-- CARROT:AUTO:SOURCE facts="526a1d8a16fa618e9b7549a56938bf214ff29396dfce907e5be35ab31aabdd8e" semantic="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `140`
- **범위:** `40` ~ `300`
- **변경 단위:** `5`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TFollowGap3 -->

<!-- CARROT:MANUAL:BEGIN TFollowGap3 -->
<!-- CARROT:REVIEW reviewed-for="9716f07b3b27c698d4848f5f0616674737d977a27f883067bb593444a3008774" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

크루즈갭 3단계에서 사용하는 기본 차간시간입니다. 높이면 기본 간격이 길어지고 낮추면 짧아집니다. 속도별 TF 배율과 주행·감속 보정이 적용됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

저장값 50은 0.50초입니다. 기본 TF가 같아도 단계별 앞차 가속 반응을 다르게 설정할 수 있습니다. 주행 경로의 바와 m 숫자는 동적 보정이 반영된 추종 목표거리입니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END TFollowGap3 -->

<!-- CARROT:SETTING:END TFollowGap3 -->
