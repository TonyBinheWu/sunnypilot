"""Home screen geometry shared by the native renderer and desktop preview."""
INK = "#eaf2ed"
MUTED = "#9aada6"
BG = "#111b19"
TEAL = "#b6ead4"


def home_scene(compact, branch, address, translate=lambda s: s, experimental=False):
  w, h = (536, 240) if compact else (920, 540)
  shapes, labels, actions = [], [], {}

  def box(x, y, width, height, color):
    shapes.append((x, y, width, height, color))

  def label(x, y, width, height, value, size, color=INK, bold=False):
    labels.append((x, y, width, height, value, size, color, bold))

  def tile(key, x, y, width, height, title, detail="", primary=False):
    actions[key] = (x, y, width, height)
    color = "#152b22" if primary else INK
    box(x, y, width, height, TEAL if primary else "#263733")
    pad = 13 if compact else 23
    label(x+pad, y+(8 if compact else 17), width-2*pad-15, 32 if compact else 58, translate(title), 23 if compact else 36, color, True)
    if detail:
      label(x+pad, y+height-(24 if compact else 48), width-2*pad, 21 if compact else 34, detail, 14 if compact else 22,
            "#324d40" if primary else "#c0cec7")
    label(x+width-pad-14, y+8, 18, 30, "›", 25, color)

  box(0, 0, w, h, BG)
  pad = 12 if compact else 32
  label(pad, 3 if compact else 22, w*.55, 40 if compact else 66, "carrotpilot", 29 if compact else 49, INK, True)
  label(w-(46 if compact else 91), 7 if compact else 33, 65, 30, "C4" if compact else "C3X", 18 if compact else 25, TEAL, True)
  if compact:
    tile("settings", 12, 48, 252, 73, "Device Settings", branch, True)
    tile("web", 272, 48, 252, 73, "Carrot Web", address)
    tile("remote", 12, 128, 252, 72, "Remote screen", translate("Pair browser"))
    tile("mode", 272, 128, 252, 72, "Driving mode", translate("Experimental mode" if experimental else "Standard mode"))
    label(13, 207, 510, 28, translate("Hold driving mode to change"), 15, MUTED)
  else:
    tile("settings", 32, 104, 415, 210, "Device Settings", branch, True)
    tile("web", 460, 104, 428, 210, "Carrot Web", address)
    tile("remote", 32, 328, 415, 148, "Remote screen", translate("Pair browser"))
    tile("more", 460, 328, 428, 148, "Device services", translate("Setup and driving mode"))

  return w, h, shapes, labels, actions
