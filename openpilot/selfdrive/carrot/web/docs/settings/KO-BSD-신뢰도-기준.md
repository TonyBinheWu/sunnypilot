<!-- CARROT:GENERATED schema="1" locale="ko" group="STEER_ONNX" param="OnnxBsdThreshold" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# BSD 신뢰도 기준

**메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD

---

<!-- CARROT:SETTING:BEGIN OnnxBsdThreshold -->
<a id="OnnxBsdThreshold"></a>

## BSD 신뢰도 기준

`OnnxBsdThreshold`

감지영역의 차량을 카메라 사각지대 경고로 판단하는 최소 신뢰도입니다.

<!-- CARROT:AUTO:BEGIN OnnxBsdThreshold -->
<!-- CARROT:AUTO:SOURCE facts="d8f43e12f3cfd3d49c55d066605465de1cabdae44248597a0ea691e92a7d4507" semantic="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `94%`
- **범위:** `0%` ~ `100%`
- **변경 단위:** `1`
- **표시 단위:** `%`
- **메뉴:** 주행 제어 \> 차량 조향 \> ONNX 차선·BSD
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END OnnxBsdThreshold -->

<!-- CARROT:MANUAL:BEGIN OnnxBsdThreshold -->
<!-- CARROT:REVIEW reviewed-for="93b3cd562cb2ac377453782fc4a8fb383aa6da0af1741171fc90eac4b5696e07" reviewed-at="2026-10-08T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

높이면 사각지대 위험 클래스에 더 높은 신뢰도를 요구하고, 낮추면 더 낮은 신뢰도에서도 경고가 켜집니다. 원거리·후방 차량 클래스는 이 경고를 켜지 않습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->
<!-- CARROT:MANUAL:END OnnxBsdThreshold -->

<!-- CARROT:SETTING:END OnnxBsdThreshold -->
