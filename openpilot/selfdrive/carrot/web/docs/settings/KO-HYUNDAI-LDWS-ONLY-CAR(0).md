<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_HYUNDAI" param="IsLdwsCar" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# HYUNDAI: LDWS ONLY CAR(0)

**메뉴:** 차량·하드웨어 \> 현대·기아

---

<!-- CARROT:SETTING:BEGIN IsLdwsCar -->
<a id="IsLdwsCar"></a>

## HYUNDAI: LDWS ONLY CAR(0)

`IsLdwsCar`

LDWS ONLY CAR는 ON

<!-- CARROT:AUTO:BEGIN IsLdwsCar -->
<!-- CARROT:AUTO:SOURCE facts="56e2a71714521fae4d2acc44e1fa09d68ccc29837aa1ec2966f66cc24a879602" semantic="34f98ba7f7fd321a9bdd1b0e97bda0d45664cf5d320a3024bcfddb0784f5c889" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 차량·하드웨어 \> 현대·기아
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END IsLdwsCar -->

<!-- CARROT:MANUAL:BEGIN IsLdwsCar -->
<!-- CARROT:REVIEW reviewed-for="34f98ba7f7fd321a9bdd1b0e97bda0d45664cf5d320a3024bcfddb0784f5c889" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 현대·기아의 레거시 `LKAS11` 메시지에서 LDWS 전용 계기판 옵션값을 사용합니다.
- **꺼짐:** 차량별 기본 LKAS/LFA 계기판 옵션을 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

차량 사양과 배선 구성을 확인한 뒤 정차 상태에서 설정하고, 다음 주행에서 SCC·차선 경고 동작을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="WARNING" -->
> [!WARNING]
> 차종·연식·HDA 세대·하네스 위치가 일치하지 않으면 SCC 또는 종방향 제어가 잘못 동작할 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END IsLdwsCar -->

<!-- CARROT:SETTING:END IsLdwsCar -->
