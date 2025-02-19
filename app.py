import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json

# -------------------------------------------------------------------------
# 1) DeepSeek-API-Key aus Streamlit-Secrets
# -------------------------------------------------------------------------
openai.api_key = st.secrets["openai_api_key"]
# Setze die Basis-URL der DeepSeek API:
openai.api_base = "https://api.deepseek.com"

# -------------------------------------------------------------------------
# 2) ALL_MODULES - Dein vollständiges Dictionary (ohne Kürzungen!)
# -------------------------------------------------------------------------
ALL_MODULES = {
    "Bild-Text": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Kurze Subheadline"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Hauptüberschrift"
        },
        {
            "Feld Name": "Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 300 Zeichen",
            "Anmerkungen": "Freier Beschreibungstext"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Text für den Call-to-Action Button"
        },
        {
            "Feld Name": "Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bild für das Modul, Bildausrichtung (links oder rechts wählbar)"
        },
        {
            "Feld Name": "Tag 1: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon, das auf dem Bild angezeigt wird"
        },
        {
            "Feld Name": "Tag 1: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text für das erste Tag"
        },
        {
            "Feld Name": "Tag 2: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Optional: Zweites Icon, das auf dem Bild angezeigt wird"
        },
        {
            "Feld Name": "Tag 2: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Optional: Text für das zweite Tag"
        },
    ],
    "Event-Teaser": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Z. B. „Nächstes Event“"
        },
        {
            "Feld Name": "Event",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": (
                "Auswahl des anzuzeigenden Events. Wenn kein Event ausgewählt ist, "
                "wird automatisch das nächste Event am Standort angezeigt. "
                "Wenn kein Event verfügbar ist, erscheint das Modul nicht"
            )
        }
    ],
    "Mixed Media Grid": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button"
        },
        {
            "Feld Name": "Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bild für ein Media-Element"
        },
        {
            "Feld Name": "Video",
            "Typ": "Video",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Self-hosted Video (startet bei Sichtbarkeit)"
        },
        {
            "Feld Name": "Subheading (auf Bild/Video)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline über dem Bild/Video"
        },
        {
            "Feld Name": "Titel (auf Bild/Video)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel, der auf dem Bild/Video angezeigt wird"
        },
        {
            "Feld Name": "Tag: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon als Tag auf dem Bild/Video (optional)"
        },
        {
            "Feld Name": "Tag: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text als Tag auf dem Bild/Video (optional)"
        },
        {
            "Feld Name": "Titel (unter Bild/Video)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel unterhalb des Bildes/Videos"
        },
        {
            "Feld Name": "Button (auf Bild/Video)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Button direkt auf dem Bild/Video"
        },
    ],
    "Testimonials Embed": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Kurze Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button"
        },
        {
            "Feld Name": "Embed-Code",
            "Typ": "Code",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Code für das Elfsight-Widget (z. B. Google Reviews)"
        },
        {
            "Feld Name": "Freitext (Content-Blocker)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Text, der im Content-Blocker angezeigt wird"
        },
    ],
    "Raum Slider": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Kurze Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button linkt zu Raum-Übersichtseite (optional)"
        },
    ],
    "Zimmer Slider": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Kurze Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button linkt zu Zimmer-Übersichtseite (optional)"
        },
    ],
    "Bild-Text Teaser-Grid": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button für das Modul"
        },
        {
            "Feld Name": "Bild 1",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bild für Kachel 1"
        },
        {
            "Feld Name": "Titel (auf Kachel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel, der auf der Kachel mit Bild 1 angezeigt wird"
        },
        {
            "Feld Name": "Subheading (unter Titel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Untertitel direkt unter dem Kachel-Titel für Bild 1"
        },
        {
            "Feld Name": "Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Beschreibungstext für die Kachel mit Bild 1"
        },
        {
            "Feld Name": "Button (auf Kachel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Button auf der Kachel mit Bild 1 (optional)"
        },
        {
            "Feld Name": "Tag 1: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon als Tag auf dem Bild 1 (optional)"
        },
        {
            "Feld Name": "Tag 1: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text für den ersten Tag (optional) für Bild 1"
        },
        {
            "Feld Name": "Tag 2: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon als Tag auf dem Bild 1 (optional)"
        },
        {
            "Feld Name": "Tag 2: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text für den zweiten Tag (optional) für Bild 1"
        },
        {
            "Feld Name": "Bild 2",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bild für Kachel 2"
        },
        {
            "Feld Name": "Titel (auf Kachel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel, der auf der Kachel 2 mit Bild 2 angezeigt wird"
        },
        {
            "Feld Name": "Subheading (unter Titel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Untertitel direkt unter dem Kachel-Titel für Bild 2"
        },
        {
            "Feld Name": "Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Beschreibungstext für die Kachel mit Bild 2"
        },
        {
            "Feld Name": "Button (auf Kachel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Button auf der Kachel mit Bild 2 (optional)"
        },
        {
            "Feld Name": "Tag 1: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon als Tag auf dem Bild 2 (optional)"
        },
        {
            "Feld Name": "Tag 1: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text für den ersten Tag (optional) für Bild 2"
        },
        {
            "Feld Name": "Tag 2: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon als Tag auf dem Bild 2 (optional)"
        },
        {
            "Feld Name": "Tag 2: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text für den zweiten Tag (optional) für Bild 2"
        },
        {
            "Feld Name": "Bild 3",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bild für Kachel 3"
        },
        {
            "Feld Name": "Titel (auf Kachel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel, der auf der Kachel 2 mit Bild 3 angezeigt wird"
        },
        {
            "Feld Name": "Subheading (unter Titel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Untertitel direkt unter dem Kachel-Titel für Bild 3"
        },
        {
            "Feld Name": "Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Beschreibungstext für die Kachel mit Bild 3"
        },
        {
            "Feld Name": "Button (auf Kachel)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Button auf der Kachel mit Bild 3 (optional)"
        },
        {
            "Feld Name": "Tag 1: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon als Tag auf dem Bild 3 (optional)"
        },
        {
            "Feld Name": "Tag 1: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text für den ersten Tag (optional) für Bild 3"
        },
        {
            "Feld Name": "Tag 2: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Icon als Tag auf dem Bild 3 (optional)"
        },
        {
            "Feld Name": "Tag 2: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Text für den zweiten Tag (optional) für Bild 3"
        },
    ],
    "Stories": [
        {
            "Feld Name": "Info",
            "Typ": "Hinweis",
            "Zeichenbegrenzung": "",
            "Anmerkungen": (
                "Infos für Content-Pfleger: Poster-Bilder/Videos müssen "
                "vom Redakteur eigenständig ausgewählt werden."
            )
        },
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Poster-Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Vorschaubild für jede Story, min. 5 Stories"
        },
        {
            "Feld Name": "Story-Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel für die Story"
        },
        {
            "Feld Name": "Link",
            "Typ": "URL",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Optional: Verlinkung der gesamten Story"
        },
        {
            "Feld Name": "Medien: Video",
            "Typ": "Video",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bis zu 8 Medien pro Story"
        },
        {
            "Feld Name": "Medien: Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bis zu 8 Medien pro Story"
        },
        {
            "Feld Name": "Medien: Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Optionaler Titel für einzelne Medien der Story"
        },
    ],
    "Hero Text": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Optional: Wenn nicht hinterlegt, wird der Seiten-Titel angezeigt"
        },
        {
            "Feld Name": "Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 300 Zeichen",
            "Anmerkungen": "Beschreibungstext unter dem Titel"
        },
        {
            "Feld Name": "Buchungs-Leiste",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": (
                "Ja/Nein: Aktiviert eine Buchungs-Leiste im Modul. Nur verwenden, "
                "wenn es Sinn macht (z.B. Zimmer, Meetings, Restaurant)"
            )
        },
    ],
    "Hero Big": [
        {
            "Feld Name": "Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Hintergrundbild für Desktop"
        },
        {
            "Feld Name": "Mobile Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Hintergrundbild für Mobilgeräte"
        },
        {
            "Feld Name": "Video",
            "Typ": "Video",
            "Zeichenbegrenzung": "",
            "Anmerkungen": (
                "Self-hosted Video für Desktop, läuft automatisch ohne Ton "
                "in Endlosschleife"
            )
        },
        {
            "Feld Name": "Mobile Video",
            "Typ": "Video",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Self-hosted Video für Mobilgeräte"
        },
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Optional: Wenn nicht hinterlegt, wird der Seiten-Titel angezeigt"
        },
        {
            "Feld Name": "Buchungs-Leiste",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Ja/Nein: Aktiviert eine Buchungs-Leiste im Modul"
        },
        {
            "Feld Name": "Button-Primär",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button"
        },
        {
            "Feld Name": "Button-Sekundär",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler sekundärer Call-to-Action-Button"
        },
    ],
    "Text Zweispaltig": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für den linken Bereich"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel für den linken Bereich"
        },
        {
            "Feld Name": "Freitext (links)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 500 Zeichen in 3 Absätzen",
            "Anmerkungen": "Text für den linken Bereich in Absätzen"
        },
        {
            "Feld Name": "Freitext (rechts)",
            "Typ": "Text",
            "Zeichenbegrenzung": (
                "max. 500 Zeichen in 3 Absätze (Aufzählungslisten erlaubt)"
            ),
            "Anmerkungen": (
                "Text für den rechten Bereich in Absätzen und Bullet-Point-Liste"
            )
        },
        {
            "Feld Name": "Button (rechts)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": (
                "Optional: Call-to-Action-Button im rechten Bereich, "
                "Vorschlag für mögliche Ziel-URL"
            )
        },
    ],
    "Galerie": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für die Galerie"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler Call-to-Action-Button"
        },
        {
            "Feld Name": "Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bilder der Galerie, Darstellung im originalen Seitenverhältnis"
        },
        {
            "Feld Name": "Tag: Icon",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Optional: Icon als Teil eines Tags"
        },
        {
            "Feld Name": "Tag: Text",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 15 Zeichen",
            "Anmerkungen": "Optional: Text, der im Tag angezeigt wird"
        },
    ],
    "Raum Übersicht": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": (
                "Kurze Subheadline, 1 bis 5 Wörter, für eine Bildergalerie mit Raumfotos"
            )
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
    ],
    "Kontakt Teaser": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
    ],
    "Formular": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Formular"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Formular"
        },
        {
            "Feld Name": "Formfelder-Variante",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Wählbare Varianten: General / MICE / b_smart Services"
        },
        {
            "Feld Name": "Privacy Checkbox Label",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Freitext für das Label der Datenschutz-Checkbox (Pflichtfeld)"
        },
        {
            "Feld Name": "Submit Button Label",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Beschriftung des Absenden-Buttons"
        },
        {
            "Feld Name": "Subheading (Success-Message)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für die Erfolgsmeldung nach Absenden"
        },
        {
            "Feld Name": "Titel (Success-Message)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel für die Erfolgsmeldung"
        },
        {
            "Feld Name": "Freitext (Success-Message)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 300 Zeichen",
            "Anmerkungen": "Beschreibungstext der Erfolgsmeldung"
        },
        {
            "Feld Name": "Hidden-Feld",
            "Typ": "Text",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Kontext des Formulars für Weiterleitungen von b_smart"
        },
    ],
    "Standortkarte (einzeln)": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button, z. B. „Route berechnen“"
        },
        {
            "Feld Name": "Standort auswählen",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Auswahl eines Standorts aus den Standort-Einstellungen"
        },
        {
            "Feld Name": "Adresse",
            "Typ": "Text",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Wird aus den Standort-Einstellungen geladen"
        },
        {
            "Feld Name": "Hotel Kontakt",
            "Typ": "Text",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Wird aus den Standort-Einstellungen geladen"
        },
        {
            "Feld Name": "Restaurant Kontakt",
            "Typ": "Text",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Optional: Wird angezeigt, wenn vorhanden"
        },
        {
            "Feld Name": "Icon für Map",
            "Typ": "Image/Icon",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Individuelles Icon für die Karte, z. B. Pin"
        },
    ],
    "Standortkarte (alle)": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button für das Modul"
        },
        {
            "Feld Name": "Manuelle Wahl der Standorte",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Auswahl der anzuzeigenden Standorte"
        },
        {
            "Feld Name": "Initial-Zentrierungsstandort",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Standort, der initial als Mittelpunkt der Map dient"
        },
        {
            "Feld Name": "Freitext (keine Standortauswahl)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Text für den Zustand, wenn kein Standort ausgewählt ist"
        },
        {
            "Feld Name": "Titel (Standort)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel des Standorts, wird bei Pin-Klick angezeigt"
        },
        {
            "Feld Name": "Adresse",
            "Typ": "Text",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Adresse des Standorts, wird aus den Standort-Einstellungen geladen"
        },
        {
            "Feld Name": "Hotel Kontakt",
            "Typ": "Text",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Kontaktinformationen des Hotels (Standort-Einstellungen)"
        },
        {
            "Feld Name": "Restaurant Kontakt",
            "Typ": "Text",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Optional: Restaurant-Kontakt, wenn vorhanden"
        },
        {
            "Feld Name": "Icon für Map",
            "Typ": "Image/Icon",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Individuelles Icon für den Standort-Pin"
        },
        {
            "Feld Name": "Button mit Link zum Standort",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Verlinkung zur Detailseite oder externer URL"
        },
    ],
    "Umgebungskarte": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button für das Modul"
        },
        {
            "Feld Name": "Standortauswahl",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Auswahl des Standorts, um die Karte zu zentrieren"
        },
        {
            "Feld Name": "Freitext (kein Pin)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Text, der angezeigt wird, wenn kein Pin ausgewählt ist"
        },
        {
            "Feld Name": "Pin: Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 300 Zeichen",
            "Anmerkungen": "Beschreibungstext, der beim Anklicken des Pins angezeigt wird"
        },
        {
            "Feld Name": "Pin: Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler Button beim Anklicken des Pins"
        },
    ],
    "Akkordeons": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Akkordeon-Tab: Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel des einzelnen Akkordeon-Tabs"
        },
        {
            "Feld Name": "Akkordeon-Tab: Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 300 Zeichen",
            "Anmerkungen": "Beschreibungstext des einzelnen Akkordeon-Tabs"
        },
        {
            "Feld Name": "Toggle (erstes Element offen)",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Einstellung, ob das erste Akkordeon-Element initial geöffnet ist"
        },
    ],
    "Leistungen Übersicht": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button (oben)",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler Call-to-Action-Button oberhalb der Kacheln"
        },
        {
            "Feld Name": "Kachel: Globale Leistung",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": (
                "Optional: Globale Leistung auswählen, deren Daten überschrieben "
                "werden können"
            )
        },
        {
            "Feld Name": "Kachel: Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": (
                "Optional: Bild für die Kachel, überschreibt Bild der globalen Leistung"
            )
        },
        {
            "Feld Name": "Kachel: Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel der Kachel"
        },
        {
            "Feld Name": "Kachel: Beschreibung",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Optional: Beschreibungstext für die Kachel"
        },
        {
            "Feld Name": "Kachel: Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": (
                "Optionaler Call-to-Action-Button in der Kachel "
                "(z. B. Link zur Self-Checkin-Seite)"
            )
        },
    ],
    "Event Übersicht (Standort)": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
    ],
    "Event Übersicht (global)": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
    ],
    "Text Grid": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler Call-to-Action-Button für das Modul"
        },
        {
            "Feld Name": "Element: Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel für jedes Grid-Element"
        },
        {
            "Feld Name": "Element: Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 150 Zeichen",
            "Anmerkungen": "Beschreibungstext für jedes Grid-Element"
        },
        {
            "Feld Name": "Element: Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler Call-to-Action-Button für jedes Grid-Element"
        },
    ],
    "Doomla Jobs (API)": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Call-to-Action-Button für das Modul"
        },
        {
            "Feld Name": "Portal: Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel eines Doomla Portals, z. B. „Alle Jobs“"
        },
        {
            "Feld Name": "Portal: ID",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 30 Zeichen",
            "Anmerkungen": "Eindeutige Portal-ID zur API-Abfrage"
        },
    ],
    "Text": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Überschrift über dem Freitext"
        },
        {
            "Feld Name": "Freitext",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 1000 Zeichen in Absätzen",
            "Anmerkungen": "Hauptinhalt des Moduls, in Absätzen"
        },
    ],
    "Bild": [
        {
            "Feld Name": "Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bild, das im Modul dargestellt wird"
        },
        {
            "Feld Name": "Darstellung",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Einstellung: „breit“ oder „schmal“"
        },
    ],
    "Video": [
        {
            "Feld Name": "Video",
            "Typ": "Video",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Eigenes Video, das im Modul dargestellt wird"
        },
        {
            "Feld Name": "Poster-Bild",
            "Typ": "Image",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Bild, das vor dem Abspielen des Videos angezeigt wird"
        },
        {
            "Feld Name": "Vimeo Embed",
            "Typ": "Embed/URL",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Vimeo-Einbettung in DSGVO-konformer „Do-Not-Track“-Variante"
        },
        {
            "Feld Name": "Darstellung",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Einstellung: „breit“ oder „schmal“"
        },
    ],
    "Standorte Slider": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler Call-to-Action-Button"
        },
    ],
    "Mitteilungen": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
        {
            "Feld Name": "Button",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Optionaler Call-to-Action-Button für das Modul"
        },
        {
            "Feld Name": "Mitteilung: Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für jede Mitteilung"
        },
        {
            "Feld Name": "Mitteilung: Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Titel für jede Mitteilung"
        },
        {
            "Feld Name": "Mitteilung: Datum",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 20 Zeichen",
            "Anmerkungen": "Datum im Textformat, z. B. „Juli 2024“"
        },
        {
            "Feld Name": "Mitteilung: Asset",
            "Typ": "File",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Datei oder Dokument, das heruntergeladen werden kann"
        },
        {
            "Feld Name": "Mitteilung: Link",
            "Typ": "URL",
            "Zeichenbegrenzung": "",
            "Anmerkungen": "Externer Link (Alternative zum Asset)"
        },
        {
            "Feld Name": "Mitteilung: Button Label",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 25 Zeichen",
            "Anmerkungen": "Beschriftung des Buttons für die jeweilige Mitteilung"
        },
    ],
    "Globaler Modulblock": [
        {
            "Feld Name": "Globaler Modul-Block",
            "Typ": "Auswahl",
            "Zeichenbegrenzung": "",
            "Anmerkungen": (
                "Stellt die im hinterlegten Modul-Block aufbereiteten Module "
                "hier dar (z. B. Gutscheine-Seite, Self-Checkin-Seite, etc.)"
            )
        }
    ],
    "Zimmer Übersicht": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline für das Modul"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel für das Modul"
        },
    ],
}

