"""The four candidate marks as inline SVG (200x200 viewBox). fg = line colour, bg = fill behind."""
RED, KRAFT, SLATE, PAPER, NAVY = "#B3362C", "#C9AE86", "#4A6274", "#F5EEE6", "#1C2F3C"


def suitcase(fg, bg):
    return f'''<path d="M80 54 C80 32 120 32 120 54" fill="none" stroke="{fg}" stroke-width="7" stroke-linecap="round"/>
<rect x="74" y="48" width="12" height="10" rx="2" fill="{fg}"/><rect x="114" y="48" width="12" height="10" rx="2" fill="{fg}"/>
<rect x="22" y="58" width="156" height="108" rx="12" fill="{bg}" stroke="{fg}" stroke-width="6"/>
<path d="M22 82 V70 A12 12 0 0 1 34 58 H46" fill="none" stroke="{fg}" stroke-width="10"/>
<path d="M154 58 H166 A12 12 0 0 1 178 70 V82" fill="none" stroke="{fg}" stroke-width="10"/>
<path d="M22 142 V154 A12 12 0 0 0 34 166 H46" fill="none" stroke="{fg}" stroke-width="10"/>
<path d="M154 166 H166 A12 12 0 0 0 178 154 V142" fill="none" stroke="{fg}" stroke-width="10"/>
<line x1="22" y1="76" x2="178" y2="76" stroke="{fg}" stroke-width="2.5"/>
<g transform="rotate(-14 44 112)"><ellipse cx="44" cy="112" rx="17" ry="12" fill="{KRAFT}"/><ellipse cx="44" cy="112" rx="12" ry="7.5" fill="none" stroke="{NAVY}" stroke-width="1.5"/></g>
<g transform="rotate(9 156 128)"><rect x="141" y="117" width="30" height="22" fill="{SLATE}"/><line x1="146" y1="124" x2="166" y2="124" stroke="{PAPER}" stroke-width="2"/><line x1="146" y1="131" x2="160" y2="131" stroke="{PAPER}" stroke-width="2"/></g>
<rect x="62" y="58" width="12" height="108" fill="{bg}" stroke="{fg}" stroke-width="3"/>
<rect x="126" y="58" width="12" height="108" fill="{bg}" stroke="{fg}" stroke-width="3"/>
<rect x="60" y="96" width="16" height="12" fill="none" stroke="{fg}" stroke-width="3"/>
<rect x="124" y="96" width="16" height="12" fill="none" stroke="{fg}" stroke-width="3"/>
<circle cx="100" cy="120" r="21" fill="{RED}"/><circle cx="100" cy="120" r="16" fill="none" stroke="{PAPER}" stroke-width="1.5"/>
<text x="100" y="127.5" text-anchor="middle" font-family="Barlow Condensed, sans-serif" font-weight="700" font-size="20" fill="{PAPER}">FN</text>
<rect x="92" y="54" width="16" height="10" rx="2" fill="{fg}"/>'''


def postmark(fg, bg):
    return f'''<rect x="34" y="34" width="122" height="146" fill="{bg}"/>
<rect x="34" y="34" width="122" height="146" fill="none" stroke="{fg}" stroke-width="8" stroke-dasharray="0 10" stroke-linecap="round"/>
<rect x="46" y="46" width="98" height="122" fill="none" stroke="{fg}" stroke-width="3"/>
<path d="M46 150 C66 140 82 146 100 140 C118 134 128 142 144 136 V168 H46 Z" fill="{SLATE}"/>
<path d="M88 150 V100 L100 72 L112 100 V150 Z" fill="{fg}"/>
<path d="M70 150 V112 L78 98 L86 112 V150 Z" fill="{fg}"/>
<rect x="97" y="106" width="6" height="10" rx="3" fill="{bg}"/>
<text x="54" y="64" font-family="IBM Plex Mono, monospace" font-weight="500" font-size="15" fill="{fg}">41</text>
<circle cx="150" cy="70" r="30" fill="none" stroke="{RED}" stroke-width="3"/>
<circle cx="150" cy="70" r="22" fill="none" stroke="{RED}" stroke-width="1.2"/>
<text x="150" y="67" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="8" fill="{RED}">FIELD</text>
<text x="150" y="78" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="8" fill="{RED}">NOTES</text>
<path d="M120 100 C130 94 140 106 150 100 S170 94 186 100" fill="none" stroke="{RED}" stroke-width="2.5"/>
<path d="M118 110 C128 104 138 116 148 110 S168 104 186 110" fill="none" stroke="{RED}" stroke-width="2.5"/>'''


def tag(fg, bg):
    return f'''<path d="M93 70 C86 44 60 34 44 22" fill="none" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>
<path d="M93 70 C88 46 66 32 52 16" fill="none" stroke="{RED}" stroke-width="5" stroke-linecap="round" stroke-dasharray="7 6"/>
<path d="M93 70 C88 46 66 32 52 16" fill="none" stroke="{PAPER}" stroke-width="5" stroke-linecap="round" stroke-dasharray="6 7" stroke-dashoffset="6.5"/>
<g transform="rotate(-8 100 120)">
<path d="M64 76 L100 48 L136 76 V178 A6 6 0 0 1 130 184 H70 A6 6 0 0 1 64 178 Z" fill="{bg}" stroke="{fg}" stroke-width="7" stroke-linejoin="round"/>
<circle cx="100" cy="70" r="11" fill="none" stroke="{fg}" stroke-width="3.5"/>
<circle cx="100" cy="70" r="5" fill="{fg}"/>
<text x="100" y="132" text-anchor="middle" font-family="Barlow Condensed, sans-serif" font-weight="700" font-size="42" fill="{fg}">FN</text>
<line x1="76" y1="148" x2="124" y2="148" stroke="{fg}" stroke-width="2.5"/>
<line x1="76" y1="160" x2="124" y2="160" stroke="{fg}" stroke-width="2.5"/>
<line x1="76" y1="172" x2="110" y2="172" stroke="{fg}" stroke-width="2.5"/>
<rect x="64" y="94" width="72" height="6" fill="{RED}"/>
</g>'''


def boat(fg, bg):
    return f'''<g fill="none" stroke="{fg}" stroke-width="7" stroke-linejoin="round">
<path d="M30 118 L170 118 L142 152 L58 152 Z"/><path d="M100 46 L132 118 L68 118 Z"/>
<path d="M68 118 L30 118 L52 90 Z"/><path d="M132 118 L170 118 L148 90 Z"/></g>
<path d="M100 46 C112 34 124 44 136 30" fill="none" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>'''


MARKS = {"tag": tag, "suitcase": suitcase, "postmark": postmark, "boat": boat}


def svg(name, size, fg, bg, label=None):
    attrs = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true" focusable="false"'
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 200 200" {attrs} '
            f'xmlns="http://www.w3.org/2000/svg">{MARKS[name](fg, bg)}</svg>')
