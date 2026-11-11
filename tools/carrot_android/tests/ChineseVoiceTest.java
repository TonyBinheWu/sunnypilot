package me.shind0.carrotweb;

import java.util.Arrays;
import java.util.Collections;
import java.util.Locale;
import static me.shind0.carrotweb.LocalCommand.*;

public final class ChineseVoiceTest {
  private static int checks;
  private static void check(boolean value) { checks++; if (!value) throw new AssertionError("Chinese voice check " + checks); }
  private static void setting(String text, String name, int value, int position) {
    SpokenSetting s = SpokenSetting.parse(text);
    check(s != null && s.name.equals(name) && s.value == value && s.position == position);
  }
  public static void main(String[] args) {
    for (String s : Arrays.asList("向左變換車道", "請幫我往左變換一條車道", "請往左換一個車道", "向左變道", "往左邊切換車道", "向左变换车道。"))
      check(LocalCommand.choose(Collections.singletonList(s), new float[]{.95f}) == LEFT);
    for (String s : Arrays.asList("向右變換車道", "請向右換車道", "往右側換道"))
      check(LocalCommand.choose(Collections.singletonList(s), new float[]{.95f}) == RIGHT);
    for (String s : Arrays.asList("不要向左變換車道", "請不要向左換道", "向左變換車道嗎", "向左變換車道？", "可以向右換道嗎",
      "向左或向右換道", "向左換道然後巡航減速", "剛才說向左變換車道", "向左換兩個車道", "如果向左換道", "向左換道，巡航加速")) {
      LocalCommand c = LocalCommand.choose(Collections.singletonList(s), new float[]{.99f});
      check(c != LEFT && c != RIGHT);
    }
    check(LocalCommand.choose(Arrays.asList("向左換道", "向右換道"), new float[]{.99f}) == UNCERTAIN);
    check(LocalCommand.choose(Arrays.asList("向左換道", "請向左變換車道"), new float[]{.99f}) == LEFT);
    check(LocalCommand.choose(Collections.singletonList("向左換道"), null) == CLARIFY_LEFT);
    check(LocalCommand.choose(Collections.singletonList("向右換道"), new float[]{.2f}) == UNCERTAIN);
    check(LocalCommand.parse("確認向左") == CONFIRM_LEFT);
    check(LocalCommand.parse("確認右邊") == CONFIRM_RIGHT);
    check(LocalCommand.parse("停止聆聽") == STOP);
    check(LocalCommand.parse("開啟方向燈設定") == BLINKER_SETTINGS);
    setting("請把螢幕亮度設為八十", "螢幕亮度", 80, 0);
    setting("把加速度設定零改成二百四十", "加速度設定零", 240, 0);
    setting("把第一個設為二四零", "第一個", 240, 1);
    setting("把第二個項目設定為２４５", "第二個項目", 245, 2);
    setting("將第二十項目調為一百零二", "第二十項目", 102, 20);
    setting("把轉向延遲設為負十", "轉向延遲", -10, 0);
    setting("把取消按鍵模式設為一", "取消按鍵模式", 1, 0);
    for (String s : Arrays.asList("不要把螢幕亮度設為80", "把亮度設為80嗎", "把亮度設為2.4", "把亮度設為80然後設為90",
      "把亮度設為一百二", "把第二十一個設為10", "巡航速度設為200", "把亮度設為一百百", "把亮度設為一百零", "把亮度設為1或2"))
      check(SpokenSetting.parse(s) == null);
    check("加速度".equals(SpokenSetting.search("請幫我搜尋加速度設定")));
    check("螢幕亮度".equals(SpokenSetting.search("搜尋螢幕亮度")));
    check(SpokenSetting.search("不要搜尋亮度") == null);
    SpokenSetting s = SpokenSetting.parse("把第一個設為二百四十");
    check(s.agreed(Arrays.asList("把第一個設為二百四十", "將第1個改成240"), new float[]{.9f}));
    check(!s.agreed(Arrays.asList("把第一個設為240", "把第二個設為240"), null));
    check(!s.agreed(Arrays.asList("把第一個設為240", "把第一個設為250"), null));
    check(!s.agreed(Collections.singletonList("把第一個設為240"), new float[]{.3f}));
    check(ChineseVoice.integer("一千零二十") == 1020);
    check(ChineseVoice.integer("一二三四") == 1234);
    check(ChineseVoice.integer("兩千三百四十五") == 2345);
    check(ChineseVoice.integer("零") == 0);
    check(ChineseVoice.integer("一百二") == null);
    check(ChineseVoice.integer("一百百") == null);
    check(ChineseVoice.recognitionLocale(Locale.forLanguageTag("zh-Hant")).equals(Locale.TAIWAN));
    check(ChineseVoice.recognitionLocale(Locale.forLanguageTag("zh-HK")).equals(Locale.TAIWAN));
    for (String text : Arrays.asList("巡航速度設為一百公里", "請幫我把巡航速度調到一百", "請把巡航速度設定為１００", "定速速度改成100公里每小時")) {
      SpokenCruise c = SpokenCruise.parse(text);
      check(c != null && c.action.equals("speed_set") && c.value == 100 && !c.confirmation);
    }
    check(SpokenCruise.parse("巡航速度降低十公里").value == 10);
    check(SpokenCruise.parse("定速減速").value == 10);
    check(SpokenCruise.parse("巡航加速").action.equals("speed_up"));
    for (String text : Arrays.asList("加速", "巡航加速十公里", "不要巡航加速", "巡航速度設為100嗎", "巡航速度設為0", "巡航速度設為200",
      "巡航速度設為負十", "巡航速度設為一百二", "巡航速度設為100或110", "巡航速度降低0公里", "巡航加速然後向左換道"))
      check(SpokenCruise.parse(text) == null);
    SpokenCruise cruise = SpokenCruise.parse("巡航速度設為100");
    check(cruise.agreed(Arrays.asList("巡航速度設為100", "請把定速速度設為一百公里"), new float[]{.95f}));
    check(!cruise.agreed(Arrays.asList("巡航速度設為100", "巡航速度設為110"), new float[]{.99f}));
    check(!cruise.agreed(Arrays.asList("巡航速度設為100", "巡航減速100"), new float[]{.99f}));
    for (float score : new float[]{.2f, Float.NaN, 1.5f}) check(!cruise.agreed(Collections.singletonList("巡航速度設為100"), new float[]{score}));
    check(SpokenCruise.missingScore(null));
    SpokenCruise.Check pending = new SpokenCruise.Check();
    SpokenCruise yes = SpokenCruise.parse(cruise.confirmationPhrase());
    check(!pending.resolve(yes, 1));
    pending.ask(cruise, 1); check(!pending.resolve(SpokenCruise.parse("確認巡航速度設為110"), 2));
    pending.ask(cruise, 1); check(!pending.resolve(yes, 6002));
    pending.ask(cruise, 1); check(pending.resolve(yes, 2)); check(!pending.resolve(yes, 3));
    pending.ask(cruise, 1); pending.clear(); check(!pending.resolve(yes, 2));
    pending.ask(cruise, 1); check(!pending.resolve(cruise, 2));
    System.out.println("Chinese voice checks passed: " + checks);
  }
}
