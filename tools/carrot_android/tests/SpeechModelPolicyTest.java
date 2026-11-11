package me.shind0.carrotweb;

import java.util.Arrays;
import java.util.Collections;
import static me.shind0.carrotweb.SpeechModelPolicy.State.*;

public final class SpeechModelPolicyTest {
  private static int checks;
  private static void check(boolean value) { checks++; if (!value) throw new AssertionError("Speech model check " + checks); }
  public static void main(String[] args) {
    check(SpeechModelPolicy.prerequisite(30, true, true) == OLD_ANDROID);
    check(SpeechModelPolicy.prerequisite(33, false, true) == PERMISSION);
    check(SpeechModelPolicy.prerequisite(33, true, false) == NO_SERVICE);
    check(SpeechModelPolicy.prerequisite(31, true, true) == MANUAL);
    check(SpeechModelPolicy.prerequisite(32, true, true) == MANUAL);
    check(SpeechModelPolicy.prerequisite(33, true, true) == CHECKING);
    check(SpeechModelPolicy.prerequisite(34, true, true) == CHECKING);
    for (String tag : Arrays.asList("zh-TW", "zh-tw", "zh_TW", "zh-Hant-TW", " zh-TW "))
      check(SpeechModelPolicy.matches(tag, "zh-TW"));
    for (String tag : Arrays.asList("zh-CN", "zh-Hans-TW", "zh-HK", "zh-Hant", "zh", "en-US", "yue-Hant-TW", "zh-TW-extra"))
      check(!SpeechModelPolicy.matches(tag, "zh-TW"));
    check(!SpeechModelPolicy.matches(null, "zh-TW"));
    check(SpeechModelPolicy.classify("zh-TW", Arrays.asList("en-US", "zh-TW"), null, null) == INSTALLED);
    check(SpeechModelPolicy.classify("zh-TW", null, Arrays.asList("zh-TW"), Arrays.asList("zh-TW")) == PENDING);
    check(SpeechModelPolicy.classify("zh-TW", Arrays.asList("en-US"), null, Arrays.asList("zh-TW")) == DOWNLOADABLE);
    check(SpeechModelPolicy.classify("zh-TW", Arrays.asList("zh-CN"), null, null) == UNSUPPORTED);
    check(SpeechModelPolicy.classify("zh-TW", Arrays.asList("zh"), null, null) == UNKNOWN);
    check(SpeechModelPolicy.classify("zh-TW", Arrays.asList("zh-Hant"), null, null) == UNKNOWN);
    check(SpeechModelPolicy.classify("zh-TW", null, null, null) == UNKNOWN);
    check(SpeechModelPolicy.classify("zh-TW", Collections.emptyList(), Collections.emptyList(), Collections.emptyList()) == UNKNOWN);
    check(SpeechModelPolicy.classify("zh-TW", Arrays.asList("zh-TW"), Arrays.asList("zh-TW"), Arrays.asList("zh-TW")) == INSTALLED);
    check(SpeechModelPolicy.canDownload(DOWNLOADABLE, 33, true, true));
    check(SpeechModelPolicy.canDownload(UNKNOWN, 34, true, true));
    check(!SpeechModelPolicy.canDownload(DOWNLOADABLE, 32, true, true));
    check(!SpeechModelPolicy.canDownload(DOWNLOADABLE, 33, false, true));
    check(!SpeechModelPolicy.canDownload(DOWNLOADABLE, 33, true, false));
    for (SpeechModelPolicy.State state : Arrays.asList(INSTALLED, REQUESTED, DOWNLOADING, PENDING, UNSUPPORTED, CHECKING))
      check(!SpeechModelPolicy.canDownload(state, 34, true, true));
    for (SpeechModelPolicy.State state : Arrays.asList(INSTALLED, MANUAL, UNKNOWN)) check(SpeechModelPolicy.mayTryListening(state));
    for (SpeechModelPolicy.State state : Arrays.asList(DOWNLOADABLE, PENDING, UNSUPPORTED, PERMISSION, NO_SERVICE, OLD_ANDROID, ERROR, REQUESTED, DOWNLOADING))
      check(!SpeechModelPolicy.mayTryListening(state));
    System.out.println("Speech model policy checks passed: " + checks);
  }
}
