package me.shind0.carrotweb;

import java.text.Normalizer;
import java.util.Locale;

/** Shared, deliberately narrow Mandarin grammar helpers; no substring command extraction. */
final class ChineseVoice {
  static final String NUMBER = "(?:-?[0-9]{1,9}|[負负]?[零〇一二三四五六七八九十百千兩两]{1,16})";
  static String text(String input) {
    if (input == null || input.length() > 180) return "";
    return Normalizer.normalize(input, Normalizer.Form.NFKC).toLowerCase(Locale.ROOT)
      .replaceAll("\\s+", "").replaceFirst("[.!。！]+$", "")
      .replace('设', '設').replace('为', '為').replace('调', '調').replace('变', '變')
      .replace('换', '換').replace('车', '車').replace('请', '請').replace('认', '認')
      .replace('寻', '尋').replace('显', '顯').replace('开', '開').replace('减', '減')
      .replace('两', '兩').replace('负', '負');
  }
  static boolean imperative(String text) {
    return !text.isEmpty() && !text.matches(".*[?？,，;；、。!！].*") &&
      !text.matches("^(?:請)?(?:不要|別|不必|不能|不想|不准|如果|假如|是否|能否|能不能|可以|昨天|剛才).*") &&
      !text.matches(".*(?:然後|並且|或者|還是|嗎|呢).*");
  }
  static Integer integer(String input) {
    String s = text(input);
    if (s.matches("-?[0-9]{1,9}")) return Integer.valueOf(s);
    boolean negative = s.startsWith("負");
    if (negative) s = s.substring(1);
    if (s.isEmpty()) return null;
    String digits = "零一二三四五六七八九";
    s = s.replace('〇', '零').replace('兩', '二');
    if (!s.matches(".*[十百千].*")) {
      if (s.length() > 9) return null;
      int n = 0;
      for (char c : s.toCharArray()) {
        int digit = digits.indexOf(c);
        if (digit < 0) return null;
        n = n * 10 + digit;
      }
      return negative ? -n : n;
    }
    int total = 0, pending = -1, lastUnit = 10000;
    boolean zero = false;
    for (char c : s.toCharArray()) {
      int digit = digits.indexOf(c);
      if (digit == 0) {
        if (total == 0 || pending != -1 || zero) return null;
        zero = true;
      } else if (digit > 0) {
        if (pending != -1) return null;
        pending = digit;
      } else {
        int unit = c == '十' ? 10 : c == '百' ? 100 : c == '千' ? 1000 : 0;
        if (unit == 0 || unit >= lastUnit || (pending == -1 && (unit != 10 || total != 0))) return null;
        total += (pending == -1 ? 1 : pending) * unit;
        pending = -1; lastUnit = unit; zero = false;
      }
    }
    // Colloquial 一百二 is ambiguous (102 or 120); require 一百零二 or 一百二十.
    if (zero && pending == -1 || pending != -1 && lastUnit > 10 && !zero) return null;
    int value = total + Math.max(0, pending);
    return negative ? -value : value;
  }
  static boolean traditional(Locale locale) {
    return "zh".equals(locale.getLanguage()) && ("Hant".equals(locale.getScript()) ||
      locale.getScript().isEmpty() && ("TW".equals(locale.getCountry()) || "HK".equals(locale.getCountry()) || "MO".equals(locale.getCountry())));
  }
  static Locale recognitionLocale(Locale locale) { return traditional(locale) ? Locale.TAIWAN : locale; }
  private ChineseVoice() {}
}
