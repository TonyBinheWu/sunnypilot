<!-- CARROT:GENERATED schema="1" locale="zh" group="SYS_SOUND" param="SoundLanguageVolume" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 导航语音音量

**菜单:** 系统 \> 声音

---

<!-- CARROT:SETTING:BEGIN SoundLanguageVolume -->
<a id="SoundLanguageVolume"></a>

## 导航语音音量

`SoundLanguageVolume`

导航转弯、减速和1–10倒计时语音的音量倍率。100%保持原音量，并与一般音量和环境噪声调节相乘。约1秒内生效，无需重启。警告音及启用音效另行控制。

<!-- CARROT:AUTO:BEGIN SoundLanguageVolume -->
<!-- CARROT:AUTO:SOURCE facts="2038e37b37c65eb0f3ca9b630db566bc1751aed5a72b1c945636aeb9e2d72c39" semantic="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **类型:** 数值
- **默认值:** `100%`
- **范围:** `5%` ~ `300%`
- **步长:** `5`
- **显示单位:** `%`
- **菜单:** 系统 \> 声音
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END SoundLanguageVolume -->

<!-- CARROT:MANUAL:BEGIN SoundLanguageVolume -->
<!-- CARROT:REVIEW reviewed-for="32c48f4cfc1ecf1e4753492b38495b772d329d24d3954eff9db073bc90a47934" reviewed-at="2026-11-13T00:00:00Z" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 运作方式

调节导航转弯、减速及数字倒计时语音。机器端乘以一般音量及环境噪声调节，网页端乘以网页音量。警告音与启用音效保持原有控制。增益后的机器端采样限制在输出范围内。
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 使用方式

停车时逐步调高，确认导航播报清楚。约一秒内生效，无需重新启动。网页音量静音时，网页语音仍然静音。
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END SoundLanguageVolume -->

<!-- CARROT:SETTING:END SoundLanguageVolume -->
