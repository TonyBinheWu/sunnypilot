<!-- CARROT:GENERATED schema="1" locale="ko" group="SYS_RECORD_BASIC" param="MaxTimeOffroadMin" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 자동전원OFF(분)

**메뉴:** 시스템 \> 녹화·전원 \> 녹화·전원

---

<!-- CARROT:SETTING:BEGIN MaxTimeOffroadMin -->
<a id="MaxTimeOffroadMin"></a>

## 자동전원OFF(분)

`MaxTimeOffroadMin`

시동이 꺼지고 해당 시간이 경과하면 콤마가 꺼집니다.

<!-- CARROT:AUTO:BEGIN MaxTimeOffroadMin -->
<!-- CARROT:AUTO:SOURCE facts="73ad2d34f944d0a65d5d88e2affc8a01b1e4e31e419af52ab3d19dddb33ead62" semantic="3c6bd1ba89c52b9eb29c02d193878767c4a527a2cd122355fc4d67ca6d8eeaa8" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `60min`
- **범위:** `0min` ~ `3000min`
- **변경 단위:** `10`
- **표시 단위:** `min`
- **메뉴:** 시스템 \> 녹화·전원 \> 녹화·전원
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END MaxTimeOffroadMin -->

<!-- CARROT:MANUAL:BEGIN MaxTimeOffroadMin -->
<!-- CARROT:REVIEW reviewed-for="3c6bd1ba89c52b9eb29c02d193878767c4a527a2cd122355fc4d67ca6d8eeaa8" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

시동이 꺼지고 해당 시간이 경과하면 콤마가 꺼집니다.

- **값을 높이면:** 적용 시간 또는 지연 기준이 길어집니다.
- **값을 낮추면:** 적용 시간 또는 지연 기준이 짧아집니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

저장 공간과 전원 조건을 확인한 뒤 설정하고, 다음 녹화 또는 오프로드 전환에서 결과를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END MaxTimeOffroadMin -->

<!-- CARROT:SETTING:END MaxTimeOffroadMin -->
