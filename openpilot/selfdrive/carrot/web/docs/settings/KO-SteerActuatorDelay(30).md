<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_FEEL" param="SteerActuatorDelay" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# SteerActuatorDelay(30)

**메뉴:** 주행 제어 \> 차량 조향 \> 조향감

---

<!-- CARROT:SETTING:BEGIN SteerActuatorDelay -->
<a id="SteerActuatorDelay"></a>

## SteerActuatorDelay(30)

`SteerActuatorDelay`

조향 반응 지연 보상: 30=0.30초, 0=자동 학습(LiveDelay). 높을수록 미리 조향합니다. 커브 진입은 무게중심 비율의 영향도 받습니다. 비교할 때 SAD·SR은 유지하세요.

<!-- CARROT:AUTO:BEGIN SteerActuatorDelay -->
<!-- CARROT:AUTO:SOURCE facts="d56cdd215544cbb7e34e24cfd0de0366e0f26de0482f5cfdf35b424c440a5334" semantic="2d1e59de8edc91af92b92e8bcb989bbc50e68cca9731d896bd7f990032ce4097" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `30`
- **범위:** `0` ~ `300`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 조향감
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SteerActuatorDelay -->

<!-- CARROT:MANUAL:BEGIN SteerActuatorDelay -->
<!-- CARROT:REVIEW reviewed-for="d72d913592441b3ae02dcad9b3d9db17842df189841f5d0a1eabaeac094725c6" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

조향지연값 / 높을수록 미리 조향 함.

- **값을 높이면:** 예상 조향 지연을 크게 보고 더 일찍 조향을 요청합니다.
- **값을 낮추면:** 조향 요청의 선행 보정이 줄어듭니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 직선과 완만한 커브에서 한 항목씩 작은 단계로 변경하고, 지연·진동·운전자 개입 후 복귀를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0`은 고정값 대신 실시간으로 추정한 조향 지연값을 사용합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SteerActuatorDelay -->

<!-- CARROT:SETTING:END SteerActuatorDelay -->
