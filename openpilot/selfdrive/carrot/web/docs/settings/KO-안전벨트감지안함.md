<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DM" param="MuteSeatbelt" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 안전벨트감지안함

**메뉴:** 차량·하드웨어 \> 운전자 모니터링

---

<!-- CARROT:SETTING:BEGIN MuteSeatbelt -->
<a id="MuteSeatbelt"></a>

## 안전벨트감지안함

`MuteSeatbelt`

안전벨트감지안함

<!-- CARROT:AUTO:BEGIN MuteSeatbelt -->
<!-- CARROT:AUTO:SOURCE facts="b0cf61b5607c6c3982caaf5e3ec51c3e1d4996f989900a02832416d5a327304c" semantic="1ebf5b7d58dbd61bfd90f74ebd2f43ac41e416f817f1109e30249922d3cd775e" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 차량·하드웨어 \> 운전자 모니터링
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MuteSeatbelt -->

<!-- CARROT:MANUAL:BEGIN MuteSeatbelt -->
<!-- CARROT:REVIEW reviewed-for="1ebf5b7d58dbd61bfd90f74ebd2f43ac41e416f817f1109e30249922d3cd775e" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 안전벨트 미착용 상태를 주행 차단 이벤트에 추가하지 않습니다.
- **꺼짐:** 안전벨트가 풀려 있으면 미착용 이벤트를 발생시킵니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

정차 상태에서 변경하고, 다음 주행에서 운전자 모니터링과 차량 경고 상태를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 켜면 안전벨트 미착용 상태가 주행 차단 이벤트에서 제외됩니다. 모든 탑승자의 안전벨트를 직접 확인해야 합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END MuteSeatbelt -->

<!-- CARROT:SETTING:END MuteSeatbelt -->
