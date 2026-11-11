<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="LeadAccelResponse" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 추종응답성 · 공통

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponse -->
<a id="LeadAccelResponse"></a>

## 추종응답성 · 공통

`LeadAccelResponse`

단계별 반응이 공통값 사용일 때 적용합니다. 낮을수록 여유 있게, 높을수록 빠르게 따라갑니다. 0은 가속 강화 없음, 5는 최대 반응입니다. 속도별 TF는 모든 반응 단계에 적용됩니다. 공통값 또는 TF별 선택값을 정한 뒤 에코는 최대 2, 안전은 최대 3으로 적용합니다. 일반·고속은 선택값을 유지하며 더 낮은 값과 0은 올리지 않습니다. 저장값은 바꾸지 않습니다. 추가 여유의 유지 조건은 TF 거리(속도×TF＋정지거리)의 1.2배까지 적용하고, 1.2~1.5배에서 점차 해제합니다. 1.5배 이상에서는 앞차 속도와 관계없이 여유를 회수합니다. 감속 시작 거리를 별도로 기억하거나 정차 후 유지하지 않습니다.

<!-- CARROT:AUTO:BEGIN LeadAccelResponse -->
<!-- CARROT:AUTO:SOURCE facts="20c1fa5ef8eaea9dcc5ea6457bc672cbd12a83dff336fb5045e397fa79e3180d" semantic="46d9ff7041e6f7680369b13cd90e72cfa05423b6ad5dbae8d537cadcb8858d89" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 0 여유로운 추종 (`0`)
- **범위:** 0 여유로운 추종 (`0`) ~ 5 최대 추종(시험) (`5`)
- **변경 단위:** `1`
- **선택지:** `0` 0 여유로운 추종, `1` 1 가장 완만함, `2` 2 완만한 추종, `3` 3 균형 추종, `4` 4 급한 추종, `5` 5 최대 추종(시험)
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponse -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponse -->
<!-- CARROT:REVIEW reviewed-for="c487c8bba8fd571071a19fdbed3ea96f03f2b4dcf735b9e796ae232b73870670" reviewed-at="2026-10-11T08:11:40.285060+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

공통값 사용으로 설정한 크루즈갭 단계에 적용합니다. 낮추면 더 여유 있게 간격을 회복하고 높이면 더 빠르게 따라갑니다. 가속 강화와 추가 간격 회복을 함께 조절합니다.

공통값 또는 TF별 반응을 정한 뒤 에코는 최대 2, 안전은 최대 3으로 적용합니다. 일반·고속은 선택값을 유지하며 낮은 값과 0을 올리거나 저장값을 바꾸지 않습니다.

0~4단계의 추가 여유 유지에는 거리 범위를 적용합니다. 기준 거리 D는 속도×기본 TF＋설정된 정지거리이며 추가 여유를 제외합니다.

- 1.2D 이내: 기존 유지·회수 조건을 적용합니다.
- 1.2~1.5D: 유지할 여유와 보충 속도를 줄이고 저속 회수 제한을 점차 풉니다.
- 1.5D 이상: 멀어지는 앞차나 정지차에도 선택 단계의 속도로 여유를 회수합니다.

여유를 즉시 없애거나 가속을 직접 추가하지 않습니다. 5단계는 이 벌어지는 간격의 여유를 적용하지 않습니다. 별도로 모든 단계에서 두 차량이 함께 감속하며 가까워질 때 감속 시작 거리를 제한된 범위에서 기억하고, 속도가 떨어져도 천천히 줄여 반영합니다. 차량 변경·입력 이상·제어 해제 시 기억을 초기화합니다.

실측·예측 여유가 충분하면 편안한 추종을 위한 TF 기준을 최대 0.4초 일시 완화하되 기준 하한은 0.7초입니다. 저장 설정과 실제 장애물 제약을 유지하는 자동 동작이며 감속 제한이나 안전 차간 보장이 아닙니다. 실제 차량 간격과 승차감은 아직 검증하지 않았습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

모든 반응 단계는 속도 배율과 주행 모드 보정이 적용된 TF를 기준으로 합니다. 4~5가 속도별 TF를 건너뛰던 특례는 제거됐습니다. 필요한 제동과 기존 가속 제한은 유지됩니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponse -->

<!-- CARROT:SETTING:END LeadAccelResponse -->
