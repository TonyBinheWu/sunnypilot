<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_CANFD" param="HDPuse" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# HDP 사용(CCNC)

**메뉴:** 차량·하드웨어 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN HDPuse -->
<a id="HDPuse"></a>

## HDP 사용(CCNC)

`HDPuse`

1:APN사용시 2:항상

<!-- CARROT:AUTO:BEGIN HDPuse -->
<!-- CARROT:AUTO:SOURCE facts="3a9fed1d0a13bdfd7946356a816a8159b4083bc8ac08a452fe91468fc6af3439" semantic="81f1a1ef230e556daa86169f16be0dde67d63f336598dd28620fff74b35b9139" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END HDPuse -->

<!-- CARROT:MANUAL:BEGIN HDPuse -->
<!-- CARROT:REVIEW reviewed-for="81f1a1ef230e556daa86169f16be0dde67d63f336598dd28620fff74b35b9139" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — HDP 메시지 동작을 사용하지 않습니다.
- `1` — APN 사용 중에만 HDP 동작을 사용합니다.
- `2` — HDP 동작을 항상 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량의 HDA·CAN FD 구성을 확인한 뒤 정차 상태에서 설정하고, 다음 주행에서 관련 기능과 오류 유무를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 검증되지 않은 CAN FD 설정은 차량 경고등이나 CAN 오류를 일으킬 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END HDPuse -->

<!-- CARROT:SETTING:END HDPuse -->
