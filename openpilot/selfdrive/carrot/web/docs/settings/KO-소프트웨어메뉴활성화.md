<!-- CARROT:GENERATED schema="1" locale="ko" group="SYS_SW" param="SoftwareMenu" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 소프트웨어메뉴활성화

**메뉴:** 시스템 \> 소프트웨어

---

<!-- CARROT:SETTING:BEGIN SoftwareMenu -->
<a id="SoftwareMenu"></a>

## 소프트웨어메뉴활성화

`SoftwareMenu`

메모리오류가 있을때 끄기

<!-- CARROT:AUTO:BEGIN SoftwareMenu -->
<!-- CARROT:AUTO:SOURCE facts="003ad3b78ac120170b8f90fd4e9772ce6b87e3cf10b094dbbe24231173ebb8a5" semantic="faefc012a681c0434720425d608a2393574213ba2bcc32f6be3bf2d32e939dff" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 시스템 \> 소프트웨어
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoftwareMenu -->

<!-- CARROT:MANUAL:BEGIN SoftwareMenu -->
<!-- CARROT:REVIEW reviewed-for="faefc012a681c0434720425d608a2393574213ba2bcc32f6be3bf2d32e939dff" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- **켜짐:** 오프로드에서 소프트웨어 업데이트 프로세스를 실행하고 Carrot Web의 소프트웨어 메뉴를 표시합니다.
- **꺼짐:** 업데이트 프로세스를 실행하지 않고 해당 메뉴를 숨깁니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

오프로드에서 변경한 뒤 Carrot Web을 다시 열어 소프트웨어 메뉴 표시 여부와 업데이트 프로세스 상태를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="IMPORTANT" -->
> [!IMPORTANT]
> 메모리 문제 진단을 위한 프로세스 구성 설정입니다. 일반 사용에서는 기본값을 유지합니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SoftwareMenu -->

<!-- CARROT:SETTING:END SoftwareMenu -->
