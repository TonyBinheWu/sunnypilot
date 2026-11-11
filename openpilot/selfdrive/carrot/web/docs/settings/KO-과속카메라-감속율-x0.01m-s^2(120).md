<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="AutoNaviSpeedDecelRate" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 과속카메라 감속율 x0.01m/s^2(120)

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN AutoNaviSpeedDecelRate -->
<a id="AutoNaviSpeedDecelRate"></a>

## 과속카메라 감속율 x0.01m/s^2(120)

`AutoNaviSpeedDecelRate`

카메라·방지턱 접근 시 감속 곡선 계산에 사용하는 값입니다. 저장값에 0.01m/s²를 곱하며 120은 1.2m/s²입니다. 낮추면 더 먼 거리에서 감속을 시작하고, 높이면 더 가까이서 시작합니다. 기존에 저장된 설정은 업데이트만으로 바뀌지 않습니다.

<!-- CARROT:AUTO:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:AUTO:SOURCE facts="0afba83fccd66983f6a5c5457f63b206d84ec6e318b8cc7f84faef3bc8962762" semantic="dd424d47dfc026837af962b9c56209e7643717b0eba2e3136437850b8bdd30c3" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `120`
- **범위:** `50` ~ `300`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoNaviSpeedDecelRate -->

<!-- CARROT:MANUAL:BEGIN AutoNaviSpeedDecelRate -->
<!-- CARROT:REVIEW reviewed-for="f8c301abb791623a5f1ff08eb2caea713c2ab3040a02a6f6035af09687c06afa" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

낮으면 멀리서부터 감속함.

- **값을 높이면:** 더 짧은 거리에서 강하게 감속합니다.
- **값을 낮추면:** 더 먼 거리부터 완만하게 감속합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 제한속도와 같은 종류의 카메라 구간에서 한 항목씩 변경해 감속 시작·완료 지점과 통과 속도를 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END AutoNaviSpeedDecelRate -->

<!-- CARROT:SETTING:END AutoNaviSpeedDecelRate -->
