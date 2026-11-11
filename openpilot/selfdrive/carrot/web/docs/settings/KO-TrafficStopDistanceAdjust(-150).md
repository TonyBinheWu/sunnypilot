<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_TRAFFIC" param="TrafficStopDistanceAdjust" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# TrafficStopDistanceAdjust(-150)

**메뉴:** 주행 제어 \> 속도·감속 \> 신호감지

---

<!-- CARROT:SETTING:BEGIN TrafficStopDistanceAdjust -->
<a id="TrafficStopDistanceAdjust"></a>

## TrafficStopDistanceAdjust(-150)

`TrafficStopDistanceAdjust`

신호정지위치 보정. 정지점 바로 앞의 정지차가 확인되면 자동으로 차량 기준 보정

<!-- CARROT:AUTO:BEGIN TrafficStopDistanceAdjust -->
<!-- CARROT:AUTO:SOURCE facts="bd497d61e61650ac64cfd54e948d27756cb0d56ba85c7fd316f2803ea727e5e4" semantic="2c0307757de5931be931759240b41c4dbfa911d065c2e58f09356222e3b41eaa" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `-150cm`
- **범위:** `-600cm` ~ `600cm`
- **변경 단위:** `100`
- **표시 단위:** `cm`
- **메뉴:** 주행 제어 \> 속도·감속 \> 신호감지
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END TrafficStopDistanceAdjust -->

<!-- CARROT:MANUAL:BEGIN TrafficStopDistanceAdjust -->
<!-- CARROT:REVIEW reviewed-for="97928b4e4d95a660327b16834bf290d7c92ac14c300939e11ba569c177f25244" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

차량이 움직이는 동안 신호 정지용 가상 장애물 위치에 더하는 거리 보정입니다.

- **양수:** 정지 목표를 도로 진행 방향으로 더 멀리 옮깁니다.
- **음수:** 정지 목표를 차량 쪽으로 당깁니다.

정지 상태에서는 코드가 별도의 `-2 m` 보정을 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

신호가 명확히 보이는 동일 교차로에서 감지·정지·출발 시점과 정지 위치를 확인합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END TrafficStopDistanceAdjust -->

<!-- CARROT:SETTING:END TrafficStopDistanceAdjust -->
