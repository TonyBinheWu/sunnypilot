<!-- CARROT:GENERATED-CATALOG -->
# 전체 설정 · Settings catalog · 设置目录

Generated from `openpilot/selfdrive/carrot_settings.json`.

## 전체 설정 사전 · `ko`

현재 설정 카탈로그에서 자동 생성된 설정별 페이지입니다.

### 주행 제어

#### 시작·오토

##### 시작 동작

- [오토인게이지](https://github.com/ajouatom/openpilot/wiki/KO-%EC%98%A4%ED%86%A0%EC%9D%B8%EA%B2%8C%EC%9D%B4%EC%A7%80) — `AutoEngage`
- [상시 조향](https://github.com/ajouatom/openpilot/wiki/KO-%EC%83%81%EC%8B%9C-%EC%A1%B0%ED%96%A5) — `AlwaysLateral`
- [Tesla 자동 방향지시등](https://github.com/ajouatom/openpilot/wiki/KO-Tesla-%EC%9E%90%EB%8F%99-%EB%B0%A9%ED%96%A5%EC%A7%80%EC%8B%9C%EB%93%B1) — `TeslaAutoTurnSignals`
- [Tesla CAN 빨간불 정지](https://github.com/ajouatom/openpilot/wiki/KO-Tesla-CAN-%EB%B9%A8%EA%B0%84%EB%B6%88-%EC%A0%95%EC%A7%80) — `TeslaCanTrafficStop`
- [Tesla 수동 차로변경 램프](https://github.com/ajouatom/openpilot/wiki/KO-Tesla-%EC%88%98%EB%8F%99-%EC%B0%A8%EB%A1%9C%EB%B3%80%EA%B2%BD-%EB%9E%A8%ED%94%84) — `TeslaManualLaneSignals`
- [Tesla 모델 의도 램프](https://github.com/ajouatom/openpilot/wiki/KO-Tesla-%EB%AA%A8%EB%8D%B8-%EC%9D%98%EB%8F%84-%EB%9E%A8%ED%94%84) — `TeslaModelDesireSignals`
- [Tesla 모델 경로 램프](https://github.com/ajouatom/openpilot/wiki/KO-Tesla-%EB%AA%A8%EB%8D%B8-%EA%B2%BD%EB%A1%9C-%EB%9E%A8%ED%94%84) — `TeslaModelPathSignals`
- [저속조향제한해제](https://github.com/ajouatom/openpilot/wiki/KO-%EC%A0%80%EC%86%8D%EC%A1%B0%ED%96%A5%EC%A0%9C%ED%95%9C%ED%95%B4%EC%A0%9C) — `DisableMinSteerSpeed`

##### 오토크루즈

- [크루즈ON거리(0cm)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88ON%EA%B1%B0%EB%A6%AC%280cm%29) — `CruiseOnDist`
- [오토크루즈제어(HKG only)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%98%A4%ED%86%A0%ED%81%AC%EB%A3%A8%EC%A6%88%EC%A0%9C%EC%96%B4%28HKG-only%29) — `AutoCruiseControl`
- [캔슬 상태 소프트홀드 허용(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%BA%94%EC%8A%AC-%EC%83%81%ED%83%9C-%EC%86%8C%ED%94%84%ED%8A%B8%ED%99%80%EB%93%9C-%ED%97%88%EC%9A%A9%280%29) — `SoftHoldOnCancel`
- [오토크루즈: 엑셀톡 시작속도](https://github.com/ajouatom/openpilot/wiki/KO-%EC%98%A4%ED%86%A0%ED%81%AC%EB%A3%A8%EC%A6%88-%EC%97%91%EC%85%80%ED%86%A1-%EC%8B%9C%EC%9E%91%EC%86%8D%EB%8F%84) — `AutoGasTokSpeed`
- [가속페달 해제 시 크루즈 해제 속도(30)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%ED%8E%98%EB%8B%AC-%ED%95%B4%EC%A0%9C-%EC%8B%9C-%ED%81%AC%EB%A3%A8%EC%A6%88-%ED%95%B4%EC%A0%9C-%EC%86%8D%EB%8F%84%2830%29) — `AutoGasCancelSpeed`
- [자동크루즈속도 업데이트](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9E%90%EB%8F%99%ED%81%AC%EB%A3%A8%EC%A6%88%EC%86%8D%EB%8F%84-%EC%97%85%EB%8D%B0%EC%9D%B4%ED%8A%B8) — `AutoGasSyncSpeed`

#### 버튼·프리셋

##### 버튼 모드

- [크루즈버튼작동모드(0)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EB%B2%84%ED%8A%BC%EC%9E%91%EB%8F%99%EB%AA%A8%EB%93%9C%280%29) — `CruiseButtonMode`
- [캔슬버튼작동모드(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%BA%94%EC%8A%AC%EB%B2%84%ED%8A%BC%EC%9E%91%EB%8F%99%EB%AA%A8%EB%93%9C%280%29) — `CancelButtonMode`
- [LFA버튼작동모드(0)](https://github.com/ajouatom/openpilot/wiki/KO-LFA%EB%B2%84%ED%8A%BC%EC%9E%91%EB%8F%99%EB%AA%A8%EB%93%9C%280%29) — `LfaButtonMode`
- [패들시프트모드(0)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%8C%A8%EB%93%A4%EC%8B%9C%ED%94%84%ED%8A%B8%EB%AA%A8%EB%93%9C%280%29) — `PaddleMode`

##### 속도 단위

- [크루즈버튼속도단위 확장(10)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EB%B2%84%ED%8A%BC%EC%86%8D%EB%8F%84%EB%8B%A8%EC%9C%84-%ED%99%95%EC%9E%A5%2810%29) — `CruiseSpeedUnit`
- [크루즈버튼롱딜레이(40)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EB%B2%84%ED%8A%BC%EB%A1%B1%EB%94%9C%EB%A0%88%EC%9D%B4%2840%29) — `CruiseButtonLongDelay`
- [크루즈버튼속도단위 기본(1)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EB%B2%84%ED%8A%BC%EC%86%8D%EB%8F%84%EB%8B%A8%EC%9C%84-%EA%B8%B0%EB%B3%B8%281%29) — `CruiseSpeedUnitBasic`

##### 버튼 테스트

- [크루즈버튼스팸쏘기(8)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EB%B2%84%ED%8A%BC%EC%8A%A4%ED%8C%B8%EC%8F%98%EA%B8%B0%288%29) — `CruiseButtonTest1`
- [크루즈버튼스팸쉬기(30)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EB%B2%84%ED%8A%BC%EC%8A%A4%ED%8C%B8%EC%89%AC%EA%B8%B0%2830%29) — `CruiseButtonTest2`
- [크루즈버튼스팸연속쏘기(1)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EB%B2%84%ED%8A%BC%EC%8A%A4%ED%8C%B8%EC%97%B0%EC%86%8D%EC%8F%98%EA%B8%B0%281%29) — `CruiseButtonTest3`

##### 속도 프리셋

- [크루즈속도1(30)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EC%86%8D%EB%8F%841%2830%29) — `CruiseSpeed1`
- [크루즈속도2(50)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EC%86%8D%EB%8F%842%2850%29) — `CruiseSpeed2`
- [크루즈속도3(80)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EC%86%8D%EB%8F%843%2880%29) — `CruiseSpeed3`
- [크루즈속도4(110)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EC%86%8D%EB%8F%844%28110%29) — `CruiseSpeed4`
- [크루즈속도5(130)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EC%86%8D%EB%8F%845%28130%29) — `CruiseSpeed5`

#### 차량 조향

##### ONNX 차선·BSD

- [ONNX 차선·BSD 인식](https://github.com/ajouatom/openpilot/wiki/KO-ONNX-%EC%B0%A8%EC%84%A0%C2%B7BSD-%EC%9D%B8%EC%8B%9D) — `ShareData`
- [ONNX 시각 BSD](https://github.com/ajouatom/openpilot/wiki/KO-ONNX-%EC%8B%9C%EA%B0%81-BSD) — `OnnxBsdEnabled`
- [차선 신뢰도 기준](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0-%EC%8B%A0%EB%A2%B0%EB%8F%84-%EA%B8%B0%EC%A4%80) — `OnnxLaneThreshold`
- [차선 계산 간격](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0-%EA%B3%84%EC%82%B0-%EA%B0%84%EA%B2%A9) — `OnnxLaneIntervalMs`
- [BSD 신뢰도 기준](https://github.com/ajouatom/openpilot/wiki/KO-BSD-%EC%8B%A0%EB%A2%B0%EB%8F%84-%EA%B8%B0%EC%A4%80) — `OnnxBsdThreshold`
- [BSD 유지 시간](https://github.com/ajouatom/openpilot/wiki/KO-BSD-%EC%9C%A0%EC%A7%80-%EC%8B%9C%EA%B0%84) — `OnnxBsdSmoothingMs`
- [BSD 계산 간격](https://github.com/ajouatom/openpilot/wiki/KO-BSD-%EA%B3%84%EC%82%B0-%EA%B0%84%EA%B2%A9) — `OnnxBsdIntervalMs`

##### 중앙 보정

- [차선치우침 좌우보정(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0%EC%B9%98%EC%9A%B0%EC%B9%A8-%EC%A2%8C%EC%9A%B0%EB%B3%B4%EC%A0%95%280%29) — `PathOffset`
- [카메라YAW보정\*0.01deg(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B9%B4%EB%A9%94%EB%9D%BCYAW%EB%B3%B4%EC%A0%95-0.01deg%280%29) — `CameraYawTrimDeg`

##### 조향감

- [SteerActuatorDelay(30)](https://github.com/ajouatom/openpilot/wiki/KO-SteerActuatorDelay%2830%29) — `SteerActuatorDelay`
- [무게중심 비율](https://github.com/ajouatom/openpilot/wiki/KO-%EB%AC%B4%EA%B2%8C%EC%A4%91%EC%8B%AC-%EB%B9%84%EC%9C%A8) — `CenterToFrontRatio`
- [LatSmoothSec(13)x0.01](https://github.com/ajouatom/openpilot/wiki/KO-LatSmoothSec%2813%29x0.01) — `LatSmoothSec`
- [자동조향일시중지각도(300)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9E%90%EB%8F%99%EC%A1%B0%ED%96%A5%EC%9D%BC%EC%8B%9C%EC%A4%91%EC%A7%80%EA%B0%81%EB%8F%84%28300%29) — `LatSuspendAngleDeg`
- [CustomSteerRatiox0.1(0)](https://github.com/ajouatom/openpilot/wiki/KO-CustomSteerRatiox0.1%280%29) — `CustomSR`
- [CustomSteerRatioRatex0.01(100)](https://github.com/ajouatom/openpilot/wiki/KO-CustomSteerRatioRatex0.01%28100%29) — `SteerRatioRate`

##### 차로 변경 (자동 턴)

- [ATC: AutoTurnControl(0)](https://github.com/ajouatom/openpilot/wiki/KO-ATC-AutoTurnControl%280%29) — `AutoTurnControl`
- [수동 차선변경 깜박이(시험)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%88%98%EB%8F%99-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EA%B9%9C%EB%B0%95%EC%9D%B4%28%EC%8B%9C%ED%97%98%29) — `ManualLaneChangeIndicator`
- [수동 턴 자동깜박이(시험)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%88%98%EB%8F%99-%ED%84%B4-%EC%9E%90%EB%8F%99%EA%B9%9C%EB%B0%95%EC%9D%B4%28%EC%8B%9C%ED%97%98%29) — `ManualTurnIndicator`
- [모델 desire 자동깜박이(시험)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%AA%A8%EB%8D%B8-desire-%EC%9E%90%EB%8F%99%EA%B9%9C%EB%B0%95%EC%9D%B4%28%EC%8B%9C%ED%97%98%29) — `ModelDesireIndicator`
- [모델 경로 자동깜박이(시험)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%AA%A8%EB%8D%B8-%EA%B2%BD%EB%A1%9C-%EC%9E%90%EB%8F%99%EA%B9%9C%EB%B0%95%EC%9D%B4%28%EC%8B%9C%ED%97%98%29) — `ModelPathIndicator`
- [우회전 전 자동 차선변경 거리(m)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9A%B0%ED%9A%8C%EC%A0%84-%EC%A0%84-%EC%9E%90%EB%8F%99-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EA%B1%B0%EB%A6%AC%28m%29) — `AutoTurnControlRightLaneChange`
- [ATC: 턴속도(20)](https://github.com/ajouatom/openpilot/wiki/KO-ATC-%ED%84%B4%EC%86%8D%EB%8F%84%2820%29) — `AutoTurnControlSpeedTurn`
- [ATC: 시간거리(3)](https://github.com/ajouatom/openpilot/wiki/KO-ATC-%EC%8B%9C%EA%B0%84%EA%B1%B0%EB%A6%AC%283%29) — `AutoTurnControlTurnEnd`
- [ATC Helper 맵전환(0)](https://github.com/ajouatom/openpilot/wiki/KO-ATC-Helper-%EB%A7%B5%EC%A0%84%ED%99%98%280%29) — `AutoTurnMapChange`
- [차선변경 조향토크 사용](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EC%A1%B0%ED%96%A5%ED%86%A0%ED%81%AC-%EC%82%AC%EC%9A%A9) — `LaneChangeNeedTorque`
- [깜박이 자동제어](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B9%9C%EB%B0%95%EC%9D%B4-%EC%9E%90%EB%8F%99%EC%A0%9C%EC%96%B4) — `AutoBlinkerControl`
- [깜빡이 레버로 회전/차선변경 구분 (km/h, 0=끔)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B9%9C%EB%B9%A1%EC%9D%B4-%EB%A0%88%EB%B2%84%EB%A1%9C-%ED%9A%8C%EC%A0%84-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EA%B5%AC%EB%B6%84-%28km-h%2C-0%3D%EB%81%94%29) — `BlinkerLatchedTurn`
- [원터치 차선변경 요청 5회 대기](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9B%90%ED%84%B0%EC%B9%98-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EC%9A%94%EC%B2%AD-5%ED%9A%8C-%EB%8C%80%EA%B8%B0) — `LaneChangeLeverWait`
- [차선변경 지연시간x0.1s(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EC%A7%80%EC%97%B0%EC%8B%9C%EA%B0%84x0.1s%280%29) — `LaneChangeDelay`
- [차선변경 BSD](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-BSD) — `LaneChangeBsd`
- [차선변경 차선판단](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EC%B0%A8%EC%84%A0%ED%8C%90%EB%8B%A8) — `LaneLineCheck`

##### 레인모드

- [\*LATMPC.PathCost(200)](https://github.com/ajouatom/openpilot/wiki/KO-LATMPC.PathCost%28200%29) — `LatMpcPathCost`
- [\*LATMPC.MotionCost(7)](https://github.com/ajouatom/openpilot/wiki/KO-LATMPC.MotionCost%287%29) — `LatMpcMotionCost`
- [\*LATMPC.AccelCost(120)](https://github.com/ajouatom/openpilot/wiki/KO-LATMPC.AccelCost%28120%29) — `LatMpcAccelCost`
- [\*LATMPC.JerkCost(4)](https://github.com/ajouatom/openpilot/wiki/KO-LATMPC.JerkCost%284%29) — `LatMpcJerkCost`
- [\*LATMPC.SteerRateCost(7)](https://github.com/ajouatom/openpilot/wiki/KO-LATMPC.SteerRateCost%287%29) — `LatMpcSteeringRateCost`
- [\*LATMPC.InputOffset(4)](https://github.com/ajouatom/openpilot/wiki/KO-LATMPC.InputOffset%284%29) — `LatMpcInputOffset`
- [레인모드: 속도(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%A0%88%EC%9D%B8%EB%AA%A8%EB%93%9C-%EC%86%8D%EB%8F%84%280%29) — `UseLaneLineSpeed`
- [레인모드: 커브속도(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%A0%88%EC%9D%B8%EB%AA%A8%EB%93%9C-%EC%BB%A4%EB%B8%8C%EC%86%8D%EB%8F%84%280%29) — `UseLaneLineCurveSpeed`
- [레인모드: 차선조절옵셋 (0)cm](https://github.com/ajouatom/openpilot/wiki/KO-%EB%A0%88%EC%9D%B8%EB%AA%A8%EB%93%9C-%EC%B0%A8%EC%84%A0%EC%A1%B0%EC%A0%88%EC%98%B5%EC%85%8B-%280%29cm) — `AdjustLaneOffset`

##### 고급 토크

###### 토크 계수

- [NNFF 토크 제어](https://github.com/ajouatom/openpilot/wiki/KO-NNFF-%ED%86%A0%ED%81%AC-%EC%A0%9C%EC%96%B4) — `NNFF`
- [\_LateralTorqueCustom(0)](https://github.com/ajouatom/openpilot/wiki/KO-_LateralTorqueCustom%280%29) — `LateralTorqueCustom`
- [\_LateralTorqueAccelFactor\*0.001(2500)](https://github.com/ajouatom/openpilot/wiki/KO-_LateralTorqueAccelFactor-0.001%282500%29) — `LateralTorqueAccelFactor`
- [\_LateralTorqueFriction\*0.001(100)](https://github.com/ajouatom/openpilot/wiki/KO-_LateralTorqueFriction-0.001%28100%29) — `LateralTorqueFriction`
- [\_LateralTorqueKp\*0.01(100)](https://github.com/ajouatom/openpilot/wiki/KO-_LateralTorqueKp-0.01%28100%29) — `LateralTorqueKpV`
- [\_LateralTorqueKi\*0.01(10)](https://github.com/ajouatom/openpilot/wiki/KO-_LateralTorqueKi-0.01%2810%29) — `LateralTorqueKiV`
- [\_LateralTorqueKf\*0.01(100)](https://github.com/ajouatom/openpilot/wiki/KO-_LateralTorqueKf-0.01%28100%29) — `LateralTorqueKf`
- [\_LateralTorqueKd\*0.01(0)](https://github.com/ajouatom/openpilot/wiki/KO-_LateralTorqueKd-0.01%280%29) — `LateralTorqueKd`

###### 조향 제한

- [\_CustomSteerMax(0)](https://github.com/ajouatom/openpilot/wiki/KO-_CustomSteerMax%280%29) — `CustomSteerMax`
- [\_CustomSteerDeltaUp(0)](https://github.com/ajouatom/openpilot/wiki/KO-_CustomSteerDeltaUp%280%29) — `CustomSteerDeltaUp`
- [\_CustomSteerDeltaDown(0)](https://github.com/ajouatom/openpilot/wiki/KO-_CustomSteerDeltaDown%280%29) — `CustomSteerDeltaDown`
- [\_CustomSteerDeltaUpLC(0)](https://github.com/ajouatom/openpilot/wiki/KO-_CustomSteerDeltaUpLC%280%29) — `CustomSteerDeltaUpLC`
- [\_CustomSteerDeltaDownLC(0)](https://github.com/ajouatom/openpilot/wiki/KO-_CustomSteerDeltaDownLC%280%29) — `CustomSteerDeltaDownLC`

#### 속도·감속

##### 과속카메라

- [후면단속 통과 후 유지 거리(m)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%9B%84%EB%A9%B4%EB%8B%A8%EC%86%8D-%ED%86%B5%EA%B3%BC-%ED%9B%84-%EC%9C%A0%EC%A7%80-%EA%B1%B0%EB%A6%AC%28m%29) — `AutoNaviRearCameraHoldDistance`
- [과속카메라감속 완료 시간(6초)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B3%BC%EC%86%8D%EC%B9%B4%EB%A9%94%EB%9D%BC%EA%B0%90%EC%86%8D-%EC%99%84%EB%A3%8C-%EC%8B%9C%EA%B0%84%286%EC%B4%88%29) — `AutoNaviSpeedCtrlEnd`
- [네비게이션감속모드(2)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%84%A4%EB%B9%84%EA%B2%8C%EC%9D%B4%EC%85%98%EA%B0%90%EC%86%8D%EB%AA%A8%EB%93%9C%282%29) — `AutoNaviSpeedCtrlMode`
- [차량 내비 CAN 감속 적용 모드](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EB%9F%89-%EB%82%B4%EB%B9%84-CAN-%EA%B0%90%EC%86%8D-%EC%A0%81%EC%9A%A9-%EB%AA%A8%EB%93%9C) — `VehicleNaviCanControl`
- [차량 내비 어린이보호구역 30km/h 제한](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EB%9F%89-%EB%82%B4%EB%B9%84-%EC%96%B4%EB%A6%B0%EC%9D%B4%EB%B3%B4%ED%98%B8%EA%B5%AC%EC%97%AD-30km-h-%EC%A0%9C%ED%95%9C) — `VehicleNaviSchoolZoneControl`
- [차량 내비 감속 중지 요청](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EB%9F%89-%EB%82%B4%EB%B9%84-%EA%B0%90%EC%86%8D-%EC%A4%91%EC%A7%80-%EC%9A%94%EC%B2%AD) — `VehicleNaviDecelCancel`
- [감속 중지: 박스형 카메라](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%90%EC%86%8D-%EC%A4%91%EC%A7%80-%EB%B0%95%EC%8A%A4%ED%98%95-%EC%B9%B4%EB%A9%94%EB%9D%BC) — `VehicleNaviDecelCancelBox`
- [감속 중지: 이동식 단속 구간](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%90%EC%86%8D-%EC%A4%91%EC%A7%80-%EC%9D%B4%EB%8F%99%EC%8B%9D-%EB%8B%A8%EC%86%8D-%EA%B5%AC%EA%B0%84) — `VehicleNaviDecelCancelMobileZone`
- [감속 중지: 과속방지턱](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%90%EC%86%8D-%EC%A4%91%EC%A7%80-%EA%B3%BC%EC%86%8D%EB%B0%A9%EC%A7%80%ED%84%B1) — `VehicleNaviDecelCancelBump`
- [감속 중지: 과속카메라 종류 미탐지 건 \[실험\]](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%90%EC%86%8D-%EC%A4%91%EC%A7%80-%EA%B3%BC%EC%86%8D%EC%B9%B4%EB%A9%94%EB%9D%BC-%EC%A2%85%EB%A5%98-%EB%AF%B8%ED%83%90%EC%A7%80-%EA%B1%B4-%EC%8B%A4%ED%97%98) — `VehicleNaviDecelCancelUnknown`
- [감속 중지: 경고 조기 시작 보정 \[실험\]](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%90%EC%86%8D-%EC%A4%91%EC%A7%80-%EA%B2%BD%EA%B3%A0-%EC%A1%B0%EA%B8%B0-%EC%8B%9C%EC%9E%91-%EB%B3%B4%EC%A0%95-%EC%8B%A4%ED%97%98) — `VehicleNaviDecelCancelEarlyWarning`
- [차량 내비 구간단속 평균속도 제어](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EB%9F%89-%EB%82%B4%EB%B9%84-%EA%B5%AC%EA%B0%84%EB%8B%A8%EC%86%8D-%ED%8F%89%EA%B7%A0%EC%86%8D%EB%8F%84-%EC%A0%9C%EC%96%B4) — `VehicleNaviSectionAvgControl`
- [차량 수신 과속카메라 감속(항상 적용)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EB%9F%89-%EC%88%98%EC%8B%A0-%EA%B3%BC%EC%86%8D%EC%B9%B4%EB%A9%94%EB%9D%BC-%EA%B0%90%EC%86%8D%28%ED%95%AD%EC%83%81-%EC%A0%81%EC%9A%A9%29) — `VehicleSpeedCameraControlMode`
- [차량 과속카메라 가상거리 시간(6.0초)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EB%9F%89-%EA%B3%BC%EC%86%8D%EC%B9%B4%EB%A9%94%EB%9D%BC-%EA%B0%80%EC%83%81%EA%B1%B0%EB%A6%AC-%EC%8B%9C%EA%B0%84%286.0%EC%B4%88%29) — `VehicleSpeedCameraDistanceTime`
- [과속카메라 감속율 x0.01m/s^2(120)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B3%BC%EC%86%8D%EC%B9%B4%EB%A9%94%EB%9D%BC-%EA%B0%90%EC%86%8D%EC%9C%A8-x0.01m-s%5E2%28120%29) — `AutoNaviSpeedDecelRate`
- [네비알림 카운트다운 방법](https://github.com/ajouatom/openpilot/wiki/KO-%EB%84%A4%EB%B9%84%EC%95%8C%EB%A6%BC-%EC%B9%B4%EC%9A%B4%ED%8A%B8%EB%8B%A4%EC%9A%B4-%EB%B0%A9%EB%B2%95) — `AutoNaviCountDownMode`
- [과속카메라 제한속도적용율(105)%](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B3%BC%EC%86%8D%EC%B9%B4%EB%A9%94%EB%9D%BC-%EC%A0%9C%ED%95%9C%EC%86%8D%EB%8F%84%EC%A0%81%EC%9A%A9%EC%9C%A8%28105%29) — `AutoNaviSpeedSafetyFactor`

##### 제한속도

- [자동속도증가 (100)%](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9E%90%EB%8F%99%EC%86%8D%EB%8F%84%EC%A6%9D%EA%B0%80-%28100%29) — `AutoSpeedUptoRoadSpeedLimit`
- [자동도로제한속도감속 (50)%](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9E%90%EB%8F%99%EB%8F%84%EB%A1%9C%EC%A0%9C%ED%95%9C%EC%86%8D%EB%8F%84%EA%B0%90%EC%86%8D-%2850%29) — `AutoRoadSpeedAdjust`
- [도로제한속도맞춤(-1)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%8F%84%EB%A1%9C%EC%A0%9C%ED%95%9C%EC%86%8D%EB%8F%84%EB%A7%9E%EC%B6%A4%28-1%29) — `AutoRoadSpeedLimitOffset`

##### 방지턱

- [사고방지턱 감속완료시간시점(1s)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%82%AC%EA%B3%A0%EB%B0%A9%EC%A7%80%ED%84%B1-%EA%B0%90%EC%86%8D%EC%99%84%EB%A3%8C%EC%8B%9C%EA%B0%84%EC%8B%9C%EC%A0%90%281s%29) — `AutoNaviSpeedBumpTime`
- [과속방지턱 속도(35Km/h)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B3%BC%EC%86%8D%EB%B0%A9%EC%A7%80%ED%84%B1-%EC%86%8D%EB%8F%84%2835Km-h%29) — `AutoNaviSpeedBumpSpeed`
- [방지턱 감속 조기 종료 거리(200cm)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%B0%A9%EC%A7%80%ED%84%B1-%EA%B0%90%EC%86%8D-%EC%A1%B0%EA%B8%B0-%EC%A2%85%EB%A3%8C-%EA%B1%B0%EB%A6%AC%28200cm%29) — `AutoNaviSpeedBumpEndDistance`

##### 커브·턴

- [커브속도 조절비율(100%)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%BB%A4%EB%B8%8C%EC%86%8D%EB%8F%84-%EC%A1%B0%EC%A0%88%EB%B9%84%EC%9C%A8%28100-%29) — `AutoCurveSpeedFactor`
- [모델 주행속도 적용 비율](https://github.com/ajouatom/openpilot/wiki/KO-%EB%AA%A8%EB%8D%B8-%EC%A3%BC%ED%96%89%EC%86%8D%EB%8F%84-%EC%A0%81%EC%9A%A9-%EB%B9%84%EC%9C%A8) — `ApplyModelSpeed`
- [커브속도 최저속도(30)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%BB%A4%EB%B8%8C%EC%86%8D%EB%8F%84-%EC%B5%9C%EC%A0%80%EC%86%8D%EB%8F%84%2830%29) — `AutoCurveSpeedLowerLimit`
- [턴속도제어방법](https://github.com/ajouatom/openpilot/wiki/KO-%ED%84%B4%EC%86%8D%EB%8F%84%EC%A0%9C%EC%96%B4%EB%B0%A9%EB%B2%95) — `TurnSpeedControlMode`
- [경로턴속도반영비율(100%)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B2%BD%EB%A1%9C%ED%84%B4%EC%86%8D%EB%8F%84%EB%B0%98%EC%98%81%EB%B9%84%EC%9C%A8%28100-%29) — `MapTurnSpeedFactor`

##### 신호감지

- [TrafficStopDistanceAdjust(-150)](https://github.com/ajouatom/openpilot/wiki/KO-TrafficStopDistanceAdjust%28-150%29) — `TrafficStopDistanceAdjust`
- [앞차 브레이크등 관찰 (실험)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%95%9E%EC%B0%A8-%EB%B8%8C%EB%A0%88%EC%9D%B4%ED%81%AC%EB%93%B1-%EA%B4%80%EC%B0%B0-%28%EC%8B%A4%ED%97%98%29) — `LeadBrakeLights`
- [신호보조 모드 (시험)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%8B%A0%ED%98%B8%EB%B3%B4%EC%A1%B0-%EB%AA%A8%EB%93%9C-%28%EC%8B%9C%ED%97%98%29) — `SignalAssistMode`
- [신호감지 기능](https://github.com/ajouatom/openpilot/wiki/KO-%EC%8B%A0%ED%98%B8%EA%B0%90%EC%A7%80-%EA%B8%B0%EB%8A%A5) — `TrafficLightDetectMode`

#### 크루즈·차간

##### 가속 성향

###### 드라이브 모드

- [드라이브모드:(3)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%B8%8C%EB%AA%A8%EB%93%9C-%283%29) — `MyDrivingMode`
- [드라이브모드: 자동](https://github.com/ajouatom/openpilot/wiki/KO-%EB%93%9C%EB%9D%BC%EC%9D%B4%EB%B8%8C%EB%AA%A8%EB%93%9C-%EC%9E%90%EB%8F%99) — `MyDrivingModeAuto`

###### 속도별 가속값

- [가속도설정 0 : 0km/h(160)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%EB%8F%84%EC%84%A4%EC%A0%95-0-0km-h%28160%29) — `CruiseMaxVals0`
- [가속도설정 1 : 10km/h(160)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%EB%8F%84%EC%84%A4%EC%A0%95-1-10km-h%28160%29) — `CruiseMaxVals1`
- [가속도설정 2 : 40km/h(120)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%EB%8F%84%EC%84%A4%EC%A0%95-2-40km-h%28120%29) — `CruiseMaxVals2`
- [가속도설정 3 : 60km/h(100)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%EB%8F%84%EC%84%A4%EC%A0%95-3-60km-h%28100%29) — `CruiseMaxVals3`
- [가속도설정 4 : 80km/h(80)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%EB%8F%84%EC%84%A4%EC%A0%95-4-80km-h%2880%29) — `CruiseMaxVals4`
- [가속도설정 5 : 110km/h(70)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%EB%8F%84%EC%84%A4%EC%A0%95-5-110km-h%2870%29) — `CruiseMaxVals5`
- [가속도설정 6 : 140km/h(60)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%80%EC%86%8D%EB%8F%84%EC%84%A4%EC%A0%95-6-140km-h%2860%29) — `CruiseMaxVals6`

##### 정차·재출발

- [StopDistance(600)cm](https://github.com/ajouatom/openpilot/wiki/KO-StopDistance%28600%29cm) — `StopDistanceCarrot`
- [AChangeCostStarting](https://github.com/ajouatom/openpilot/wiki/KO-AChangeCostStarting) — `AChangeCostStarting`
- [정지출발민감도(50)x0.01](https://github.com/ajouatom/openpilot/wiki/KO-%EC%A0%95%EC%A7%80%EC%B6%9C%EB%B0%9C%EB%AF%BC%EA%B0%90%EB%8F%84%2850%29x0.01) — `VEgoStopping`
- [정지시작가속도x0.01(-50)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%A0%95%EC%A7%80%EC%8B%9C%EC%9E%91%EA%B0%80%EC%86%8D%EB%8F%84x0.01%28-50%29) — `StoppingAccel`

##### 가감속 튜닝

- [Long KpV(100)x0.01](https://github.com/ajouatom/openpilot/wiki/KO-Long-KpV%28100%29x0.01) — `LongTuningKpV`
- [Long Kf(100)x0.01](https://github.com/ajouatom/openpilot/wiki/KO-Long-Kf%28100%29x0.01) — `LongTuningKf`
- [Long KiV(0)x0.001](https://github.com/ajouatom/openpilot/wiki/KO-Long-KiV%280%29x0.001) — `LongTuningKiV`
- [LongActuatorDelay(20)x0.01](https://github.com/ajouatom/openpilot/wiki/KO-LongActuatorDelay%2820%29x0.01) — `LongActuatorDelay`

##### 차간거리

- [갭 단계 수](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%AD-%EB%8B%A8%EA%B3%84-%EC%88%98) — `CruiseGapLevels`
- [TF(1): 차량간격시간1x0.01s(110)](https://github.com/ajouatom/openpilot/wiki/KO-TF%281%29-%EC%B0%A8%EB%9F%89%EA%B0%84%EA%B2%A9%EC%8B%9C%EA%B0%841x0.01s%28110%29) — `TFollowGap1`
- [TF(2): 차량간격시간2x0.01s(120)](https://github.com/ajouatom/openpilot/wiki/KO-TF%282%29-%EC%B0%A8%EB%9F%89%EA%B0%84%EA%B2%A9%EC%8B%9C%EA%B0%842x0.01s%28120%29) — `TFollowGap2`
- [TF(3): 차량간격시간3x0.01s(140)](https://github.com/ajouatom/openpilot/wiki/KO-TF%283%29-%EC%B0%A8%EB%9F%89%EA%B0%84%EA%B2%A9%EC%8B%9C%EA%B0%843x0.01s%28140%29) — `TFollowGap3`
- [TF(4): 차량간격시간4x0.01s(160)](https://github.com/ajouatom/openpilot/wiki/KO-TF%284%29-%EC%B0%A8%EB%9F%89%EA%B0%84%EA%B2%A9%EC%8B%9C%EA%B0%844x0.01s%28160%29) — `TFollowGap4`
- [추종응답성 · 공통](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B6%94%EC%A2%85%EC%9D%91%EB%8B%B5%EC%84%B1-%C2%B7-%EA%B3%B5%ED%86%B5) — `LeadAccelResponse`
- [TF1 추종응답성](https://github.com/ajouatom/openpilot/wiki/KO-TF1-%EC%B6%94%EC%A2%85%EC%9D%91%EB%8B%B5%EC%84%B1) — `LeadAccelResponseTF1`
- [TF2 추종응답성](https://github.com/ajouatom/openpilot/wiki/KO-TF2-%EC%B6%94%EC%A2%85%EC%9D%91%EB%8B%B5%EC%84%B1) — `LeadAccelResponseTF2`
- [TF3 추종응답성](https://github.com/ajouatom/openpilot/wiki/KO-TF3-%EC%B6%94%EC%A2%85%EC%9D%91%EB%8B%B5%EC%84%B1) — `LeadAccelResponseTF3`
- [TF4 추종응답성](https://github.com/ajouatom/openpilot/wiki/KO-TF4-%EC%B6%94%EC%A2%85%EC%9D%91%EB%8B%B5%EC%84%B1) — `LeadAccelResponseTF4`
- [속도별 TF 배율](https://github.com/ajouatom/openpilot/wiki/KO-%EC%86%8D%EB%8F%84%EB%B3%84-TF-%EB%B0%B0%EC%9C%A8) — `SpeedTFFactor`
- [차선변경 반응(100%)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0%EB%B3%80%EA%B2%BD-%EB%B0%98%EC%9D%91%28100-%29) — `DynamicTFollowLC`
- [감속 시 차간 여유(0%)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B0%90%EC%86%8D-%EC%8B%9C-%EC%B0%A8%EA%B0%84-%EC%97%AC%EC%9C%A0%280-%29) — `TFollowDecelBoost`

##### 당근 크루즈

- [크루즈연비제어(2km/h)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88%EC%97%B0%EB%B9%84%EC%A0%9C%EC%96%B4%282km-h%29) — `CruiseEcoControl`
- [크루즈 코스팅 여유](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%AC%EB%A3%A8%EC%A6%88-%EC%BD%94%EC%8A%A4%ED%8C%85-%EC%97%AC%EC%9C%A0) — `CruiseCoastingPercent`
- [당근크루즈감속도x0.01(-1)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%8B%B9%EA%B7%BC%ED%81%AC%EB%A3%A8%EC%A6%88%EA%B0%90%EC%86%8D%EB%8F%84x0.01%28-1%29) — `CarrotCruiseDecel`
- [당근크루즈감속도ATCx0.01(-1)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%8B%B9%EA%B7%BC%ED%81%AC%EB%A3%A8%EC%A6%88%EA%B0%90%EC%86%8D%EB%8F%84ATCx0.01%28-1%29) — `CarrotCruiseAtcDecel`

### 차량·하드웨어

#### 현대·기아

- [핸들햅틱기능사용(0)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%95%B8%EB%93%A4%ED%96%85%ED%8B%B1%EA%B8%B0%EB%8A%A5%EC%82%AC%EC%9A%A9%280%29) — `HapticFeedbackWhenSpeedCamera`
- [HYUNDAI: CAMERA SCC](https://github.com/ajouatom/openpilot/wiki/KO-HYUNDAI-CAMERA-SCC) — `HyundaiCameraSCC`
- [HYUNDAI: LDWS ONLY CAR(0)](https://github.com/ajouatom/openpilot/wiki/KO-HYUNDAI-LDWS-ONLY-CAR%280%29) — `IsLdwsCar`

#### CANFD·HDA

- [정차 SPAS 깜박이 시험](https://github.com/ajouatom/openpilot/wiki/KO-%EC%A0%95%EC%B0%A8-SPAS-%EA%B9%9C%EB%B0%95%EC%9D%B4-%EC%8B%9C%ED%97%98) — `CanfdBlinkerTest`
- [CAN-FD SPAS 깜박이 사용(시험)](https://github.com/ajouatom/openpilot/wiki/KO-CAN-FD-SPAS-%EA%B9%9C%EB%B0%95%EC%9D%B4-%EC%82%AC%EC%9A%A9%28%EC%8B%9C%ED%97%98%29) — `CanfdBlinkerControl`
- [HDP 사용(CCNC)](https://github.com/ajouatom/openpilot/wiki/KO-HDP-%EC%82%AC%EC%9A%A9%28CCNC%29) — `HDPuse`
- [CANFD HDA2지원(0)](https://github.com/ajouatom/openpilot/wiki/KO-CANFD-HDA2%EC%A7%80%EC%9B%90%280%29) — `CanfdHDA2`
- [계기판 CAN 직접 송신](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B3%84%EA%B8%B0%ED%8C%90-CAN-%EC%A7%81%EC%A0%91-%EC%86%A1%EC%8B%A0) — `HyundaiCanfdClusterDirectTx`
- [CANFD Debug(0)](https://github.com/ajouatom/openpilot/wiki/KO-CANFD-Debug%280%29) — `CanfdDebug`

#### 레이더

- [레이더트랙,SCC레이더설정(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%A0%88%EC%9D%B4%EB%8D%94%ED%8A%B8%EB%9E%99%2CSCC%EB%A0%88%EC%9D%B4%EB%8D%94%EC%84%A4%EC%A0%95%280%29) — `EnableRadarTracks`
- [레이더 좌우 반전](https://github.com/ajouatom/openpilot/wiki/KO-%EB%A0%88%EC%9D%B4%EB%8D%94-%EC%A2%8C%EC%9A%B0-%EB%B0%98%EC%A0%84) — `RadarTrackFlip`
- [코너레이더 사용(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%BD%94%EB%84%88%EB%A0%88%EC%9D%B4%EB%8D%94-%EC%82%AC%EC%9A%A9%280%29) — `EnableCornerRadar`

#### 운전자 모니터링

- [운전자 감시 사용 (예외 설정)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9A%B4%EC%A0%84%EC%9E%90-%EA%B0%90%EC%8B%9C-%EC%82%AC%EC%9A%A9-%28%EC%98%88%EC%99%B8-%EC%84%A4%EC%A0%95%29) — `DriverMonitoringEnabled`
- [운전자 감시 모드](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9A%B4%EC%A0%84%EC%9E%90-%EA%B0%90%EC%8B%9C-%EB%AA%A8%EB%93%9C) — `DriverMonitoringMode`
- [Carrot Vision 사용](https://github.com/ajouatom/openpilot/wiki/KO-Carrot-Vision-%EC%82%AC%EC%9A%A9) — `CarrotVisionEnabled`
- [도어감지안함](https://github.com/ajouatom/openpilot/wiki/KO-%EB%8F%84%EC%96%B4%EA%B0%90%EC%A7%80%EC%95%88%ED%95%A8) — `MuteDoor`
- [안전벨트감지안함](https://github.com/ajouatom/openpilot/wiki/KO-%EC%95%88%EC%A0%84%EB%B2%A8%ED%8A%B8%EA%B0%90%EC%A7%80%EC%95%88%ED%95%A8) — `MuteSeatbelt`

#### 차량 보조

- [PCM차량속도제어](https://github.com/ajouatom/openpilot/wiki/KO-PCM%EC%B0%A8%EB%9F%89%EC%86%8D%EB%8F%84%EC%A0%9C%EC%96%B4) — `SpeedFromPCM`
- [MaxAngleFrames(89)](https://github.com/ajouatom/openpilot/wiki/KO-MaxAngleFrames%2889%29) — `MaxAngleFrames`

#### 기기 하드웨어

- [Comma Pedal사용](https://github.com/ajouatom/openpilot/wiki/KO-Comma-Pedal%EC%82%AC%EC%9A%A9) — `CommaPedalEnabled`
- [C3X Lite 하드웨어](https://github.com/ajouatom/openpilot/wiki/KO-C3X-Lite-%ED%95%98%EB%93%9C%EC%9B%A8%EC%96%B4) — `HardwareC3xLite`

### 화면 표시

#### 정보 표시

- [디버그정보 표시](https://github.com/ajouatom/openpilot/wiki/KO-%EB%94%94%EB%B2%84%EA%B7%B8%EC%A0%95%EB%B3%B4-%ED%91%9C%EC%8B%9C) — `ShowDebugUI`
- [TPMS정보 표시](https://github.com/ajouatom/openpilot/wiki/KO-TPMS%EC%A0%95%EB%B3%B4-%ED%91%9C%EC%8B%9C) — `ShowTpms`
- [시간정보표시](https://github.com/ajouatom/openpilot/wiki/KO-%EC%8B%9C%EA%B0%84%EC%A0%95%EB%B3%B4%ED%91%9C%EC%8B%9C) — `ShowDateTime`
- [패스끝표시](https://github.com/ajouatom/openpilot/wiki/KO-%ED%8C%A8%EC%8A%A4%EB%81%9D%ED%91%9C%EC%8B%9C) — `ShowPathEnd`
- [디바이스정보 표시](https://github.com/ajouatom/openpilot/wiki/KO-%EB%94%94%EB%B0%94%EC%9D%B4%EC%8A%A4%EC%A0%95%EB%B3%B4-%ED%91%9C%EC%8B%9C) — `ShowDeviceState`
- [차선정보](https://github.com/ajouatom/openpilot/wiki/KO-%EC%B0%A8%EC%84%A0%EC%A0%95%EB%B3%B4) — `ShowLaneInfo`
- [레이더감지정보(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%A0%88%EC%9D%B4%EB%8D%94%EA%B0%90%EC%A7%80%EC%A0%95%EB%B3%B4%280%29) — `ShowRadarInfo`
- [경로AR표시(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B2%BD%EB%A1%9CAR%ED%91%9C%EC%8B%9C%280%29) — `ShowRouteInfo`
- [디버그플롯(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EB%94%94%EB%B2%84%EA%B7%B8%ED%94%8C%EB%A1%AF%280%29) — `ShowPlotMode`

#### 경로 표시

- [타이어 궤적](https://github.com/ajouatom/openpilot/wiki/KO-%ED%83%80%EC%9D%B4%EC%96%B4-%EA%B6%A4%EC%A0%81) — `CarrotTireTrajectory`
- [패스종류,레인리스(9)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%8C%A8%EC%8A%A4%EC%A2%85%EB%A5%98%2C%EB%A0%88%EC%9D%B8%EB%A6%AC%EC%8A%A4%289%29) — `ShowPathMode`
- [패스색상,레인리스(12)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%8C%A8%EC%8A%A4%EC%83%89%EC%83%81%2C%EB%A0%88%EC%9D%B8%EB%A6%AC%EC%8A%A4%2812%29) — `ShowPathColor`
- [패스색상,크루즈OFF(1)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%8C%A8%EC%8A%A4%EC%83%89%EC%83%81%2C%ED%81%AC%EB%A3%A8%EC%A6%88OFF%281%29) — `ShowPathColorCruiseOff`
- [패스종류,레인모드(11)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%8C%A8%EC%8A%A4%EC%A2%85%EB%A5%98%2C%EB%A0%88%EC%9D%B8%EB%AA%A8%EB%93%9C%2811%29) — `ShowPathModeLane`
- [패스색상,레인모드(3)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%8C%A8%EC%8A%A4%EC%83%89%EC%83%81%2C%EB%A0%88%EC%9D%B8%EB%AA%A8%EB%93%9C%283%29) — `ShowPathColorLane`

#### 밝기·주행화면

- [주행중 화면밝기(100%)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%A3%BC%ED%96%89%EC%A4%91-%ED%99%94%EB%A9%B4%EB%B0%9D%EA%B8%B0%28100-%29) — `ShowCustomBrightness`
- [주행화면 구성(C4)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%A3%BC%ED%96%89%ED%99%94%EB%A9%B4-%EA%B5%AC%EC%84%B1%28C4%29) — `ShowModelView`
- [외부 HUD 연결 시 본체 카메라(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EC%97%B0%EA%B2%B0-%EC%8B%9C-%EB%B3%B8%EC%B2%B4-%EC%B9%B4%EB%A9%94%EB%9D%BC%280%29) — `ShowCameraWithCluster`

#### 외부 HUD

##### 기본

- [외부 HUD 활성화(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%ED%99%9C%EC%84%B1%ED%99%94%280%29) — `ClusterHud`
- [외부 HUD 미러 모드(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EB%AF%B8%EB%9F%AC-%EB%AA%A8%EB%93%9C%280%29) — `ClusterHudMirror`
- [외부 HUD 밝기(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EB%B0%9D%EA%B8%B0%280%29) — `ClusterHudBrightness`
- [외부 HUD 화면 회전(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%ED%99%94%EB%A9%B4-%ED%9A%8C%EC%A0%84%280%29) — `ClusterHudOrientation`
- [외부 HUD 테마(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%ED%85%8C%EB%A7%88%280%29) — `ClusterHudTheme`
- [클러스터 내비 지도 테마(1)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%B4%EB%9F%AC%EC%8A%A4%ED%84%B0-%EB%82%B4%EB%B9%84-%EC%A7%80%EB%8F%84-%ED%85%8C%EB%A7%88%281%29) — `ClusterNaviMapTheme`
- [클러스터 내비 지도 종류(0)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%B4%EB%9F%AC%EC%8A%A4%ED%84%B0-%EB%82%B4%EB%B9%84-%EC%A7%80%EB%8F%84-%EC%A2%85%EB%A5%98%280%29) — `ClusterNaviMapType`
- [클러스터 내비 지도 FPS(1)](https://github.com/ajouatom/openpilot/wiki/KO-%ED%81%B4%EB%9F%AC%EC%8A%A4%ED%84%B0-%EB%82%B4%EB%B9%84-%EC%A7%80%EB%8F%84-FPS%281%29) — `ClusterNaviMapFps`

##### 화면·카메라

- [외부 HUD 인코더(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EC%9D%B8%EC%BD%94%EB%8D%94%280%29) — `ClusterHudEncoder`
- [외부 HUD 화면 모드(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%ED%99%94%EB%A9%B4-%EB%AA%A8%EB%93%9C%280%29) — `ClusterHudScreenMode`
- [외부 HUD 좌우 배치(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EC%A2%8C%EC%9A%B0-%EB%B0%B0%EC%B9%98%280%29) — `ClusterHudPanelLayout`
- [외부 HUD 카메라 뷰 모드(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EC%B9%B4%EB%A9%94%EB%9D%BC-%EB%B7%B0-%EB%AA%A8%EB%93%9C%280%29) — `ClusterHudCameraViewMode`

##### 레이더 표시

- [외부 HUD 레이더 정보 표시(4)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EB%A0%88%EC%9D%B4%EB%8D%94-%EC%A0%95%EB%B3%B4-%ED%91%9C%EC%8B%9C%284%29) — `ClusterHudRadarInfo`
- [외부 HUD 레이더 표시 옵션(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EB%A0%88%EC%9D%B4%EB%8D%94-%ED%91%9C%EC%8B%9C-%EC%98%B5%EC%85%98%280%29) — `ClusterHudRadarDisplay`
- [외부 HUD 레이더 소스 색구분(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EB%A0%88%EC%9D%B4%EB%8D%94-%EC%86%8C%EC%8A%A4-%EC%83%89%EA%B5%AC%EB%B6%84%280%29) — `ClusterHudRadarSourceColor`

##### 성능·디버그

- [외부 HUD 디버깅(0)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%99%B8%EB%B6%80-HUD-%EB%94%94%EB%B2%84%EA%B9%85%280%29) — `ClusterHudDebug`

### 시스템

#### 녹화·전원

##### 녹화·전원

- [RoadCam녹화](https://github.com/ajouatom/openpilot/wiki/KO-RoadCam%EB%85%B9%ED%99%94) — `RecordRoadCam`
- [자동전원OFF(분)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%9E%90%EB%8F%99%EC%A0%84%EC%9B%90OFF%28%EB%B6%84%29) — `MaxTimeOffroadMin`

#### 카메라

- [광각 전방 카메라 사용](https://github.com/ajouatom/openpilot/wiki/KO-%EA%B4%91%EA%B0%81-%EC%A0%84%EB%B0%A9-%EC%B9%B4%EB%A9%94%EB%9D%BC-%EC%82%AC%EC%9A%A9) — `UseWideCamera`

#### 네트워크·지도

- [맵박스 스타일](https://github.com/ajouatom/openpilot/wiki/KO-%EB%A7%B5%EB%B0%95%EC%8A%A4-%EC%8A%A4%ED%83%80%EC%9D%BC) — `MapboxStyle`
- [부팅시 핫스팟켜기](https://github.com/ajouatom/openpilot/wiki/KO-%EB%B6%80%ED%8C%85%EC%8B%9C-%ED%95%AB%EC%8A%A4%ED%8C%9F%EC%BC%9C%EA%B8%B0) — `HotspotOnBoot`

#### 사운드

- [사운드 언어](https://github.com/ajouatom/openpilot/wiki/KO-%EC%82%AC%EC%9A%B4%EB%93%9C-%EC%96%B8%EC%96%B4) — `SoundLanguageSetting`
- [내비게이션 음성 볼륨](https://github.com/ajouatom/openpilot/wiki/KO-%EB%82%B4%EB%B9%84%EA%B2%8C%EC%9D%B4%EC%85%98-%EC%9D%8C%EC%84%B1-%EB%B3%BC%EB%A5%A8) — `SoundLanguageVolume`
- [사운드볼륨조절(100%)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%82%AC%EC%9A%B4%EB%93%9C%EB%B3%BC%EB%A5%A8%EC%A1%B0%EC%A0%88%28100-%29) — `SoundVolumeAdjust`
- [사운드볼륨조절, 인게이지 볼륨(10%)](https://github.com/ajouatom/openpilot/wiki/KO-%EC%82%AC%EC%9A%B4%EB%93%9C%EB%B3%BC%EB%A5%A8%EC%A1%B0%EC%A0%88%2C-%EC%9D%B8%EA%B2%8C%EC%9D%B4%EC%A7%80-%EB%B3%BC%EB%A5%A8%2810-%29) — `SoundVolumeAdjustEngage`

#### 소프트웨어

- [소프트웨어메뉴활성화](https://github.com/ajouatom/openpilot/wiki/KO-%EC%86%8C%ED%94%84%ED%8A%B8%EC%9B%A8%EC%96%B4%EB%A9%94%EB%89%B4%ED%99%9C%EC%84%B1%ED%99%94) — `SoftwareMenu`

## Settings catalog · `en`

Per-setting pages generated from the current settings catalog.

### Driving

#### Start & Auto

##### Engage

- [Auto Engage on onroad](https://github.com/ajouatom/openpilot/wiki/EN-Auto-Engage-on-onroad) — `AutoEngage`
- [Always Lateral](https://github.com/ajouatom/openpilot/wiki/EN-Always-Lateral) — `AlwaysLateral`
- [Tesla Automatic Turn Signals](https://github.com/ajouatom/openpilot/wiki/EN-Tesla-Automatic-Turn-Signals) — `TeslaAutoTurnSignals`
- [Tesla CAN Red Light Stop](https://github.com/ajouatom/openpilot/wiki/EN-Tesla-CAN-Red-Light-Stop) — `TeslaCanTrafficStop`
- [Tesla Manual Lane Lamps](https://github.com/ajouatom/openpilot/wiki/EN-Tesla-Manual-Lane-Lamps) — `TeslaManualLaneSignals`
- [Tesla Model Desire Lamps](https://github.com/ajouatom/openpilot/wiki/EN-Tesla-Model-Desire-Lamps) — `TeslaModelDesireSignals`
- [Tesla Model Path Lamps](https://github.com/ajouatom/openpilot/wiki/EN-Tesla-Model-Path-Lamps) — `TeslaModelPathSignals`
- [DisableMinSteerSpeed](https://github.com/ajouatom/openpilot/wiki/EN-DisableMinSteerSpeed) — `DisableMinSteerSpeed`

##### Auto Cruise

- [CruiseOnDist(0cm)](https://github.com/ajouatom/openpilot/wiki/EN-CruiseOnDist%280cm%29) — `CruiseOnDist`
- [Auto Cruise control(HKG only)](https://github.com/ajouatom/openpilot/wiki/EN-Auto-Cruise-control%28HKG-only%29) — `AutoCruiseControl`
- [Allow Soft Hold After Cancel(0)](https://github.com/ajouatom/openpilot/wiki/EN-Allow-Soft-Hold-After-Cancel%280%29) — `SoftHoldOnCancel`
- [Auto Cruise: Accelerator Tap Start Speed](https://github.com/ajouatom/openpilot/wiki/EN-Auto-Cruise-Accelerator-Tap-Start-Speed) — `AutoGasTokSpeed`
- [Auto Cruise: Gas Release Cancel Speed](https://github.com/ajouatom/openpilot/wiki/EN-Auto-Cruise-Gas-Release-Cancel-Speed) — `AutoGasCancelSpeed`
- [Auto update Cruise speed](https://github.com/ajouatom/openpilot/wiki/EN-Auto-update-Cruise-speed) — `AutoGasSyncSpeed`

#### Buttons & Presets

##### Button Modes

- [Cruise Button Mode(0)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Button-Mode%280%29) — `CruiseButtonMode`
- [Cancel Button Mode(0)](https://github.com/ajouatom/openpilot/wiki/EN-Cancel-Button-Mode%280%29) — `CancelButtonMode`
- [LFA Button Mode(0)](https://github.com/ajouatom/openpilot/wiki/EN-LFA-Button-Mode%280%29) — `LfaButtonMode`
- [PaddleShift Mode(0)](https://github.com/ajouatom/openpilot/wiki/EN-PaddleShift-Mode%280%29) — `PaddleMode`

##### Speed Units

- [Cruise Speed Unit Extra(10)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Speed-Unit-Extra%2810%29) — `CruiseSpeedUnit`
- [Cruise Button Long Delay (40)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Button-Long-Delay-%2840%29) — `CruiseButtonLongDelay`
- [Cruise Speed Unit Baic(10)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Speed-Unit-Baic%2810%29) — `CruiseSpeedUnitBasic`

##### Button Test

- [Cruise Button spam1(8)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Button-spam1%288%29) — `CruiseButtonTest1`
- [Cruise Button spam2(30)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Button-spam2%2830%29) — `CruiseButtonTest2`
- [Cruise Button spam3(1)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Button-spam3%281%29) — `CruiseButtonTest3`

##### Speed Presets

- [Cruise Speed1(30)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Speed1%2830%29) — `CruiseSpeed1`
- [Cruise Speed2(50)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Speed2%2850%29) — `CruiseSpeed2`
- [Cruise Speed3(80)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Speed3%2880%29) — `CruiseSpeed3`
- [Cruise Speed4(110)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Speed4%28110%29) — `CruiseSpeed4`
- [Cruise Speed5(130)](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Speed5%28130%29) — `CruiseSpeed5`

#### Steering

##### ONNX Lane & BSD

- [ONNX Lane and BSD Detection](https://github.com/ajouatom/openpilot/wiki/EN-ONNX-Lane-and-BSD-Detection) — `ShareData`
- [ONNX Vision BSD](https://github.com/ajouatom/openpilot/wiki/EN-ONNX-Vision-BSD) — `OnnxBsdEnabled`
- [Lane Confidence Threshold](https://github.com/ajouatom/openpilot/wiki/EN-Lane-Confidence-Threshold) — `OnnxLaneThreshold`
- [Lane Inference Interval](https://github.com/ajouatom/openpilot/wiki/EN-Lane-Inference-Interval) — `OnnxLaneIntervalMs`
- [BSD Confidence Threshold](https://github.com/ajouatom/openpilot/wiki/EN-BSD-Confidence-Threshold) — `OnnxBsdThreshold`
- [BSD Hold Time](https://github.com/ajouatom/openpilot/wiki/EN-BSD-Hold-Time) — `OnnxBsdSmoothingMs`
- [BSD Inference Interval](https://github.com/ajouatom/openpilot/wiki/EN-BSD-Inference-Interval) — `OnnxBsdIntervalMs`

##### Centering

- [Lane Deviation Left/Right Correction(0)](https://github.com/ajouatom/openpilot/wiki/EN-Lane-Deviation-Left-Right-Correction%280%29) — `PathOffset`
- [Camera YAW Correction(0)](https://github.com/ajouatom/openpilot/wiki/EN-Camera-YAW-Correction%280%29) — `CameraYawTrimDeg`

##### Steering Feel

- [SteerActuatorDelay(30)](https://github.com/ajouatom/openpilot/wiki/EN-SteerActuatorDelay%2830%29) — `SteerActuatorDelay`
- [Center of gravity ratio](https://github.com/ajouatom/openpilot/wiki/EN-Center-of-gravity-ratio) — `CenterToFrontRatio`
- [LatSmoothSec(13)](https://github.com/ajouatom/openpilot/wiki/EN-LatSmoothSec%2813%29) — `LatSmoothSec`
- [AutoSteering Suspend Angle(300)](https://github.com/ajouatom/openpilot/wiki/EN-AutoSteering-Suspend-Angle%28300%29) — `LatSuspendAngleDeg`
- [CustomSteerRatiox0.1(0)](https://github.com/ajouatom/openpilot/wiki/EN-CustomSteerRatiox0.1%280%29) — `CustomSR`
- [CustomSteerRatioRatex0.01(100)](https://github.com/ajouatom/openpilot/wiki/EN-CustomSteerRatioRatex0.01%28100%29) — `SteerRatioRate`

##### Lane Change (Auto Turn)

- [ATC: AutoTurnControl](https://github.com/ajouatom/openpilot/wiki/EN-ATC-AutoTurnControl) — `AutoTurnControl`
- [Manual lane-change indicator (trial)](https://github.com/ajouatom/openpilot/wiki/EN-Manual-lane-change-indicator-%28trial%29) — `ManualLaneChangeIndicator`
- [Manual turn indicator (trial)](https://github.com/ajouatom/openpilot/wiki/EN-Manual-turn-indicator-%28trial%29) — `ManualTurnIndicator`
- [Model desire indicator (trial)](https://github.com/ajouatom/openpilot/wiki/EN-Model-desire-indicator-%28trial%29) — `ModelDesireIndicator`
- [Model path indicator (trial)](https://github.com/ajouatom/openpilot/wiki/EN-Model-path-indicator-%28trial%29) — `ModelPathIndicator`
- [Right lane-change distance before a turn (m)](https://github.com/ajouatom/openpilot/wiki/EN-Right-lane-change-distance-before-a-turn-%28m%29) — `AutoTurnControlRightLaneChange`
- [ATC: Turn Speed(20)](https://github.com/ajouatom/openpilot/wiki/EN-ATC-Turn-Speed%2820%29) — `AutoTurnControlSpeedTurn`
- [ATC: Speed Ctrl left Time(3)](https://github.com/ajouatom/openpilot/wiki/EN-ATC-Speed-Ctrl-left-Time%283%29) — `AutoTurnControlTurnEnd`
- [ATC Helper Map display(0)](https://github.com/ajouatom/openpilot/wiki/EN-ATC-Helper-Map-display%280%29) — `AutoTurnMapChange`
- [LaneChange use steering torque](https://github.com/ajouatom/openpilot/wiki/EN-LaneChange-use-steering-torque) — `LaneChangeNeedTorque`
- [Automatic turn signals](https://github.com/ajouatom/openpilot/wiki/EN-Automatic-turn-signals) — `AutoBlinkerControl`
- [Turn-signal lever selects turn / lane change (km/h, 0=off)](https://github.com/ajouatom/openpilot/wiki/EN-Turn-signal-lever-selects-turn-lane-change-%28km-h%2C-0%3Doff%29) — `BlinkerLatchedTurn`
- [One-touch lane change request waits 5 flashes](https://github.com/ajouatom/openpilot/wiki/EN-One-touch-lane-change-request-waits-5-flashes) — `LaneChangeLeverWait`
- [LaneChange delayx0.1s(0)](https://github.com/ajouatom/openpilot/wiki/EN-LaneChange-delayx0.1s%280%29) — `LaneChangeDelay`
- [LaneChange BSD](https://github.com/ajouatom/openpilot/wiki/EN-LaneChange-BSD) — `LaneChangeBsd`
- [LaneChange LineCheck](https://github.com/ajouatom/openpilot/wiki/EN-LaneChange-LineCheck) — `LaneLineCheck`

##### Lane Mode

- [\*LATMPC.PathCost(200)](https://github.com/ajouatom/openpilot/wiki/EN-LATMPC.PathCost%28200%29) — `LatMpcPathCost`
- [\*LATMPC.MotionCost(7)](https://github.com/ajouatom/openpilot/wiki/EN-LATMPC.MotionCost%287%29) — `LatMpcMotionCost`
- [\*LATMPC.AccelCost(120)](https://github.com/ajouatom/openpilot/wiki/EN-LATMPC.AccelCost%28120%29) — `LatMpcAccelCost`
- [\*LATMPC.JerkCost(4)](https://github.com/ajouatom/openpilot/wiki/EN-LATMPC.JerkCost%284%29) — `LatMpcJerkCost`
- [\*LATMPC.SteerRateCost(7)](https://github.com/ajouatom/openpilot/wiki/EN-LATMPC.SteerRateCost%287%29) — `LatMpcSteeringRateCost`
- [\*LATMPC.InputOffset(4)](https://github.com/ajouatom/openpilot/wiki/EN-LATMPC.InputOffset%284%29) — `LatMpcInputOffset`
- [Laneline: Speed(0)](https://github.com/ajouatom/openpilot/wiki/EN-Laneline-Speed%280%29) — `UseLaneLineSpeed`
- [Laneline: Curve Speed(0)](https://github.com/ajouatom/openpilot/wiki/EN-Laneline-Curve-Speed%280%29) — `UseLaneLineCurveSpeed`
- [LaneLine: AdjustLaneOffset (0)cm](https://github.com/ajouatom/openpilot/wiki/EN-LaneLine-AdjustLaneOffset-%280%29cm) — `AdjustLaneOffset`

##### Advanced Torque

###### Torque Coefficients

- [NNFF Torque Control](https://github.com/ajouatom/openpilot/wiki/EN-NNFF-Torque-Control) — `NNFF`
- [\_LateralTorqueCustom(0)](https://github.com/ajouatom/openpilot/wiki/EN-_LateralTorqueCustom%280%29) — `LateralTorqueCustom`
- [\_LateralTorqueAccelFactor\*0.001(2500)](https://github.com/ajouatom/openpilot/wiki/EN-_LateralTorqueAccelFactor-0.001%282500%29) — `LateralTorqueAccelFactor`
- [\_LateralTorqueFriction\*0.001(100)](https://github.com/ajouatom/openpilot/wiki/EN-_LateralTorqueFriction-0.001%28100%29) — `LateralTorqueFriction`
- [\_LateralTorqueKp\*0.01(100)](https://github.com/ajouatom/openpilot/wiki/EN-_LateralTorqueKp-0.01%28100%29) — `LateralTorqueKpV`
- [\_LateralTorqueKi\*0.01(10)](https://github.com/ajouatom/openpilot/wiki/EN-_LateralTorqueKi-0.01%2810%29) — `LateralTorqueKiV`
- [\_LateralTorqueKf\*0.001(100)](https://github.com/ajouatom/openpilot/wiki/EN-_LateralTorqueKf-0.001%28100%29) — `LateralTorqueKf`
- [\_LateralTorqueKd\*0.01(0)](https://github.com/ajouatom/openpilot/wiki/EN-_LateralTorqueKd-0.01%280%29) — `LateralTorqueKd`

###### Steering Limits

- [\_CustomSteerMax(0)](https://github.com/ajouatom/openpilot/wiki/EN-_CustomSteerMax%280%29) — `CustomSteerMax`
- [\_CustomSteerDeltaUp(0)](https://github.com/ajouatom/openpilot/wiki/EN-_CustomSteerDeltaUp%280%29) — `CustomSteerDeltaUp`
- [\_CustomSteerDeltaDown(0)](https://github.com/ajouatom/openpilot/wiki/EN-_CustomSteerDeltaDown%280%29) — `CustomSteerDeltaDown`
- [\_CustomSteerDeltaUpLC(0)](https://github.com/ajouatom/openpilot/wiki/EN-_CustomSteerDeltaUpLC%280%29) — `CustomSteerDeltaUpLC`
- [\_CustomSteerDeltaDownLC(0)](https://github.com/ajouatom/openpilot/wiki/EN-_CustomSteerDeltaDownLC%280%29) — `CustomSteerDeltaDownLC`

#### Speed & Decel

##### Speed Camera

- [Rear Camera Post-pass Hold Distance (m)](https://github.com/ajouatom/openpilot/wiki/EN-Rear-Camera-Post-pass-Hold-Distance-%28m%29) — `AutoNaviRearCameraHoldDistance`
- [NaviSpeedEndingPoint(6s)](https://github.com/ajouatom/openpilot/wiki/EN-NaviSpeedEndingPoint%286s%29) — `AutoNaviSpeedCtrlEnd`
- [NaviSpeedControlMode(2)](https://github.com/ajouatom/openpilot/wiki/EN-NaviSpeedControlMode%282%29) — `AutoNaviSpeedCtrlMode`
- [Vehicle Navigation CAN Deceleration Mode](https://github.com/ajouatom/openpilot/wiki/EN-Vehicle-Navigation-CAN-Deceleration-Mode) — `VehicleNaviCanControl`
- [Stock Navigation 30 km/h Zone Limit](https://github.com/ajouatom/openpilot/wiki/EN-Stock-Navigation-30-km-h-Zone-Limit) — `VehicleNaviSchoolZoneControl`
- [Stock Navigation Deceleration Cancel Request](https://github.com/ajouatom/openpilot/wiki/EN-Stock-Navigation-Deceleration-Cancel-Request) — `VehicleNaviDecelCancel`
- [Deceleration Cancel: Box Camera](https://github.com/ajouatom/openpilot/wiki/EN-Deceleration-Cancel-Box-Camera) — `VehicleNaviDecelCancelBox`
- [Deceleration Cancel: Mobile Zone](https://github.com/ajouatom/openpilot/wiki/EN-Deceleration-Cancel-Mobile-Zone) — `VehicleNaviDecelCancelMobileZone`
- [Deceleration Cancel: Speed Bump](https://github.com/ajouatom/openpilot/wiki/EN-Deceleration-Cancel-Speed-Bump) — `VehicleNaviDecelCancelBump`
- [Deceleration Cancel: Undetected Camera Kind \[Experimental\]](https://github.com/ajouatom/openpilot/wiki/EN-Deceleration-Cancel-Undetected-Camera-Kind-Experimental) — `VehicleNaviDecelCancelUnknown`
- [Deceleration Cancel: Early Warning Correction \[Experimental\]](https://github.com/ajouatom/openpilot/wiki/EN-Deceleration-Cancel-Early-Warning-Correction-Experimental) — `VehicleNaviDecelCancelEarlyWarning`
- [Stock Navigation Section Average-speed Control](https://github.com/ajouatom/openpilot/wiki/EN-Stock-Navigation-Section-Average-speed-Control) — `VehicleNaviSectionAvgControl`
- [Vehicle-received Speed Camera Deceleration(Always apply)](https://github.com/ajouatom/openpilot/wiki/EN-Vehicle-received-Speed-Camera-Deceleration%28Always-apply%29) — `VehicleSpeedCameraControlMode`
- [Vehicle Speed Camera Virtual Distance Time (6.0 s)](https://github.com/ajouatom/openpilot/wiki/EN-Vehicle-Speed-Camera-Virtual-Distance-Time-%286.0-s%29) — `VehicleSpeedCameraDistanceTime`
- [NaviSpeedDecelRate 0.01m/s^2x(120)](https://github.com/ajouatom/openpilot/wiki/EN-NaviSpeedDecelRate-0.01m-s%5E2x%28120%29) — `AutoNaviSpeedDecelRate`
- [NaviCountDownMode](https://github.com/ajouatom/openpilot/wiki/EN-NaviCountDownMode) — `AutoNaviCountDownMode`
- [NaviSpeedLimitRatio(105)%](https://github.com/ajouatom/openpilot/wiki/EN-NaviSpeedLimitRatio%28105%29) — `AutoNaviSpeedSafetyFactor`

##### Speed Limit

- [AutoSpeedUpx:(100)%](https://github.com/ajouatom/openpilot/wiki/EN-AutoSpeedUpx-%28100%29) — `AutoSpeedUptoRoadSpeedLimit`
- [AutoRoadLimitSpeedAdjust (50)%](https://github.com/ajouatom/openpilot/wiki/EN-AutoRoadLimitSpeedAdjust-%2850%29) — `AutoRoadSpeedAdjust`
- [RoadSpeedLimitOffset(-1)](https://github.com/ajouatom/openpilot/wiki/EN-RoadSpeedLimitOffset%28-1%29) — `AutoRoadSpeedLimitOffset`

##### Speed Bump

- [SpeedBumpEndingPoint(1s)](https://github.com/ajouatom/openpilot/wiki/EN-SpeedBumpEndingPoint%281s%29) — `AutoNaviSpeedBumpTime`
- [SpeedBumpSpeed(35km/h)](https://github.com/ajouatom/openpilot/wiki/EN-SpeedBumpSpeed%2835km-h%29) — `AutoNaviSpeedBumpSpeed`
- [Speed Bump Early Release Distance (200 cm)](https://github.com/ajouatom/openpilot/wiki/EN-Speed-Bump-Early-Release-Distance-%28200-cm%29) — `AutoNaviSpeedBumpEndDistance`

##### Curve & Turn

- [CurveSpeedFactor(100%)](https://github.com/ajouatom/openpilot/wiki/EN-CurveSpeedFactor%28100-%29) — `AutoCurveSpeedFactor`
- [Model Speed Apply Ratio](https://github.com/ajouatom/openpilot/wiki/EN-Model-Speed-Apply-Ratio) — `ApplyModelSpeed`
- [AutoCurveSpeed LowerLimit(30)](https://github.com/ajouatom/openpilot/wiki/EN-AutoCurveSpeed-LowerLimit%2830%29) — `AutoCurveSpeedLowerLimit`
- [TurnSpeedControlMode](https://github.com/ajouatom/openpilot/wiki/EN-TurnSpeedControlMode) — `TurnSpeedControlMode`
- [MapTurnSpeedFactor](https://github.com/ajouatom/openpilot/wiki/EN-MapTurnSpeedFactor) — `MapTurnSpeedFactor`

##### Traffic Light

- [TrafficStopDistanceAdjust](https://github.com/ajouatom/openpilot/wiki/EN-TrafficStopDistanceAdjust) — `TrafficStopDistanceAdjust`
- [Lead Brake Lamp Observation (Trial)](https://github.com/ajouatom/openpilot/wiki/EN-Lead-Brake-Lamp-Observation-%28Trial%29) — `LeadBrakeLights`
- [Signal Assistance Mode (Trial)](https://github.com/ajouatom/openpilot/wiki/EN-Signal-Assistance-Mode-%28Trial%29) — `SignalAssistMode`
- [TrafficLightDetectMode](https://github.com/ajouatom/openpilot/wiki/EN-TrafficLightDetectMode) — `TrafficLightDetectMode`

#### Cruise & Gap

##### Accel Profile

###### Drive Mode

- [DrivingMode:Init(3)](https://github.com/ajouatom/openpilot/wiki/EN-DrivingMode-Init%283%29) — `MyDrivingMode`
- [DrivingMode: Auto](https://github.com/ajouatom/openpilot/wiki/EN-DrivingMode-Auto) — `MyDrivingModeAuto`

###### Speed Accel Table

- [AccelSet0:0km/h(160)](https://github.com/ajouatom/openpilot/wiki/EN-AccelSet0-0km-h%28160%29) — `CruiseMaxVals0`
- [AccelSet1:10km/h(160)](https://github.com/ajouatom/openpilot/wiki/EN-AccelSet1-10km-h%28160%29) — `CruiseMaxVals1`
- [AccelSet2:40km/h(120)](https://github.com/ajouatom/openpilot/wiki/EN-AccelSet2-40km-h%28120%29) — `CruiseMaxVals2`
- [AccelSet3:60km/h(100)](https://github.com/ajouatom/openpilot/wiki/EN-AccelSet3-60km-h%28100%29) — `CruiseMaxVals3`
- [AccelSet4:80km/h(80)](https://github.com/ajouatom/openpilot/wiki/EN-AccelSet4-80km-h%2880%29) — `CruiseMaxVals4`
- [AccelSet5:110km/h(70)](https://github.com/ajouatom/openpilot/wiki/EN-AccelSet5-110km-h%2870%29) — `CruiseMaxVals5`
- [AccelSet6:140km/h(60)](https://github.com/ajouatom/openpilot/wiki/EN-AccelSet6-140km-h%2860%29) — `CruiseMaxVals6`

##### Stop & Resume

- [StopDistance(600)cm](https://github.com/ajouatom/openpilot/wiki/EN-StopDistance%28600%29cm) — `StopDistanceCarrot`
- [AChangeCostStarting](https://github.com/ajouatom/openpilot/wiki/EN-AChangeCostStarting) — `AChangeCostStarting`
- [VEgoStopping(50)x0.01](https://github.com/ajouatom/openpilot/wiki/EN-VEgoStopping%2850%29x0.01) — `VEgoStopping`
- [StoppingStartAccelx0.01(-50)](https://github.com/ajouatom/openpilot/wiki/EN-StoppingStartAccelx0.01%28-50%29) — `StoppingAccel`

##### Accel/Brake Tuning

- [Long KpV(100)x0.01](https://github.com/ajouatom/openpilot/wiki/EN-Long-KpV%28100%29x0.01) — `LongTuningKpV`
- [Long Kf(100)x0.01](https://github.com/ajouatom/openpilot/wiki/EN-Long-Kf%28100%29x0.01) — `LongTuningKf`
- [Long KiV(0)x0.001](https://github.com/ajouatom/openpilot/wiki/EN-Long-KiV%280%29x0.001) — `LongTuningKiV`
- [LongActuatorDelay(20)x0.01](https://github.com/ajouatom/openpilot/wiki/EN-LongActuatorDelay%2820%29x0.01) — `LongActuatorDelay`

##### Follow Gap

- [Gap cycle levels](https://github.com/ajouatom/openpilot/wiki/EN-Gap-cycle-levels) — `CruiseGapLevels`
- [TF(1): TimeFollow1x0.01s(110)](https://github.com/ajouatom/openpilot/wiki/EN-TF%281%29-TimeFollow1x0.01s%28110%29) — `TFollowGap1`
- [TF(2): TimeFollow2x0.01s(120)](https://github.com/ajouatom/openpilot/wiki/EN-TF%282%29-TimeFollow2x0.01s%28120%29) — `TFollowGap2`
- [TF(3): TimeFollow3x0.01s(140)](https://github.com/ajouatom/openpilot/wiki/EN-TF%283%29-TimeFollow3x0.01s%28140%29) — `TFollowGap3`
- [TF(4): TimeFollow4x0.01s(160)](https://github.com/ajouatom/openpilot/wiki/EN-TF%284%29-TimeFollow4x0.01s%28160%29) — `TFollowGap4`
- [Following responsiveness · common](https://github.com/ajouatom/openpilot/wiki/EN-Following-responsiveness-%C2%B7-common) — `LeadAccelResponse`
- [TF1 following responsiveness](https://github.com/ajouatom/openpilot/wiki/EN-TF1-following-responsiveness) — `LeadAccelResponseTF1`
- [TF2 following responsiveness](https://github.com/ajouatom/openpilot/wiki/EN-TF2-following-responsiveness) — `LeadAccelResponseTF2`
- [TF3 following responsiveness](https://github.com/ajouatom/openpilot/wiki/EN-TF3-following-responsiveness) — `LeadAccelResponseTF3`
- [TF4 following responsiveness](https://github.com/ajouatom/openpilot/wiki/EN-TF4-following-responsiveness) — `LeadAccelResponseTF4`
- [Speed TF multiplier](https://github.com/ajouatom/openpilot/wiki/EN-Speed-TF-multiplier) — `SpeedTFFactor`
- [Lane Change Response (100%)](https://github.com/ajouatom/openpilot/wiki/EN-Lane-Change-Response-%28100-%29) — `DynamicTFollowLC`
- [Deceleration Gap Margin (0%)](https://github.com/ajouatom/openpilot/wiki/EN-Deceleration-Gap-Margin-%280-%29) — `TFollowDecelBoost`

##### Carrot Cruise

- [CruiseEcoControl(2km/h)](https://github.com/ajouatom/openpilot/wiki/EN-CruiseEcoControl%282km-h%29) — `CruiseEcoControl`
- [Cruise Coasting Margin](https://github.com/ajouatom/openpilot/wiki/EN-Cruise-Coasting-Margin) — `CruiseCoastingPercent`
- [CarrotCruiseDecel(-1)](https://github.com/ajouatom/openpilot/wiki/EN-CarrotCruiseDecel%28-1%29) — `CarrotCruiseDecel`
- [CarrotCruiseDecelATCx0.01(-1)](https://github.com/ajouatom/openpilot/wiki/EN-CarrotCruiseDecelATCx0.01%28-1%29) — `CarrotCruiseAtcDecel`

### Vehicle & Hardware

#### Hyundai·Kia

- [HapticFeedbackSpeedCamera(0)](https://github.com/ajouatom/openpilot/wiki/EN-HapticFeedbackSpeedCamera%280%29) — `HapticFeedbackWhenSpeedCamera`
- [HYUNDAI: CAMERA SCC(0)](https://github.com/ajouatom/openpilot/wiki/EN-HYUNDAI-CAMERA-SCC%280%29) — `HyundaiCameraSCC`
- [HYUNDAI: LDWS ONLY CAR(0)](https://github.com/ajouatom/openpilot/wiki/EN-HYUNDAI-LDWS-ONLY-CAR%280%29) — `IsLdwsCar`

#### CANFD·HDA

- [Parked SPAS indicator test](https://github.com/ajouatom/openpilot/wiki/EN-Parked-SPAS-indicator-test) — `CanfdBlinkerTest`
- [CAN-FD SPAS indicators (trial)](https://github.com/ajouatom/openpilot/wiki/EN-CAN-FD-SPAS-indicators-%28trial%29) — `CanfdBlinkerControl`
- [Use HDP(CCNC)](https://github.com/ajouatom/openpilot/wiki/EN-Use-HDP%28CCNC%29) — `HDPuse`
- [CANFD HDA2(0)](https://github.com/ajouatom/openpilot/wiki/EN-CANFD-HDA2%280%29) — `CanfdHDA2`
- [Cluster CAN Direct Send](https://github.com/ajouatom/openpilot/wiki/EN-Cluster-CAN-Direct-Send) — `HyundaiCanfdClusterDirectTx`
- [CANFD Debug(0)](https://github.com/ajouatom/openpilot/wiki/EN-CANFD-Debug%280%29) — `CanfdDebug`

#### Radar

- [Enable radar tracks(0)](https://github.com/ajouatom/openpilot/wiki/EN-Enable-radar-tracks%280%29) — `EnableRadarTracks`
- [Radar Left/Right Inversion](https://github.com/ajouatom/openpilot/wiki/EN-Radar-Left-Right-Inversion) — `RadarTrackFlip`
- [Enable Corner radar(0)](https://github.com/ajouatom/openpilot/wiki/EN-Enable-Corner-radar%280%29) — `EnableCornerRadar`

#### Driver Monitor

- [Enable Driver Monitoring (Exception)](https://github.com/ajouatom/openpilot/wiki/EN-Enable-Driver-Monitoring-%28Exception%29) — `DriverMonitoringEnabled`
- [Driver Monitoring Mode](https://github.com/ajouatom/openpilot/wiki/EN-Driver-Monitoring-Mode) — `DriverMonitoringMode`
- [Enable Carrot Vision](https://github.com/ajouatom/openpilot/wiki/EN-Enable-Carrot-Vision) — `CarrotVisionEnabled`
- [MuteDoor](https://github.com/ajouatom/openpilot/wiki/EN-MuteDoor) — `MuteDoor`
- [MuteSeatbelt](https://github.com/ajouatom/openpilot/wiki/EN-MuteSeatbelt) — `MuteSeatbelt`

#### Vehicle Aux

- [Speed from PCM(StockSCC)](https://github.com/ajouatom/openpilot/wiki/EN-Speed-from-PCM%28StockSCC%29) — `SpeedFromPCM`
- [MaxAngleFrames(89)](https://github.com/ajouatom/openpilot/wiki/EN-MaxAngleFrames%2889%29) — `MaxAngleFrames`

#### Device Hardware

- [Comma Pedal longitudinal control](https://github.com/ajouatom/openpilot/wiki/EN-Comma-Pedal-longitudinal-control) — `CommaPedalEnabled`
- [C3X Lite Hardware](https://github.com/ajouatom/openpilot/wiki/EN-C3X-Lite-Hardware) — `HardwareC3xLite`

### Display

#### On-screen Info

- [Show Debug Info](https://github.com/ajouatom/openpilot/wiki/EN-Show-Debug-Info) — `ShowDebugUI`
- [Show TPMS Info](https://github.com/ajouatom/openpilot/wiki/EN-Show-TPMS-Info) — `ShowTpms`
- [Show Time Info](https://github.com/ajouatom/openpilot/wiki/EN-Show-Time-Info) — `ShowDateTime`
- [Show Path End](https://github.com/ajouatom/openpilot/wiki/EN-Show-Path-End) — `ShowPathEnd`
- [Show Device Info](https://github.com/ajouatom/openpilot/wiki/EN-Show-Device-Info) — `ShowDeviceState`
- [Show Lane Info](https://github.com/ajouatom/openpilot/wiki/EN-Show-Lane-Info) — `ShowLaneInfo`
- [Show Radar Info](https://github.com/ajouatom/openpilot/wiki/EN-Show-Radar-Info) — `ShowRadarInfo`
- [Show Route Info](https://github.com/ajouatom/openpilot/wiki/EN-Show-Route-Info) — `ShowRouteInfo`
- [Show Debug Plot(0)](https://github.com/ajouatom/openpilot/wiki/EN-Show-Debug-Plot%280%29) — `ShowPlotMode`

#### Path Display

- [Tire Trajectory](https://github.com/ajouatom/openpilot/wiki/EN-Tire-Trajectory) — `CarrotTireTrajectory`
- [Show Path Mode:LaneLess(9)](https://github.com/ajouatom/openpilot/wiki/EN-Show-Path-Mode-LaneLess%289%29) — `ShowPathMode`
- [Show Path Color:LaneLess(12)](https://github.com/ajouatom/openpilot/wiki/EN-Show-Path-Color-LaneLess%2812%29) — `ShowPathColor`
- [Show Path Color:CruiseOFF(1)](https://github.com/ajouatom/openpilot/wiki/EN-Show-Path-Color-CruiseOFF%281%29) — `ShowPathColorCruiseOff`
- [Show Path Mode:LaneMode(11)](https://github.com/ajouatom/openpilot/wiki/EN-Show-Path-Mode-LaneMode%2811%29) — `ShowPathModeLane`
- [Show Path Color:LaneMode(3)](https://github.com/ajouatom/openpilot/wiki/EN-Show-Path-Color-LaneMode%283%29) — `ShowPathColorLane`

#### Brightness & View

- [Onroad Screen Brightness(100%)](https://github.com/ajouatom/openpilot/wiki/EN-Onroad-Screen-Brightness%28100-%29) — `ShowCustomBrightness`
- [Driving Screen Layout(C4)](https://github.com/ajouatom/openpilot/wiki/EN-Driving-Screen-Layout%28C4%29) — `ShowModelView`
- [On-device Camera with External HUD(0)](https://github.com/ajouatom/openpilot/wiki/EN-On-device-Camera-with-External-HUD%280%29) — `ShowCameraWithCluster`

#### External HUD

##### Basic

- [External HUD Display(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Display%280%29) — `ClusterHud`
- [External HUD Mirror Mode(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Mirror-Mode%280%29) — `ClusterHudMirror`
- [External HUD Brightness(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Brightness%280%29) — `ClusterHudBrightness`
- [External HUD Screen Rotation(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Screen-Rotation%280%29) — `ClusterHudOrientation`
- [External HUD Theme(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Theme%280%29) — `ClusterHudTheme`
- [Cluster Navi Map Theme(1)](https://github.com/ajouatom/openpilot/wiki/EN-Cluster-Navi-Map-Theme%281%29) — `ClusterNaviMapTheme`
- [Cluster Navi Map Type(0)](https://github.com/ajouatom/openpilot/wiki/EN-Cluster-Navi-Map-Type%280%29) — `ClusterNaviMapType`
- [Cluster Navi Map FPS(1)](https://github.com/ajouatom/openpilot/wiki/EN-Cluster-Navi-Map-FPS%281%29) — `ClusterNaviMapFps`

##### Screen & Camera

- [External HUD Encoder(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Encoder%280%29) — `ClusterHudEncoder`
- [External HUD Screen Mode(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Screen-Mode%280%29) — `ClusterHudScreenMode`
- [External HUD Panel Layout(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Panel-Layout%280%29) — `ClusterHudPanelLayout`
- [External HUD Camera View Mode(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Camera-View-Mode%280%29) — `ClusterHudCameraViewMode`

##### Radar Display

- [External HUD Radar Info(4)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Radar-Info%284%29) — `ClusterHudRadarInfo`
- [External HUD Radar Display(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Radar-Display%280%29) — `ClusterHudRadarDisplay`
- [External HUD Radar Source Colors(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Radar-Source-Colors%280%29) — `ClusterHudRadarSourceColor`

##### Performance & Debug

- [External HUD Debug(0)](https://github.com/ajouatom/openpilot/wiki/EN-External-HUD-Debug%280%29) — `ClusterHudDebug`

### System

#### Record & Power

##### Record & Power

- [Record RoadCam](https://github.com/ajouatom/openpilot/wiki/EN-Record-RoadCam) — `RecordRoadCam`
- [PowerOffTime(min)](https://github.com/ajouatom/openpilot/wiki/EN-PowerOffTime%28min%29) — `MaxTimeOffroadMin`

#### Camera

- [Use Wide Road Camera](https://github.com/ajouatom/openpilot/wiki/EN-Use-Wide-Road-Camera) — `UseWideCamera`

#### Network & Map

- [MapboxStyle](https://github.com/ajouatom/openpilot/wiki/EN-MapboxStyle) — `MapboxStyle`
- [Enable HotSpot(0)](https://github.com/ajouatom/openpilot/wiki/EN-Enable-HotSpot%280%29) — `HotspotOnBoot`

#### Sound

- [Sound Language](https://github.com/ajouatom/openpilot/wiki/EN-Sound-Language) — `SoundLanguageSetting`
- [Navigation Voice Volume](https://github.com/ajouatom/openpilot/wiki/EN-Navigation-Voice-Volume) — `SoundLanguageVolume`
- [Sound Volume adjust(100%)](https://github.com/ajouatom/openpilot/wiki/EN-Sound-Volume-adjust%28100-%29) — `SoundVolumeAdjust`
- [Sound Volume adjust,Engage(10%)](https://github.com/ajouatom/openpilot/wiki/EN-Sound-Volume-adjust%2CEngage%2810-%29) — `SoundVolumeAdjustEngage`

#### Software

- [Enable Software menu](https://github.com/ajouatom/openpilot/wiki/EN-Enable-Software-menu) — `SoftwareMenu`

## 设置目录 · `zh`

根据当前设置目录自动生成的各项设置页面。

### 驾驶控制

#### 启动·自动

##### 起步动作

- [上路自动激活](https://github.com/ajouatom/openpilot/wiki/ZH-%E4%B8%8A%E8%B7%AF%E8%87%AA%E5%8A%A8%E6%BF%80%E6%B4%BB) — `AutoEngage`
- [全时横向控制](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%85%A8%E6%97%B6%E6%A8%AA%E5%90%91%E6%8E%A7%E5%88%B6) — `AlwaysLateral`
- [特斯拉自动转向灯](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%89%B9%E6%96%AF%E6%8B%89%E8%87%AA%E5%8A%A8%E8%BD%AC%E5%90%91%E7%81%AF) — `TeslaAutoTurnSignals`
- [特斯拉 CAN 红灯停车](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%89%B9%E6%96%AF%E6%8B%89-CAN-%E7%BA%A2%E7%81%AF%E5%81%9C%E8%BD%A6) — `TeslaCanTrafficStop`
- [特斯拉手动变道灯](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%89%B9%E6%96%AF%E6%8B%89%E6%89%8B%E5%8A%A8%E5%8F%98%E9%81%93%E7%81%AF) — `TeslaManualLaneSignals`
- [特斯拉模型意图灯](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%89%B9%E6%96%AF%E6%8B%89%E6%A8%A1%E5%9E%8B%E6%84%8F%E5%9B%BE%E7%81%AF) — `TeslaModelDesireSignals`
- [特斯拉模型路径灯](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%89%B9%E6%96%AF%E6%8B%89%E6%A8%A1%E5%9E%8B%E8%B7%AF%E5%BE%84%E7%81%AF) — `TeslaModelPathSignals`
- [解除最小转向速度限制](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%A7%A3%E9%99%A4%E6%9C%80%E5%B0%8F%E8%BD%AC%E5%90%91%E9%80%9F%E5%BA%A6%E9%99%90%E5%88%B6) — `DisableMinSteerSpeed`

##### 自动巡航

- [巡航开启距离(0cm)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E5%BC%80%E5%90%AF%E8%B7%9D%E7%A6%BB%280cm%29) — `CruiseOnDist`
- [自动巡航控制 (仅限现代/起亚)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%8A%A8%E5%B7%A1%E8%88%AA%E6%8E%A7%E5%88%B6-%28%E4%BB%85%E9%99%90%E7%8E%B0%E4%BB%A3-%E8%B5%B7%E4%BA%9A%29) — `AutoCruiseControl`
- [取消后允许软驻车(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%96%E6%B6%88%E5%90%8E%E5%85%81%E8%AE%B8%E8%BD%AF%E9%A9%BB%E8%BD%A6%280%29) — `SoftHoldOnCancel`
- [自动巡航: 踩油门起步速度](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%8A%A8%E5%B7%A1%E8%88%AA-%E8%B8%A9%E6%B2%B9%E9%97%A8%E8%B5%B7%E6%AD%A5%E9%80%9F%E5%BA%A6) — `AutoGasTokSpeed`
- [自动巡航: 松开油门取消速度](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%8A%A8%E5%B7%A1%E8%88%AA-%E6%9D%BE%E5%BC%80%E6%B2%B9%E9%97%A8%E5%8F%96%E6%B6%88%E9%80%9F%E5%BA%A6) — `AutoGasCancelSpeed`
- [自动更新巡航速度](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%8A%A8%E6%9B%B4%E6%96%B0%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A6) — `AutoGasSyncSpeed`

#### 按钮·预设

##### 按钮模式

- [巡航按钮模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%92%AE%E6%A8%A1%E5%BC%8F%280%29) — `CruiseButtonMode`
- [取消按钮模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%96%E6%B6%88%E6%8C%89%E9%92%AE%E6%A8%A1%E5%BC%8F%280%29) — `CancelButtonMode`
- [LFA 按钮模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-LFA-%E6%8C%89%E9%92%AE%E6%A8%A1%E5%BC%8F%280%29) — `LfaButtonMode`
- [换挡拨片模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%8D%A2%E6%8C%A1%E6%8B%A8%E7%89%87%E6%A8%A1%E5%BC%8F%280%29) — `PaddleMode`

##### 速度单位

- [巡航速度单位扩展(10)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A6%E5%8D%95%E4%BD%8D%E6%89%A9%E5%B1%95%2810%29) — `CruiseSpeedUnit`
- [巡航按键长按延迟(40)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%94%AE%E9%95%BF%E6%8C%89%E5%BB%B6%E8%BF%9F%2840%29) — `CruiseButtonLongDelay`
- [巡航速度单位基础(10)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A6%E5%8D%95%E4%BD%8D%E5%9F%BA%E7%A1%80%2810%29) — `CruiseSpeedUnitBasic`

##### 按钮测试

- [巡航按钮连发1(8)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%92%AE%E8%BF%9E%E5%8F%911%288%29) — `CruiseButtonTest1`
- [巡航按钮连发2(30)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%92%AE%E8%BF%9E%E5%8F%912%2830%29) — `CruiseButtonTest2`
- [巡航按钮连发3(1)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%92%AE%E8%BF%9E%E5%8F%913%281%29) — `CruiseButtonTest3`

##### 速度预设

- [巡航速度1(30)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A61%2830%29) — `CruiseSpeed1`
- [巡航速度2(50)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A62%2850%29) — `CruiseSpeed2`
- [巡航速度3(80)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A63%2880%29) — `CruiseSpeed3`
- [巡航速度4(110)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A64%28110%29) — `CruiseSpeed4`
- [巡航速度5(130)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A65%28130%29) — `CruiseSpeed5`

#### 转向

##### ONNX 车道与盲点

- [ONNX 车道与盲点识别](https://github.com/ajouatom/openpilot/wiki/ZH-ONNX-%E8%BD%A6%E9%81%93%E4%B8%8E%E7%9B%B2%E7%82%B9%E8%AF%86%E5%88%AB) — `ShareData`
- [ONNX 摄像头盲点识别](https://github.com/ajouatom/openpilot/wiki/ZH-ONNX-%E6%91%84%E5%83%8F%E5%A4%B4%E7%9B%B2%E7%82%B9%E8%AF%86%E5%88%AB) — `OnnxBsdEnabled`
- [车道置信度阈值](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E9%81%93%E7%BD%AE%E4%BF%A1%E5%BA%A6%E9%98%88%E5%80%BC) — `OnnxLaneThreshold`
- [车道计算间隔](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E9%81%93%E8%AE%A1%E7%AE%97%E9%97%B4%E9%9A%94) — `OnnxLaneIntervalMs`
- [盲区置信度阈值](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%9B%B2%E5%8C%BA%E7%BD%AE%E4%BF%A1%E5%BA%A6%E9%98%88%E5%80%BC) — `OnnxBsdThreshold`
- [盲区保持时间](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%9B%B2%E5%8C%BA%E4%BF%9D%E6%8C%81%E6%97%B6%E9%97%B4) — `OnnxBsdSmoothingMs`
- [盲区计算间隔](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%9B%B2%E5%8C%BA%E8%AE%A1%E7%AE%97%E9%97%B4%E9%9A%94) — `OnnxBsdIntervalMs`

##### 居中校正

- [车道偏移左右修正(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E9%81%93%E5%81%8F%E7%A7%BB%E5%B7%A6%E5%8F%B3%E4%BF%AE%E6%AD%A3%280%29) — `PathOffset`
- [摄像头YAW校正(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%91%84%E5%83%8F%E5%A4%B4YAW%E6%A0%A1%E6%AD%A3%280%29) — `CameraYawTrimDeg`

##### 转向手感

- [转向执行器延迟(30)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E6%89%A7%E8%A1%8C%E5%99%A8%E5%BB%B6%E8%BF%9F%2830%29) — `SteerActuatorDelay`
- [重心位置比例](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%87%8D%E5%BF%83%E4%BD%8D%E7%BD%AE%E6%AF%94%E4%BE%8B) — `CenterToFrontRatio`
- [转向平滑时间(30)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E5%B9%B3%E6%BB%91%E6%97%B6%E9%97%B4%2830%29) — `LatSmoothSec`
- [AutoSteering Suspend Angle(300)](https://github.com/ajouatom/openpilot/wiki/ZH-AutoSteering-Suspend-Angle%28300%29) — `LatSuspendAngleDeg`
- [自定义转向比x0.1(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%AE%9A%E4%B9%89%E8%BD%AC%E5%90%91%E6%AF%94x0.1%280%29) — `CustomSR`
- [自定义转向比率x0.01(100)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%AE%9A%E4%B9%89%E8%BD%AC%E5%90%91%E6%AF%94%E7%8E%87x0.01%28100%29) — `SteerRatioRate`

##### 变道 (自动转向)

- [ATC: 自动转向控制](https://github.com/ajouatom/openpilot/wiki/ZH-ATC-%E8%87%AA%E5%8A%A8%E8%BD%AC%E5%90%91%E6%8E%A7%E5%88%B6) — `AutoTurnControl`
- [手动变道转向灯（试验）](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%89%8B%E5%8A%A8%E5%8F%98%E9%81%93%E8%BD%AC%E5%90%91%E7%81%AF%28%E8%AF%95%E9%AA%8C%29) — `ManualLaneChangeIndicator`
- [手动转弯转向灯（试验）](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%89%8B%E5%8A%A8%E8%BD%AC%E5%BC%AF%E8%BD%AC%E5%90%91%E7%81%AF%28%E8%AF%95%E9%AA%8C%29) — `ManualTurnIndicator`
- [模型意图转向灯（试验）](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%A1%E5%9E%8B%E6%84%8F%E5%9B%BE%E8%BD%AC%E5%90%91%E7%81%AF%28%E8%AF%95%E9%AA%8C%29) — `ModelDesireIndicator`
- [模型路径转向灯（试验）](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%A1%E5%9E%8B%E8%B7%AF%E5%BE%84%E8%BD%AC%E5%90%91%E7%81%AF%28%E8%AF%95%E9%AA%8C%29) — `ModelPathIndicator`
- [右转前自动变道距离(米)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%B3%E8%BD%AC%E5%89%8D%E8%87%AA%E5%8A%A8%E5%8F%98%E9%81%93%E8%B7%9D%E7%A6%BB%28%E7%B1%B3%29) — `AutoTurnControlRightLaneChange`
- [ATC: 转向速度(20)](https://github.com/ajouatom/openpilot/wiki/ZH-ATC-%E8%BD%AC%E5%90%91%E9%80%9F%E5%BA%A6%2820%29) — `AutoTurnControlSpeedTurn`
- [ATC: 速度控制剩余时间(3)](https://github.com/ajouatom/openpilot/wiki/ZH-ATC-%E9%80%9F%E5%BA%A6%E6%8E%A7%E5%88%B6%E5%89%A9%E4%BD%99%E6%97%B6%E9%97%B4%283%29) — `AutoTurnControlTurnEnd`
- [ATC 辅助地图显示(0)](https://github.com/ajouatom/openpilot/wiki/ZH-ATC-%E8%BE%85%E5%8A%A9%E5%9C%B0%E5%9B%BE%E6%98%BE%E7%A4%BA%280%29) — `AutoTurnMapChange`
- [变道使用转向力矩](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%98%E9%81%93%E4%BD%BF%E7%94%A8%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9) — `LaneChangeNeedTorque`
- [自动转向灯](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%8A%A8%E8%BD%AC%E5%90%91%E7%81%AF) — `AutoBlinkerControl`
- [转向灯拨杆区分转弯/变道 (km/h, 0=关)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E7%81%AF%E6%8B%A8%E6%9D%86%E5%8C%BA%E5%88%86%E8%BD%AC%E5%BC%AF-%E5%8F%98%E9%81%93-%28km-h%2C-0%3D%E5%85%B3%29) — `BlinkerLatchedTurn`
- [单触变道请求等待 5 次闪烁](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8D%95%E8%A7%A6%E5%8F%98%E9%81%93%E8%AF%B7%E6%B1%82%E7%AD%89%E5%BE%85-5-%E6%AC%A1%E9%97%AA%E7%83%81) — `LaneChangeLeverWait`
- [变道延迟 x0.1s(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%98%E9%81%93%E5%BB%B6%E8%BF%9F-x0.1s%280%29) — `LaneChangeDelay`
- [变道盲点监测 (BSD)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%98%E9%81%93%E7%9B%B2%E7%82%B9%E7%9B%91%E6%B5%8B-%28BSD%29) — `LaneChangeBsd`
- [变道车道判断](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%98%E9%81%93%E8%BD%A6%E9%81%93%E5%88%A4%E6%96%AD) — `LaneLineCheck`

##### 车道模式

- [横向MPC路径代价(200)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%AA%E5%90%91MPC%E8%B7%AF%E5%BE%84%E4%BB%A3%E4%BB%B7%28200%29) — `LatMpcPathCost`
- [横向MPC运动代价(7)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%AA%E5%90%91MPC%E8%BF%90%E5%8A%A8%E4%BB%A3%E4%BB%B7%287%29) — `LatMpcMotionCost`
- [横向MPC加速代价(120)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%AA%E5%90%91MPC%E5%8A%A0%E9%80%9F%E4%BB%A3%E4%BB%B7%28120%29) — `LatMpcAccelCost`
- [横向MPC冲击代价(4)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%AA%E5%90%91MPC%E5%86%B2%E5%87%BB%E4%BB%A3%E4%BB%B7%284%29) — `LatMpcJerkCost`
- [横向MPC转向速率代价(7)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%AA%E5%90%91MPC%E8%BD%AC%E5%90%91%E9%80%9F%E7%8E%87%E4%BB%A3%E4%BB%B7%287%29) — `LatMpcSteeringRateCost`
- [横向MPC输入偏移(4)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%AA%E5%90%91MPC%E8%BE%93%E5%85%A5%E5%81%8F%E7%A7%BB%284%29) — `LatMpcInputOffset`
- [车道线: 速度 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E9%81%93%E7%BA%BF-%E9%80%9F%E5%BA%A6-%280%29) — `UseLaneLineSpeed`
- [车道线: 弯道速度 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E9%81%93%E7%BA%BF-%E5%BC%AF%E9%81%93%E9%80%9F%E5%BA%A6-%280%29) — `UseLaneLineCurveSpeed`
- [车道线: 车道偏移调整 (0)cm](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E9%81%93%E7%BA%BF-%E8%BD%A6%E9%81%93%E5%81%8F%E7%A7%BB%E8%B0%83%E6%95%B4-%280%29cm) — `AdjustLaneOffset`

##### 高级扭矩

###### 扭矩系数

- [NNFF 扭矩控制](https://github.com/ajouatom/openpilot/wiki/ZH-NNFF-%E6%89%AD%E7%9F%A9%E6%8E%A7%E5%88%B6) — `NNFF`
- [自定义转向力矩(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%AE%9A%E4%B9%89%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9%280%29) — `LateralTorqueCustom`
- [转向力矩加速系数\*0.001(2500)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9%E5%8A%A0%E9%80%9F%E7%B3%BB%E6%95%B0-0.001%282500%29) — `LateralTorqueAccelFactor`
- [转向力矩摩擦系数\*0.001(100)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9%E6%91%A9%E6%93%A6%E7%B3%BB%E6%95%B0-0.001%28100%29) — `LateralTorqueFriction`
- [转向力矩 Kp\*0.01(100)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9-Kp-0.01%28100%29) — `LateralTorqueKpV`
- [转向力矩 Ki\*0.01(10)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9-Ki-0.01%2810%29) — `LateralTorqueKiV`
- [转向力矩 Kf\*0.001(100)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9-Kf-0.001%28100%29) — `LateralTorqueKf`
- [转向力矩 Kd\*0.01(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9-Kd-0.01%280%29) — `LateralTorqueKd`

###### 转向限制

- [自定义最大转向力矩(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%AE%9A%E4%B9%89%E6%9C%80%E5%A4%A7%E8%BD%AC%E5%90%91%E5%8A%9B%E7%9F%A9%280%29) — `CustomSteerMax`
- [自定义转向增大斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%AE%9A%E4%B9%89%E8%BD%AC%E5%90%91%E5%A2%9E%E5%A4%A7%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaUp`
- [自定义转向减小斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%AE%9A%E4%B9%89%E8%BD%AC%E5%90%91%E5%87%8F%E5%B0%8F%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaDown`
- [变道自定义转向增大斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%98%E9%81%93%E8%87%AA%E5%AE%9A%E4%B9%89%E8%BD%AC%E5%90%91%E5%A2%9E%E5%A4%A7%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaUpLC`
- [变道自定义转向减小斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%98%E9%81%93%E8%87%AA%E5%AE%9A%E4%B9%89%E8%BD%AC%E5%90%91%E5%87%8F%E5%B0%8F%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaDownLC`

#### 速度与减速

##### 测速摄像头

- [后向摄像头通过后保持距离(m)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%90%8E%E5%90%91%E6%91%84%E5%83%8F%E5%A4%B4%E9%80%9A%E8%BF%87%E5%90%8E%E4%BF%9D%E6%8C%81%E8%B7%9D%E7%A6%BB%28m%29) — `AutoNaviRearCameraHoldDistance`
- [导航减速结束点 (6秒)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%AF%BC%E8%88%AA%E5%87%8F%E9%80%9F%E7%BB%93%E6%9D%9F%E7%82%B9-%286%E7%A7%92%29) — `AutoNaviSpeedCtrlEnd`
- [导航减速模式 (2)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%AF%BC%E8%88%AA%E5%87%8F%E9%80%9F%E6%A8%A1%E5%BC%8F-%282%29) — `AutoNaviSpeedCtrlMode`
- [车辆导航 CAN 减速应用模式](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E8%BE%86%E5%AF%BC%E8%88%AA-CAN-%E5%87%8F%E9%80%9F%E5%BA%94%E7%94%A8%E6%A8%A1%E5%BC%8F) — `VehicleNaviCanControl`
- [原车导航 30 km/h 区域限速](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8E%9F%E8%BD%A6%E5%AF%BC%E8%88%AA-30-km-h-%E5%8C%BA%E5%9F%9F%E9%99%90%E9%80%9F) — `VehicleNaviSchoolZoneControl`
- [原车导航减速中止请求](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8E%9F%E8%BD%A6%E5%AF%BC%E8%88%AA%E5%87%8F%E9%80%9F%E4%B8%AD%E6%AD%A2%E8%AF%B7%E6%B1%82) — `VehicleNaviDecelCancel`
- [减速中止：箱式摄像头](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E4%B8%AD%E6%AD%A2-%E7%AE%B1%E5%BC%8F%E6%91%84%E5%83%8F%E5%A4%B4) — `VehicleNaviDecelCancelBox`
- [减速中止：移动测速区间](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E4%B8%AD%E6%AD%A2-%E7%A7%BB%E5%8A%A8%E6%B5%8B%E9%80%9F%E5%8C%BA%E9%97%B4) — `VehicleNaviDecelCancelMobileZone`
- [减速中止：减速带](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E4%B8%AD%E6%AD%A2-%E5%87%8F%E9%80%9F%E5%B8%A6) — `VehicleNaviDecelCancelBump`
- [减速中止：未识别类型的测速摄像头 \[实验\]](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E4%B8%AD%E6%AD%A2-%E6%9C%AA%E8%AF%86%E5%88%AB%E7%B1%BB%E5%9E%8B%E7%9A%84%E6%B5%8B%E9%80%9F%E6%91%84%E5%83%8F%E5%A4%B4-%E5%AE%9E%E9%AA%8C) — `VehicleNaviDecelCancelUnknown`
- [减速中止：提前警告修正 \[实验\]](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E4%B8%AD%E6%AD%A2-%E6%8F%90%E5%89%8D%E8%AD%A6%E5%91%8A%E4%BF%AE%E6%AD%A3-%E5%AE%9E%E9%AA%8C) — `VehicleNaviDecelCancelEarlyWarning`
- [原车导航区间测速平均速度控制](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8E%9F%E8%BD%A6%E5%AF%BC%E8%88%AA%E5%8C%BA%E9%97%B4%E6%B5%8B%E9%80%9F%E5%B9%B3%E5%9D%87%E9%80%9F%E5%BA%A6%E6%8E%A7%E5%88%B6) — `VehicleNaviSectionAvgControl`
- [车辆接收测速摄像头减速（始终应用）](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E8%BE%86%E6%8E%A5%E6%94%B6%E6%B5%8B%E9%80%9F%E6%91%84%E5%83%8F%E5%A4%B4%E5%87%8F%E9%80%9F%28%E5%A7%8B%E7%BB%88%E5%BA%94%E7%94%A8%29) — `VehicleSpeedCameraControlMode`
- [车辆测速摄像头虚拟距离时间（6.0秒）](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E8%BE%86%E6%B5%8B%E9%80%9F%E6%91%84%E5%83%8F%E5%A4%B4%E8%99%9A%E6%8B%9F%E8%B7%9D%E7%A6%BB%E6%97%B6%E9%97%B4%286.0%E7%A7%92%29) — `VehicleSpeedCameraDistanceTime`
- [导航减速效率 0.01m/s^2x(120)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%AF%BC%E8%88%AA%E5%87%8F%E9%80%9F%E6%95%88%E7%8E%87-0.01m-s%5E2x%28120%29) — `AutoNaviSpeedDecelRate`
- [导航倒计时模式](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%AF%BC%E8%88%AA%E5%80%92%E8%AE%A1%E6%97%B6%E6%A8%A1%E5%BC%8F) — `AutoNaviCountDownMode`
- [导航限速比例 (105)%](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%AF%BC%E8%88%AA%E9%99%90%E9%80%9F%E6%AF%94%E4%BE%8B-%28105%29) — `AutoNaviSpeedSafetyFactor`

##### 限速

- [自动加速至: (100)%](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%8A%A8%E5%8A%A0%E9%80%9F%E8%87%B3-%28100%29) — `AutoSpeedUptoRoadSpeedLimit`
- [自动道路限速调整 (50)%](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%87%AA%E5%8A%A8%E9%81%93%E8%B7%AF%E9%99%90%E9%80%9F%E8%B0%83%E6%95%B4-%2850%29) — `AutoRoadSpeedAdjust`
- [道路限速偏移 (-1)](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%81%93%E8%B7%AF%E9%99%90%E9%80%9F%E5%81%8F%E7%A7%BB-%28-1%29) — `AutoRoadSpeedLimitOffset`

##### 减速带

- [减速带结束点 (1秒)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E5%B8%A6%E7%BB%93%E6%9D%9F%E7%82%B9-%281%E7%A7%92%29) — `AutoNaviSpeedBumpTime`
- [减速带速度 (35km/h)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E5%B8%A6%E9%80%9F%E5%BA%A6-%2835km-h%29) — `AutoNaviSpeedBumpSpeed`
- [减速带减速提前解除距离（200厘米）](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E5%B8%A6%E5%87%8F%E9%80%9F%E6%8F%90%E5%89%8D%E8%A7%A3%E9%99%A4%E8%B7%9D%E7%A6%BB%28200%E5%8E%98%E7%B1%B3%29) — `AutoNaviSpeedBumpEndDistance`

##### 弯道与转弯

- [弯道速度调节比例(100%)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%BC%AF%E9%81%93%E9%80%9F%E5%BA%A6%E8%B0%83%E8%8A%82%E6%AF%94%E4%BE%8B%28100-%29) — `AutoCurveSpeedFactor`
- [模型车速应用比例](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%A8%A1%E5%9E%8B%E8%BD%A6%E9%80%9F%E5%BA%94%E7%94%A8%E6%AF%94%E4%BE%8B) — `ApplyModelSpeed`
- [弯道自动减速下限 (30)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%BC%AF%E9%81%93%E8%87%AA%E5%8A%A8%E5%87%8F%E9%80%9F%E4%B8%8B%E9%99%90-%2830%29) — `AutoCurveSpeedLowerLimit`
- [转向速度控制模式](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AC%E5%90%91%E9%80%9F%E5%BA%A6%E6%8E%A7%E5%88%B6%E6%A8%A1%E5%BC%8F) — `TurnSpeedControlMode`
- [地图转向速度因子](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%9C%B0%E5%9B%BE%E8%BD%AC%E5%90%91%E9%80%9F%E5%BA%A6%E5%9B%A0%E5%AD%90) — `MapTurnSpeedFactor`

##### 信号灯

- [交通信号停止距离调整](https://github.com/ajouatom/openpilot/wiki/ZH-%E4%BA%A4%E9%80%9A%E4%BF%A1%E5%8F%B7%E5%81%9C%E6%AD%A2%E8%B7%9D%E7%A6%BB%E8%B0%83%E6%95%B4) — `TrafficStopDistanceAdjust`
- [前车制动灯观察（试验）](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%89%8D%E8%BD%A6%E5%88%B6%E5%8A%A8%E7%81%AF%E8%A7%82%E5%AF%9F%28%E8%AF%95%E9%AA%8C%29) — `LeadBrakeLights`
- [信号辅助模式（试验）](https://github.com/ajouatom/openpilot/wiki/ZH-%E4%BF%A1%E5%8F%B7%E8%BE%85%E5%8A%A9%E6%A8%A1%E5%BC%8F%28%E8%AF%95%E9%AA%8C%29) — `SignalAssistMode`
- [红绿灯检测模式](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%BA%A2%E7%BB%BF%E7%81%AF%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%BC%8F) — `TrafficLightDetectMode`

#### 巡航与车距

##### 加速特性

###### 驾驶模式

- [驾驶模式: 初始 (3)](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%A9%BE%E9%A9%B6%E6%A8%A1%E5%BC%8F-%E5%88%9D%E5%A7%8B-%283%29) — `MyDrivingMode`
- [驾驶模式: 自动](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%A9%BE%E9%A9%B6%E6%A8%A1%E5%BC%8F-%E8%87%AA%E5%8A%A8) — `MyDrivingModeAuto`

###### 速度加速表

- [加速度设置 0: 0km/h(160)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%AE%BE%E7%BD%AE-0-0km-h%28160%29) — `CruiseMaxVals0`
- [加速度设置 1: 10km/h(160)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%AE%BE%E7%BD%AE-1-10km-h%28160%29) — `CruiseMaxVals1`
- [加速度设置 2: 40km/h(120)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%AE%BE%E7%BD%AE-2-40km-h%28120%29) — `CruiseMaxVals2`
- [加速度设置 3: 60km/h(100)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%AE%BE%E7%BD%AE-3-60km-h%28100%29) — `CruiseMaxVals3`
- [加速度设置 4: 80km/h(80)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%AE%BE%E7%BD%AE-4-80km-h%2880%29) — `CruiseMaxVals4`
- [加速度设置 5: 110km/h(70)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%AE%BE%E7%BD%AE-5-110km-h%2870%29) — `CruiseMaxVals5`
- [加速度设置 6: 140km/h(60)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%AE%BE%E7%BD%AE-6-140km-h%2860%29) — `CruiseMaxVals6`

##### 停车与再起步

- [停止距离(600)cm](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%81%9C%E6%AD%A2%E8%B7%9D%E7%A6%BB%28600%29cm) — `StopDistanceCarrot`
- [启动加速度限制](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%90%AF%E5%8A%A8%E5%8A%A0%E9%80%9F%E5%BA%A6%E9%99%90%E5%88%B6) — `AChangeCostStarting`
- [停止/启动灵敏度(50)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%81%9C%E6%AD%A2-%E5%90%AF%E5%8A%A8%E7%81%B5%E6%95%8F%E5%BA%A6%2850%29x0.01) — `VEgoStopping`
- [停止起步加速度 x0.01(-50)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%81%9C%E6%AD%A2%E8%B5%B7%E6%AD%A5%E5%8A%A0%E9%80%9F%E5%BA%A6-x0.01%28-50%29) — `StoppingAccel`

##### 加减速调校

- [纵向 KpV(100)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%BA%B5%E5%90%91-KpV%28100%29x0.01) — `LongTuningKpV`
- [纵向 Kf(100)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%BA%B5%E5%90%91-Kf%28100%29x0.01) — `LongTuningKf`
- [纵向 KiV(0)x0.001](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%BA%B5%E5%90%91-KiV%280%29x0.001) — `LongTuningKiV`
- [纵向执行器延迟(20)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%BA%B5%E5%90%91%E6%89%A7%E8%A1%8C%E5%99%A8%E5%BB%B6%E8%BF%9F%2820%29x0.01) — `LongActuatorDelay`

##### 车距

- [车距循环级数](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%A6%E8%B7%9D%E5%BE%AA%E7%8E%AF%E7%BA%A7%E6%95%B0) — `CruiseGapLevels`
- [跟车时间(1): TimeFollow1x0.01s(110)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%B7%9F%E8%BD%A6%E6%97%B6%E9%97%B4%281%29-TimeFollow1x0.01s%28110%29) — `TFollowGap1`
- [跟车时间(2): TimeFollow2x0.01s(120)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%B7%9F%E8%BD%A6%E6%97%B6%E9%97%B4%282%29-TimeFollow2x0.01s%28120%29) — `TFollowGap2`
- [跟车时间(3): TimeFollow3x0.01s(140)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%B7%9F%E8%BD%A6%E6%97%B6%E9%97%B4%283%29-TimeFollow3x0.01s%28140%29) — `TFollowGap3`
- [跟车时间(4): TimeFollow4x0.01s(160)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%B7%9F%E8%BD%A6%E6%97%B6%E9%97%B4%284%29-TimeFollow4x0.01s%28160%29) — `TFollowGap4`
- [跟车响应性 · 通用](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%B7%9F%E8%BD%A6%E5%93%8D%E5%BA%94%E6%80%A7-%C2%B7-%E9%80%9A%E7%94%A8) — `LeadAccelResponse`
- [TF1 跟车响应性](https://github.com/ajouatom/openpilot/wiki/ZH-TF1-%E8%B7%9F%E8%BD%A6%E5%93%8D%E5%BA%94%E6%80%A7) — `LeadAccelResponseTF1`
- [TF2 跟车响应性](https://github.com/ajouatom/openpilot/wiki/ZH-TF2-%E8%B7%9F%E8%BD%A6%E5%93%8D%E5%BA%94%E6%80%A7) — `LeadAccelResponseTF2`
- [TF3 跟车响应性](https://github.com/ajouatom/openpilot/wiki/ZH-TF3-%E8%B7%9F%E8%BD%A6%E5%93%8D%E5%BA%94%E6%80%A7) — `LeadAccelResponseTF3`
- [TF4 跟车响应性](https://github.com/ajouatom/openpilot/wiki/ZH-TF4-%E8%B7%9F%E8%BD%A6%E5%93%8D%E5%BA%94%E6%80%A7) — `LeadAccelResponseTF4`
- [速度 TF 倍率](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%80%9F%E5%BA%A6-TF-%E5%80%8D%E7%8E%87) — `SpeedTFFactor`
- [变道响应 (100%)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%8F%98%E9%81%93%E5%93%8D%E5%BA%94-%28100-%29) — `DynamicTFollowLC`
- [减速时车距余量 (0%)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%87%8F%E9%80%9F%E6%97%B6%E8%BD%A6%E8%B7%9D%E4%BD%99%E9%87%8F-%280-%29) — `TFollowDecelBoost`

##### Carrot巡航

- [巡航节能控制(2km/h)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E8%8A%82%E8%83%BD%E6%8E%A7%E5%88%B6%282km-h%29) — `CruiseEcoControl`
- [巡航滑行余量](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B7%A1%E8%88%AA%E6%BB%91%E8%A1%8C%E4%BD%99%E9%87%8F) — `CruiseCoastingPercent`
- [胡萝卜巡航减速度(-1)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%83%A1%E8%90%9D%E5%8D%9C%E5%B7%A1%E8%88%AA%E5%87%8F%E9%80%9F%E5%BA%A6%28-1%29) — `CarrotCruiseDecel`
- [胡萝卜巡航 ATC 减速度(-1)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%83%A1%E8%90%9D%E5%8D%9C%E5%B7%A1%E8%88%AA-ATC-%E5%87%8F%E9%80%9F%E5%BA%A6%28-1%29) — `CarrotCruiseAtcDecel`

### 车辆与硬件

#### 现代·起亚

- [超速照相触感反馈 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%B6%85%E9%80%9F%E7%85%A7%E7%9B%B8%E8%A7%A6%E6%84%9F%E5%8F%8D%E9%A6%88-%280%29) — `HapticFeedbackWhenSpeedCamera`
- [现代: 摄像头 SCC (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%8E%B0%E4%BB%A3-%E6%91%84%E5%83%8F%E5%A4%B4-SCC-%280%29) — `HyundaiCameraSCC`
- [现代: 仅配备 LDWS 的车辆 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E7%8E%B0%E4%BB%A3-%E4%BB%85%E9%85%8D%E5%A4%87-LDWS-%E7%9A%84%E8%BD%A6%E8%BE%86-%280%29) — `IsLdwsCar`

#### CANFD·HDA

- [Parked SPAS indicator test](https://github.com/ajouatom/openpilot/wiki/ZH-Parked-SPAS-indicator-test) — `CanfdBlinkerTest`
- [CAN-FD SPAS indicators (trial)](https://github.com/ajouatom/openpilot/wiki/ZH-CAN-FD-SPAS-indicators-%28trial%29) — `CanfdBlinkerControl`
- [使用 HDP (CCNC)](https://github.com/ajouatom/openpilot/wiki/ZH-%E4%BD%BF%E7%94%A8-HDP-%28CCNC%29) — `HDPuse`
- [CANFD HDA2 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-CANFD-HDA2-%280%29) — `CanfdHDA2`
- [仪表 CAN 直接发送](https://github.com/ajouatom/openpilot/wiki/ZH-%E4%BB%AA%E8%A1%A8-CAN-%E7%9B%B4%E6%8E%A5%E5%8F%91%E9%80%81) — `HyundaiCanfdClusterDirectTx`
- [CANFD 调试 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-CANFD-%E8%B0%83%E8%AF%95-%280%29) — `CanfdDebug`

#### 雷达

- [开启雷达轨迹 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%BC%80%E5%90%AF%E9%9B%B7%E8%BE%BE%E8%BD%A8%E8%BF%B9-%280%29) — `EnableRadarTracks`
- [雷达左右反转](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%9B%B7%E8%BE%BE%E5%B7%A6%E5%8F%B3%E5%8F%8D%E8%BD%AC) — `RadarTrackFlip`
- [开启角雷达 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%BC%80%E5%90%AF%E8%A7%92%E9%9B%B7%E8%BE%BE-%280%29) — `EnableCornerRadar`

#### 驾驶员监控

- [启用驾驶员监控（例外设置）](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%90%AF%E7%94%A8%E9%A9%BE%E9%A9%B6%E5%91%98%E7%9B%91%E6%8E%A7%28%E4%BE%8B%E5%A4%96%E8%AE%BE%E7%BD%AE%29) — `DriverMonitoringEnabled`
- [驾驶员监控模式](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%A9%BE%E9%A9%B6%E5%91%98%E7%9B%91%E6%8E%A7%E6%A8%A1%E5%BC%8F) — `DriverMonitoringMode`
- [启用 Carrot Vision](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%90%AF%E7%94%A8-Carrot-Vision) — `CarrotVisionEnabled`
- [屏蔽车门感应](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B1%8F%E8%94%BD%E8%BD%A6%E9%97%A8%E6%84%9F%E5%BA%94) — `MuteDoor`
- [屏蔽安全带感应](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%B1%8F%E8%94%BD%E5%AE%89%E5%85%A8%E5%B8%A6%E6%84%9F%E5%BA%94) — `MuteSeatbelt`

#### 车辆辅助

- [来自 PCM 的速度 (原厂 SCC)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%9D%A5%E8%87%AA-PCM-%E7%9A%84%E9%80%9F%E5%BA%A6-%28%E5%8E%9F%E5%8E%82-SCC%29) — `SpeedFromPCM`
- [最大角度帧数 (89)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%9C%80%E5%A4%A7%E8%A7%92%E5%BA%A6%E5%B8%A7%E6%95%B0-%2889%29) — `MaxAngleFrames`

#### 设备硬件

- [Comma Pedal纵向控制](https://github.com/ajouatom/openpilot/wiki/ZH-Comma-Pedal%E7%BA%B5%E5%90%91%E6%8E%A7%E5%88%B6) — `CommaPedalEnabled`
- [C3X Lite 硬件](https://github.com/ajouatom/openpilot/wiki/ZH-C3X-Lite-%E7%A1%AC%E4%BB%B6) — `HardwareC3xLite`

### 显示

#### 信息显示

- [显示调试信息](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B0%83%E8%AF%95%E4%BF%A1%E6%81%AF) — `ShowDebugUI`
- [显示胎压 (TPMS) 信息](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%83%8E%E5%8E%8B-%28TPMS%29-%E4%BF%A1%E6%81%AF) — `ShowTpms`
- [显示时间信息](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E6%97%B6%E9%97%B4%E4%BF%A1%E6%81%AF) — `ShowDateTime`
- [显示路径终点](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B7%AF%E5%BE%84%E7%BB%88%E7%82%B9) — `ShowPathEnd`
- [显示设备信息](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%AE%BE%E5%A4%87%E4%BF%A1%E6%81%AF) — `ShowDeviceState`
- [显示车道信息](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%BD%A6%E9%81%93%E4%BF%A1%E6%81%AF) — `ShowLaneInfo`
- [显示雷达信息](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E9%9B%B7%E8%BE%BE%E4%BF%A1%E6%81%AF) — `ShowRadarInfo`
- [显示路线信息](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B7%AF%E7%BA%BF%E4%BF%A1%E6%81%AF) — `ShowRouteInfo`
- [显示调试图表 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B0%83%E8%AF%95%E5%9B%BE%E8%A1%A8-%280%29) — `ShowPlotMode`

#### 路径显示

- [轮胎轨迹](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%BD%AE%E8%83%8E%E8%BD%A8%E8%BF%B9) — `CarrotTireTrajectory`
- [显示路径模式: 无车道 (9)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B7%AF%E5%BE%84%E6%A8%A1%E5%BC%8F-%E6%97%A0%E8%BD%A6%E9%81%93-%289%29) — `ShowPathMode`
- [显示路径颜色: 无车道 (12)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B7%AF%E5%BE%84%E9%A2%9C%E8%89%B2-%E6%97%A0%E8%BD%A6%E9%81%93-%2812%29) — `ShowPathColor`
- [显示路径颜色: 巡航关闭 (1)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B7%AF%E5%BE%84%E9%A2%9C%E8%89%B2-%E5%B7%A1%E8%88%AA%E5%85%B3%E9%97%AD-%281%29) — `ShowPathColorCruiseOff`
- [显示路径模式: 车道模式 (11)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B7%AF%E5%BE%84%E6%A8%A1%E5%BC%8F-%E8%BD%A6%E9%81%93%E6%A8%A1%E5%BC%8F-%2811%29) — `ShowPathModeLane`
- [显示路径颜色: 车道模式 (3)](https://github.com/ajouatom/openpilot/wiki/ZH-%E6%98%BE%E7%A4%BA%E8%B7%AF%E5%BE%84%E9%A2%9C%E8%89%B2-%E8%BD%A6%E9%81%93%E6%A8%A1%E5%BC%8F-%283%29) — `ShowPathColorLane`

#### 亮度与视图

- [行车中屏幕亮度(100%)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%A1%8C%E8%BD%A6%E4%B8%AD%E5%B1%8F%E5%B9%95%E4%BA%AE%E5%BA%A6%28100-%29) — `ShowCustomBrightness`
- [行车画面布局(C4)](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%A1%8C%E8%BD%A6%E7%94%BB%E9%9D%A2%E5%B8%83%E5%B1%80%28C4%29) — `ShowModelView`
- [外部 HUD 连接时本机摄像头(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E8%BF%9E%E6%8E%A5%E6%97%B6%E6%9C%AC%E6%9C%BA%E6%91%84%E5%83%8F%E5%A4%B4%280%29) — `ShowCameraWithCluster`

#### 外部HUD

##### 基本

- [外部 HUD 显示(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E6%98%BE%E7%A4%BA%280%29) — `ClusterHud`
- [外部 HUD 镜像模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E9%95%9C%E5%83%8F%E6%A8%A1%E5%BC%8F%280%29) — `ClusterHudMirror`
- [外部 HUD 亮度(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E4%BA%AE%E5%BA%A6%280%29) — `ClusterHudBrightness`
- [外部 HUD 屏幕旋转(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E5%B1%8F%E5%B9%95%E6%97%8B%E8%BD%AC%280%29) — `ClusterHudOrientation`
- [外部 HUD 主题(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E4%B8%BB%E9%A2%98%280%29) — `ClusterHudTheme`
- [集群导航地图主题(1)](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%9B%86%E7%BE%A4%E5%AF%BC%E8%88%AA%E5%9C%B0%E5%9B%BE%E4%B8%BB%E9%A2%98%281%29) — `ClusterNaviMapTheme`
- [集群导航地图类型(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%9B%86%E7%BE%A4%E5%AF%BC%E8%88%AA%E5%9C%B0%E5%9B%BE%E7%B1%BB%E5%9E%8B%280%29) — `ClusterNaviMapType`
- [集群导航地图 FPS(1)](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%9B%86%E7%BE%A4%E5%AF%BC%E8%88%AA%E5%9C%B0%E5%9B%BE-FPS%281%29) — `ClusterNaviMapFps`

##### 画面·摄像头

- [外部 HUD 编码器(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E7%BC%96%E7%A0%81%E5%99%A8%280%29) — `ClusterHudEncoder`
- [外部 HUD 画面模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E7%94%BB%E9%9D%A2%E6%A8%A1%E5%BC%8F%280%29) — `ClusterHudScreenMode`
- [External HUD Panel Layout(0)](https://github.com/ajouatom/openpilot/wiki/ZH-External-HUD-Panel-Layout%280%29) — `ClusterHudPanelLayout`
- [External HUD Camera View Mode(0)](https://github.com/ajouatom/openpilot/wiki/ZH-External-HUD-Camera-View-Mode%280%29) — `ClusterHudCameraViewMode`

##### 雷达显示

- [外部 HUD 雷达信息(4)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E9%9B%B7%E8%BE%BE%E4%BF%A1%E6%81%AF%284%29) — `ClusterHudRadarInfo`
- [外部 HUD 雷达显示选项(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E9%9B%B7%E8%BE%BE%E6%98%BE%E7%A4%BA%E9%80%89%E9%A1%B9%280%29) — `ClusterHudRadarDisplay`
- [外部 HUD 雷达来源颜色(0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A4%96%E9%83%A8-HUD-%E9%9B%B7%E8%BE%BE%E6%9D%A5%E6%BA%90%E9%A2%9C%E8%89%B2%280%29) — `ClusterHudRadarSourceColor`

##### 性能·调试

- [External HUD Debug(0)](https://github.com/ajouatom/openpilot/wiki/ZH-External-HUD-Debug%280%29) — `ClusterHudDebug`

### 系统

#### 录制与电源

##### 录制与电源

- [记录路面摄像头](https://github.com/ajouatom/openpilot/wiki/ZH-%E8%AE%B0%E5%BD%95%E8%B7%AF%E9%9D%A2%E6%91%84%E5%83%8F%E5%A4%B4) — `RecordRoadCam`
- [关机时间 (分钟)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%85%B3%E6%9C%BA%E6%97%B6%E9%97%B4-%28%E5%88%86%E9%92%9F%29) — `MaxTimeOffroadMin`

#### 摄像头

- [使用广角前置摄像头](https://github.com/ajouatom/openpilot/wiki/ZH-%E4%BD%BF%E7%94%A8%E5%B9%BF%E8%A7%92%E5%89%8D%E7%BD%AE%E6%91%84%E5%83%8F%E5%A4%B4) — `UseWideCamera`

#### 网络与地图

- [Mapbox 样式](https://github.com/ajouatom/openpilot/wiki/ZH-Mapbox-%E6%A0%B7%E5%BC%8F) — `MapboxStyle`
- [开启热点 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%BC%80%E5%90%AF%E7%83%AD%E7%82%B9-%280%29) — `HotspotOnBoot`

#### 声音

- [声音语言](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%A3%B0%E9%9F%B3%E8%AF%AD%E8%A8%80) — `SoundLanguageSetting`
- [导航语音音量](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%AF%BC%E8%88%AA%E8%AF%AD%E9%9F%B3%E9%9F%B3%E9%87%8F) — `SoundLanguageVolume`
- [音量调节 (100%)](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%9F%B3%E9%87%8F%E8%B0%83%E8%8A%82-%28100-%29) — `SoundVolumeAdjust`
- [音量调节，激活音量 (10%)](https://github.com/ajouatom/openpilot/wiki/ZH-%E9%9F%B3%E9%87%8F%E8%B0%83%E8%8A%82%2C%E6%BF%80%E6%B4%BB%E9%9F%B3%E9%87%8F-%2810-%29) — `SoundVolumeAdjustEngage`

#### 软件

- [开启软件菜单](https://github.com/ajouatom/openpilot/wiki/ZH-%E5%BC%80%E5%90%AF%E8%BD%AF%E4%BB%B6%E8%8F%9C%E5%8D%95) — `SoftwareMenu`

## 設定目錄 · `zh-tw`

根據當前設定目錄自動生成的各項設定頁面。

### 駕駛控制

#### 啟動·自動

##### 起步動作

- [上路自動啟用](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E4%B8%8A%E8%B7%AF%E8%87%AA%E5%8B%95%E5%95%9F%E7%94%A8) — `AutoEngage`
- [全時橫向控制](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%85%A8%E6%99%82%E6%A9%AB%E5%90%91%E6%8E%A7%E5%88%B6) — `AlwaysLateral`
- [特斯拉自動轉向燈](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%89%B9%E6%96%AF%E6%8B%89%E8%87%AA%E5%8B%95%E8%BD%89%E5%90%91%E7%87%88) — `TeslaAutoTurnSignals`
- [特斯拉 CAN 紅燈停車](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%89%B9%E6%96%AF%E6%8B%89-CAN-%E7%B4%85%E7%87%88%E5%81%9C%E8%BB%8A) — `TeslaCanTrafficStop`
- [特斯拉手動變道燈](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%89%B9%E6%96%AF%E6%8B%89%E6%89%8B%E5%8B%95%E8%AE%8A%E9%81%93%E7%87%88) — `TeslaManualLaneSignals`
- [特斯拉模型意圖燈](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%89%B9%E6%96%AF%E6%8B%89%E6%A8%A1%E5%9E%8B%E6%84%8F%E5%9C%96%E7%87%88) — `TeslaModelDesireSignals`
- [特斯拉模型路徑燈](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%89%B9%E6%96%AF%E6%8B%89%E6%A8%A1%E5%9E%8B%E8%B7%AF%E5%BE%91%E7%87%88) — `TeslaModelPathSignals`
- [解除最小轉向速度限制](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%A7%A3%E9%99%A4%E6%9C%80%E5%B0%8F%E8%BD%89%E5%90%91%E9%80%9F%E5%BA%A6%E9%99%90%E5%88%B6) — `DisableMinSteerSpeed`

##### 自動巡航

- [巡航開啟距離(0cm)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%96%8B%E5%95%9F%E8%B7%9D%E9%9B%A2%280cm%29) — `CruiseOnDist`
- [自動巡航控制 (僅限現代/起亞)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%8B%95%E5%B7%A1%E8%88%AA%E6%8E%A7%E5%88%B6-%28%E5%83%85%E9%99%90%E7%8F%BE%E4%BB%A3-%E8%B5%B7%E4%BA%9E%29) — `AutoCruiseControl`
- [取消後允許軟駐車(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8F%96%E6%B6%88%E5%BE%8C%E5%85%81%E8%A8%B1%E8%BB%9F%E9%A7%90%E8%BB%8A%280%29) — `SoftHoldOnCancel`
- [自動巡航: 踩油門起步速度](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%8B%95%E5%B7%A1%E8%88%AA-%E8%B8%A9%E6%B2%B9%E9%96%80%E8%B5%B7%E6%AD%A5%E9%80%9F%E5%BA%A6) — `AutoGasTokSpeed`
- [自動巡航: 鬆開油門取消速度](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%8B%95%E5%B7%A1%E8%88%AA-%E9%AC%86%E9%96%8B%E6%B2%B9%E9%96%80%E5%8F%96%E6%B6%88%E9%80%9F%E5%BA%A6) — `AutoGasCancelSpeed`
- [自動更新巡航速度](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%8B%95%E6%9B%B4%E6%96%B0%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A6) — `AutoGasSyncSpeed`

#### 按鈕·預設

##### 按鈕模式

- [巡航按鈕模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%88%95%E6%A8%A1%E5%BC%8F%280%29) — `CruiseButtonMode`
- [取消按鈕模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8F%96%E6%B6%88%E6%8C%89%E9%88%95%E6%A8%A1%E5%BC%8F%280%29) — `CancelButtonMode`
- [LFA 按鈕模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-LFA-%E6%8C%89%E9%88%95%E6%A8%A1%E5%BC%8F%280%29) — `LfaButtonMode`
- [換擋撥片模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%8F%9B%E6%93%8B%E6%92%A5%E7%89%87%E6%A8%A1%E5%BC%8F%280%29) — `PaddleMode`

##### 速度單位

- [巡航速度單位擴充套件(10)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A6%E5%96%AE%E4%BD%8D%E6%93%B4%E5%85%85%E5%A5%97%E4%BB%B6%2810%29) — `CruiseSpeedUnit`
- [巡航按鍵長按延遲(40)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%8D%B5%E9%95%B7%E6%8C%89%E5%BB%B6%E9%81%B2%2840%29) — `CruiseButtonLongDelay`
- [巡航速度單位基礎(10)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A6%E5%96%AE%E4%BD%8D%E5%9F%BA%E7%A4%8E%2810%29) — `CruiseSpeedUnitBasic`

##### 按鈕測試

- [巡航按鈕連發1(8)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%88%95%E9%80%A3%E7%99%BC1%288%29) — `CruiseButtonTest1`
- [巡航按鈕連發2(30)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%88%95%E9%80%A3%E7%99%BC2%2830%29) — `CruiseButtonTest2`
- [巡航按鈕連發3(1)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E6%8C%89%E9%88%95%E9%80%A3%E7%99%BC3%281%29) — `CruiseButtonTest3`

##### 速度預設

- [巡航速度1(30)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A61%2830%29) — `CruiseSpeed1`
- [巡航速度2(50)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A62%2850%29) — `CruiseSpeed2`
- [巡航速度3(80)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A63%2880%29) — `CruiseSpeed3`
- [巡航速度4(110)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A64%28110%29) — `CruiseSpeed4`
- [巡航速度5(130)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E9%80%9F%E5%BA%A65%28130%29) — `CruiseSpeed5`

#### 轉向

##### ONNX 車道與盲點

- [ONNX 車道與盲點識別](https://github.com/ajouatom/openpilot/wiki/ZH-TW-ONNX-%E8%BB%8A%E9%81%93%E8%88%87%E7%9B%B2%E9%BB%9E%E8%AD%98%E5%88%A5) — `ShareData`
- [ONNX 攝影機盲點識別](https://github.com/ajouatom/openpilot/wiki/ZH-TW-ONNX-%E6%94%9D%E5%BD%B1%E6%A9%9F%E7%9B%B2%E9%BB%9E%E8%AD%98%E5%88%A5) — `OnnxBsdEnabled`
- [車道置信度閾值](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E9%81%93%E7%BD%AE%E4%BF%A1%E5%BA%A6%E9%96%BE%E5%80%BC) — `OnnxLaneThreshold`
- [車道計算間隔](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E9%81%93%E8%A8%88%E7%AE%97%E9%96%93%E9%9A%94) — `OnnxLaneIntervalMs`
- [盲區置信度閾值](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%9B%B2%E5%8D%80%E7%BD%AE%E4%BF%A1%E5%BA%A6%E9%96%BE%E5%80%BC) — `OnnxBsdThreshold`
- [盲區保持時間](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%9B%B2%E5%8D%80%E4%BF%9D%E6%8C%81%E6%99%82%E9%96%93) — `OnnxBsdSmoothingMs`
- [盲區計算間隔](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%9B%B2%E5%8D%80%E8%A8%88%E7%AE%97%E9%96%93%E9%9A%94) — `OnnxBsdIntervalMs`

##### 居中校正

- [車道偏移左右修正(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E9%81%93%E5%81%8F%E7%A7%BB%E5%B7%A6%E5%8F%B3%E4%BF%AE%E6%AD%A3%280%29) — `PathOffset`
- [攝影機YAW校正(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%94%9D%E5%BD%B1%E6%A9%9FYAW%E6%A0%A1%E6%AD%A3%280%29) — `CameraYawTrimDeg`

##### 轉向手感

- [轉向執行器延遲(30)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%9F%B7%E8%A1%8C%E5%99%A8%E5%BB%B6%E9%81%B2%2830%29) — `SteerActuatorDelay`
- [重心位置比例](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%87%8D%E5%BF%83%E4%BD%8D%E7%BD%AE%E6%AF%94%E4%BE%8B) — `CenterToFrontRatio`
- [轉向平滑時間(30)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%B9%B3%E6%BB%91%E6%99%82%E9%96%93%2830%29) — `LatSmoothSec`
- [AutoSteering Suspend Angle(300)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-AutoSteering-Suspend-Angle%28300%29) — `LatSuspendAngleDeg`
- [自定義轉向比x0.1(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%AE%9A%E7%BE%A9%E8%BD%89%E5%90%91%E6%AF%94x0.1%280%29) — `CustomSR`
- [自定義轉向比率x0.01(100)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%AE%9A%E7%BE%A9%E8%BD%89%E5%90%91%E6%AF%94%E7%8E%87x0.01%28100%29) — `SteerRatioRate`

##### 變道 (自動轉向)

- [ATC: 自動轉向控制](https://github.com/ajouatom/openpilot/wiki/ZH-TW-ATC-%E8%87%AA%E5%8B%95%E8%BD%89%E5%90%91%E6%8E%A7%E5%88%B6) — `AutoTurnControl`
- [手動變道轉向燈（試驗）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%89%8B%E5%8B%95%E8%AE%8A%E9%81%93%E8%BD%89%E5%90%91%E7%87%88%28%E8%A9%A6%E9%A9%97%29) — `ManualLaneChangeIndicator`
- [手動轉彎轉向燈（試驗）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%89%8B%E5%8B%95%E8%BD%89%E5%BD%8E%E8%BD%89%E5%90%91%E7%87%88%28%E8%A9%A6%E9%A9%97%29) — `ManualTurnIndicator`
- [模型意圖轉向燈（試驗）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A8%A1%E5%9E%8B%E6%84%8F%E5%9C%96%E8%BD%89%E5%90%91%E7%87%88%28%E8%A9%A6%E9%A9%97%29) — `ModelDesireIndicator`
- [模型路徑轉向燈（試驗）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A8%A1%E5%9E%8B%E8%B7%AF%E5%BE%91%E8%BD%89%E5%90%91%E7%87%88%28%E8%A9%A6%E9%A9%97%29) — `ModelPathIndicator`
- [右轉前自動變道距離(米)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8F%B3%E8%BD%89%E5%89%8D%E8%87%AA%E5%8B%95%E8%AE%8A%E9%81%93%E8%B7%9D%E9%9B%A2%28%E7%B1%B3%29) — `AutoTurnControlRightLaneChange`
- [ATC: 轉向速度(20)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-ATC-%E8%BD%89%E5%90%91%E9%80%9F%E5%BA%A6%2820%29) — `AutoTurnControlSpeedTurn`
- [ATC: 速度控制剩餘時間(3)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-ATC-%E9%80%9F%E5%BA%A6%E6%8E%A7%E5%88%B6%E5%89%A9%E9%A4%98%E6%99%82%E9%96%93%283%29) — `AutoTurnControlTurnEnd`
- [ATC 輔助地圖顯示(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-ATC-%E8%BC%94%E5%8A%A9%E5%9C%B0%E5%9C%96%E9%A1%AF%E7%A4%BA%280%29) — `AutoTurnMapChange`
- [變道使用轉向力矩](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AE%8A%E9%81%93%E4%BD%BF%E7%94%A8%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9) — `LaneChangeNeedTorque`
- [自動轉向燈](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%8B%95%E8%BD%89%E5%90%91%E7%87%88) — `AutoBlinkerControl`
- [轉向燈撥杆區分轉彎/變道 (km/h, 0=關)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E7%87%88%E6%92%A5%E6%9D%86%E5%8D%80%E5%88%86%E8%BD%89%E5%BD%8E-%E8%AE%8A%E9%81%93-%28km-h%2C-0%3D%E9%97%9C%29) — `BlinkerLatchedTurn`
- [單觸變道請求等待 5 次閃爍](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%96%AE%E8%A7%B8%E8%AE%8A%E9%81%93%E8%AB%8B%E6%B1%82%E7%AD%89%E5%BE%85-5-%E6%AC%A1%E9%96%83%E7%88%8D) — `LaneChangeLeverWait`
- [變道延遲 x0.1s(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AE%8A%E9%81%93%E5%BB%B6%E9%81%B2-x0.1s%280%29) — `LaneChangeDelay`
- [變道盲點監測 (BSD)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AE%8A%E9%81%93%E7%9B%B2%E9%BB%9E%E7%9B%A3%E6%B8%AC-%28BSD%29) — `LaneChangeBsd`
- [變道車道判斷](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AE%8A%E9%81%93%E8%BB%8A%E9%81%93%E5%88%A4%E6%96%B7) — `LaneLineCheck`

##### 車道模式

- [橫向MPC路徑代價(200)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A9%AB%E5%90%91MPC%E8%B7%AF%E5%BE%91%E4%BB%A3%E5%83%B9%28200%29) — `LatMpcPathCost`
- [橫向MPC運動代價(7)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A9%AB%E5%90%91MPC%E9%81%8B%E5%8B%95%E4%BB%A3%E5%83%B9%287%29) — `LatMpcMotionCost`
- [橫向MPC加速代價(120)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A9%AB%E5%90%91MPC%E5%8A%A0%E9%80%9F%E4%BB%A3%E5%83%B9%28120%29) — `LatMpcAccelCost`
- [橫向MPC衝擊代價(4)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A9%AB%E5%90%91MPC%E8%A1%9D%E6%93%8A%E4%BB%A3%E5%83%B9%284%29) — `LatMpcJerkCost`
- [橫向MPC轉向速率代價(7)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A9%AB%E5%90%91MPC%E8%BD%89%E5%90%91%E9%80%9F%E7%8E%87%E4%BB%A3%E5%83%B9%287%29) — `LatMpcSteeringRateCost`
- [橫向MPC輸入偏移(4)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A9%AB%E5%90%91MPC%E8%BC%B8%E5%85%A5%E5%81%8F%E7%A7%BB%284%29) — `LatMpcInputOffset`
- [車道線: 速度 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E9%81%93%E7%B7%9A-%E9%80%9F%E5%BA%A6-%280%29) — `UseLaneLineSpeed`
- [車道線: 彎道速度 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E9%81%93%E7%B7%9A-%E5%BD%8E%E9%81%93%E9%80%9F%E5%BA%A6-%280%29) — `UseLaneLineCurveSpeed`
- [車道線: 車道偏移調整 (0)cm](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E9%81%93%E7%B7%9A-%E8%BB%8A%E9%81%93%E5%81%8F%E7%A7%BB%E8%AA%BF%E6%95%B4-%280%29cm) — `AdjustLaneOffset`

##### 高階扭矩

###### 扭矩係數

- [NNFF 扭矩控制](https://github.com/ajouatom/openpilot/wiki/ZH-TW-NNFF-%E6%89%AD%E7%9F%A9%E6%8E%A7%E5%88%B6) — `NNFF`
- [自定義轉向力矩(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%AE%9A%E7%BE%A9%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9%280%29) — `LateralTorqueCustom`
- [轉向力矩加速係數\*0.001(2500)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9%E5%8A%A0%E9%80%9F%E4%BF%82%E6%95%B8-0.001%282500%29) — `LateralTorqueAccelFactor`
- [轉向力矩摩擦係數\*0.001(100)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9%E6%91%A9%E6%93%A6%E4%BF%82%E6%95%B8-0.001%28100%29) — `LateralTorqueFriction`
- [轉向力矩 Kp\*0.01(100)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9-Kp-0.01%28100%29) — `LateralTorqueKpV`
- [轉向力矩 Ki\*0.01(10)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9-Ki-0.01%2810%29) — `LateralTorqueKiV`
- [轉向力矩 Kf\*0.001(100)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9-Kf-0.001%28100%29) — `LateralTorqueKf`
- [轉向力矩 Kd\*0.01(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9-Kd-0.01%280%29) — `LateralTorqueKd`

###### 轉向限制

- [自定義最大轉向力矩(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%AE%9A%E7%BE%A9%E6%9C%80%E5%A4%A7%E8%BD%89%E5%90%91%E5%8A%9B%E7%9F%A9%280%29) — `CustomSteerMax`
- [自定義轉向增大斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%AE%9A%E7%BE%A9%E8%BD%89%E5%90%91%E5%A2%9E%E5%A4%A7%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaUp`
- [自定義轉向減小斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%AE%9A%E7%BE%A9%E8%BD%89%E5%90%91%E6%B8%9B%E5%B0%8F%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaDown`
- [變道自定義轉向增大斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AE%8A%E9%81%93%E8%87%AA%E5%AE%9A%E7%BE%A9%E8%BD%89%E5%90%91%E5%A2%9E%E5%A4%A7%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaUpLC`
- [變道自定義轉向減小斜率(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AE%8A%E9%81%93%E8%87%AA%E5%AE%9A%E7%BE%A9%E8%BD%89%E5%90%91%E6%B8%9B%E5%B0%8F%E6%96%9C%E7%8E%87%280%29) — `CustomSteerDeltaDownLC`

#### 速度與減速

##### 測速攝影機

- [後向攝影機透過後保持距離(m)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%BE%8C%E5%90%91%E6%94%9D%E5%BD%B1%E6%A9%9F%E9%80%8F%E9%81%8E%E5%BE%8C%E4%BF%9D%E6%8C%81%E8%B7%9D%E9%9B%A2%28m%29) — `AutoNaviRearCameraHoldDistance`
- [導航減速結束點 (6秒)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B0%8E%E8%88%AA%E6%B8%9B%E9%80%9F%E7%B5%90%E6%9D%9F%E9%BB%9E-%286%E7%A7%92%29) — `AutoNaviSpeedCtrlEnd`
- [導航減速模式 (2)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B0%8E%E8%88%AA%E6%B8%9B%E9%80%9F%E6%A8%A1%E5%BC%8F-%282%29) — `AutoNaviSpeedCtrlMode`
- [車輛導航 CAN 減速應用模式](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E8%BC%9B%E5%B0%8E%E8%88%AA-CAN-%E6%B8%9B%E9%80%9F%E6%87%89%E7%94%A8%E6%A8%A1%E5%BC%8F) — `VehicleNaviCanControl`
- [原車導航 30 km/h 區域限速](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8E%9F%E8%BB%8A%E5%B0%8E%E8%88%AA-30-km-h-%E5%8D%80%E5%9F%9F%E9%99%90%E9%80%9F) — `VehicleNaviSchoolZoneControl`
- [原車導航減速中止請求](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8E%9F%E8%BB%8A%E5%B0%8E%E8%88%AA%E6%B8%9B%E9%80%9F%E4%B8%AD%E6%AD%A2%E8%AB%8B%E6%B1%82) — `VehicleNaviDecelCancel`
- [減速中止：箱式攝影機](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E4%B8%AD%E6%AD%A2-%E7%AE%B1%E5%BC%8F%E6%94%9D%E5%BD%B1%E6%A9%9F) — `VehicleNaviDecelCancelBox`
- [減速中止：移動測速區間](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E4%B8%AD%E6%AD%A2-%E7%A7%BB%E5%8B%95%E6%B8%AC%E9%80%9F%E5%8D%80%E9%96%93) — `VehicleNaviDecelCancelMobileZone`
- [減速中止：減速帶](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E4%B8%AD%E6%AD%A2-%E6%B8%9B%E9%80%9F%E5%B8%B6) — `VehicleNaviDecelCancelBump`
- [減速中止：未識別型別的測速攝影機 \[實驗\]](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E4%B8%AD%E6%AD%A2-%E6%9C%AA%E8%AD%98%E5%88%A5%E5%9E%8B%E5%88%A5%E7%9A%84%E6%B8%AC%E9%80%9F%E6%94%9D%E5%BD%B1%E6%A9%9F-%E5%AF%A6%E9%A9%97) — `VehicleNaviDecelCancelUnknown`
- [減速中止：提前警告修正 \[實驗\]](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E4%B8%AD%E6%AD%A2-%E6%8F%90%E5%89%8D%E8%AD%A6%E5%91%8A%E4%BF%AE%E6%AD%A3-%E5%AF%A6%E9%A9%97) — `VehicleNaviDecelCancelEarlyWarning`
- [原車導航區間測速平均速度控制](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8E%9F%E8%BB%8A%E5%B0%8E%E8%88%AA%E5%8D%80%E9%96%93%E6%B8%AC%E9%80%9F%E5%B9%B3%E5%9D%87%E9%80%9F%E5%BA%A6%E6%8E%A7%E5%88%B6) — `VehicleNaviSectionAvgControl`
- [車輛接收測速攝影機減速（始終應用）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E8%BC%9B%E6%8E%A5%E6%94%B6%E6%B8%AC%E9%80%9F%E6%94%9D%E5%BD%B1%E6%A9%9F%E6%B8%9B%E9%80%9F%28%E5%A7%8B%E7%B5%82%E6%87%89%E7%94%A8%29) — `VehicleSpeedCameraControlMode`
- [車輛測速攝影機虛擬距離時間（6.0秒）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E8%BC%9B%E6%B8%AC%E9%80%9F%E6%94%9D%E5%BD%B1%E6%A9%9F%E8%99%9B%E6%93%AC%E8%B7%9D%E9%9B%A2%E6%99%82%E9%96%93%286.0%E7%A7%92%29) — `VehicleSpeedCameraDistanceTime`
- [導航減速效率 0.01m/s^2x(120)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B0%8E%E8%88%AA%E6%B8%9B%E9%80%9F%E6%95%88%E7%8E%87-0.01m-s%5E2x%28120%29) — `AutoNaviSpeedDecelRate`
- [導航倒計時模式](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B0%8E%E8%88%AA%E5%80%92%E8%A8%88%E6%99%82%E6%A8%A1%E5%BC%8F) — `AutoNaviCountDownMode`
- [導航限速比例 (105)%](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B0%8E%E8%88%AA%E9%99%90%E9%80%9F%E6%AF%94%E4%BE%8B-%28105%29) — `AutoNaviSpeedSafetyFactor`

##### 限速

- [自動加速至: (100)%](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%8B%95%E5%8A%A0%E9%80%9F%E8%87%B3-%28100%29) — `AutoSpeedUptoRoadSpeedLimit`
- [自動道路限速調整 (50)%](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%87%AA%E5%8B%95%E9%81%93%E8%B7%AF%E9%99%90%E9%80%9F%E8%AA%BF%E6%95%B4-%2850%29) — `AutoRoadSpeedAdjust`
- [道路限速偏移 (-1)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%81%93%E8%B7%AF%E9%99%90%E9%80%9F%E5%81%8F%E7%A7%BB-%28-1%29) — `AutoRoadSpeedLimitOffset`

##### 減速帶

- [減速帶結束點 (1秒)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E5%B8%B6%E7%B5%90%E6%9D%9F%E9%BB%9E-%281%E7%A7%92%29) — `AutoNaviSpeedBumpTime`
- [減速帶速度 (35km/h)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E5%B8%B6%E9%80%9F%E5%BA%A6-%2835km-h%29) — `AutoNaviSpeedBumpSpeed`
- [減速帶減速提前解除距離（200釐米）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E5%B8%B6%E6%B8%9B%E9%80%9F%E6%8F%90%E5%89%8D%E8%A7%A3%E9%99%A4%E8%B7%9D%E9%9B%A2%28200%E9%87%90%E7%B1%B3%29) — `AutoNaviSpeedBumpEndDistance`

##### 彎道與轉彎

- [彎道速度調節比例(100%)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%BD%8E%E9%81%93%E9%80%9F%E5%BA%A6%E8%AA%BF%E7%AF%80%E6%AF%94%E4%BE%8B%28100-%29) — `AutoCurveSpeedFactor`
- [模型車速應用比例](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%A8%A1%E5%9E%8B%E8%BB%8A%E9%80%9F%E6%87%89%E7%94%A8%E6%AF%94%E4%BE%8B) — `ApplyModelSpeed`
- [彎道自動減速下限 (30)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%BD%8E%E9%81%93%E8%87%AA%E5%8B%95%E6%B8%9B%E9%80%9F%E4%B8%8B%E9%99%90-%2830%29) — `AutoCurveSpeedLowerLimit`
- [轉向速度控制模式](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BD%89%E5%90%91%E9%80%9F%E5%BA%A6%E6%8E%A7%E5%88%B6%E6%A8%A1%E5%BC%8F) — `TurnSpeedControlMode`
- [地圖轉向速度因子](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%9C%B0%E5%9C%96%E8%BD%89%E5%90%91%E9%80%9F%E5%BA%A6%E5%9B%A0%E5%AD%90) — `MapTurnSpeedFactor`

##### 訊號燈

- [交通訊號停止距離調整](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E4%BA%A4%E9%80%9A%E8%A8%8A%E8%99%9F%E5%81%9C%E6%AD%A2%E8%B7%9D%E9%9B%A2%E8%AA%BF%E6%95%B4) — `TrafficStopDistanceAdjust`
- [前車制動燈觀察（試驗）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%89%8D%E8%BB%8A%E5%88%B6%E5%8B%95%E7%87%88%E8%A7%80%E5%AF%9F%28%E8%A9%A6%E9%A9%97%29) — `LeadBrakeLights`
- [訊號輔助模式（試驗）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%A8%8A%E8%99%9F%E8%BC%94%E5%8A%A9%E6%A8%A1%E5%BC%8F%28%E8%A9%A6%E9%A9%97%29) — `SignalAssistMode`
- [紅綠燈檢測模式](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%B4%85%E7%B6%A0%E7%87%88%E6%AA%A2%E6%B8%AC%E6%A8%A1%E5%BC%8F) — `TrafficLightDetectMode`

#### 巡航與車距

##### 加速特性

###### 駕駛模式

- [駕駛模式: 初始 (3)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A7%95%E9%A7%9B%E6%A8%A1%E5%BC%8F-%E5%88%9D%E5%A7%8B-%283%29) — `MyDrivingMode`
- [駕駛模式: 自動](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A7%95%E9%A7%9B%E6%A8%A1%E5%BC%8F-%E8%87%AA%E5%8B%95) — `MyDrivingModeAuto`

###### 速度加速表

- [加速度設定 0: 0km/h(160)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%A8%AD%E5%AE%9A-0-0km-h%28160%29) — `CruiseMaxVals0`
- [加速度設定 1: 10km/h(160)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%A8%AD%E5%AE%9A-1-10km-h%28160%29) — `CruiseMaxVals1`
- [加速度設定 2: 40km/h(120)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%A8%AD%E5%AE%9A-2-40km-h%28120%29) — `CruiseMaxVals2`
- [加速度設定 3: 60km/h(100)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%A8%AD%E5%AE%9A-3-60km-h%28100%29) — `CruiseMaxVals3`
- [加速度設定 4: 80km/h(80)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%A8%AD%E5%AE%9A-4-80km-h%2880%29) — `CruiseMaxVals4`
- [加速度設定 5: 110km/h(70)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%A8%AD%E5%AE%9A-5-110km-h%2870%29) — `CruiseMaxVals5`
- [加速度設定 6: 140km/h(60)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8A%A0%E9%80%9F%E5%BA%A6%E8%A8%AD%E5%AE%9A-6-140km-h%2860%29) — `CruiseMaxVals6`

##### 停車與再起步

- [停止距離(600)cm](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%81%9C%E6%AD%A2%E8%B7%9D%E9%9B%A2%28600%29cm) — `StopDistanceCarrot`
- [啟動加速度限制](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%95%9F%E5%8B%95%E5%8A%A0%E9%80%9F%E5%BA%A6%E9%99%90%E5%88%B6) — `AChangeCostStarting`
- [停止/啟動靈敏度(50)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%81%9C%E6%AD%A2-%E5%95%9F%E5%8B%95%E9%9D%88%E6%95%8F%E5%BA%A6%2850%29x0.01) — `VEgoStopping`
- [停止起步加速度 x0.01(-50)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%81%9C%E6%AD%A2%E8%B5%B7%E6%AD%A5%E5%8A%A0%E9%80%9F%E5%BA%A6-x0.01%28-50%29) — `StoppingAccel`

##### 加減速調校

- [縱向 KpV(100)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%B8%B1%E5%90%91-KpV%28100%29x0.01) — `LongTuningKpV`
- [縱向 Kf(100)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%B8%B1%E5%90%91-Kf%28100%29x0.01) — `LongTuningKf`
- [縱向 KiV(0)x0.001](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%B8%B1%E5%90%91-KiV%280%29x0.001) — `LongTuningKiV`
- [縱向執行器延遲(20)x0.01](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%B8%B1%E5%90%91%E5%9F%B7%E8%A1%8C%E5%99%A8%E5%BB%B6%E9%81%B2%2820%29x0.01) — `LongActuatorDelay`

##### 車距

- [車距迴圈級數](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BB%8A%E8%B7%9D%E8%BF%B4%E5%9C%88%E7%B4%9A%E6%95%B8) — `CruiseGapLevels`
- [跟車時間(1): TimeFollow1x0.01s(110)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%B7%9F%E8%BB%8A%E6%99%82%E9%96%93%281%29-TimeFollow1x0.01s%28110%29) — `TFollowGap1`
- [跟車時間(2): TimeFollow2x0.01s(120)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%B7%9F%E8%BB%8A%E6%99%82%E9%96%93%282%29-TimeFollow2x0.01s%28120%29) — `TFollowGap2`
- [跟車時間(3): TimeFollow3x0.01s(140)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%B7%9F%E8%BB%8A%E6%99%82%E9%96%93%283%29-TimeFollow3x0.01s%28140%29) — `TFollowGap3`
- [跟車時間(4): TimeFollow4x0.01s(160)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%B7%9F%E8%BB%8A%E6%99%82%E9%96%93%284%29-TimeFollow4x0.01s%28160%29) — `TFollowGap4`
- [跟車響應性 · 通用](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%B7%9F%E8%BB%8A%E9%9F%BF%E6%87%89%E6%80%A7-%C2%B7-%E9%80%9A%E7%94%A8) — `LeadAccelResponse`
- [TF1 跟車響應性](https://github.com/ajouatom/openpilot/wiki/ZH-TW-TF1-%E8%B7%9F%E8%BB%8A%E9%9F%BF%E6%87%89%E6%80%A7) — `LeadAccelResponseTF1`
- [TF2 跟車響應性](https://github.com/ajouatom/openpilot/wiki/ZH-TW-TF2-%E8%B7%9F%E8%BB%8A%E9%9F%BF%E6%87%89%E6%80%A7) — `LeadAccelResponseTF2`
- [TF3 跟車響應性](https://github.com/ajouatom/openpilot/wiki/ZH-TW-TF3-%E8%B7%9F%E8%BB%8A%E9%9F%BF%E6%87%89%E6%80%A7) — `LeadAccelResponseTF3`
- [TF4 跟車響應性](https://github.com/ajouatom/openpilot/wiki/ZH-TW-TF4-%E8%B7%9F%E8%BB%8A%E9%9F%BF%E6%87%89%E6%80%A7) — `LeadAccelResponseTF4`
- [速度 TF 倍率](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%80%9F%E5%BA%A6-TF-%E5%80%8D%E7%8E%87) — `SpeedTFFactor`
- [變道響應 (100%)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AE%8A%E9%81%93%E9%9F%BF%E6%87%89-%28100-%29) — `DynamicTFollowLC`
- [減速時車距餘量 (0%)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%B8%9B%E9%80%9F%E6%99%82%E8%BB%8A%E8%B7%9D%E9%A4%98%E9%87%8F-%280-%29) — `TFollowDecelBoost`

##### Carrot巡航

- [巡航節能控制(2km/h)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E7%AF%80%E8%83%BD%E6%8E%A7%E5%88%B6%282km-h%29) — `CruiseEcoControl`
- [巡航滑行餘量](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%B7%A1%E8%88%AA%E6%BB%91%E8%A1%8C%E9%A4%98%E9%87%8F) — `CruiseCoastingPercent`
- [胡蘿蔔巡航減速度(-1)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%83%A1%E8%98%BF%E8%94%94%E5%B7%A1%E8%88%AA%E6%B8%9B%E9%80%9F%E5%BA%A6%28-1%29) — `CarrotCruiseDecel`
- [胡蘿蔔巡航 ATC 減速度(-1)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%83%A1%E8%98%BF%E8%94%94%E5%B7%A1%E8%88%AA-ATC-%E6%B8%9B%E9%80%9F%E5%BA%A6%28-1%29) — `CarrotCruiseAtcDecel`

### 車輛與硬體

#### 現代·起亞

- [超速照相觸感反饋 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%B6%85%E9%80%9F%E7%85%A7%E7%9B%B8%E8%A7%B8%E6%84%9F%E5%8F%8D%E9%A5%8B-%280%29) — `HapticFeedbackWhenSpeedCamera`
- [現代: 攝影機 SCC (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%8F%BE%E4%BB%A3-%E6%94%9D%E5%BD%B1%E6%A9%9F-SCC-%280%29) — `HyundaiCameraSCC`
- [現代: 僅配備 LDWS 的車輛 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E7%8F%BE%E4%BB%A3-%E5%83%85%E9%85%8D%E5%82%99-LDWS-%E7%9A%84%E8%BB%8A%E8%BC%9B-%280%29) — `IsLdwsCar`

#### CANFD·HDA

- [Parked SPAS indicator test](https://github.com/ajouatom/openpilot/wiki/ZH-TW-Parked-SPAS-indicator-test) — `CanfdBlinkerTest`
- [CAN-FD SPAS indicators (trial)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-CAN-FD-SPAS-indicators-%28trial%29) — `CanfdBlinkerControl`
- [使用 HDP (CCNC)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E4%BD%BF%E7%94%A8-HDP-%28CCNC%29) — `HDPuse`
- [CANFD HDA2 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-CANFD-HDA2-%280%29) — `CanfdHDA2`
- [儀表 CAN 直接傳送](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%84%80%E8%A1%A8-CAN-%E7%9B%B4%E6%8E%A5%E5%82%B3%E9%80%81) — `HyundaiCanfdClusterDirectTx`
- [CANFD 除錯 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-CANFD-%E9%99%A4%E9%8C%AF-%280%29) — `CanfdDebug`

#### 雷達

- [開啟雷達軌跡 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%96%8B%E5%95%9F%E9%9B%B7%E9%81%94%E8%BB%8C%E8%B7%A1-%280%29) — `EnableRadarTracks`
- [雷達左右反轉](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%9B%B7%E9%81%94%E5%B7%A6%E5%8F%B3%E5%8F%8D%E8%BD%89) — `RadarTrackFlip`
- [開啟角雷達 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%96%8B%E5%95%9F%E8%A7%92%E9%9B%B7%E9%81%94-%280%29) — `EnableCornerRadar`

#### 駕駛員監控

- [啟用駕駛員監控（例外設定）](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%95%9F%E7%94%A8%E9%A7%95%E9%A7%9B%E5%93%A1%E7%9B%A3%E6%8E%A7%28%E4%BE%8B%E5%A4%96%E8%A8%AD%E5%AE%9A%29) — `DriverMonitoringEnabled`
- [駕駛員監控模式](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A7%95%E9%A7%9B%E5%93%A1%E7%9B%A3%E6%8E%A7%E6%A8%A1%E5%BC%8F) — `DriverMonitoringMode`
- [啟用 Carrot Vision](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%95%9F%E7%94%A8-Carrot-Vision) — `CarrotVisionEnabled`
- [遮蔽車門感應](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%81%AE%E8%94%BD%E8%BB%8A%E9%96%80%E6%84%9F%E6%87%89) — `MuteDoor`
- [遮蔽安全帶感應](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%81%AE%E8%94%BD%E5%AE%89%E5%85%A8%E5%B8%B6%E6%84%9F%E6%87%89) — `MuteSeatbelt`

#### 車輛輔助

- [來自 PCM 的速度 (原廠 SCC)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E4%BE%86%E8%87%AA-PCM-%E7%9A%84%E9%80%9F%E5%BA%A6-%28%E5%8E%9F%E5%BB%A0-SCC%29) — `SpeedFromPCM`
- [最大角度幀數 (89)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E6%9C%80%E5%A4%A7%E8%A7%92%E5%BA%A6%E5%B9%80%E6%95%B8-%2889%29) — `MaxAngleFrames`

#### 裝置硬體

- [Comma Pedal縱向控制](https://github.com/ajouatom/openpilot/wiki/ZH-TW-Comma-Pedal%E7%B8%B1%E5%90%91%E6%8E%A7%E5%88%B6) — `CommaPedalEnabled`
- [C3X Lite 硬體](https://github.com/ajouatom/openpilot/wiki/ZH-TW-C3X-Lite-%E7%A1%AC%E9%AB%94) — `HardwareC3xLite`

### 顯示

#### 資訊顯示

- [顯示除錯資訊](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E9%99%A4%E9%8C%AF%E8%B3%87%E8%A8%8A) — `ShowDebugUI`
- [顯示胎壓 (TPMS) 資訊](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%83%8E%E5%A3%93-%28TPMS%29-%E8%B3%87%E8%A8%8A) — `ShowTpms`
- [顯示時間資訊](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E6%99%82%E9%96%93%E8%B3%87%E8%A8%8A) — `ShowDateTime`
- [顯示路徑終點](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%B7%AF%E5%BE%91%E7%B5%82%E9%BB%9E) — `ShowPathEnd`
- [顯示裝置資訊](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%A3%9D%E7%BD%AE%E8%B3%87%E8%A8%8A) — `ShowDeviceState`
- [顯示車道資訊](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%BB%8A%E9%81%93%E8%B3%87%E8%A8%8A) — `ShowLaneInfo`
- [顯示雷達資訊](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E9%9B%B7%E9%81%94%E8%B3%87%E8%A8%8A) — `ShowRadarInfo`
- [顯示路線資訊](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%B7%AF%E7%B7%9A%E8%B3%87%E8%A8%8A) — `ShowRouteInfo`
- [顯示除錯圖表 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E9%99%A4%E9%8C%AF%E5%9C%96%E8%A1%A8-%280%29) — `ShowPlotMode`

#### 路徑顯示

- [輪胎軌跡](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%BC%AA%E8%83%8E%E8%BB%8C%E8%B7%A1) — `CarrotTireTrajectory`
- [顯示路徑模式: 無車道 (9)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%B7%AF%E5%BE%91%E6%A8%A1%E5%BC%8F-%E7%84%A1%E8%BB%8A%E9%81%93-%289%29) — `ShowPathMode`
- [顯示路徑顏色: 無車道 (12)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%B7%AF%E5%BE%91%E9%A1%8F%E8%89%B2-%E7%84%A1%E8%BB%8A%E9%81%93-%2812%29) — `ShowPathColor`
- [顯示路徑顏色: 巡航關閉 (1)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%B7%AF%E5%BE%91%E9%A1%8F%E8%89%B2-%E5%B7%A1%E8%88%AA%E9%97%9C%E9%96%89-%281%29) — `ShowPathColorCruiseOff`
- [顯示路徑模式: 車道模式 (11)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%B7%AF%E5%BE%91%E6%A8%A1%E5%BC%8F-%E8%BB%8A%E9%81%93%E6%A8%A1%E5%BC%8F-%2811%29) — `ShowPathModeLane`
- [顯示路徑顏色: 車道模式 (3)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%A1%AF%E7%A4%BA%E8%B7%AF%E5%BE%91%E9%A1%8F%E8%89%B2-%E8%BB%8A%E9%81%93%E6%A8%A1%E5%BC%8F-%283%29) — `ShowPathColorLane`

#### 亮度與檢視

- [行車中螢幕亮度(100%)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%A1%8C%E8%BB%8A%E4%B8%AD%E8%9E%A2%E5%B9%95%E4%BA%AE%E5%BA%A6%28100-%29) — `ShowCustomBrightness`
- [行車畫面佈局(C4)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%A1%8C%E8%BB%8A%E7%95%AB%E9%9D%A2%E4%BD%88%E5%B1%80%28C4%29) — `ShowModelView`
- [外部 HUD 連線時本機攝影機(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E9%80%A3%E7%B7%9A%E6%99%82%E6%9C%AC%E6%A9%9F%E6%94%9D%E5%BD%B1%E6%A9%9F%280%29) — `ShowCameraWithCluster`

#### 外部HUD

##### 基本

- [外部 HUD 顯示(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E9%A1%AF%E7%A4%BA%280%29) — `ClusterHud`
- [外部 HUD 映象模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E6%98%A0%E8%B1%A1%E6%A8%A1%E5%BC%8F%280%29) — `ClusterHudMirror`
- [外部 HUD 亮度(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E4%BA%AE%E5%BA%A6%280%29) — `ClusterHudBrightness`
- [外部 HUD 螢幕旋轉(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E8%9E%A2%E5%B9%95%E6%97%8B%E8%BD%89%280%29) — `ClusterHudOrientation`
- [外部 HUD 主題(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E4%B8%BB%E9%A1%8C%280%29) — `ClusterHudTheme`
- [叢集導航地圖主題(1)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8F%A2%E9%9B%86%E5%B0%8E%E8%88%AA%E5%9C%B0%E5%9C%96%E4%B8%BB%E9%A1%8C%281%29) — `ClusterNaviMapTheme`
- [叢集導航地圖型別(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8F%A2%E9%9B%86%E5%B0%8E%E8%88%AA%E5%9C%B0%E5%9C%96%E5%9E%8B%E5%88%A5%280%29) — `ClusterNaviMapType`
- [叢集導航地圖 FPS(1)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%8F%A2%E9%9B%86%E5%B0%8E%E8%88%AA%E5%9C%B0%E5%9C%96-FPS%281%29) — `ClusterNaviMapFps`

##### 畫面·攝影機

- [外部 HUD 編碼器(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E7%B7%A8%E7%A2%BC%E5%99%A8%280%29) — `ClusterHudEncoder`
- [外部 HUD 畫面模式(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E7%95%AB%E9%9D%A2%E6%A8%A1%E5%BC%8F%280%29) — `ClusterHudScreenMode`
- [External HUD Panel Layout(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-External-HUD-Panel-Layout%280%29) — `ClusterHudPanelLayout`
- [External HUD Camera View Mode(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-External-HUD-Camera-View-Mode%280%29) — `ClusterHudCameraViewMode`

##### 雷達顯示

- [外部 HUD 雷達資訊(4)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E9%9B%B7%E9%81%94%E8%B3%87%E8%A8%8A%284%29) — `ClusterHudRadarInfo`
- [外部 HUD 雷達顯示選項(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E9%9B%B7%E9%81%94%E9%A1%AF%E7%A4%BA%E9%81%B8%E9%A0%85%280%29) — `ClusterHudRadarDisplay`
- [外部 HUD 雷達來源顏色(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E5%A4%96%E9%83%A8-HUD-%E9%9B%B7%E9%81%94%E4%BE%86%E6%BA%90%E9%A1%8F%E8%89%B2%280%29) — `ClusterHudRadarSourceColor`

##### 效能·除錯

- [External HUD Debug(0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-External-HUD-Debug%280%29) — `ClusterHudDebug`

### 系統

#### 錄製與電源

##### 錄製與電源

- [記錄路面攝影機](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%A8%98%E9%8C%84%E8%B7%AF%E9%9D%A2%E6%94%9D%E5%BD%B1%E6%A9%9F) — `RecordRoadCam`
- [關機時間 (分鐘)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%97%9C%E6%A9%9F%E6%99%82%E9%96%93-%28%E5%88%86%E9%90%98%29) — `MaxTimeOffroadMin`

#### 攝影機

- [使用廣角前置攝影機](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E4%BD%BF%E7%94%A8%E5%BB%A3%E8%A7%92%E5%89%8D%E7%BD%AE%E6%94%9D%E5%BD%B1%E6%A9%9F) — `UseWideCamera`

#### 網路與地圖

- [Mapbox 樣式](https://github.com/ajouatom/openpilot/wiki/ZH-TW-Mapbox-%E6%A8%A3%E5%BC%8F) — `MapboxStyle`
- [開啟熱點 (0)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%96%8B%E5%95%9F%E7%86%B1%E9%BB%9E-%280%29) — `HotspotOnBoot`

#### 聲音

- [聲音語言](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%81%B2%E9%9F%B3%E8%AA%9E%E8%A8%80) — `SoundLanguageSetting`
- [語音播報音量](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E8%AA%9E%E9%9F%B3%E6%92%AD%E5%A0%B1%E9%9F%B3%E9%87%8F) — `SoundLanguageVolume`
- [音量調節 (100%)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%9F%B3%E9%87%8F%E8%AA%BF%E7%AF%80-%28100-%29) — `SoundVolumeAdjust`
- [音量調節，啟用音量 (10%)](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%9F%B3%E9%87%8F%E8%AA%BF%E7%AF%80%2C%E5%95%9F%E7%94%A8%E9%9F%B3%E9%87%8F-%2810-%29) — `SoundVolumeAdjustEngage`

#### 軟體

- [開啟軟體選單](https://github.com/ajouatom/openpilot/wiki/ZH-TW-%E9%96%8B%E5%95%9F%E8%BB%9F%E9%AB%94%E9%81%B8%E5%96%AE) — `SoftwareMenu`
