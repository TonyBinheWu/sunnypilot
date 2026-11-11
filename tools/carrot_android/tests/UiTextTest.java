import java.util.Locale;
import me.shind0.carrotweb.UiText;

public final class UiTextTest {
  private static void expect(Locale locale, String expected) {
    Locale.setDefault(locale);
    String actual = UiText.get("다시 검색", "Search again");
    if (!expected.equals(actual)) throw new AssertionError(locale + ": " + actual);
    if (!"en".equals(UiText.get("ko", "en"))) {
      if (!"ko".equals(locale.getLanguage())) throw new AssertionError("Protocol language changed");
    }
  }

  public static void main(String[] args) {
    Locale previous = Locale.getDefault();
    try {
      expect(Locale.TAIWAN, "重新搜尋");
      expect(Locale.forLanguageTag("zh-Hant"), "重新搜尋");
      expect(Locale.forLanguageTag("zh-HK"), "重新搜尋");
      expect(Locale.forLanguageTag("zh-MO"), "重新搜尋");
      expect(Locale.CHINA, "Search again");
      expect(Locale.forLanguageTag("zh-Hans-TW"), "Search again");
      expect(Locale.ENGLISH, "Search again");
      expect(Locale.KOREAN, "다시 검색");
      Locale.setDefault(Locale.TAIWAN);
      if (!"untranslated fallback".equals(UiText.get("fallback", "untranslated fallback"))) {
        throw new AssertionError("English fallback was lost");
      }
      if (!"正在準備裝置端語音".equals(UiText.get("준비", "Preparing on-device speech"))) {
        throw new AssertionError("Voice status translation missing");
      }
      if (!"允許範圍為 1 至 100。".equals(UiText.format("%s..%s", "Allowed range is %s to %s.", 1, 100))) {
        throw new AssertionError("Formatted status lost its values");
      }
    } finally {
      Locale.setDefault(previous);
    }
    System.out.println("UiText locale checks passed");
  }
}
