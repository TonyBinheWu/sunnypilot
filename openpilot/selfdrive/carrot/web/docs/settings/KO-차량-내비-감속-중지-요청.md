<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CAMERA" param="VehicleNaviDecelCancel" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 차량 내비 감속 중지 요청

**메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라

---

<!-- CARROT:SETTING:BEGIN VehicleNaviDecelCancel -->
<a id="VehicleNaviDecelCancel"></a>

## 차량 내비 감속 중지 요청

`VehicleNaviDecelCancel`

외부 내비가 연결되지 않았을 때만 적용합니다(순정 내비 CAN). 켜면 openpilot 작동 중(약 18km/h 이상) 아래에서 켠 종류로 감속하는 동안 크루즈 + 버튼을 한 번 누르거나 악셀톡(가속 페달을 0.4초 미만으로 밟았다 뗌)을 해서 그 지점의 감속을 중지합니다. 이 입력은 설정 속도를 올리지 않습니다(+1, 악셀톡 +10 모두 반영 안 함). 중지는 그 카메라·방지턱 하나에만 적용되고 다음 것은 다시 감속합니다. 신호·후면 카메라와 구간단속은 중지할 수 없고, 고정식 카메라는 세부 항목을 따로 켰을 때만 중지합니다. 세부 항목(박스형 카메라, 이동식 구간, 과속방지턱, 고정식 카메라)에서 종류별로 켜고 끕니다.

<!-- CARROT:AUTO:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:AUTO:SOURCE facts="15103c79ca00e6ca98b45c32723719bef3c32198766bc1564ee14c086038e8a9" semantic="b4932756ef27f4ad90176e3da43004bb00e3808dc92ffd2bff98e1c48d5fe10f" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 토글
- **기본값:** `0`
- **범위:** `0` ~ `1`
- **메뉴:** 주행 제어 \> 속도·감속 \> 과속카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END VehicleNaviDecelCancel -->

<!-- CARROT:MANUAL:BEGIN VehicleNaviDecelCancel -->
<!-- CARROT:REVIEW reviewed-for="b4932756ef27f4ad90176e3da43004bb00e3808dc92ffd2bff98e1c48d5fe10f" reviewed-at="2026-10-14T00:00:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

켜면 지원하는 순정 내비 감속 중 크루즈 + 또는 악셀톡으로 선택한 종류의 감속을 중지할 수 있습니다. 끄면 이 중지 입력을 사용하지 않습니다. 고정식·신호·후면 단속은 중지 대상에서 제외합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

하위 항목에서 허용할 종류를 고릅니다. 입력을 감속 중지에 사용한 주기에는 설정속도를 함께 올리지 않습니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END VehicleNaviDecelCancel -->

<!-- CARROT:SETTING:END VehicleNaviDecelCancel -->
