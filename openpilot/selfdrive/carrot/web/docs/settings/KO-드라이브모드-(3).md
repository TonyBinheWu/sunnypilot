<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_DRIVE_MODE" param="MyDrivingMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 드라이브모드:(3)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 가속 성향 \> 드라이브 모드

---

<!-- CARROT:SETTING:BEGIN MyDrivingMode -->
<a id="MyDrivingMode"></a>

## 드라이브모드:(3)

`MyDrivingMode`

1: 에코 - 최대 가속도 ×0.9, 시간 차간 ×1.1, 앞차 반응 최대 2. 2: 안전 - 최대 가속도 ×0.8, 시간 차간 ×1.2, 앞차 반응 최대 3. 멀리서부터 천천히 감속하도록 제동 여유를 둡니다. 3: 일반 - 기본 가속·차간과 선택한 앞차 반응을 사용합니다. 4: 고속 - 최대 가속도 ×1.2, 선택한 앞차 반응 유지. 신호등 자동 정지는 사용하지 않습니다. 모드별 별도 저크 보정은 없으며 모드 차간 여유는 복귀 때 서서히 줄어듭니다. 낮은 반응 설정과 0은 올리지 않습니다.

<!-- CARROT:AUTO:BEGIN MyDrivingMode -->
<!-- CARROT:AUTO:SOURCE facts="ceac82c00bbd85e9ee6c6f138b543d39ccc5dc1ff8167f9bd675a7f1a4a8c103" semantic="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `3`
- **범위:** `1` ~ `4`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 가속 성향 \> 드라이브 모드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MyDrivingMode -->

<!-- CARROT:MANUAL:BEGIN MyDrivingMode -->
<!-- CARROT:REVIEW reviewed-for="6405b6142b9c6696548a67a172fbe0c6fcae9520e0055bb628b5ca3647987b6e" reviewed-at="2026-09-13T10:16:28.802623+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

연비는 최대 가속도 ×0.9·차간 ×1.1, 안전은 최대 가속도 ×0.8·차간 ×1.2와 부드러운 정지 접근을 사용합니다. 일반은 기본 동작이며 고속은 최대 가속도 ×1.2를 적용하고 신호 정지·출발 감지를 끕니다.

공통값 또는 TF별 반응을 정한 뒤 에코는 최대 2, 안전은 최대 3으로 적용합니다. 일반·고속은 선택값을 유지하며 낮은 값과 0을 올리거나 저장값을 바꾸지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 속도와 선행차 조건에서 모드별 가속·감속 반응을 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

모드별 별도 저크 보정은 없으며 최종 앞차 반응이 가속 강화와 일시적인 간격 회복을 함께 조절합니다. 모드 차간 배율이 낮아질 때는 초당 0.05씩 줄어들지만 사용자가 차간 단계를 직접 낮추는 동작은 별도로 지연시키지 않습니다.

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MyDrivingMode -->

<!-- CARROT:SETTING:END MyDrivingMode -->
