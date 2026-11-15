"use strict";
import {setupBody,setupChanges} from '../draft.js';

/* 6단계 — 마무리 (마지막)
 *
 * 여기서 실제 쓰기가 일어난다:
 *   1. apply_preset  — 서버가 param 7개 일괄 적용 (복원 경로에서는 건너뜀)
 *   2. complete      — /data/carrot/state/intro.json 에 완료 기록
 *
 * 복원으로 온 경우(ctx.restored)에는 프리셋을 적용하지 않는다.
 * 백업이 이미 담고 있는 값을 프리셋으로 덮어쓰면 안 된다.
 *
 * 선택할 게 없는 단계라 진행 액션이 하나 있다. */

CarrotIntro.register({
  id: "outro",
  file: "step6_outro.js",
  flow: true,

  render(el) {
    const { t, br, ctx } = CarrotIntro;
    if(ctx.reconfigure){
      const heading=document.createElement('h2');heading.className='intro-title';heading.textContent=t('againReview');
      const list=document.createElement('div');list.className='intro-review';
      const changes=setupChanges(ctx);
      for(const row of changes){const item=document.createElement('p');
        const title=row.key==='CarSelected3'?t('againVehicle'):row.key==='web_language'?t('againLanguage'):row.key==='CanfdHDA2'?t('hdaTitle'):row.title;
        const value=v=>row.key==='CanfdHDA2'&&[0,1].includes(v)?t(v===1?'hda2':'hda1'):v??'—';
        item.textContent=`${title}: ${value(row.before)} → ${value(row.after)}`;list.appendChild(item);}
      if(!changes.length)list.textContent=t('againNoChanges');
      const help=document.createElement('p');help.className='intro-lead';help.textContent=t('againReviewHelp');
      const button=document.createElement('button');button.type='button';button.className='intro-cta';button.textContent=t('againApply');
      el.append(heading,list,help,button);
      button.onclick=async()=>{
        if(ctx.applied){CarrotIntroShell.finish();return;}
        el.querySelector('.intro-error')?.remove();
        button.disabled=true;CarrotIntroShell.setApplying(true);
        try{
          const result=await CarrotIntroApi.reconfigure(setupBody(ctx));ctx.applied=true;
          for(const [name,value] of Object.entries(result.applied||{}))globalThis.dispatchEvent(new CustomEvent('carrot:paramchange',{detail:{name,value,source:'intro_reconfigure'}}));
          if(globalThis.CarrotWebSettingsState)globalThis.CarrotWebSettingsState.web_language=result.webLanguage;
          if(globalThis.__CARROT_BOOTSTRAP__?.webSettings)globalThis.__CARROT_BOOTSTRAP__.webSettings.web_language=result.webLanguage;
          try{globalThis.setWebLanguage?.(result.webLanguage,{persist:false});}catch{}
          try{globalThis.applyCurrentCarLabel?.(stripMaker(ctx.car,ctx.maker));}catch{}
          heading.textContent=t('againSaved');help.textContent=t(result.requiresRestart?'againRestart':'againSavedHelp');
          button.textContent=t('againReturn');
        }catch(error){CarrotIntroShell.error(t(`againError_${error.message}`)===`againError_${error.message}`?t('againError_apply_unconfirmed'):t(`againError_${error.message}`));}
        finally{button.disabled=false;CarrotIntroShell.setApplying(false);}
      };
      return;
    }

    el.innerHTML = `
      ${CarrotIntroIcons.chill}
      <h2 class="intro-title">${t("outTitle")}</h2>
      <p class="intro-lead">${ctx.restored ? t("rsDone") + "<br>" : ""}${br(t("outSub"))}</p>
      <button class="intro-cta" type="button" data-done>${t(ctx.preview ? "previewDone" : "start")}</button>`;

    const cta = el.querySelector("[data-done]");

    cta.addEventListener("click", async () => {
      cta.disabled = true;

      try {
        if (ctx.preset && !ctx.restored) await CarrotIntroApi.applyPreset(ctx.preset);
        await CarrotIntroApi.complete(ctx.restored ? "restored_file" : "user_finished");
      } catch (err) {
        /* 완료 기록에 실패하면 다음 접속에 인트로가 또 뜬다.
           그래도 앱 진입은 막지 않는다 — 사용자를 가두는 게 더 나쁘다.
           여기서는 재시도할 수 있게 되돌린다. */
        cta.disabled = false;
        CarrotIntroShell.error(`설정 적용 실패: ${err.message}`);
        return;
      }

      CarrotIntroShell.finish();
    });
  },
});
