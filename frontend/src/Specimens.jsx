// Schematic drawings of what a person is looking at, shown beside the words.
//
// Why these exist (AUDIT.md D-026): the differential questions ask someone to tell
// apart things that look alike, and words alone are a poor way to do that. Anna
// Atkins published the first photographically illustrated book in 1843 -- cyanotypes
// of British algae -- precisely because Harvey's written manual could not be used to
// identify them. Same problem, same answer: show the specimen.
//
// Two rules these must keep:
//   1. COLOUR CARRIES THE DIAGNOSIS. The options name colours -- "green strands",
//      "blue-green like spilled paint", "grey or dirty-white slime" -- so each
//      drawing is in its own colour. An earlier draft drew them all in one ink and
//      threw away the first thing a person matches (AUDIT.md D-027).
//   2. SHAPE CARRIES IT TOO. Strands vs colonies vs tufts, shattered plates vs a
//      continuous sheet, loose bubbles vs a packed mass -- so the distinction
//      survives colour blindness, greyscale printing and a dim screen.
//
// These are schematic AIDS, not identification plates. They have not been validated
// against real field examples, and the UI says so.

const STROKE = { fill: 'none', strokeLinecap: 'round', strokeLinejoin: 'round' }

// long flowing strands, "like wet hair"
const FILAMENT = [['M18 98 C 25 72 20 50 33 26', 3], ['M33 26 C 38 15 45 10 52 5', 2],
  ['M28 52 C 40 43 50 39 62 31', 1.7], ['M24 70 C 37 63 47 60 58 54', 1.5],
  ['M40 98 C 44 72 43 48 54 24', 2.6], ['M54 24 C 59 14 65 9 73 4', 1.8],
  ['M47 60 C 58 53 67 50 78 44', 1.4], ['M62 98 C 64 74 66 52 76 30', 2.2],
  ['M70 66 C 79 60 85 57 93 52', 1.3], ['M84 98 C 84 78 86 60 92 44', 1.7],
  ['M8 98 C 12 80 11 64 16 48', 1.5]]

// dense shaggy tufts on the bed, all leaning downstream
const TUFTS = [['M0 88h100', 3.4], ['M10 88c2-12 10-16 22-18', 2.4],
  ['M18 88c1-15 11-21 24-24', 2], ['M27 88c0-11 9-17 20-19', 1.7],
  ['M36 88c-1-18 12-25 27-28', 2.2], ['M45 88c0-12 10-18 22-21', 1.6],
  ['M54 88c-1-16 12-22 26-25', 2], ['M63 88c0-10 9-15 19-17', 1.5],
  ['M72 88c-1-14 11-19 24-22', 1.8], ['M82 88c0-9 8-13 17-15', 1.4],
  ['M5 88c1-8 6-11 13-13', 1.5]]

const Strokes = ({ paths, color, weight = 1 }) => (
  <g stroke={color} {...STROKE}>
    {paths.map(([d, w], i) => <path key={i} d={d} strokeWidth={w * weight} />)}
  </g>
)

// Surface scum: coalescing colonies, deliberately NOT filaments. The visual point
// is that this one is a different KIND of thing from the other two.
const Colonies = ({ color }) => (
  <g fill={color}>
    <path d="M12 34c6-9 19-11 27-5s18 2 25-3 19-1 22 8-6 16-15 15-13 5-22 6-17-4-25-3-12-9-12-18z" />
    <ellipse cx="30" cy="63" rx="15" ry="10" /><ellipse cx="55" cy="70" rx="19" ry="11" />
    <ellipse cx="78" cy="58" rx="11" ry="8" /><ellipse cx="68" cy="85" rx="13" ry="7" />
    <ellipse cx="32" cy="86" rx="9" ry="5.5" />
    <circle cx="16" cy="55" r="3.4" /><circle cx="88" cy="76" r="2.8" />
    <circle cx="46" cy="47" r="2.4" /><circle cx="22" cy="20" r="2.2" />
    <circle cx="84" cy="26" r="2" /><circle cx="60" cy="16" r="1.7" />
  </g>
)

