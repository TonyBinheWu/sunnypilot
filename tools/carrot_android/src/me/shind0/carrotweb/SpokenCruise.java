package me.shind0.carrotweb;

import java.util.List;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Existing speed intents only: one RES/+ step, explicit decrease, or absolute target in km/h. */
final class SpokenCruise {
  private static final String SUBJECT = "(?:巡航|定速)(?:目標)?(?:速度|車速)?";
  private static final String UNIT = "(?:公里(?:每小時)?|公裏(?:每小時)?|km/h)?";
  private static final Pattern SET = Pattern.compile("(?:請)?(?:幫我)?(?:把|將)?" + SUBJECT + "(?:設定為|設為|調整為|調為|改為|改成|設定成|設成|設定到|調整到|調到)(" + ChineseVoice.NUMBER + ")" + UNIT);
  private static final Pattern DOWN = Pattern.compile("(?:請)?(?:幫我)?(?:把|將)?" + SUBJECT + "(?:降低|減少|減速|調低)(" + ChineseVoice.NUMBER + ")?" + UNIT);
  final String action;
  final Integer value;
  final boolean confirmation;
  private SpokenCruise(String action, Integer value, boolean confirmation) { this.action = action; this.value = value; this.confirmation = confirmation; }

  static SpokenCruise parse(String input) {
    String text = ChineseVoice.text(input);
    if (!ChineseVoice.imperative(text)) return null;
    boolean confirmation = text.startsWith("確認");
    if (confirmation) text = text.substring(2);
    if (text.matches("(?:請)?(?:幫我)?" + SUBJECT + "(?:提高|增加|加速|調高)")) return new SpokenCruise("speed_up", null, confirmation);
    Matcher m = SET.matcher(text);
    String action = "speed_set";
    if (!m.matches()) { m = DOWN.matcher(text); action = "speed_down"; if (!m.matches()) return null; }
    Integer value = m.group(1) == null ? Integer.valueOf(10) : ChineseVoice.integer(m.group(1));
    return value != null && value >= 1 && value <= 199 ? new SpokenCruise(action, value, confirmation) : null;
  }
  boolean same(SpokenCruise other) { return other != null && action.equals(other.action) && Objects.equals(value, other.value); }
  boolean agreed(List<String> alternatives, float[] scores) {
    if (alternatives == null || alternatives.isEmpty()) return false;
    if (!missingScore(scores) && !(scores[0] >= .8f && scores[0] <= 1)) return false;
    for (String text : alternatives) {
      SpokenCruise other = parse(text);
      if (!same(other) || confirmation != other.confirmation) return false;
    }
    return true;
  }
  static boolean missingScore(float[] scores) { return scores == null || scores.length == 0 || scores[0] == -1f; }
  String confirmationPhrase() {
    return action.equals("speed_up") ? "確認巡航加速" : action.equals("speed_down") ? "確認巡航減速" + value + "公里" : "確認巡航速度設為" + value + "公里";
  }
  static final class Check {
    private SpokenCruise expected;
    private long deadline;
    void clear() { expected = null; }
    void ask(SpokenCruise command, long now) { expected = command; deadline = now + 6000; }
    boolean resolve(SpokenCruise heard, long now) {
      boolean ok = heard != null && heard.confirmation && expected != null && expected.same(heard) && now <= deadline;
      clear(); return ok;
    }
  }
}
