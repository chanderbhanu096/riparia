// Decorative landscape, separate from the diagnostic specimens.
export default function RiverScene() {
  return (
    <svg className="river-scene" viewBox="0 0 700 340" fill="none" aria-hidden="true">
      <defs><pattern id="field-grid" width="38" height="38" patternUnits="userSpaceOnUse"><path d="M38 0H0V38" stroke="currentColor" strokeOpacity=".1" /></pattern></defs>
      <rect width="700" height="340" fill="url(#field-grid)" />
      <g stroke="currentColor" strokeWidth="1" opacity=".28">
        <path d="M-50 67C80 140 94-40 237 25S392 25 451-50M-50 82C80 155 97-22 237 43S400 42 467-40M-50 97C80 170 95-4 237 61S402 59 480-20M-50 112C80 185 95 14 237 79S407 77 495-10M-50 127C80 200 95 32 237 97S415 96 512 0" />
        <path d="M400 365C309 270 583 348 572 235S688 214 750 160M386 372C286 259 565 339 555 224S683 193 747 146M369 377C269 240 546 327 538 211S680 177 747 128M352 383C250 224 529 314 520 198S676 158 745 110M335 389C231 210 510 301 502 185S665 138 741 90" />
      </g>
      <path d="M523-30C494 47 322 22 319 97S474 153 410 198 213 177 201 236 331 294 255 370" stroke="currentColor" strokeWidth="58" />
      <path d="M523-30C494 47 322 22 319 97S474 153 410 198 213 177 201 236 331 294 255 370" stroke="#163b32" strokeWidth="1.5" strokeDasharray="4 7" />
      <g stroke="currentColor" strokeWidth="1.5">
        <circle cx="270" cy="174" r="25" /><circle cx="270" cy="174" r="18" /><path d="M270 141v13m0 40v13m-33-33h13m40 0h13M253 151l-37-39h-69" />
        <circle cx="445" cy="259" r="5" /><path d="m450 261 45 23h71" />
        <path d="m599 60 7-23 7 23-7-5-7 5ZM606 66v31M59 274h88m-88-5v10m44-10v10m44-10v10" />
      </g>
      <g fill="currentColor" fontFamily="monospace" fontSize="11" letterSpacing="1.5"><text x="146" y="101">OBSERVE HERE</text><text x="495" y="306">LIFE AROUND WATER</text><text x="602" y="27">N</text><text x="59" y="303">FIELD NOTES / 001</text></g>
      <g stroke="currentColor" strokeWidth="1.4" opacity=".7"><path d="m124 229 3-32m-3 21-13-11m15 3 13-12m-5 34 7-28m-3 12 12-8M523 90l5-34m-3 16-12-10m14 3 13-7" /></g>
    </svg>
  )
}
