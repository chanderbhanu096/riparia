"""Specimen geometry for the three lookalike growths, drawn once, styled per direction.

The three shapes stay geometrically IDENTICAL across every design direction, so a
viewer comparing directions is comparing design and not redrawn illustrations.
Only stroke, fill and effects change.

Why illustrate at all: in 1843 Anna Atkins published "Photographs of British Algae:
Cyanotype Impressions" -- the first book illustrated with photographs -- explicitly
as a visual companion to Harvey's unillustrated 1841 "Manual of British Algae",
because written descriptions of algae were not enough to identify them by. That is
this screen's exact problem, and the answer has been known for 183 years: show the
specimen, do not describe it.

Shapes are drawn from the diagnostic features in field_protocol.py:
  filament  long unbranched-to-sparsely-branched strands streaming from a holdfast
  cyano     surface scum: coalescing irregular colonies, not filaments at all
  fungus    dense shaggy tufts anchored to the bed, all streaming with the flow
"""

# (path, stroke-width) -- long flowing strands, "like wet hair"
FILAMENT = [
    ("M18 98 C 25 72 20 50 33 26", 3.0),
    ("M33 26 C 38 15 45 10 52 5", 2.0),
    ("M28 52 C 40 43 50 39 62 31", 1.7),
    ("M24 70 C 37 63 47 60 58 54", 1.5),
    ("M40 98 C 44 72 43 48 54 24", 2.6),
    ("M54 24 C 59 14 65 9 73 4", 1.8),
    ("M47 60 C 58 53 67 50 78 44", 1.4),
    ("M62 98 C 64 74 66 52 76 30", 2.2),
    ("M70 66 C 79 60 85 57 93 52", 1.3),
    ("M84 98 C 84 78 86 60 92 44", 1.7),
    ("M8 98 C 12 80 11 64 16 48", 1.5),
]

# Surface scum: a coalescing film plus discrete colonies. Deliberately NOT filaments
# -- the visual point is that this one is a different KIND of thing.
CYANO_FILM = ("M12 34c6-9 19-11 27-5s18 2 25-3 19-1 22 8-6 16-15 15-13 5-22 6"
              "-17-4-25-3-12-9-12-18z")
CYANO_BLOBS = [
    ("ellipse", 30, 63, 15, 10), ("ellipse", 55, 70, 19, 11),
    ("ellipse", 78, 58, 11, 8), ("ellipse", 68, 85, 13, 7),
    ("ellipse", 32, 86, 9, 5.5),
]
CYANO_SPECKS = [(16, 55, 3.4), (88, 76, 2.8), (46, 47, 2.4),
                (22, 20, 2.2), (84, 26, 2.0), (60, 16, 1.7)]

# Shaggy tufts on a substrate line, all leaning downstream
FUNGUS = [
    ("M0 88h100", 3.4),
    ("M10 88c2-12 10-16 22-18", 2.4),
    ("M18 88c1-15 11-21 24-24", 2.0),
    ("M27 88c0-11 9-17 20-19", 1.7),
    ("M36 88c-1-18 12-25 27-28", 2.2),
    ("M45 88c0-12 10-18 22-21", 1.6),
    ("M54 88c-1-16 12-22 26-25", 2.0),
    ("M63 88c0-10 9-15 19-17", 1.5),
    ("M72 88c-1-14 11-19 24-22", 1.8),
    ("M82 88c0-9 8-13 17-15", 1.4),
    ("M5 88c1-8 6-11 13-13", 1.5),
]


def draw(kind, size, ink, *, bg="none", opacity=0.95, weight=1.0, filt=""):
    """One specimen as an inline <svg>. `filt` is an optional filter= attribute value."""
    f = f' filter="{filt}"' if filt else ""
    rect = f'<rect width="100" height="100" fill="{bg}"></rect>' if bg != "none" else ""
    if kind == "cyano":
        body = [f'<path d="{CYANO_FILM}"></path>']
        body += [f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"></ellipse>'
                 for _, x, y, rx, ry in CYANO_BLOBS]
        body += [f'<circle cx="{x}" cy="{y}" r="{r}"></circle>'
                 for x, y, r in CYANO_SPECKS]
        inner = (f'<g fill="{ink}" opacity="{opacity}"{f}>' + "".join(body) + "</g>")
    else:
        paths = FILAMENT if kind == "filament" else FUNGUS
        body = "".join(
            f'<path d="{d}" stroke-width="{round(w * weight, 2)}"></path>'
            for d, w in paths)
        inner = (f'<g stroke="{ink}" fill="none" stroke-linecap="round" '
                 f'opacity="{opacity}"{f}>' + body + "</g>")
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" '
            f'style="flex-shrink: 0; display: block">{rect}{inner}</svg>')
