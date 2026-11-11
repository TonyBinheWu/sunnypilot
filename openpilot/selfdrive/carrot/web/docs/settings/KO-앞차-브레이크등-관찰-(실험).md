<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_TRAFFIC" param="LeadBrakeLights" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 앞차 브레이크등 관찰 (실험)

**메뉴:** 주행 제어 \> 속도·감속 \> 신호감지

---

<!-- CARROT:SETTING:BEGIN LeadBrakeLights -->
<a id="LeadBrakeLights"></a>

## 앞차 브레이크등 관찰 (실험)

`LeadBrakeLights`

0: 끔. 1: 신호보조 모드 1/2에서 바로 앞차의 중앙 제동등 후보를 카메라 화면에 표시하고 기록합니다. 기본 OFF. BRAKE?는 제동등 후보이며 확정된 제동 상태가 아닙니다. 미검출은 꺼짐이 아닌 미확인입니다. 감속·정지·출발 제어에는 사용하지 않습니다. 신호 처리에 여유가 없거나 회전·앞차 연결이 불확실하면 검사를 건너뜁니다. 신호보조 모드 0에서는 작동하지 않습니다.

<!-- CARROT:AUTO:BEGIN LeadBrakeLights -->
<!-- CARROT:AUTO:SOURCE facts="f40f44a3fb0671b4e0908e06bcc21674985b923337afa1943d235505213f740c" semantic="1c52b548b46d979bac0118c3daafe7304a87141b48ac8f9662b240448cd8289a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 신호감지
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END LeadBrakeLights -->

<!-- CARROT:MANUAL:BEGIN LeadBrakeLights -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END LeadBrakeLights -->

<!-- CARROT:SETTING:END LeadBrakeLights -->
