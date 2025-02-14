import streamlit as st
import openai

openai.api_key = st.secrets["openai_api_key"]

import requests
from bs4 import BeautifulSoup
import json

# -------------------------------------------------------------------------
# 1) Hier das Dictionary ALL_MODULES mit allen Modulen.
#    (1:1 aus deinem Skript kopiert)
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
    # ---- Deine weiteren Module analog ergänzt (Event-Teaser, Mixed Media Grid, ...)
    # ---- Aus Platzgründen hier abgekürzt, aber du kannst einfach alles reinkopieren.
    # ----
}


# -------------------------------------------------------------------------
# 2) Hilfsfunktion zum Auslesen der Inhalte der alten URLs
# -------------------------------------------------------------------------
def scrape_page_content(url: str) -> str:
    """
    Ruft die angegebene URL auf und gibt den reinen Text (sichtbaren Content)
    zurück. Hier in einfacher Variante (keine komplexe Token-Optimierung).
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.warning(f"Fehler beim Abrufen von {url}: {e}")
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    # Nur reinen Text auslesen; Du kannst natürlich auch
    # Feinjustierungen machen, z. B. nur <p>-Inhalte
    page_text = soup.get_text(separator="\n")
    return page_text.strip()


# -------------------------------------------------------------------------
# 3) Streamlit-Anwendung
# -------------------------------------------------------------------------
def main():
    st.title("Website-Relaunch Content-Mapping")

    # Hier ggf. deinen OpenAI API-Key einlesen:
    # Option A) Direkt:
    # openai.api_key = "DEIN_OPENAI_KEY"
    #
    # Option B) Über Text-Input-Feld (nicht empfohlen für produktiven Einsatz)
    # api_key_input = st.text_input("OpenAI API Key", type="password")
    # if api_key_input:
    #     openai.api_key = api_key_input
    #
    # Option C) Über st.secrets["openai_api_key"], falls in Streamlit Cloud
    # openai.api_key = st.secrets["openai_api_key"]

    # 1) Nutzer kann die alten URLs eingeben
    st.header("1) Alte Seiten (URLs)")
    old_urls_input = st.text_area(
        "Gib hier die alten Seiten-URLs ein (jeweils eine pro Zeile):",
        height=150,
        value="https://example.com/alte-seite-1\nhttps://example.com/alte-seite-2"
    )

    # 2) Nutzer gibt die neue Sitemap / neue Seiten ein
    st.header("2) Neue Seiten (Sitemap)")
    new_sitemap_input = st.text_area(
        "Gib hier die neuen Seiten an (jeweils eine pro Zeile):",
        height=150,
        value="Startseite\nÜber uns\nZimmer & Suiten\nKontakt\nDatenschutz"
    )

    # Button zum Starten der Zuordnung
    if st.button("Content mapping generieren"):
        # Parsen:
        old_urls = [u.strip() for u in old_urls_input.split("\n") if u.strip()]
        new_pages = [p.strip() for p in new_sitemap_input.split("\n") if p.strip()]

        if not old_urls or not new_pages:
            st.warning("Bitte mindestens eine alte URL und mindestens eine neue Seite angeben.")
            return

        # 2.1) Alte Seiten auslesen
        st.info("Scraping läuft – bitte warten...")
        url_content_map = {}
        for url in old_urls:
            text_content = scrape_page_content(url)
            url_content_map[url] = text_content

        st.success("Scraping abgeschlossen!")

        # 3) Aufruf an OpenAI: Wir übergeben dem Modell alle alten Inhalte,
        #    die neue Sitemap sowie die Modul-Liste, damit es ein Mapping vorschlägt.
        #    ACHTUNG: Bei sehr vielen oder langen Seiten kann das Prompt sehr groß werden.
        #    In der Praxis ggfs. chunken oder abkürzen.

        # Prompt vorbereiten
        system_prompt = (
            "Du bist ein hilfreicher Assistent für Website-Relaunches. "
            "Dir stehen verschiedene Module zur Verfügung, in die Content eingepflegt werden kann. "
            "Die folgende Python-ähnliche Datenstruktur listet alle Module und deren Felder auf:\n\n"
            f"{json.dumps(ALL_MODULES, ensure_ascii=False, indent=2)}\n\n"
            "Deine Aufgabe: Basiere auf der folgenden Liste mit alten Seiten (und deren Inhalt), "
            "und auf der neuen Sitemap (Auflistung neuer Seiten), um ein möglichst hilfreiches Mapping zu generieren. "
            "Für jede NEUE Seite mache bitte Vorschläge, welche Module man verwenden könnte, "
            "und welche Textpassagen (Titel, Subheading, Freitext etc.) sich aus dem alten Content eignen, "
            "wo sie in den Modulen eingepflegt werden sollten (z. B. 'Titel' = 'Willkommen im Hotel XYZ'). "
            "Gib dein Ergebnis in einer klaren, strukturierten Form (z. B. JSON, Markdown-Tabelle o. Ä.) zurück.\n"
        )

        # Wir geben dem Modell in user_prompt alle relevanten Infos:
        user_prompt = "## Neue Seiten (Sitemap)\n"
        for newp in new_pages:
            user_prompt += f"- {newp}\n"

        user_prompt += "\n## Alte Seiten (und ausgelesener Inhalt)\n\n"
        for url in url_content_map:
            user_prompt += f"### {url}\n"
            # Inhalt ggf. kürzen, um nicht das gesamte Modell zu überfordern
            # user_prompt += url_content_map[url][:4000]  # z.B. auf 4000 Zeichen beschränken
            user_prompt += url_content_map[url]
            user_prompt += "\n\n"

        # Dann rufen wir die API:
        # Beispiel-Konfiguration: GPT-3.5 oder GPT-4
        try:
            with st.spinner("Rufe OpenAI-API auf..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # oder gpt-4
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.0,
                )
            ai_answer = response["choices"][0]["message"]["content"]
            st.success("Antwort vom KI-Modell erhalten!")
            st.markdown("### Vorschlag für die Content-Zuordnung:")
            st.write(ai_answer)

        except Exception as e:
            st.error(f"Fehler beim OpenAI-Aufruf: {e}")


if __name__ == "__main__":
    main()
