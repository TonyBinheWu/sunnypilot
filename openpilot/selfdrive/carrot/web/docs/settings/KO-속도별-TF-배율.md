<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_GAP" param="SpeedTFFactor" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 속도별 TF 배율

**메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리

---

<!-- CARROT:SETTING:BEGIN SpeedTFFactor -->
<a id="SpeedTFFactor"></a>

## 속도별 TF 배율

`SpeedTFFactor`

100km/h에서 적용할 TF 배율입니다. 10=1.0배(변화 없음), 20=2.0배. 정지 시 1.0배이며 속도에 따라 선형으로 증가합니다. 추종응답성은 바꾸지 않습니다.

<!-- CARROT:AUTO:BEGIN SpeedTFFactor -->
<!-- CARROT:AUTO:SOURCE facts="735cfd99aacae84ccac33291860f717fd41431e90592c240abf2b1562ede14fb" semantic="5a06220209167170871cd56a8bbad19e3a0ee27e7de4e1e4e83b573a1dc6126a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** 1.0× (`10`)
- **범위:** 1.0× (`10`) ~ 3.0× (`30`)
- **변경 단위:** `1`
- **선택지:** `10` 1.0×, `11` 1.1×, `12` 1.2×, `13` 1.3×, `14` 1.4×, `15` 1.5×, `16` 1.6×, `17` 1.7×, `18` 1.8×, `19` 1.9×, `20` 2.0×, `21` 2.1×, `22` 2.2×, `23` 2.3×, `24` 2.4×, `25` 2.5×, `26` 2.6×, `27` 2.7×, `28` 2.8×, `29` 2.9×, `30` 3.0×
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 차간거리
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedTFFactor -->

<!-- CARROT:MANUAL:BEGIN SpeedTFFactor -->
<!-- CARROT:REVIEW reviewed-for="84e34b1b5a1f71494a36b091cec0a6993009fc835fe70f30e264bd5cbe6db98b" reviewed-at="2026-09-13T08:45:37.358542+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

높이면 같은 속도에서 선택한 기본 TF를 더 늘립니다. 정지 시 기본 TF를 유지하며, 100km/h를 넘어도 같은 기울기로 증가합니다. 앞차 가속 반응 단계는 바꾸지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

설정값 20과 기본 TF 0.50초이면 0/50/100km/h에서 0.50/0.75/1.00초입니다. 이후 주행 모드와 감속 보정이 적용됩니다. 기존 EnableSpeedTF 값은 새 설정으로 변환하지 않습니다.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END SpeedTFFactor -->

<!-- CARROT:SETTING:END SpeedTFFactor -->
