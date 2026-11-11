<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_RADAR" param="EnableCornerRadar" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 코너레이더 사용(0)

**메뉴:** 차량·하드웨어 \> 레이더

---

<!-- CARROT:SETTING:BEGIN EnableCornerRadar -->
<a id="EnableCornerRadar"></a>

## 코너레이더 사용(0)

`EnableCornerRadar`

1:코너레이더활성화,2:끼어드는 차량 검출

<!-- CARROT:AUTO:BEGIN EnableCornerRadar -->
<!-- CARROT:AUTO:SOURCE facts="6bb2b2249dddeeed0116b111f5781ae72f0e67b55f4afdfae950a73aa92db16a" semantic="f3344cc43f62d863ecb64a7db5ee5dc1890061598ea1a111001723780943390c" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> 레이더
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END EnableCornerRadar -->

<!-- CARROT:MANUAL:BEGIN EnableCornerRadar -->
<!-- CARROT:REVIEW reviewed-for="f3344cc43f62d863ecb64a7db5ee5dc1890061598ea1a111001723780943390c" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 코너 레이더를 사용하지 않습니다.
- `1` — 지원되는 코너 레이더 트랙을 사용합니다.
- `2` — 코너 레이더 트랙과 끼어드는 차량 검출을 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원되는 레이더 구성에서 한 항목씩 변경하고, 같은 선행차·끼어들기 조건에서 탐지와 추적을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 물리적 레이더 장착 여부만으로 지원을 판단할 수 없습니다. 동일 차량 구성에서 메시지 수신과 추적 결과를 확인해야 합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/radar.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END EnableCornerRadar -->

<!-- CARROT:SETTING:END EnableCornerRadar -->
