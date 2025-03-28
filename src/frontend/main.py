import os
import requests
import json
from typing import Dict, Any
import streamlit as st

# Configure the app
st.set_page_config(
    page_title="Dezambiguizarea Sensului Cuvintelor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API settings
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state for text input if it doesn't exist
if 'text_input' not in st.session_state:
    st.session_state.text_input = ""

def set_example_text():
    """Set example text in session state"""
    st.session_state.text_input = """Banca a refuzat împrumutul pentru că nu credeau că aș putea conduce o afacere de succes. 
    Între timp, îmi place să alerg pe malul băncii râului pentru a-mi limpezi mintea."""

def main():
    st.title("📚 Dezambiguizarea Sensului Cuvintelor")
    st.subheader("Procesarea Limbajului Natural pentru Analiza Contextului Semantic")
    
    # Sidebar
    st.sidebar.title("Despre")
    st.sidebar.info(
        """
        ### Ce este Dezambiguizarea Sensului Cuvintelor?
        
        Dezambiguizarea Sensului Cuvintelor (WSD) este capacitatea de a identifica ce sens 
        al unui cuvânt este folosit într-un context dat. Multe cuvinte au sensuri multiple 
        (polisemie), iar WSD urmărește să rezolve această ambiguitate.
        
        ### Cum funcționează această aplicație
        
        Această aplicație utilizează framework-ul Teprolin NLP pentru a analiza textul și 
        a identifica sensul corect al cuvintelor ambigue în funcție de contextul lor.
        
        1. Introduceți textul în zona de introducere
        2. Ajustați setările de analiză, dacă este necesar
        3. Faceți clic pe 'Analizează' pentru a procesa textul
        4. Explorați cuvintele dezambiguizate și sensurile lor
        
        ### Exemple de cuvinte ambigue
        
        - **Bancă**: Instituție financiară vs. Loc pentru șezut
        - **Cal**: Animal vs. Aparat de gimnastică
        - **Broască**: Animal vs. Încuietoare
        """
    )
    
    # API connection status
    api_status = check_detailed_api_status()
    
    # Show API status information
    st.sidebar.markdown("### Starea Sistemului")
    
    if api_status.get("connected", False):
        st.sidebar.success("✅ Conectat la API")
        
        # Show more detailed status information
        teprolin_status = api_status.get("dependencies", {}).get("teprolin", {})
        if teprolin_status.get("teprolin_status") == "available":
            st.sidebar.success("✅ Serviciul Teprolin conectat")
        else:
            st.sidebar.error("❌ Serviciul Teprolin indisponibil")
            st.sidebar.info(f"Eroare: {teprolin_status.get('error', 'Eroare necunoscută')}")
    else:
        st.sidebar.error("❌ Conexiune API eșuată")
        st.warning(
            "Nu s-a putut conecta la API-ul backend. Vă rugăm să vă asigurați că serverul backend rulează."
        )
    
    # Example text button - placed before text input to ensure proper UI flow
    st.button("Încarcă text exemplu", on_click=set_example_text)
    
    # Text input with value from session state
    text_input = st.text_area(
        "Introduceți text pentru analiză:",
        value=st.session_state.text_input,
        height=150,
        placeholder="Introduceți aici un text pentru a analiza sensurile cuvintelor...",
    )
    
    # Analysis options
    with st.expander("Opțiuni de analiză"):
        col1, col2 = st.columns(2)
        with col1:
            confidence_threshold = st.slider(
                "Pragul de încredere",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Scorul minim de încredere pentru afișarea rezultatelor",
            )
        with col2:
            max_senses = st.slider(
                "Număr maxim de sensuri per cuvânt",
                min_value=1,
                max_value=10,
                value=3,
                step=1,
                help="Numărul maxim de sensuri de afișat per cuvânt",
            )
    
    # Show information about the analysis options
    st.info(
        """
        **Pragul de încredere**: Valorile mai mari afișează doar rezultate cu încredere mai mare.
        **Număr maxim de sensuri**: Numărul maxim de sensuri alternative afișate per cuvânt.
        """
    )

    # Analyze button
    if st.button("Analizează textul", type="primary", disabled=not api_status.get("connected", False) or not text_input):
        if text_input:
            with st.spinner("Se analizează textul..."):
                try:
                    # Send request to API
                    result = analyze_text(
                        text_input, 
                        {
                            "confidence_threshold": confidence_threshold,
                            "max_senses": max_senses
                        }
                    )
                    
                    # Display results
                    display_results(result)
                    
                except Exception as e:
                    st.error(f"Eroare la analizarea textului: {str(e)}")
        else:
            st.warning("Vă rugăm să introduceți un text pentru analiză.")


def check_detailed_api_status() -> Dict[str, Any]:
    """Get detailed API status information"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        if response.status_code == 200:
            status_data = response.json()
            status_data["connected"] = True
            return status_data
        else:
            return {"connected": False, "error": f"API a returnat statusul {response.status_code}"}
    except Exception as e:
        return {"connected": False, "error": str(e)}


def analyze_text(text: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send text to API for analysis
    
    Args:
        text: Text to analyze
        options: Analysis options
        
    Returns:
        Analysis results
    """
    options = options or {}
    data = {
        "text": text,
        "options": options
    }
    
    response = requests.post(
        f"{API_URL}/api/disambiguate",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    response.raise_for_status()
    return response.json()


def display_results(result: Dict[str, Any]):
    st.subheader("Rezultate")
    
    # Processing stats
    st.text(f"Timp de procesare: {result.get('processing_time', 0):.3f} secunde")
    
    # Display processed text
    st.subheader("Text procesat")
    st.write(result.get("processed_text", ""))
    
    # Display disambiguated words
    st.subheader("Cuvinte dezambiguizate")
    
    disambiguated_words = result.get("disambiguated_words", [])
    
    if not disambiguated_words:
        st.info("Nu au fost găsite cuvinte dezambiguizate în text.")
        return
    
    # Create columns for word information
    for word_info in disambiguated_words:
        with st.expander(f"{word_info.get('word')} → {word_info.get('lemma')}"):
            st.markdown(f"**Poziție:** {word_info.get('position')}")
            
            # Show selected sense
            selected_sense = word_info.get("selected_sense", {})
            if selected_sense:
                st.markdown("**Sens selectat:**")
                st.json(selected_sense)
            
            # Show alternative senses
            senses = word_info.get("senses", [])
            if len(senses) > 1:
                st.markdown("**Sensuri alternative:**")
                for sense in senses[1:]:  # Skip the first one (selected)
                    st.json(sense)


if __name__ == "__main__":
    main() 