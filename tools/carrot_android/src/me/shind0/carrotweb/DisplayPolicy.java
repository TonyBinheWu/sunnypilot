package me.shind0.carrotweb;

public final class DisplayPolicy {
  private DisplayPolicy() {}
  public static final int[] TEXT_SCALES = {80,90,100,110,125,150,175,200};
  public static int normalize(int value) {
    for (int allowed : TEXT_SCALES) if (value == allowed) return value;
    return 100;
  }
}
