"use strict";

// CAN-FD steering bus: 2 detects observed LKAS frames; 0 and 1 select the harness explicitly.

CarrotIntro.register({
  id: "hda",
  file: "step3_hda.js",
  flow: true,
  hkgOnly: true,

  render(el) {
    const { t, ctx } = CarrotIntro;

    el.innerHTML = `
      ${CarrotIntroIcons.hda}
      <h2 class="intro-title">${t("hdaTitle")}</h2>
      <p class="intro-lead"><b>${escapeHtml(ctx.car)}</b></p>
      <div class="intro-opts">
        ${[[2, "hdaAuto", "hdaAutoD"], [0, "hda1", "hda1d"], [1, "hda2", "hda2d"]].map(([v, tk, dk]) => `
          <button class="intro-opt intro-opt--desc ${ctx.hda === v ? "is-picked" : ""}"
                  type="button" data-hda="${v}" aria-pressed="${ctx.hda === v}">
            ${t(tk)}
            <span class="intro-opt__d">${t(dk)}</span>
          </button>`).join("")}
      </div>`;
    if(ctx.reconfigure){const keep=document.createElement('button');keep.className='intro-ghost';keep.type='button';
      keep.textContent=t('againKeepHda');keep.onclick=()=>{ctx.hda=null;CarrotIntroShell.goTo('control');};el.appendChild(keep);}

    el.querySelectorAll("[data-hda]").forEach((opt) => {
      opt.addEventListener("click", () => {
        ctx.hda = Number(opt.dataset.hda);
        CarrotIntroApi.setHda(ctx.hda).catch(() => {});
        CarrotIntroShell.pick(opt, "control");
      });
    });
  },
});