// Iron-oxidising biofilm: brittle, so it breaks into angular plates with clear
// gaps between them and does not rejoin. Rust-coloured, as iron bacteria are.
const Shattered = ({ color }) => (
  <g fill={color} opacity="0.9">
    <path d="M10 26 38 18 46 40 20 48z" /><path d="M52 14 80 22 74 44 50 38z" />
    <path d="M14 58 40 54 44 78 18 82z" /><path d="M50 50 78 52 84 74 56 78z" />
    <path d="M86 30 96 44 88 50 82 36z" /><path d="M6 36 14 50 8 54 2 42z" />
  </g>
)

// Petroleum: cohesive and elastic, so it swirls back into one continuous sheet.
const Sheet = ({ color }) => (
  <g>
    <path d="M6 30c14-14 36-16 52-6s30 10 36 2v46c-10 12-30 10-44 2s-32-6-44 6z"
          fill={color} opacity="0.5" />
    <g stroke={color} strokeWidth="1.8" {...STROKE} opacity="0.95">
      <path d="M16 44c10-8 24-8 34-2s22 6 30 0" />
      <path d="M14 58c12-7 24-5 34 1s24 5 34-2" />
      <path d="M22 70c9-5 19-3 27 2s18 4 26-1" />
    </g>
  </g>
)

// Natural foam from decomposing plant matter: loose, uneven, gaps between bubbles,
// tea-coloured from dissolved organic carbon.
const LooseBubbles = ({ color }) => (
  <g stroke={color} strokeWidth="2.2" {...STROKE}>
    <circle cx="24" cy="38" r="11" /><circle cx="50" cy="30" r="7" />
    <circle cx="70" cy="42" r="13" /><circle cx="36" cy="64" r="9" />
    <circle cx="60" cy="70" r="6" /><circle cx="86" cy="64" r="7" />
    <circle cx="12" cy="62" r="5" /><circle cx="46" cy="47" r="4" />
  </g>
)

// Surfactant foam: dense, packed, uniform, persistent -- a solid mass rather than
// separate bubbles.
const PackedFoam = ({ color }) => (
  <g stroke={color} strokeWidth="2" {...STROKE}>
    <path d="M2 74h96" strokeWidth="2.6" />
    {[[14, 30], [30, 26], [46, 28], [62, 25], [78, 29], [90, 34],
      [10, 48], [26, 46], [42, 47], [58, 45], [74, 48], [88, 52],
      [18, 62], [34, 62], [50, 61], [66, 63], [82, 63]].map(([x, y], i) => (
      <circle key={i} cx={x} cy={y} r={i % 3 === 0 ? 9 : 7.5} />
    ))}
  </g>
)

// differential id -> option key -> { draw, color, note }
const PLATES = {
  growth_type: {
    filamentous:   { el: c => <Strokes paths={FILAMENT} color={c} weight={1.35} />, color: 'var(--color-algae)' },
    cyanobacteria: { el: c => <Colonies color={c} />,                               color: 'var(--color-cyano)' },
    sewage_fungus: { el: c => <Strokes paths={TUFTS} color={c} weight={1.35} />,    color: 'var(--color-fungus)' },
  },
  sheen_shatter_test: {
    shatters: { el: c => <Shattered color={c} />, color: '#9a6b2f' },
    reforms:  { el: c => <Sheet color={c} />,     color: '#434a56' },
  },
  foam_character: {
    natural:    { el: c => <LooseBubbles color={c} />, color: '#7a5f3a' },
    surfactant: { el: c => <PackedFoam color={c} />,   color: '#5a6068' },
  },
}

/**
 * A schematic drawing for one differential option, or null when none exists.
 * Returning null rather than a placeholder is deliberate: an empty box teaches a
 * person nothing and a wrong drawing teaches them something false.
 */
export default function Specimen({ differential, option, size = 58, alt }) {
  const plate = PLATES[differential]?.[option]
  if (!plate) return null
  return (
    <svg width={size} height={size} viewBox="0 0 100 100" role="img"
         aria-label={alt || 'Schematic drawing of this option'}
         style={{ flexShrink: 0, display: 'block' }}>
      {plate.el(plate.color)}
    </svg>
  )
}

