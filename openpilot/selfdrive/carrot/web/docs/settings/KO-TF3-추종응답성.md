<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="LeadAccelResponseTF3" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TF3 추종응답성

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN LeadAccelResponseTF3 -->
<a id="LeadAccelResponseTF3"></a>

## TF3 추종응답성

`LeadAccelResponseTF3`

크루즈갭 3단계의 추종응답성입니다. -1은 공통값 사용, 0~5는 이 단계에만 적용합니다. 기본 TF가 같아도 반응을 다르게 설정할 수 있습니다. 공통값 또는 TF별 선택값을 정한 뒤 에코는 최대 2, 안전은 최대 3으로 적용합니다. 일반·고속은 선택값을 유지하며 더 낮은 값과 0은 올리지 않습니다. 저장값은 바꾸지 않습니다. 추가 여유의 유지 조건은 TF 거리(속도×TF＋정지거리)의 1.2배까지 적용하고, 1.2~1.5배에서 점차 해제합니다. 1.5배 이상에서는 앞차 속도와 관계없이 여유를 회수합니다. 감속 시작 거리를 별도로 기억하거나 정차 후 유지하지 않습니다.

<!-- CARROT:AUTO:BEGIN LeadAccelResponseTF3 -->
<!-- CARROT:AUTO:SOURCE facts="ab61018e7004810014f17600f38231f9042d83a88a288228e268f87d00752a32" semantic="9af4c11b9f64844d55da9a63b084ab005796d68f1cd8c7c7b0e9d6a5d2e9e497" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 공통값 사용 (`-1`)
- **범위:** 공통값 사용 (`-1`) ~ 5 최대 추종(시험) (`5`)
- **변경 단위:** `1`
- **선택지:** `-1` 공통값 사용, `0` 0 여유로운 추종, `1` 1 가장 완만함, `2` 2 완만한 추종, `3` 3 균형 추종, `4` 4 급한 추종, `5` 5 최대 추종(시험)
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadAccelResponseTF3 -->

<!-- CARROT:MANUAL:BEGIN LeadAccelResponseTF3 -->
<!-- CARROT:REVIEW reviewed-for="687ab3a0919feb729b8ff37017deb95ce1af5bd88d2d1ff6c5f47ed4b9537618" reviewed-at="2026-10-05T01:00:23.781778+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

크루즈갭 3단계에서 공통값 또는 별도로 선택한 반응을 사용합니다. 높이면 더 빠르게 따라가며, 낮추면 간격을 더 여유 있게 회복합니다.

공통값 또는 TF별 반응을 정한 뒤 에코는 최대 2, 안전은 최대 3으로 적용합니다. 일반·고속은 선택값을 유지하며 낮은 값과 0을 올리거나 저장값을 바꾸지 않습니다.

0~4단계의 추가 여유 유지에는 거리 범위를 적용합니다. 기준 거리 D는 속도×기본 TF＋설정된 정지거리이며 추가 여유를 제외합니다.

- 1.2D 이내: 기존 유지·회수 조건을 적용합니다.
- 1.2~1.5D: 유지할 여유와 보충 속도를 줄이고 저속 회수 제한을 점차 풉니다.
- 1.5D 이상: 멀어지는 앞차나 정지차에도 선택 단계의 속도로 여유를 회수합니다.

여유를 즉시 없애거나 가속을 직접 추가하지 않습니다. 기본 TF·정지거리·제동 제한과 5단계의 추가 여유 없음은 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

기본 TF가 같은 두 단계에 서로 다른 반응을 설정할 수 있습니다. 가속 강화와 추가 간격 회복에 같은 반응값을 사용하며 속도별 TF 배율은 유지합니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END LeadAccelResponseTF3 -->

<!-- CARROT:SETTING:END LeadAccelResponseTF3 -->
