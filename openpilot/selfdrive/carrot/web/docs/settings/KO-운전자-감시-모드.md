<!-- CARROT:GENERATED schema="1" locale="ko" group="VEH_DM" param="DriverMonitoringMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 운전자 감시 모드

**메뉴:** 차량·하드웨어 \> 운전자 모니터링

---

<!-- CARROT:SETTING:BEGIN DriverMonitoringMode -->
<a id="DriverMonitoringMode"></a>

## 운전자 감시 모드

`DriverMonitoringMode`

0: 기본, 1: 실험 모드. 실험 모드는 법규에 위배될 수 있으므로 통제된 시험 환경에서만 사용하세요. 카메라 없는 기본 감시는 15/30/45초이며, 실험 모드는 관측 가능한 빈 직선도로에서 30/60/90초로 늘립니다. 주변 이동 차량이 없다가 처음 확인될 때만 20초간 기본 모드 기준으로 감시합니다. 차량 추가나 지속 관측으로 연장하지 않으며 이후 실험 감시로 복귀합니다. 이 구간에는 카메라 조작 유예·전방주시 강제 초기화·검출 완화를 적용하지 않고 이전 유예도 종료합니다. 카메라 있는 0은 콤마 순정입니다. 카메라 있는 1은 10/16/26초, 빈 도로에서는 20/32/52초이며 고개 방향 허용 폭을 20% 늘립니다. 운전자·BT 조작은 감시시간을 초기화하고 카메라 경고를 45초 또는 90초 유예한 뒤 카메라 감시를 시작합니다. 유예는 졸음·눈 감김·휴대전화 경고도 지연합니다. 뚜렷한 전방주시가 2초 유지되면 카메라 감시시간을 초기화합니다. 최고 경고·재사용 제한은 조작으로 해제하지 않습니다. 카메라 고장은 자동으로 조작 감시로 전환합니다. 0도 법적 인증을 보장하지 않습니다. 모드 변경은 재부팅 없이 약 0.5초 주기로 적용됩니다. 전환해도 누적 감시시간·경고 횟수·재사용 제한은 초기화되지 않으며, 이전 조작 유예와 전방주시 연속 판정은 종료됩니다. 현대·기아·제네시스 CAN-FD에서 차종명 제한 없이 수신 형식·체크섬·카운터·최신성이 검증된 원본 STEER\_TOUCH\_2AF 터치는 카메라 불가 시 접촉 중 감시시간을 초기화하며, 카메라 정상·1번은 새 접촉만 조작으로 인정합니다. 카메라 정상·0번은 그대로입니다. 공통 예외: 카메라 유무와 0·1번 모두 P단·완전 정차·인게이지 해제가 유효한 신호로 1초간 확인되면 누적 경고와 재사용 제한을 초기화합니다. 속도 0이나 OFF/ON만으로는 해제하지 않으며 재인게이지는 수동입니다.

<!-- CARROT:AUTO:BEGIN DriverMonitoringMode -->
<!-- CARROT:AUTO:SOURCE facts="e7058b72c554b6cdba80c8e1855432f592ae58d17ed4dda15b9dc8bbdd7b8bf7" semantic="41de43ecd7b558bf3408066b776219f5a1367f4ed91a5aae8a31995a4f0b821a" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 선택
- **기본값:** 기본 (`0`)
- **범위:** 기본 (`0`) ~ 실험 모드 (시험 전용) (`1`)
- **변경 단위:** `1`
- **선택지:** `0` 기본, `1` 실험 모드 (시험 전용)
- **메뉴:** 차량·하드웨어 \> 운전자 모니터링
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END DriverMonitoringMode -->

<!-- CARROT:MANUAL:BEGIN DriverMonitoringMode -->
<!-- CARROT:REVIEW reviewed-for="71597058dbc3a5673ec5c3fa80f182b7386309654371ebfdfcbf577dd83a765d" reviewed-at="2026-09-28T23:46:27.836670+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

기본 모드는 정상 카메라에서 콤마 순정을 유지하고 카메라 사용 불가 시 별도 조작 감시를 사용합니다. 실험 모드는 빈 도로에서 시간을 늘리며, 운전자·BT 조작 후 카메라 경고를 유예하고 전방주시로 감시시간을 초기화합니다.

현대·기아·제네시스 CAN-FD에서 차종명 제한 없이 원본 STEER_TOUCH_2AF의 형식·체크섬·카운터·최신성을 검증한 핸들 터치는 카메라 사용 불가 시 접촉 중 조작 감시시간을 초기화합니다. 카메라 정상·실험 모드는 유효한 손 뗌 뒤 새 접촉만 조작으로 인정하며, 계속 잡거나 신호가 복구된 것만으로 유예를 반복하지 않습니다. 카메라 정상·기본 모드는 그대로이고 최고 경고는 터치로 해제하지 않습니다.
카메라 미장착·준비 지연·고장 시 별도 안내 없이 조작 감시로 전환하고, 필요한 데이터가 2초 연속 정상이면 카메라 감시로 복귀합니다. 조작 무반응 경고와 DM 프로세스·차량 통신 오류 감지는 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

실험 모드는 통제된 시험 환경에서만 사용하세요. 모드 변경은 재부팅 없이 약 0.5초 주기로 적용되며 누적 감시시간·경고 횟수·재사용 제한은 유지합니다. 이전 조작 유예와 전방주시 연속 판정은 종료됩니다. 주변 이동 차량이 없다가 처음 확인될 때만 20초간 기본 감시로 전환합니다. 추가 차량이나 지속 관측은 연장 사유가 아니며, 이후 실험 감시로 복귀하되 차량이 남아 있으면 빈 도로 추가 배율은 적용하지 않습니다. 카메라가 정상이면 이 구간에는 순정 판단·입력을 적용하고 실험 조작 유예와 전방주시 강제 초기화를 중단합니다. 이전 유예는 종료되며, 모든 차량의 마지막 관측 이후 2초 보존시간이 지나 비어야 다음 출현을 새로 인정합니다.

카메라 유무와 모드에 관계없이, P단·완전 정차·인게이지 해제가 유효한 차량 신호로 1초간 확인되면 누적 경고와 재사용 제한을 초기화합니다. 이는 기본 모드에도 적용되는 순정 대비 예외이며, 속도 0이나 OFF/ON만으로는 해제되지 않고 재인게이지는 수동입니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

조작 유예는 졸음·눈 감김·휴대전화 경고도 지연하며, 각성이나 법적 적합성을 보장하지 않습니다. [네 가지 모드의 시간·유예·초기화·최고 경고 제한](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/driver-monitoring.md)을 확인하세요.
<!-- CARROT:SECTION:END REFERENCE -->

<!-- CARROT:MANUAL:END DriverMonitoringMode -->

<!-- CARROT:SETTING:END DriverMonitoringMode -->
