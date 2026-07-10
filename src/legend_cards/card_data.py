"""Curated native-page crop data for the 2006 CAA legend."""

from typing import Final

from legend_cards.models import CardSpec, ObjectSelection
from legend_cards.models import card as _card
from legend_cards.models import object_card as _object_card

CARDS: Final[tuple[CardSpec, ...]] = (
    _card(
        "aerodrome-civil",
        "Aerodrome — Civil",
        "Aerodromes",
        (271.25, 50.0, 285.0, 65.0),
        ((271.25, 58.5, 272.25, 61.5), (271.25, 64.0, 285.0, 65.0)),
    ),
    _card(
        "aerodrome-civil-limited",
        "Aerodrome — Civil, limited or no facilities",
        "Aerodromes",
        (273.0, 64.0, 283.5, 74.5),
    ),
    _card("heliport-civil", "Heliport — Civil", "Aerodromes", (273.0, 75.0, 283.5, 85.5)),
    _object_card(
        "aerodrome-government-civil",
        "Government aerodrome available for civil use",
        "Aerodromes",
        (270.5, 85.0, 283.75, 100.0),
        ObjectSelection((154, 155, 156), ()),
    ),
    _object_card(
        "aerodrome-government",
        "Aerodrome — Government",
        "Aerodromes",
        (272.25, 98.25, 283.75, 109.75),
        ObjectSelection((159, 160), ()),
    ),
    _card(
        "heliport-government",
        "Heliport — Government",
        "Aerodromes",
        (272.75, 110.0, 283.75, 121.25),
    ),
    _card(
        "microlight-site", "Microlight flying site", "Aerodromes", (273.25, 124.75, 283.5, 135.0)
    ),
    _object_card(
        "aerodrome-disused",
        "Disused or abandoned aerodrome",
        "Aerodromes",
        (272.25, 138.75, 283.75, 150.25),
        ObjectSelection((157, 158), ()),
    ),
    _card(
        "aerodrome-light-beacon-blue",
        "Aerodrome light beacon — flashing green",
        "Aerodromes",
        (222.75, 181.5, 254.0, 191.25),
    ),
    _card(
        "aerodrome-light-beacon-magenta",
        "Aerodrome light beacon — flashing red",
        "Aerodromes",
        (254.5, 181.5, 288.0, 191.25),
    ),
    _card(
        "glider-primary-winch",
        "Glider launching site — primary activity with maximum winch altitude",
        "Aerial activities",
        (261.2, 215.3, 283.2, 238.3),
        ((261.2, 232.0, 265.0, 238.3),),
    ),
    _object_card(
        "glider-additional-winch",
        "Glider launching site — additional activity with maximum winch altitude",
        "Aerial activities",
        (248.05, 236.15, 280.0, 257.85),
        ObjectSelection((1,), ("G/2.5",)),
    ),
    _object_card(
        "glider-additional-no-cables",
        "Glider launching site — additional activity without cables",
        "Aerial activities",
        (260.9, 256.4, 282.5, 280.1),
        ObjectSelection((3,), ("G",)),
    ),
    _object_card(
        "hang-para-winch",
        "Hang/para gliding winch launch site with maximum altitude",
        "Aerial activities",
        (249.55, 277.15, 273.0, 299.9),
        ObjectSelection((4, 5), ("/2.5",)),
    ),
    _card(
        "parachuting-drop-zone",
        "Free-fall parachuting drop zone",
        "Aerial activities",
        (251.0, 360.0, 283.0, 392.0),
    ),
    _card(
        "vor",
        "VOR — VHF Omnidirectional Radio Range",
        "Radio navigation aids",
        (200.35, 398.05, 209.95, 406.65),
    ),
    _card(
        "dme",
        "DME — Distance Measuring Equipment",
        "Radio navigation aids",
        (200.15, 407.75, 210.8, 416.3),
    ),
    _card(
        "vor-dme",
        "Collocated, frequency-paired VOR/DME",
        "Radio navigation aids",
        (199.8, 432.4, 210.5, 440.95),
    ),
    _card(
        "tacan",
        "TACAN — UHF Tactical Air Navigation Aid",
        "Radio navigation aids",
        (199.55, 440.7, 210.75, 451.1),
    ),
    _card(
        "ndb",
        "NDB and NDB(L) — Non-Directional Radio Beacon",
        "Radio navigation aids",
        (191.5, 451.35, 218.8, 478.7),
    ),
    _card(
        "other-navigational-aids",
        "Other navigational aids",
        "Radio navigation aids",
        (200.45, 478.65, 208.5, 486.7),
    ),
    _card(
        "vor-compass-rose",
        "VOR compass rose oriented on magnetic north",
        "Radio navigation aids",
        (214.9, 394.1, 283.35, 462.55),
        ((214.9, 458.9, 221.5, 462.55),),
    ),
    _card(
        "obstacle-exceptionally-high",
        "Exceptionally high obstacle, lighted, 1000 ft or more AGL",
        "Obstacles",
        (256.6, 498.7, 282.7, 520.4),
    ),
    _card(
        "obstacle-single-unlighted",
        "Single obstacle — unlighted",
        "Obstacles",
        (221.5, 518.5, 244.5, 535.5),
        ((234.25, 529.5, 244.5, 535.5),),
    ),
    _card(
        "obstacle-multiple-lighted",
        "Multiple obstacle — lighted",
        "Obstacles",
        (255.5, 526.0, 283.0, 541.35),
    ),
    _card(
        "controlled-airspace-class-a",
        "Class A controlled airspace boundary and vertical limits",
        "Controlled airspace",
        (491.5, 55.0, 553.25, 70.0),
    ),
    _card(
        "controlled-airspace-class-c",
        "Class C controlled airspace boundary and vertical limits",
        "Controlled airspace",
        (490.5, 74.25, 553.25, 90.5),
    ),
    _card(
        "controlled-airspace-class-d",
        "Class D controlled airspace boundary and vertical limits",
        "Controlled airspace",
        (490.75, 95.0, 553.5, 110.5),
    ),
    _card(
        "controlled-airspace-class-e",
        "Class E controlled airspace boundary and vertical limits",
        "Controlled airspace",
        (490.75, 111.1, 553.6, 130.8),
    ),
    _card(
        "advisory-route",
        "Advisory route centre line and limits",
        "Routes and points",
        (490.75, 132.75, 553.5, 149.75),
    ),
    _card(
        "airspace-class-g",
        "Airspace not covered by Classes A-F (Class G)",
        "Controlled airspace",
        (490.75, 153.25, 553.25, 161.75),
    ),
    _card(
        "low-level-corridor",
        "Low level corridor or special route",
        "Routes and points",
        (487.5, 164.5, 553.5, 175.5),
    ),
    _card(
        "reporting-point", "Reporting point", "Routes and points", (544.75, 197.5, 553.5, 204.25)
    ),
    _card(
        "special-access-lane",
        "Special access lane entry or exit",
        "Routes and points",
        (512.25, 204.75, 553.75, 219.75),
    ),
    _card(
        "visual-reference-point",
        "Visual reference point (VRP)",
        "Routes and points",
        (480.75, 224.35, 488.95, 232.6),
    ),
    _object_card(
        "atz",
        "Aerodrome traffic zone (ATZ)",
        "Controlled airspace",
        (519.25, 284.85, 554.25, 319.85),
        ObjectSelection((147, 148), ()),
    ),
    _object_card(
        "matz",
        "Standard MATZ with two stubs and LARS",
        "Military airspace",
        (472.25, 360.0, 554.0, 413.75),
        ObjectSelection(
            tuple(range(192, 207)),
            ("5NM", "4NM", "MATZ", "LARS", "126", ".", "5"),
        ),
    ),
    _card(
        "danger-area",
        "Prohibited, restricted or danger area boundary",
        "Airspace restrictions",
        (482.25, 462.25, 517.25, 486.75),
    ),
    _card(
        "scheduled-danger-area",
        "Danger area activated by NOTAM",
        "Airspace restrictions",
        (518.5, 461.5, 553.5, 487.25),
    ),
    _card(
        "aiaa-ata",
        "AIAA or aerial tactics area boundary",
        "Military airspace",
        (484.0, 651.25, 553.25, 655.25),
    ),
    _card(
        "hirta",
        "High intensity radio transmission area (HIRTA)",
        "Hazards",
        (526.25, 667.75, 553.75, 695.25),
        ((526.25, 691.0, 529.5, 695.25),),
    ),
    _card("bird-sanctuary", "Bird sanctuary", "Hazards", (538.4, 694.75, 552.9, 711.5)),
    _card(
        "gas-venting",
        "Circular gas venting marker — GVS label gives the upper limit",
        "Hazards",
        (533.7, 715.25, 553.95, 737.2),
    ),
    _card(
        "laser-site",
        "Circular laser marker — LASER SITE label gives the upper limit",
        "Hazards",
        (513.5, 738.25, 553.5, 759.1),
    ),
)
