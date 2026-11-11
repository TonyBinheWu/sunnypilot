<!-- CARROT:GENERATED schema="1" locale="ko" group="HUD_SCREEN" param="ClusterHudEncoder" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 외부 HUD 인코더(0)

**메뉴:** 화면 표시 \> 외부 HUD \> 화면·카메라

---

<!-- CARROT:SETTING:BEGIN ClusterHudEncoder -->
<a id="ClusterHudEncoder"></a>

## 외부 HUD 인코더(0)

`ClusterHudEncoder`

0: 자동(하드웨어 H264 -\> 소프트웨어 H264 -\> JPEG) 1: JPEG 2: 하드웨어 H264 3: 소프트웨어 H264(ffmpeg/libx264)

<!-- CARROT:AUTO:BEGIN ClusterHudEncoder -->
<!-- CARROT:AUTO:SOURCE facts="505dbaca9428b6d745d75af0fb3b16001100ae37a57cceb5416684dc13f6b4a7" semantic="e7f0467150d4fda3feb1928b6ea87dac5141cb3e8bea9565855221b17bb9f0e6" review="needs_review" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 구간 선택
- **기본값:** `0`
- **범위:** `0` ~ `3`
- **변경 단위:** `1`
- **메뉴:** 화면 표시 \> 외부 HUD \> 화면·카메라
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ClusterHudEncoder -->

<!-- CARROT:MANUAL:BEGIN ClusterHudEncoder -->
<!-- CARROT:REVIEW reviewed-for="bfbf70df61e7ca677ecf0cdf6ba8f498aa2ce1b76fb9fc7641423889a6f5810c" reviewed-at="2026-10-16T21:40:00+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 자동(하드웨어 H264 -> 소프트웨어 H264 -> JPEG)
- `1` — JPEG
- `2` — 하드웨어 H264
- `3` — 소프트웨어 H264(ffmpeg/libx264)

S3 Wi-Fi는 1.2.0 지원 확인 후 H.264를 자동 선택합니다. 위 선택은 H.264의 하드웨어/소프트웨어 인코더에 적용되며 Wi-Fi 코덱 선택을 덮어쓰지 않습니다. 자동 모드의 인코더 초기화가 모두 실패하면 JPEG로 복구할 수 있고, 이전 S3 펌웨어는 JPEG를 사용합니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

외부 HUD에서 화면 지연·선명도·CPU 사용량을 함께 확인하며 모드를 선택합니다.
<!-- CARROT:SECTION:END USAGE -->
<!-- CARROT:MANUAL:END ClusterHudEncoder -->

<!-- CARROT:SETTING:END ClusterHudEncoder -->
