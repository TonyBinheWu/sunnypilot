<!-- CARROT:GENERATED schema="1" locale="ko" group="CRUISE_STOPGO" param="StoppingAccel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 정지시작가속도x0.01(-50)

**메뉴:** 주행 제어 \> 크루즈·차간 \> 정차·재출발

---

<!-- CARROT:SETTING:BEGIN StoppingAccel -->
<a id="StoppingAccel"></a>

## 정지시작가속도x0.01(-50)

`StoppingAccel`

정지 제어 진입 가속도와 정지 감속 목표를 조정합니다. -100~-50만 설정할 수 있으며 -50은 -0.50m/s²입니다. 더 음수일수록 감속 목표가 강해집니다. 이미 더 강한 감속은 유지하며, 소프트홀드는 차종별 정지 유지 가속도를 사용합니다. 변경은 주행 중에도 약 1초 안에 반영됩니다. 현대·기아 CANFD 오픈파일럿 종방향 제어에서는 StopReq를 켜는 첫 프레임부터 aReqRaw·aReqValue를 0으로 보내므로, 이 설정은 StopReq 유지 중 송신 가속도를 바꾸지 않습니다. 자동 해제·재시도는 제거되었습니다.

<!-- CARROT:AUTO:BEGIN StoppingAccel -->
<!-- CARROT:AUTO:SOURCE facts="80fecbfd3f3e9d4f5595a681e2f3a0bf765eb85a6a0a9e9410804b13b63f5677" semantic="804fd76b953b107e414ad27b3ef47d2d75140f0fd06273972f700c8ec2f23490" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `-50`
- **범위:** `-100` ~ `-50`
- **변경 단위:** `10`
- **메뉴:** 주행 제어 \> 크루즈·차간 \> 정차·재출발
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END StoppingAccel -->

<!-- CARROT:MANUAL:BEGIN StoppingAccel -->
<!-- CARROT:REVIEW reviewed-for="804fd76b953b107e414ad27b3ef47d2d75140f0fd06273972f700c8ec2f23490" reviewed-at="2026-10-10T09:34:34+00:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

**높이면(덜 음수):** 감속 목표가 약해지고 일반적인 가속도 기준의 정지 진입이 늦어집니다.

**낮추면(더 음수):** 감속 목표가 강해지고 정지 진입이 빨라지며 정지 충격이 커질 수 있습니다. 이미 더 강한 감속 요청은 유지하고, 소프트홀드는 차종별 정지 유지 가속도를 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

변경은 주행 중에도 약 1초 안에 반영됩니다. 진행 중인 정지에서 목표를 약하게 바꿔도 이미 더 강해진 출력은 즉시 줄이지 않습니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

저장값에 0.01을 곱한 m/s²를 사용합니다. 제어에서도 설정 범위를 제한합니다. 순정 ACC 종방향 제어에는 직접 적용되지 않으며, 현대·기아 CANFD에서는 StopReq 첫 프레임부터 두 aReq를 0으로 보내고 자동 재시도는 하지 않습니다. 이 설정은 정지 진입 판단에 계속 사용하지만 StopReq 유지 중 최종 송신 가속도는 바꾸지 않습니다. 소프트홀드에도 이 예외를 적용합니다. [정차·재출발 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/cruise-gap.md#stop-resume)를 참고하세요.
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END StoppingAccel -->

<!-- CARROT:SETTING:END StoppingAccel -->
