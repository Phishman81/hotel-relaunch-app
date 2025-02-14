import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import json

# -------------------------------------------------------------------------
# 1) OpenAI-API-Key aus Streamlit-Secrets
#    => Hinterlege in Streamlit Cloud:
#       openai_api_key = "sk-..."
# -------------------------------------------------------------------------
openai.api_key = st.secrets["openai_api_key"]

# -------------------------------------------------------------------------
# 2) Vollständiges ALL_MODULES-Dictionary
#    (hier beispielhaft abgekürzt – bitte deine Komplettfassung verwenden)
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
        # ... usw. ...
    ],
    "Event-Teaser": [
        # ...
    ],
    # Bitte alle weiteren Module hier 1:1 reinkopieren
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
    # ...
}

# -------------------------------------------------------------------------
# 3) Scraping-Funktion (alte URLs -> Text)
# -------------------------------------------------------------------------
def scrape_page_content(url: str) -> str:
    """
    Lädt die angegebene URL und extrahiert den reinen Text.
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
# 4) Haupt-App: Streamlit
# -------------------------------------------------------------------------
def main():
    st.title("Website-Relaunch Content-Mapping (OpenAI 1.14.0)")

    st.markdown(
        """
        **Ablauf**:
        1. Gib alte URLs (eine pro Zeile) ein, damit wir deren Inhalte scrapen.
        2. Gib die neue Sitemap ein (wieder pro Zeile).
        3. Klick auf "Content mapping generieren":  
           Wir rufen das Modell *o3-mini-2025-01-31* mit *reasoning_effort=high* via **Stream** auf,
           um einen Mapping-Vorschlag (Module & Felder) zu erhalten.
        """
    )

    # Eingabe: alte URLs
    st.header("1) Alte Seiten (URLs)")
    old_urls_input = st.text_area(
        "Alte Seiten-URLs:",
        value="https://example.com/alte-seite-1\nhttps://example.com/alte-seite-2",
        height=150,
    )

    # Eingabe: neue Sitemap
    st.header("2) Neue Seiten (Sitemap)")
    new_sitemap_input = st.text_area(
        "Neue Sitemap (eine pro Zeile):",
        value="Startseite\nÜber uns\nZimmer\nKontakt\nDatenschutz",
        height=150,
    )

    if st.button("Content mapping generieren"):
        old_urls = [u.strip() for u in old_urls_input.split("\n") if u.strip()]
        new_pages = [p.strip() for p in new_sitemap_input.split("\n") if p.strip()]

        if not old_urls or not new_pages:
            st.warning("Bitte mindestens 1 alte URL und 1 neue Seite angeben!")
            return

        st.info("Scraping startet...")
        url_content_map = {}
        for url in old_urls:
            txt_content = scrape_page_content(url)
            url_content_map[url] = txt_content
        st.success("Scraping abgeschlossen!")

        # System-Prompt
        system_prompt = (
            "Du bist ein Website-Relaunch-Assistent. "
            "Hier das JSON mit allen verfügbaren Modulen:\n\n"
            + json.dumps(ALL_MODULES, ensure_ascii=False, indent=2)
            + "\n\nNutze diese Module, um die alten Inhalte bestmöglich "
            "auf die neue Sitemap zu verteilen (Mapping)."
        )

        # User-Prompt
        user_prompt = "## Neue Sitemap:\n"
        for page in new_pages:
            user_prompt += f"- {page}\n"

        user_prompt += "\n## Alte Seiten:\n"
        for url, content in url_content_map.items():
            user_prompt += f"\n### {url}\n"
            user_prompt += content[:3000]  # ggf. kürzen
            user_prompt += "\n"

        try:
            with st.spinner("Frage o3-mini-2025-01-31 mit reasoning=high (Stream) ..."):

                # NEUE API: openai.chat_completions.create
                response = openai.chat_completions.create(
                    model="o3-mini-2025-01-31",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    stream=True,         # => Streaming!
                    reasoning_effort="high",
                    max_completion_tokens=600,
                    temperature=0.7
                )

                # Dynamische Ausgabe in Streamlit
                streamed_answer_placeholder = st.empty()
                final_answer = ""

                for chunk in response:
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        # Füge neuen Token hinzu und aktualisiere live
                        final_answer += delta["content"]
                        streamed_answer_placeholder.markdown(final_answer)

            st.success("Fertig! Komplette Antwort erhalten.")

        except Exception as e:
            st.error(f"Fehler beim OpenAI-Aufruf: {e}")


# -------------------------------------------------------------------------
# 5) App starten
# -------------------------------------------------------------------------
if __name__ == "__main__":
    main()
