<!-- CARROT:GENERATED schema="1" locale="ko" group="SPEED_CURVE" param="ApplyModelSpeed" -->
<!-- CARROT:AUTHORING guide="https://github.com/ajouatom/openpilot/blob/carrot-wip/tools/docs/wiki_settings/AUTHORING_GUIDE.md" editable="CARROT:MANUAL only" -->
# 모델 주행속도 적용 비율

**메뉴:** 주행 제어 \> 속도·감속 \> 커브·턴

---

<!-- CARROT:SETTING:BEGIN ApplyModelSpeed -->
<a id="ApplyModelSpeed"></a>

## 모델 주행속도 적용 비율

`ApplyModelSpeed`

모델이 계산한 주행속도를 설정한 비율만큼 적용합니다.

<!-- CARROT:AUTO:BEGIN ApplyModelSpeed -->
<!-- CARROT:AUTO:SOURCE facts="c600b8715290851c0d1420039659e3583d28cb320fa08e511c2be294ac242bcb" semantic="8039edb57e0c4c2bb0d6e9911d247c64a6f0c42f2e912402bc572f0a4701f388" review="current" -->
<!-- CARROT:SECTION:BEGIN OVERVIEW -->
- **종류:** 숫자
- **기본값:** `0%`
- **범위:** `-120%` ~ `120%`
- **변경 단위:** `1`
- **표시 단위:** `%`
- **메뉴:** 주행 제어 \> 속도·감속 \> 커브·턴
<!-- CARROT:SECTION:END OVERVIEW -->
<!-- CARROT:AUTO:END ApplyModelSpeed -->

<!-- CARROT:MANUAL:BEGIN ApplyModelSpeed -->
<!-- CARROT:REVIEW reviewed-for="8039edb57e0c4c2bb0d6e9911d247c64a6f0c42f2e912402bc572f0a4701f388" reviewed-at="2026-07-24T16:44:29+09:00" -->
<!-- CARROT:SECTION:BEGIN BEHAVIOR -->
### 동작

- `0` — 모델 예측 속도를 크루즈 설정 속도에 반영하지 않습니다.
- **양수:** 모델 예측 속도에 비율을 곱한 값이 현재 설정 속도보다 높을 때 설정 속도를 올립니다. 도로 제한속도의 110%를 상한으로 사용합니다.
- **음수:** 같은 비율의 모델 목표를 설정 속도에 직접 적용하므로 급격히 낮아질 수 있습니다.
<!-- CARROT:SECTION:END BEHAVIOR -->

<!-- CARROT:SECTION:BEGIN USAGE -->
### 사용

같은 커브와 경로 안내 조건에서 한 항목씩 조정하고, 진입 전 목표 속도와 커브 통과 속도를 비교합니다.
<!-- CARROT:SECTION:END USAGE -->

<!-- CARROT:SECTION:BEGIN REFERENCE -->
### 참고

<!-- CARROT:NOTICE level="NOTE" -->
> [!NOTE]
> `0`은 모델 주행속도를 목표 속도에 반영하지 않습니다. 양수와 음수는 코드의 모델 속도 혼합 방향을 서로 다르게 적용합니다.
<!-- CARROT:NOTICE:END -->

[관련 사용자 가이드](https://github.com/ajouatom/openpilot/blob/carrot-wip/docs/user/ko/speed-deceleration.md)
<!-- CARROT:SECTION:END REFERENCE -->
<!-- CARROT:MANUAL:END ApplyModelSpeed -->

<!-- CARROT:SETTING:END ApplyModelSpeed -->