# -------------------------------------------------------------------------
# 3) Scraping-Funktion (alte Seiten)
# -------------------------------------------------------------------------
def scrape_page_content(url: str) -> str:
    """
    Lädt eine URL und gibt den reinen Text des HTML aus.
    """
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        st.warning(f"Fehler beim Abrufen von {url}: {e}")
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    return soup.get_text(separator="\n").strip()

# -------------------------------------------------------------------------
# 4) Haupt-App
# -------------------------------------------------------------------------
def main():
    st.title("Website-Relaunch Content-Mapping (mit DeepSeek-Reasoner)")

    st.markdown(
        """
        **Vorgehen**:
        1. Gebe im ersten Feld die alten Seiten (URLs) ein, je Zeile eine.
        2. Gebe im zweiten Feld die neue Sitemap ein, wieder je Zeile eine Seite.
        3. Wir scrapen die alten Seiten, schicken alles an das Modell **DeepSeek-Reasoner** 
           und du erhältst ein Mapping, welche Module (aus ALL_MODULES) zu den neuen Seiten passen 
           und wie du die Felder befüllen könntest.
        """
    )

    # Eingabe: alte URLs
    st.header("1) Alte Seiten (URLs)")
    old_urls_input = st.text_area(
        "Alte Seiten (eine pro Zeile):",
        value="https://example.com/alte-seite-1\nhttps://example.com/alte-seite-2",
        height=150
    )

    # Eingabe: neue Sitemap
    st.header("2) Neue Seiten (Sitemap)")
    new_sitemap_input = st.text_area(
        "Neue Seiten (eine pro Zeile):",
        value="Startseite\nÜber uns\nZimmer\nKontakt\nDatenschutz",
        height=150
    )

    if st.button("Content mapping generieren"):
        old_urls = [u.strip() for u in old_urls_input.split("\n") if u.strip()]
        new_pages = [p.strip() for p in new_sitemap_input.split("\n") if p.strip()]

        if not old_urls or not new_pages:
            st.warning("Bitte mindestens 1 alte URL und 1 neue Seite angeben!")
            return

        st.info("Scraping der alten Seiten läuft ...")
        url_content_map = {}
        for url in old_urls:
            scraped_text = scrape_page_content(url)
            url_content_map[url] = scraped_text
        st.success("Scraping abgeschlossen!")

        # System-Prompt
        system_prompt = (
            "Du bist ein hilfreicher Assistent für Website-Relaunches. "
            "Du kennst ein Dictionary mit verfügbaren Modulen (siehe unten) "
            "und sollst auf Basis der alten Seiten (Scraping) und der neuen Sitemap "
            "einen Vorschlag machen, wie die Inhalte bestmöglich den Modulen "
            "zugeordnet werden können. Hier das JSON der Module:\n\n"
            + json.dumps(ALL_MODULES, ensure_ascii=False, indent=2)
        )

        # User-Prompt
        user_prompt = "## Neue Sitemap:\n"
        for p in new_pages:
            user_prompt += f"- {p}\n"

        user_prompt += "\n## Alte Seiten & deren Inhalt:\n"
        for url, content in url_content_map.items():
            user_prompt += f"\n### {url}\n"
            # ggf. kürzen (wenn sehr viel Text)
            user_prompt += content[:4000]
            user_prompt += "\n"

        try:
            with st.spinner("Frage DeepSeek-Reasoner (stream) nach einem Mapping-Vorschlag..."):
                response = openai.ChatCompletion.create(
                    model="deepseek-reasoner",  # DeepSeek Reasoning-Modell
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,          # live Ausgabe
                    max_completion_tokens=600,
                    temperature=0.7       # Steuerung der Kreativität
                )

                # Streaming-Ausgabe
                streamed_answer_placeholder = st.empty()
                final_answer = ""

                for chunk in response:
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        final_answer += delta["content"]
                        streamed_answer_placeholder.markdown(final_answer)

            st.success("Fertig! Mapping-Vorschlag erhalten.")

        except Exception as e:
            st.error(f"Fehler beim DeepSeek-Aufruf: {e}")

# -------------------------------------------------------------------------
# 5) Streamlit-App starten
# -------------------------------------------------------------------------
if __name__ == "__main__":
    main()
