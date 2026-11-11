<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_AUX" param="SpeedFromPCM" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# PCM차량속도제어

**메뉴:** 차량·하드웨어 \> 차량 보조

---

<!-- CARROT:SETTING:BEGIN SpeedFromPCM -->
<a id="SpeedFromPCM"></a>

## PCM차량속도제어

`SpeedFromPCM`

PCM 차량의 속도 제어 방식 0:커브/카메라 감속+롱컨 1:순정 설정속도 사용·버튼스패밍 안 함 2:커브/카메라 감속 3:Honda/Toyota (토요타·렉서스는 순정 설정속도 사용, 가감속 모드 전환 아님)

<!-- CARROT:AUTO:BEGIN SpeedFromPCM -->
<!-- CARROT:AUTO:SOURCE facts="4ecf0822287341163f431b103e6facadaa4663d80a4df0b13d03263d6d1eb6aa" semantic="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `2`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> 차량 보조
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SpeedFromPCM -->

<!-- CARROT:MANUAL:BEGIN SpeedFromPCM -->
<!-- CARROT:REVIEW reviewed-for="826f2d40ddf5f91d56d0f427bee488abab5c3cb4e0d0c3487843d985b45560cc" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

선택값에 따라 다음과 같이 동작합니다.

- `0` — 커브/카메라 감속+롱컨
- `1` — 버튼스패밍안함(순정SCC)
- `2` — 커브/카메라 감속
- `3` — Honda/Toyota
토요타·렉서스의 `3`은 순정 SET/RES 설정속도를 기본 목표로 사용하고, 순정 계기판 설정속도를 표시합니다. `1`도 순정 설정속도를 사용하며 `0`과 `2`는 기존 카롯 속도 선택을 유지합니다. Honda의 `3` 동작은 바뀌지 않습니다. 이 설정 자체는 가감속 제어 주체나 레이더 사용 여부를 전환하지 않습니다.

`0`의 예외로, `TOYOTA_RAV4_TSS2_2022`의 PCM·openpilot 직접 가감속 구성에서는 유효한 CAN으로 관측한 순정 설정속도 변경이나 크루즈 비활성→활성 전이를 기본 목표에 반영합니다. 처음부터 활성인 표본은 기준만 저장하고 같은 주기의 로컬 버튼·블루투스 속도 변경이 우선하며, 낮은 앞차·커브·지도 감속 목표를 유지하고 RES/SET CAN 송신을 추가하지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

지원 차량에서만 한 항목씩 변경하고, 다음 주행에서 조향 또는 순정 SCC 동작을 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="CAUTION" -->
> [!CAUTION]
> 차량 제어 방식과 일치하지 않는 값은 조향 또는 순정 SCC 동작을 바꿀 수 있습니다.
<!-- CARROT:NOTICE:END -->
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END SpeedFromPCM -->

<!-- CARROT:SETTING:END SpeedFromPCM -->
