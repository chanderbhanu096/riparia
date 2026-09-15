"""Generate every design artboard from one canonical copy block.

Run: python3 build.py

Parity by construction: the copy lives in content.py and the specimen geometry in
specimens.py, so no artboard can quietly disagree with another about what the
product says or what the three growths look like. Design is the only variable.

Accessibility floors enforced here, after a review found them broken in the first
draft (AUDIT.md D-019 -- UX is 15% of the score and is never traded away):
  - no text below 12px anywhere
  - the URGENCY line is never the smallest type on the screen; it was, in all
    three first-draft directions, which inverts the hierarchy exactly where it
    costs most
  - body text at or above 4.5:1 contrast
  - tap targets at or above 44px
  - icons are inline SVG only, never a dingbat glyph
"""

import pathlib
from content import COPY as C
from specimens import draw

OUT = pathlib.Path(__file__).parent

HEAD = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
%s
</helmet>
"""
FOOT = "</x-dc>\n</body>\n</html>\n"


def page(helmet, body):
    return (HEAD % helmet) + body + FOOT


def write(name, html):
    (OUT / name).write_text(html, encoding="utf-8")
    return name


# ---------------------------------------------------------------- CYANOTYPE ---
def cyanotype():
    ink, blue = "#f2f7fd", "#082a52"
    rows = [
        ("I", draw("filament", 70, ink, opacity=0.95, weight=1.4),
         C["opt1"], C["opt1_name"], False),
        ("II", draw("cyano", 70, ink, bg="#04162e", opacity=1.0),
         C["opt2"], C["opt2_name"], True),
        ("III", draw("fungus", 70, ink, opacity=0.95, weight=1.4),
         C["opt3"], C["opt3_name"], False),
    ]
    items = []
    for num, svg, label, latin, sel in rows:
        if sel:
            box = ("border: 1px solid #f4f8fd; background: #eef4fb;")
            n_c, t_c, l_c = "#2f6aa5", "#082a52", "#3d6d9f"
            num = num + " &middot; your answer"
        else:
            box = "border: 1px solid rgba(214,232,250,0.28); background: transparent;"
            n_c, t_c, l_c = "#b6d2ee", "#eaf2fb", "#a6c4e4"
        items.append(f"""
      <div style="display: flex; align-items: center; gap: 15px; padding: 10px 12px;
                  min-height: 44px; box-sizing: border-box; {box}">
        {svg}
        <div>
          <div style="font-family: Archivo, system-ui, sans-serif; font-size: 12px;
                      letter-spacing: 0.16em; text-transform: uppercase; font-weight: 600;
                      color: {n_c}">{num}</div>
          <div style="font-size: 16px; line-height: 21px; color: {t_c}; margin-top: 2px;
                      text-wrap: pretty">{label}</div>
          <div style="font-size: 13.5px; line-height: 18px; font-style: italic;
                      color: {l_c}">{latin}</div>
        </div>
      </div>""")

    helmet = """  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Archivo:wght@400;500;600&display=swap">
  <style>
    body { margin: 0; background: #082a52; color: #f2f7fd;
           font-family: "EB Garamond", Georgia, serif; -webkit-font-smoothing: antialiased; }
    a { color: #b9d4ef; } a:hover { color: #ffffff; }
    .micro { font-family: Archivo, system-ui, sans-serif; font-size: 12px;
             letter-spacing: 0.16em; text-transform: uppercase; font-weight: 600; }
  </style>"""

    body = f"""
<div style="position: relative; width: 390px; height: 844px; overflow: hidden; background: #082a52">
  <svg width="390" height="844" viewBox="0 0 390 844" preserveAspectRatio="none" style="position: absolute; inset: 0">
    <defs>
      <radialGradient id="w1" cx="22%" cy="12%" r="72%">
        <stop offset="0%" stop-color="#17548f" stop-opacity="0.5"></stop>
        <stop offset="100%" stop-color="#082a52" stop-opacity="0"></stop>
      </radialGradient>
      <radialGradient id="w2" cx="88%" cy="66%" r="64%">
        <stop offset="0%" stop-color="#082a52" stop-opacity="0"></stop>
        <stop offset="100%" stop-color="#04162e" stop-opacity="0.92"></stop>
      </radialGradient>
      <radialGradient id="w3" cx="46%" cy="103%" r="56%">
        <stop offset="0%" stop-color="#1b5c97" stop-opacity="0.38"></stop>
        <stop offset="100%" stop-color="#082a52" stop-opacity="0"></stop>
      </radialGradient>
      <filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7"></feTurbulence><feColorMatrix type="saturate" values="0"></feColorMatrix></filter>
    </defs>
    <rect width="390" height="844" fill="#082a52"></rect>
    <rect width="390" height="844" fill="url(#w1)"></rect>
    <rect width="390" height="844" fill="url(#w3)"></rect>
    <rect width="390" height="844" fill="url(#w2)"></rect>
    <rect width="390" height="844" filter="url(#grain)" opacity="0.05"></rect>
  </svg>

  <div style="position: relative; display: flex; flex-direction: column; height: 844px;
              box-sizing: border-box; padding: 18px 20px 0">

    <div style="display: flex; align-items: baseline; justify-content: space-between;
                border-bottom: 1px solid rgba(214,232,250,0.36); padding-bottom: 8px">
      <div style="font-size: 20px; letter-spacing: 0.2em; color: #f4f8fd">{C["brand"]}</div>
      <div class="micro" style="color: #b6d2ee">Pl. III &middot; green growth</div>
    </div>

    <div style="padding-top: 10px; font-size: 13.5px; font-style: italic; color: #a6c4e4">{C["site"]}</div>

    <div style="padding-top: 12px">
      <div class="micro" style="color: #ffc08f">{C["prompt_kicker"]}</div>
      <div style="font-size: 25px; line-height: 30px; color: #f6f9fd; margin-top: 5px;
                  text-wrap: pretty">{C["question"]}</div>
      <div style="font-size: 14.5px; line-height: 20px; font-style: italic; color: #b3cde8;
                  margin-top: 4px; text-wrap: pretty">{C["question_sub"]}</div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 9px; padding-top: 14px">{"".join(items)}
    </div>

    <div style="margin-top: 18px; border-top: 1px solid rgba(214,232,250,0.36); padding-top: 13px">
      <div style="font-size: 20px; line-height: 25px; color: #ffc08f; text-wrap: pretty">{C["reading_label"]}</div>
      <div style="font-size: 14.5px; line-height: 20px; color: #dce8f5; margin-top: 4px;
                  text-wrap: pretty">{C["reading"]}</div>
    </div>

    <div style="margin-top: 14px; display: flex; gap: 10px; background: rgba(255,203,155,0.14);
                border: 1px solid rgba(255,193,140,0.55); padding: 10px 12px">
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="#ffc08f" stroke-width="1.7"
           stroke-linecap="round" style="flex-shrink: 0; margin-top: 2px">
        <path d="M12 9v4.5M12 17h.01"></path>
        <path d="M10.3 3.9 2.4 17.6A1.9 1.9 0 0 0 4 20.5h16a1.9 1.9 0 0 0 1.6-2.9L13.7 3.9a1.9 1.9 0 0 0-3.4 0Z"></path>
      </svg>
      <div style="font-size: 13.5px; line-height: 19px; color: #ffe6d0; text-wrap: pretty">
        <span style="font-weight: 500; color: #fff4e9">{C["precaution_label"]}.</span> {C["precaution"]}
      </div>
    </div>

    <div style="margin-top: auto; padding: 12px 0 16px; border-top: 1px solid rgba(214,232,250,0.22);
                display: flex; align-items: baseline; justify-content: space-between; gap: 14px">
      <div style="font-size: 13px; font-style: italic; color: #a6c4e4; text-wrap: pretty">{C["footer"]}</div>
      <div class="micro" style="color: #6f96c4; flex-shrink: 0">No. 0412</div>
    </div>
  </div>
</div>
"""
    return write("Main.dc.html", page(helmet, body))


# ----------------------------------------------------------------- NOCTURNE ---
def nocturne():
    """Dark, luminous, instrument-like. Justified by field reality: people report
    urban streams at dawn and dusk on a phone at full brightness, and a white
    screen at 6am is hostile."""
    mint, amber = "#57dfae", "#ff8a5c"
    rows = [
        ("01", draw("filament", 66, "#8fdc72", opacity=0.95, weight=1.3, filt="url(#glow)"),
         C["opt1"], C["opt1_name"], False),
        ("02", draw("cyano", 66, mint, opacity=1.0, filt="url(#glow)"),
         C["opt2"], C["opt2_name"], True),
        ("03", draw("fungus", 66, "#cfd6cd", opacity=0.95, weight=1.3, filt="url(#glow)"),
         C["opt3"], C["opt3_name"], False),
    ]
    items = []
    for num, svg, label, latin, sel in rows:
        if sel:
            box = f"border: 1px solid {mint}; background: rgba(87,223,174,0.1);"
            n_c, t_c, l_c = mint, "#eafbf5", "#96c9bb"
        else:
            box = "border: 1px solid rgba(143,217,232,0.24); background: rgba(10,30,36,0.55);"
            n_c, t_c, l_c = "#7fb6c4", "#dceef2", "#8fabb4"
        items.append(f"""
      <div style="display: flex; align-items: center; gap: 14px; padding: 7px 11px;
                  min-height: 44px; box-sizing: border-box; border-radius: 2px; {box}">
        {svg}
        <div>
          <div class="mono" style="font-size: 12px; letter-spacing: 0.14em; color: {n_c}">{num}</div>
          <div style="font-size: 15.5px; line-height: 20px; color: {t_c}; margin-top: 2px;
                      text-wrap: pretty">{label}</div>
          <div style="font-size: 13px; line-height: 17px; color: {l_c}">{latin}</div>
        </div>
      </div>""")

    helmet = """  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
  <style>
    body { margin: 0; background: #071316; color: #dceef2;
           font-family: "Space Grotesk", system-ui, sans-serif; -webkit-font-smoothing: antialiased; }
    a { color: #57dfae; } a:hover { color: #8ff2cc; }
    .mono { font-family: "JetBrains Mono", ui-monospace, monospace; text-transform: uppercase;
            font-weight: 500; }
  </style>"""

    body = f"""
<div style="position: relative; width: 390px; height: 844px; overflow: hidden; background: #071316">
  <svg width="390" height="844" viewBox="0 0 390 844" preserveAspectRatio="none" style="position: absolute; inset: 0">
    <defs>
      <radialGradient id="deep" cx="50%" cy="0%" r="95%">
        <stop offset="0%" stop-color="#11363f" stop-opacity="1"></stop>
        <stop offset="100%" stop-color="#050f12" stop-opacity="1"></stop>
      </radialGradient>
      <filter id="caustic" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="7"></feGaussianBlur>
      </filter>
      <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="1.6" result="b"></feGaussianBlur>
        <feMerge><feMergeNode in="b"></feMergeNode><feMergeNode in="SourceGraphic"></feMergeNode></feMerge>
      </filter>
    </defs>
    <rect width="390" height="844" fill="url(#deep)"></rect>
    <g filter="url(#caustic)" fill="none" stroke="#5fd8c6" stroke-width="3" opacity="0.34">
      <path d="M-30 90 C 60 40 120 150 210 96 S 350 30 430 86"></path>
      <path d="M-30 150 C 70 106 130 208 220 156 S 360 96 430 148"></path>
      <path d="M-30 690 C 70 640 140 748 230 694 S 360 632 430 686"></path>
      <path d="M-30 760 C 80 712 140 812 232 762 S 356 704 430 756"></path>
    </g>
    <g filter="url(#caustic)" fill="none" stroke="#9fe8ff" stroke-width="1.8" opacity="0.24">
      <path d="M-30 120 C 80 70 130 176 226 124 S 356 62 430 116"></path>
      <path d="M-30 726 C 74 676 142 782 232 728 S 358 668 430 722"></path>
    </g>
  </svg>

  <div style="position: relative; display: flex; flex-direction: column; height: 844px;
              box-sizing: border-box; padding: 18px 20px 0">

    <div style="display: flex; align-items: center; justify-content: space-between;
                border-bottom: 1px solid rgba(143,217,232,0.24); padding-bottom: 10px">
      <span class="mono" style="font-size: 15px; letter-spacing: 0.22em; color: #eafbf5;
                                font-weight: 500">{C["brand"]}</span>
      <span class="mono" style="font-size: 12px; letter-spacing: 0.12em; color: {mint}">field check</span>
    </div>

    <div style="padding-top: 10px; font-size: 13.5px; color: #8fabb4">{C["site"]}</div>

    <div style="padding-top: 12px">
      <div class="mono" style="font-size: 12px; letter-spacing: 0.12em; color: {amber}">{C["prompt_kicker"]}</div>
      <div style="font-size: 26px; line-height: 32px; font-weight: 600; letter-spacing: -0.02em;
                  color: #f2fbfd; margin-top: 6px; text-wrap: pretty">{C["question"]}</div>
      <div style="font-size: 14.5px; line-height: 20px; color: #9dbcc4; margin-top: 5px;
                  text-wrap: pretty">{C["question_sub"]}</div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 7px; padding-top: 13px">{"".join(items)}
    </div>

    <div style="margin-top: 13px; border-left: 2px solid {amber}; padding: 2px 0 2px 12px">
      <div style="font-size: 19px; line-height: 24px; font-weight: 600; color: {amber};
                  text-wrap: pretty">{C["reading_label"]}</div>
      <div style="font-size: 14.5px; line-height: 20px; color: #cfe4e9; margin-top: 4px;
                  text-wrap: pretty">{C["reading"]}</div>
    </div>

    <div style="margin-top: 12px; display: flex; gap: 10px; background: rgba(255,138,92,0.1);
                border: 1px solid rgba(255,138,92,0.45); border-radius: 2px; padding: 10px 12px">
      <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="{amber}" stroke-width="1.8"
           stroke-linecap="round" style="flex-shrink: 0; margin-top: 1px">
        <path d="M12 9v4.5M12 17h.01"></path>
        <path d="M10.3 3.9 2.4 17.6A1.9 1.9 0 0 0 4 20.5h16a1.9 1.9 0 0 0 1.6-2.9L13.7 3.9a1.9 1.9 0 0 0-3.4 0Z"></path>
      </svg>
      <div style="font-size: 13.5px; line-height: 19px; color: #ffddcb; text-wrap: pretty">
        <span style="font-weight: 600; color: #fff0e7">{C["precaution_label"]}.</span> {C["precaution"]}
      </div>
    </div>

    <div style="margin-top: auto; padding: 10px 0 14px; border-top: 1px solid rgba(143,217,232,0.18);
                display: flex; align-items: center; gap: 8px">
      <svg width="8" height="8" viewBox="0 0 8 8" style="flex-shrink: 0"><circle cx="4" cy="4" r="4" fill="{mint}"></circle></svg>
      <span style="font-size: 12.5px; line-height: 17px; color: #9dbcc4; text-wrap: pretty">{C["footer"]}</span>
    </div>
  </div>
</div>
"""
    return write("Nocturne.dc.html", page(helmet, body))


# --------------------------------------------------------------- BROADSHEET ---
def broadsheet():
    """A field observation sheet. Newsprint ground, one display face, one red.

    Colour carries the diagnosis. The three options name colours -- "green strands",
    "blue-green, like spilled paint", "grey or dirty-white slime" -- so drawing them
    all in one ink threw away the first thing a person matches. Each specimen is now
    drawn in its own colour, and shape still differs (strands / blobs / tufts) so the
    distinction survives colour blindness and greyscale print.

    Red is reserved for the precaution. A routine report must not look like an
    emergency, and a citizen report is not an official warning -- hence "Field
    observation", not "Water notice".
    """
    ink, red, cream, rule = "#15120e", "#b02d18", "#f3f0e7", "#cdc5b4"
    # diagnostic colours, legible on cream and distinct in greyscale by value
    algae, cyano, fungus = "#3f6b24", "#137a72", "#7e7d74"
    rows = [
        ("I", draw("filament", 58, algae, opacity=1.0, weight=1.4),
         C["opt1"], C["opt1_name"], False),
        ("II", draw("cyano", 58, cyano, opacity=1.0),
         C["opt2"], C["opt2_name"], True),
        ("III", draw("fungus", 58, fungus, opacity=1.0, weight=1.4),
         C["opt3"], C["opt3_name"], False),
    ]
    check = ('<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="%s" '
             'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" '
             'style="flex-shrink: 0"><path d="M20 6 9 17l-5-5"></path></svg>') % ink
    items = []
    for num, svg, label, latin, sel in rows:
        if sel:
            box = f"background: #ffffff; border: 2px solid {ink}; padding: 7px 10px;"
            tag = (f'<span style="display: inline-flex; align-items: center; gap: 5px; '
                   f'color: {ink}; font-weight: 700">{check}Your answer</span>')
        else:
            box = f"background: transparent; border: 1px solid {rule}; padding: 8px 11px;"
            tag = f'<span style="color: #7a7061">{num}</span>'
        items.append(f"""
      <div style="display: flex; align-items: center; gap: 12px; min-height: 44px;
                  box-sizing: border-box; {box}">
        {svg}
        <div>
          <div style="font-family: Archivo, system-ui, sans-serif; font-size: 12px;
                      letter-spacing: 0.14em; text-transform: uppercase; font-weight: 700">{tag}</div>
          <div style="font-family: Archivo, system-ui, sans-serif; font-size: 15px;
                      line-height: 20px; font-weight: 500; color: {ink}; margin-top: 2px;
                      text-wrap: pretty">{label}</div>
          <div style="font-family: Archivo, system-ui, sans-serif; font-size: 12.5px;
                      line-height: 16px; color: #6d6354">{latin}</div>
        </div>
      </div>""")

    helmet = """  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400;0,6..96,700&family=Archivo:wght@400;500;600;700&display=swap">
  <style>
    body { margin: 0; background: #f3f0e7; color: #15120e;
           font-family: Archivo, system-ui, sans-serif; -webkit-font-smoothing: antialiased; }
    a { color: #b02d18; } a:hover { color: #8a2212; }
    .disp { font-family: "Bodoni Moda", Georgia, serif; }
    .kick { font-size: 12px; letter-spacing: 0.18em; text-transform: uppercase; font-weight: 700; }
  </style>"""

    body = f"""
<div style="width: 390px; height: 844px; overflow: hidden; background: {cream};
            display: flex; flex-direction: column; box-sizing: border-box; padding: 13px 20px 0">

  <div style="border-bottom: 3px solid {ink}; padding-bottom: 7px; display: flex;
              align-items: baseline; justify-content: space-between; gap: 12px">
    <span class="disp" style="font-size: 25px; font-weight: 700; letter-spacing: 0.02em">{C["brand"]}</span>
    <span class="kick" style="color: #5c5347">Field observation</span>
  </div>
  <div style="border-bottom: 1px solid {rule}; padding: 5px 0 6px; font-size: 12.5px; color: #4a4137">{C["site"]}</div>

  <div style="padding-top: 13px">
    <div class="kick" style="color: {red}">{C["prompt_kicker"]}</div>
    <div class="disp" style="font-size: 28px; line-height: 30px; font-weight: 700;
                             margin-top: 5px; text-wrap: pretty">{C["question"]}</div>
    <div style="font-size: 14px; line-height: 19px; color: #4a4137; margin-top: 6px;
                text-wrap: pretty">{C["question_sub"]}</div>
  </div>

  <div style="display: flex; flex-direction: column; gap: 6px; padding-top: 11px">{"".join(items)}
  </div>

  <div style="margin-top: 11px; border-top: 3px solid {ink}; padding-top: 8px">
    <div style="display: flex; align-items: baseline; justify-content: space-between; gap: 10px">
      <div class="disp" style="font-size: 19px; line-height: 23px; font-weight: 700;
                               text-wrap: pretty">{C["reading_label"]}</div>
      <span class="kick" style="font-size: 11.5px; color: #5c5347; flex-shrink: 0;
                                white-space: nowrap">Awaiting review</span>
    </div>
    <div style="font-size: 14.5px; line-height: 20px; color: #2b241c; margin-top: 4px;
                text-wrap: pretty">{C["reading"]}</div>
  </div>

  <div style="margin-top: 9px; border: 2px solid {red}; background: #fbf1ee; padding: 11px 13px;
              display: flex; gap: 10px">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{red}" stroke-width="1.9"
         stroke-linecap="round" style="flex-shrink: 0; margin-top: 1px">
      <path d="M12 9v4.5M12 17h.01"></path>
      <path d="M10.3 3.9 2.4 17.6A1.9 1.9 0 0 0 4 20.5h16a1.9 1.9 0 0 0 1.6-2.9L13.7 3.9a1.9 1.9 0 0 0-3.4 0Z"></path>
    </svg>
    <div style="font-size: 15px; line-height: 21px; color: #45201a; text-wrap: pretty">
      <span style="font-weight: 700; color: {red}">{C["precaution_label"]}.</span> {C["precaution"]}
    </div>
  </div>

  <div style="margin-top: auto; border-top: 1px solid {rule}; padding: 8px 0 12px">
    <div style="font-size: 12.5px; line-height: 17px; color: #4a4137; text-wrap: pretty">{C["footer"]}</div>
  </div>
</div>
"""
    return write("Broadsheet.dc.html", page(helmet, body))


# ------------------------------------------------------------------ CURRENT ---
def current():
    """The live UI as deployed, reproduced from frontend/src/index.css and the
    real components: stream-50/100/300/600/700/900, system-ui, Tailwind's 8px
    rounding, amber-50/300/900 and red-50/300/900 for the two alerts.

    Shown with the SAME canonical copy as the directions so the comparison is
    fair. The real screen scrolls; this is one 844px frame of it.
    """
    s6, s7, s9 = "#2f6f76", "#245358", "#12292c"
    s1, s3 = "#f0f7f7", "#8cbcc0"
    rows = [(C["opt1"], False), (C["opt2"], True), (C["opt3"], False)]
    items = []
    for label, sel in rows:
        bg = s1 if sel else "#ffffff"
        fw = "500" if sel else "400"
        items.append(f"""
        <div style="border: 1px solid {s6}; border-radius: 8px; padding: 10px 12px;
                    background: {bg}; font-size: 14px; line-height: 20px; color: {s7};
                    font-weight: {fw}; min-height: 44px; box-sizing: border-box;
                    display: flex; align-items: center">{label}</div>""")

    helmet = """  <style>
    body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
           background: #ffffff; color: #12292c; -webkit-font-smoothing: antialiased; }
    a { color: #2f6f76; } a:hover { color: #245358; }
  </style>"""

    body = f"""
<div style="width: 390px; height: 844px; overflow: hidden; display: flex; flex-direction: column;
            background: #ffffff">

  <div style="background: {s1}; border-bottom: 1px solid {s3}; padding: 14px 16px">
    <div style="display: flex; align-items: baseline; justify-content: space-between; gap: 14px">
      <div>
        <div style="font-size: 20px; line-height: 26px; font-weight: 700; color: {s9}">{C["brand"]}</div>
        <div style="font-size: 13px; line-height: 18px; color: {s7}">AI asks. The person answers. A reviewer decides.</div>
      </div>
      <div style="display: flex; gap: 4px; border: 1px solid {s3}; border-radius: 8px;
                  background: #fff; padding: 4px">
        <div style="border-radius: 6px; background: {s6}; color: #fff; padding: 7px 11px;
                    font-size: 13px; font-weight: 500">Report</div>
        <div style="border-radius: 6px; color: {s7}; padding: 7px 11px; font-size: 13px;
                    font-weight: 500">Review</div>
      </div>
    </div>
  </div>

  <div style="padding: 16px; display: flex; flex-direction: column; gap: 14px">

    <div style="font-size: 13px; line-height: 18px; color: {s7}">{C["site"]}</div>

    <div>
      <div style="font-size: 18px; line-height: 24px; font-weight: 600">{C["question"]}</div>
      <div style="font-size: 14px; line-height: 20px; color: {s7}; margin-top: 4px;
                  text-wrap: pretty">{C["question_sub"]}</div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 8px">{"".join(items)}
    </div>

    <div style="border: 1px solid #fca5a5; background: #fef2f2; border-radius: 8px; padding: 12px">
      <div style="font-size: 14px; line-height: 20px; font-weight: 600; color: #7f1d1d">{C["reading_label"]}</div>
      <div style="font-size: 14px; line-height: 20px; color: #7f1d1d; margin-top: 3px;
                  text-wrap: pretty">{C["reading"]}</div>
    </div>

    <div style="border: 1px solid #fcd34d; background: #fffbeb; border-radius: 8px; padding: 12px;
                font-size: 13.5px; line-height: 19px; color: #78350f; text-wrap: pretty">
      <span style="font-weight: 700">{C["precaution_label"]}: </span>{C["precaution"]}
    </div>

    <div style="font-size: 13px; line-height: 18px; color: {s7}; text-wrap: pretty">{C["footer"]}</div>
  </div>
</div>
"""
    return write("Current.dc.html", page(helmet, body))


if __name__ == "__main__":
    for fn in (current, cyanotype, nocturne, broadsheet):
        print("wrote", fn())
