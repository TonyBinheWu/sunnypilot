package me.shind0.carrotweb;

import java.util.List;
import java.util.Locale;

/** Capability evidence is not interchangeable with a completed model installation. */
final class SpeechModelPolicy {
  enum State { OLD_ANDROID, PERMISSION, NO_SERVICE, MANUAL, CHECKING, INSTALLED, DOWNLOADABLE, PENDING, UNSUPPORTED, UNKNOWN, REQUESTED, DOWNLOADING, ERROR }
  static State prerequisite(int sdk, boolean microphone, boolean service) {
    if (sdk < 31) return State.OLD_ANDROID;
    if (!microphone) return State.PERMISSION;
    if (!service) return State.NO_SERVICE;
    return sdk < 33 ? State.MANUAL : State.CHECKING;
  }
  static boolean matches(String raw, String requested) {
    if (raw == null || requested == null) return false;
    String tag = raw.trim().replace('_', '-').toLowerCase(Locale.ROOT);
    String target = requested.replace('_', '-').toLowerCase(Locale.ROOT);
    if (target.equals("zh-tw")) return tag.equals("zh-tw") || tag.equals("zh-hant-tw");
    return tag.equals(target);
  }
  private static boolean contains(List<String> list, String requested) {
    if (list != null) for (String tag : list) if (matches(tag, requested)) return true;
    return false;
  }
  private static boolean genericChinese(List<String> list) {
    if (list != null) for (String tag : list) {
      if (tag != null && (tag.equalsIgnoreCase("zh") || tag.replace('_', '-').equalsIgnoreCase("zh-Hant"))) return true;
    }
    return false;
  }
  static State classify(String requested, List<String> installed, List<String> pending, List<String> downloadable) {
    if (contains(installed, requested)) return State.INSTALLED;
    if (contains(pending, requested)) return State.PENDING;
    if (contains(downloadable, requested)) return State.DOWNLOADABLE;
    if (requested.equalsIgnoreCase("zh-TW") && (genericChinese(installed) || genericChinese(pending) || genericChinese(downloadable))) return State.UNKNOWN;
    if ((installed == null || installed.isEmpty()) && (pending == null || pending.isEmpty()) &&
        (downloadable == null || downloadable.isEmpty())) return State.UNKNOWN;
    return State.UNSUPPORTED;
  }
  static boolean canDownload(State state, int sdk, boolean permission, boolean service) {
    return sdk >= 33 && permission && service && (state == State.DOWNLOADABLE || state == State.UNKNOWN || state == State.ERROR);
  }
  static boolean mayTryListening(State state) { return state == State.INSTALLED || state == State.MANUAL || state == State.UNKNOWN; }
  private SpeechModelPolicy() {}
}
