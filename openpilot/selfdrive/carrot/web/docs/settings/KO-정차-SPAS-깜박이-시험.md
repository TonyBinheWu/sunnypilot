<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_CANFD" param="CanfdBlinkerTest" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 정차 SPAS 깜박이 시험

**메뉴:** 차량·하드웨어 \> CANFD·HDA

---

<!-- CARROT:SETTING:BEGIN CanfdBlinkerTest -->
<a id="CanfdBlinkerTest"></a>

## 정차 SPAS 깜박이 시험

`CanfdBlinkerTest`

SPAS 사용 설정 후 재부팅해야 합니다. 0 취소, 1/2 ECU 응답 확인 후 좌/우 연속, 3/4 응답 확인 후 짧은 신호+유지. 아이오닉5PE 정차 비교: 5/6 연속 3초, 7/8 0.2초 송신+기존 유지(총 10초), 9/10 0.2초만 송신. 11/12 순정 수신 직후 시작 신호를 수신당 한 번씩 점등 확인 후 0.1초까지(최대 0.5초) 보내고 기존 유지(총 10초). 13/14 순정 수신 직후 SPAS만 반복해 최대 10초 유지(기존 유지 신호 없음). 동시 송신 시험은 ECU 정지 명령을 보내지 않습니다. P·속도 0·제어 비활성을 계속 확인하며 시작 후 30초 대기합니다. 취소 또는 재시도는 0을 선택하세요. 시작 시 0으로 초기화합니다. 15/16: 첨부 원본 패치 순서(APRK 1003→5프레임 뒤 288301, 응답 대기 없이 SPAS 50Hz) 좌/우 정차 시험. 실제 제어 프레임과 원본 패커 사용, 최대 10초 후 1001 복구. CAN 오류·차량 상태 변화 시 중단. 17/18: parked left/right 0x3C1 lever replay at 20Hz, max 10s; no APRK/SPAS, cancel on driver/input/CAN change.

<!-- CARROT:AUTO:BEGIN CanfdBlinkerTest -->
<!-- CARROT:AUTO:SOURCE facts="237f0de6a8d6eb97f93fbecbdaa7f56cecb9c59c7b2b191f9a66e78e586b9c7c" semantic="fb7269f5f606690f79807f0151cfbd3c0ce1118aee4eacbe624733fae2caa93e" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0`
- **범위:** `0` ~ `18`
- **변경 단위:** `1`
- **메뉴:** 차량·하드웨어 \> CANFD·HDA
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END CanfdBlinkerTest -->

<!-- CARROT:MANUAL:BEGIN CanfdBlinkerTest -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:MANUAL:END CanfdBlinkerTest -->

<!-- CARROT:SETTING:END CanfdBlinkerTest -->
