<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_TORQUE_COEFF" param="NNFF" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# NNFF 토크 제어

**메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수

---

<!-- CARROT:SETTING:BEGIN NNFF -->
<a id="NNFF"></a>

## NNFF 토크 제어

`NNFF`

토크 조향의 신경망 피드포워드 옵션입니다. 켜면 조향각 제어가 아닌 차량에 토크 제어 튜닝을 사용하며, 대응 모델이 있으면 NNFF를 적용합니다. comma 자체 NNFF 지원 차종은 기존 자체 경로가 우선합니다. 끄면 이 NNFF 옵션을 사용하지 않으며 NNFFLite 설정은 바꾸지 않습니다. 기본값은 꺼짐이고 Carrot Web 검색에서만 표시됩니다. 변경은 다음 주행 시작 또는 기기 재부팅 후 적용됩니다. 조향각 제어 차량에는 적용되지 않습니다.

<!-- CARROT:AUTO:BEGIN NNFF -->
<!-- CARROT:AUTO:SOURCE facts="7bf26dff3a95af2d27d9c6a1b80870d62ae1eea3f05c00b253e53098af7f40df" semantic="bf1b67050f021288a3be062698bf0689878aedc8c326f0f30176feec716d40f2" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 차량 조향 \> 고급 토크 \> 토크 계수
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END NNFF -->

<!-- CARROT:MANUAL:BEGIN NNFF -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END NNFF -->

<!-- CARROT:SETTING:END NNFF -->
