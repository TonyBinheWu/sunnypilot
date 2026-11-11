<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_TRAFFIC" param="SignalAssistMode" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 신호보조 모드 (시험)

**메뉴:** 주행 제어 \> 속도·감속 \> 신호감지

---

<!-- CARROT:SETTING:BEGIN SignalAssistMode -->
<a id="SignalAssistMode"></a>

## 신호보조 모드 (시험)

`SignalAssistMode`

0:신호보조 인식·표시·제어 모두 끔. 1:주행 중에도 인식 결과를 표시하고 알림·정차 중 적색 출발 제한을 사용합니다. 2:1의 기능에 주행 중 감속 준비 추가. 앞차가 없거나 두 추적 앞차 모두 50m보다 멀 때 유효한 적색을 확인하면 약 -0.5m/s²까지 점진적으로 감속을 요청합니다. 50m 이내 앞차가 있으면 보조 감속을 해제하고 기존 앞차 추종을 사용합니다. 정차 후에는 1과 동일하며 보조 감속만으로 정지시키지 않습니다. 정차용 적색 출발 제한은 5km/h 이하에서만 유지하며, 그보다 빨라지면 이전 정지 기억을 해제합니다. 야간에는 적색 램프 2개 이상과 도로 방향 지지가 필요합니다. 적색 증거 소실·녹색 충돌 시 감속 준비를 해제합니다. 인식 표시는 제어 개입과 별개이며 이전 결과는 최대 2초간 흐리게 표시한 뒤 미확인으로 전환합니다. 기본 모델과 별개인 시험 기능으로 오감지·미감지가 가능합니다.

<!-- CARROT:AUTO:BEGIN SignalAssistMode -->
<!-- CARROT:AUTO:SOURCE facts="91f3c9bb108d40eefcb7fbb59fea1c9d74108d8f20da0fb23b1588df3e644d77" semantic="ba8119151eab7971db5323d2e70e29e83140178360a67bae13fb690b0084d730" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `2`
- **변경 단위:** `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 신호감지
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SignalAssistMode -->

<!-- CARROT:MANUAL:BEGIN SignalAssistMode -->
<!-- CARROT:REVIEW reviewed-for="" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

정차용 적색 출발 제한은 정차·저속 출발 중 유지하며, 5km/h를 넘으면 이전 정지 기억을 해제합니다. 출발 후 앞차 인식이 끊겨도 이 기억으로 다시 정지시키지 않으며, 기존 모델·앞차 제어와 운전자가 지정한 정지는 유지합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END SignalAssistMode -->

<!-- CARROT:SETTING:END SignalAssistMode -->
