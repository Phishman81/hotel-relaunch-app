import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json

# -------------------------------------------------------------------------
# 1) OpenAI-API-Key
# -------------------------------------------------------------------------
openai.api_key = st.secrets["openai_api_key"]

# -------------------------------------------------------------------------
# 2) Vollständiges ALL_MODULES
#    (bei dir bitte wirklich ALLE Module, hier beispielhaft gekürzt)
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
        # ... etc. ...
    ],
    # ... andere Module ...
    "Zimmer Übersicht": [
        {
            "Feld Name": "Subheading",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Subheadline"
        },
        {
            "Feld Name": "Titel",
            "Typ": "Text",
            "Zeichenbegrenzung": "max. 60 Zeichen",
            "Anmerkungen": "Haupttitel"
        },
    ],
}

# -------------------------------------------------------------------------
# 3) Scraping-Funktion (alte Seiten per URL)
# -------------------------------------------------------------------------
def scrape_page_content(url: str) -> str:
    """
    Lädt die angegebene URL, extrahiert den reinen Text und gibt ihn zurück.
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
# 4) Haupt-App (Streamlit)
# -------------------------------------------------------------------------
def main():
    st.title("Website-Relaunch Content-Mapping (OpenAI 1.14.0)")

    st.markdown("""
    **Ablauf**:
    1. Alte Seiten (URLs) eingeben -> werden gescraped.
    2. Neue Sitemap eingeben.
    3. o3-mini-2025-01-31 (oder anderes Modell) aufrufen -> Vorschlag für Module & Felder.
    """)

    # Eingabe: Alte URLs
    st.header("1) Alte Seiten (URLs)")
    old_urls_input = st.text_area(
        "Liste der alten URLs:",
        value="https://example.com/alte-seite-1\nhttps://example.com/alte-seite-2",
        height=150,
    )

    # Eingabe: Neue Sitemap
    st.header("2) Neue Seiten (Sitemap)")
    new_sitemap_input = st.text_area(
        "Liste der neuen Seiten (eine pro Zeile):",
        value="Startseite\nÜber uns\nZimmer\nKontakt\nDatenschutz",
        height=150,
    )

    # Button -> Mapping generieren
    if st.button("Content mapping generieren"):
        old_urls = [u.strip() for u in old_urls_input.split("\n") if u.strip()]
        new_pages = [p.strip() for p in new_sitemap_input.split("\n") if p.strip()]

        if not old_urls or not new_pages:
            st.warning("Bitte mindestens 1 alte URL und 1 neue Seite angeben.")
            return

        st.info("Scrape gestartet...")
        url_content_map = {}
        for url in old_urls:
            textval = scrape_page_content(url)
            url_content_map[url] = textval
        st.success("Scrape abgeschlossen!")

        # System-Prompt
        system_prompt = (
            "Du bist ein hilfreicher Assistent für Website-Relaunches. "
            "Hier alle verfügbaren Module:\n\n"
            + json.dumps(ALL_MODULES, ensure_ascii=False, indent=2)
            + "\n\n"
            "Bitte erstelle auf Basis der alten Seiteninhalte (URLs) "
            "und der neuen Sitemap ein Mapping, welche Module pro neuer Seite "
            "geeignet sind und wie die Felder (Titel, Subheading, Freitext etc.) "
            "gefüllt werden sollen."
        )

        # User-Prompt
        user_prompt = "## Neue Sitemap:\n"
        for page in new_pages:
            user_prompt += f"- {page}\n"

        user_prompt += "\n## Alte Seiten (Content):\n"
        for url, txt in url_content_map.items():
            user_prompt += f"### {url}\n"
            # ggf. Text kürzen, wenn sehr lang
            user_prompt += txt[:3000]
            user_prompt += "\n"

        # OpenAI-Aufruf mit openai.Chat.create(...)
        try:
            with st.spinner("Frage das Modell (Stream) ..."):
                response = openai.Chat.create(
                    model="o3-mini-2025-01-31",   # Beispiel: o3-mini
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,  # wir wollen live den Text
                    reasoning_effort="high",  # nur, wenn dein Modell das unterstützt
                    max_completion_tokens=500,
                    temperature=0.7
                )

                # Streaming-Ausgabe
                streamed_answer_placeholder = st.empty()
                final_answer = ""

                for chunk in response:
                    # chunk["choices"] -> array
                    # chunk["choices"][0]["delta"] -> dict mit partial "content"
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        final_answer += delta["content"]
                        streamed_answer_placeholder.markdown(final_answer)

            st.success("Antwort erhalten!")

        except Exception as e:
            st.error(f"Fehler beim OpenAI-Aufruf: {e}")


# Start der App
if __name__ == "__main__":
    main()
