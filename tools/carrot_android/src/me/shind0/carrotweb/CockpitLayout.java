package me.shind0.carrotweb;

/** Layout-only compatibility for existing vehicle pages on older Android WebViews. */
public final class CockpitLayout {
  private CockpitLayout() {}

  // Percentages follow the actual WebView viewport on rotation, immersive-mode
  // and keyboard resize. Do not depend on dvh support or cache pixel heights.
  public static final String SCRIPT = "(()=>{if(location.pathname!=='/cockpit')return;var id='carrot-cockpit-viewport';if(document.getElementById(id))return;var style=document.createElement('style');style.id=id;style.textContent='html{height:100%;overflow:hidden}body{height:100%!important;min-height:0!important}';document.head.appendChild(style);})()";
}
