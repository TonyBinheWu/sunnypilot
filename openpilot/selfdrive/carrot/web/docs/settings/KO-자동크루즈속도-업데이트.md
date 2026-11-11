<!-- CARROT:GENERATED schema="1" locale="ko" group="BASIC_AUTOCRUISE" param="AutoGasSyncSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 자동크루즈속도 업데이트

**메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈

---

<!-- CARROT:SETTING:BEGIN AutoGasSyncSpeed -->
<a id="AutoGasSyncSpeed"></a>

## 자동크루즈속도 업데이트

`AutoGasSyncSpeed`

액셀을 밟아 속도가 설정속도보다 빨라지면 설정속도 변경

<!-- CARROT:AUTO:BEGIN AutoGasSyncSpeed -->
<!-- CARROT:AUTO:SOURCE facts="f36a8fb280e9bd471274b4f18190f36eade1a3e7d47385d771f9388c54aa7452" semantic="b7d50e021ae02dfaf5a91c4919bed99b902eecbb6a56c177e5cbdc093c729db0" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 시작·오토 \> 오토크루즈
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END AutoGasSyncSpeed -->

<!-- CARROT:MANUAL:BEGIN AutoGasSyncSpeed -->
<!-- CARROT:REVIEW reviewed-for="b7d50e021ae02dfaf5a91c4919bed99b902eecbb6a56c177e5cbdc093c729db0" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 가속 페달을 밟아 실제 속도가 크루즈 설정 속도보다 높아지면 설정 속도를 현재 속도까지 올립니다.
- **꺼짐:** 가속 페달 사용 후에도 기존 설정 속도를 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 출발·가속 페달·선행차 조건에서 한 항목씩 변경하고, 크루즈 활성화 시점과 설정 속도를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END AutoGasSyncSpeed -->

<!-- CARROT:SETTING:END AutoGasSyncSpeed -->