// ---------------------------------------------------------------------------
// Indicator marks: one drawn mark per thing a person can notice, for the picker
// on the first screen.
//
// Why they exist: the capture form was ten identical text rectangles -- the
// dullest surface in the app and the first one anyone sees, while the drawings
// that make this product what it is only appeared AFTER submitting. Moving
// illustration to the front is the same argument as D-026, applied one screen
// earlier.
//
// All marks are drawn in ink, deliberately. Colour in this app means DIAGNOSIS
// (AUDIT.md D-027), and at this point nothing has been diagnosed -- the person is
// only saying what they can see. Colour arrives at the differential, where it
// carries meaning.
// ---------------------------------------------------------------------------

const M = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.7,
            strokeLinecap: 'round', strokeLinejoin: 'round' }

const MARKS = {
  // an iridescent film lying on the surface
  oily_sheen: <g {...M}><path d="M4 30c6-7 14-8 20-4s14 3 20-3" />
    <path d="M9 21c5-5 12-6 17-3s11 2 15-2" /><path d="M14 13c4-3 9-4 13-2" />
    <path d="M6 37c7-5 15-5 22-1s13 2 18-3" /></g>,
  // bubbles gathered on the water line
  foam: <g {...M}><circle cx="15" cy="20" r="6" /><circle cx="26" cy="15" r="4.5" />
    <circle cx="33" cy="22" r="7" /><circle cx="21" cy="28" r="4" />
    <path d="M4 36h40" /></g>,
  // colonies on the surface
  green_growth: <g {...M}><ellipse cx="17" cy="19" rx="8" ry="5.5" />
    <ellipse cx="30" cy="25" rx="9" ry="6" /><ellipse cx="20" cy="31" rx="6" ry="4" />
    <circle cx="35" cy="15" r="2" /><circle cx="10" cy="28" r="1.7" /></g>,
  // an outfall running into the water
  pipe_discharge: <g {...M}><path d="M6 14h14v9H6z" /><path d="M20 19c4 0 6 4 6 8" />
    <path d="M26 27c3 3 8 4 14 4" /><path d="M6 37h36" /><path d="M23 24c2 2 3 4 3 6" /></g>,
  // belly-up
  dead_fish: <g {...M}><path d="M10 24c6-7 17-7 23 0-6 7-17 7-23 0z" />
    <path d="M33 24l7-5v10z" /><path d="M17 21l2 2m0-2l-2 2" /><path d="M4 34h40" /></g>,
  // wipes caught on a branch
  sewage_debris: <g {...M}><path d="M5 15c8 2 14 5 20 11" />
    <path d="M14 19c-1 6 1 11 4 14" /><path d="M24 26c-2 5-1 9 2 12" />
    <path d="M18 33c2 2 5 2 7 0" /><path d="M31 34h10" /></g>,
  // odour rising
  smell_sewage: <g {...M}><path d="M6 34h36" />
    <path d="M14 27c3-3-3-6 0-9s-3-6 0-9" /><path d="M24 27c3-3-3-6 0-9s-3-6 0-9" />
    <path d="M34 27c3-3-3-6 0-9" /></g>,
  // odour plus a droplet
  smell_chemical: <g {...M}><path d="M6 34h36" />
    <path d="M15 27c3-3-3-6 0-9s-3-6 0-9" /><path d="M26 27c3-3-3-6 0-9s-3-6 0-9" />
    <path d="M36 20c2.5 3 4 5 4 7a4 4 0 0 1-8 0c0-2 1.5-4 4-7z" /></g>,
  // a bank giving way
  erosion: <g {...M}><path d="M4 16h13c3 0 4 3 4 6v6c0 3 2 5 5 5h18" />
    <path d="M21 22l7-3M23 29l8-2" /><path d="M4 39h40" /><path d="M30 24l4-2" /></g>,
  // a bottle and a can
  litter: <g {...M}><path d="M13 16h6v4c0 2 3 3 3 6v10c0 2-1 3-3 3h-6c-2 0-3-1-3-3V26c0-3 3-4 3-6z" />
    <path d="M29 22h9v14a2 2 0 0 1-2 2h-5a2 2 0 0 1-2-2z" /><path d="M29 22c0-1.5 2-2.5 4.5-2.5S38 20.5 38 22" /></g>,
}

/** A drawn mark for one indicator, or null when none is defined. */
export function IndicatorMark({ indicator, size = 40 }) {
  const mark = MARKS[indicator]
  if (!mark) return null
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" aria-hidden="true"
         style={{ flexShrink: 0, display: 'block' }}>{mark}</svg>
  )
}
