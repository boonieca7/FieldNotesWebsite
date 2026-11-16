"""Editorial structure for the Field Notes From Abroad site.

Everything a person would want to change by hand lives here: which mark the header uses,
how posts group into journeys, series and threads, and the short intro lines.
The TL;DR summaries live in tldr.json (drafts, meant to be rewritten in your own voice).
"""

# Header/favicon mark: "tag", "suitcase", "postmark" or "boat"
MARK = "tag"

SITE_TITLE = "Field Notes From Abroad"
AUTHOR = "Chrystin McLelland"
PORTFOLIO_URL = "https://camclelland.wixsite.com/chrystin-mclelland"
HERO_IMAGE = "https://camclelland-jhibt.wordpress.com/wp-content/uploads/2026/03/corvin-castle-2-1.jpeg"
HERO_CAPTION = ("Corvin Castle, Hunedoara", "09.03.2026")

# Display titles where the WordPress title was a duplicate or cut off.
DISPLAY_TITLES = {
    3: "A Year in the Making: Saying Yes to Romania",
    246: "Corvin Castle and the Problem with Dracula",
    288: "Stories of Romania: The Well of the Three Prisoners",
    341: "Stories of Romania: The Raven of Corvin Castle",
    351: "Chronicles of Romania: John Hunyadi and Matthias Corvinus",
    376: "Chronicles of Romania: Vlad III of Wallachia",
    574: "Stories of Romania: Baba Dochia",
    631: "Bucharest: Crisis Creates Opportunities… But for Who?",
    1015: "The History of Florence Is Full of Women… If You Know Where to Look",
}

JOURNEYS = [
    dict(slug="timisoara", num="01", place="Timișoara", name="Arriving in Timișoara", when="Feb–Mar 2026",
         cover=564, intro="Leaving home, landing in Romania, and learning the city one coffee, menu and Mărțișor charm at a time.",
         posts=[3, 33, 59, 122, 165, 178, 208, 215, 564, 574, 586]),
    dict(slug="hunedoara", num="02", place="Hunedoara", name="Hunedoara and Corvin Castle", when="March 2026",
         cover=376, intro="A castle, its legends and its stairs, and the small town that turned out to be more than its headline attraction.",
         posts=[246, 288, 304, 341, 351, 376, 417, 438, 471, 520, 533, 548]),
    dict(slug="bucuresti", num="03", place="București", name="București", when="Mar–Apr 2026",
         cover=609, intro="An overnight train to the capital, a city shaped by communism and the 1977 earthquake, and one very long spa day.",
         posts=[598, 599, 609, 631, 651]),
    dict(slug="wien", num="04", place="Wien", name="Spring Break: Vienna", when="April 2026",
         cover=680, intro="Traveling without a plan for once: white horses, a wrong turn on Easter, and three floors of the Belvedere.",
         posts=[680, 708, 734, 747, 767, 771, 820, 873]),
    dict(slug="krakow", num="05", place="Kraków", name="Spring Break: Kraków", when="April 2026",
         cover=944, intro="A cancelled tour that became a private one, and the city's dragon, bugler and enchanted pigeons.",
         posts=[884, 926, 944]),
    dict(slug="firenze", num="06", place="Firenze", name="Florence: Women Lead", when="May 2026",
         cover=1015, intro="Field notes from a week-long women's leadership conference with Gonzaga in Florence.",
         posts=[972, 979, 1015, 1069, 1097, 1117, 1133, 1142, 1165, 1201, 1231]),
    dict(slug="romania", num="07", place="Romania", name="Back in Romania", when="May–Jun 2026",
         cover=1389, intro="Visa offices, a salt mine, Seat 41, the people of the semester, and finally Bran Castle.",
         posts=[947, 964, 1275, 1333, 1362, 1375, 1389]),
]

SERIES = [
    dict(slug="stories", label="Stories of", name="Folktales, retold where I heard them",
         intro="Legends from the places I visited, told the way they were told to me.",
         posts=[288, 341, 574, 747, 944, 1362]),
    dict(slug="chronicles", label="Chronicles of", name="The history underneath the view",
         intro="Hunyadi, Vlad III, communism, and the city that was rebuilt after the earthquake.",
         posts=[351, 376, 599, 609, 631]),
    dict(slug="leadership", label="Leadership notes", name="Leadership, ethics and systems",
         intro="The posts where travel turned into thinking about leadership, care, power and governance.",
         posts=[631, 708, 734, 947, 964, 979, 1015, 1069, 1097, 1117, 1133, 1142, 1165, 1201, 1231]),
]

THREADS = [
    dict(slug="planned-self", name="The planned self", posts=[680, 767, 1275, 1333]),
    dict(slug="pentimento", name="Pentimento", posts=[734, 972, 1165]),
    dict(slug="systems", name="Systems and waiting", posts=[947, 964, 1375]),
    dict(slug="castles", name="Castles and Dracula", posts=[246, 304, 376, 1389]),
    dict(slug="museums", name="Museums and looking", posts=[438, 471, 520, 771, 820, 873, 1165]),
    dict(slug="trains", name="Trains", posts=[598, 1333]),
    dict(slug="liver", name="The liver situation", posts=[122, 178, 947]),
]
