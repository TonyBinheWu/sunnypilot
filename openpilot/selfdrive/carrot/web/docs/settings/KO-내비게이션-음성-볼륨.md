<!-- CARROT:GENERATED schema="1" locale="ko" group="SYS_SOUND" param="SoundLanguageVolume" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 내비게이션 음성 볼륨

**메뉴:** 시스템 \> 사운드

---

<!-- CARROT:SETTING:BEGIN SoundLanguageVolume -->
<a id="SoundLanguageVolume"></a>

## 내비게이션 음성 볼륨

`SoundLanguageVolume`

회전·감속 안내와 1~10초 카운트다운 음성의 상대 음량입니다. 100%는 기존 음량이며 일반 음량과 주변 소음 보정에 곱해집니다. 약 1초 안에 적용되고 재시작은 필요 없습니다. 경고음과 인게이지 음량은 별도입니다.

<!-- CARROT:AUTO:BEGIN SoundLanguageVolume -->
<!-- CARROT:AUTO:SOURCE facts="be9e28d9189a919f853465b606c0e18f5c6dd19b9e52161fe60d4f3c19e6fe44" semantic="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `100%`
- **범위:** `5%` ~ `300%`
- **변경 단위:** `5`
- **표시 단위:** `%`
- **메뉴:** 시스템 \> 사운드
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoundLanguageVolume -->

<!-- CARROT:MANUAL:BEGIN SoundLanguageVolume -->
<!-- CARROT:REVIEW reviewed-for="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" reviewed-at="2026-11-13T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

회전·감속 안내와 숫자 카운트다운 음성을 조절합니다. 기기에서는 일반 음량과 주변 소음 보정에, 웹에서는 웹 볼륨에 곱해집니다. 경고음과 인게이지 소리는 기존 음량을 유지합니다. 증폭된 기기 샘플은 출력 범위로 제한됩니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

정차 중 안내가 명확하게 들릴 때까지 조금씩 올려 확인하세요. 약 한 초 안에 반영되며 재시작이 필요 없습니다. 웹 볼륨을 음소거하면 웹 음성도 나오지 않습니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END SoundLanguageVolume -->

<!-- CARROT:SETTING:END SoundLanguageVolume -->
