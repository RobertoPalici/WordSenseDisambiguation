import os
import requests
import json
from typing import Dict, Any, List
import streamlit as st
import pandas as pd

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

# Initialize session states for storing results
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

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
    
    # Function to run analysis and store results in session state
    def run_analysis():
        with st.spinner("Se analizează textul..."):
            try:
                # Send request to API
                result = analyze_text(text_input)
                # Store in session state
                st.session_state.analysis_results = result
            except Exception as e:
                st.error(f"Eroare la analizarea textului: {str(e)}")

    # Analyze button
    if st.button("Analizează textul", type="primary", disabled=not api_status.get("connected", False) or not text_input):
        if text_input:
            run_analysis()
        else:
            st.warning("Vă rugăm să introduceți un text pentru analiză.")
    
    # Display results if available
    if st.session_state.analysis_results:
        display_results(st.session_state.analysis_results)


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


def analyze_text(text: str) -> Dict[str, Any]:
    """
    Send text to API for analysis
    
    Args:
        text: Text to analyze
        
    Returns:
        Analysis results
    """
    data = {
        "text": text,
    }
    
    response = requests.post(
        f"{API_URL}/api/disambiguate",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    response.raise_for_status()
    return response.json()


def display_results(result: Dict[str, Any]):
    """
    Display disambiguation results
    
    Args:
        result: The API response containing the disambiguation results
    """
    st.subheader("Rezultatele Analizei")
    
    # Processing stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Timp total de procesare", 
            f"{result.get('total_execution_time', 0):.3f} sec"
        )
    with col2:
        st.metric(
            "Timp de îmbogățire (OpenAI)", 
            f"{result.get('enrichment_time', 0):.3f} sec"
        )
    
    # Display original text
    st.subheader("Textul Original")
    st.write(result.get("text", ""))
    
    # Display ambiguous words
    ambiguous_words = result.get("ambiguous_words", [])
    
    if not ambiguous_words:
        st.info("Nu au fost găsite cuvinte ambigue în text.")
        return
    
    st.subheader(f"Cuvinte Ambigue Detectate ({len(ambiguous_words)})")
    
    # Create a metrics overview
    metrics_data = []
    for word_data in ambiguous_words:
        metrics_data.append({
            "Cuvânt": word_data.get("word", ""),
            "POS": format_pos(word_data.get("pos", "")),
            "Scor Ambiguitate": f"{word_data.get('ambiguity_score', 0):.2f}",
            "Sensuri": len(word_data.get("top_meanings", [])) + len(word_data.get("other_meanings", []))
        })
    
    if metrics_data:
        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True)
    
    # Display each ambiguous word with its meanings
    for word_idx, word_data in enumerate(ambiguous_words):
        word = word_data.get("word", "")
        pos = word_data.get("pos", "")
        position = word_data.get("position", 0)
        ambiguity_score = word_data.get("ambiguity_score", 0)
        
        # Create expander for each word
        with st.expander(f"{word} ({format_pos(pos)}) - Scor Ambiguitate: {ambiguity_score:.2f}"):
            st.markdown(f"**Poziția în text:** {position + 1}")
            
            # Display top meanings
            top_meanings = word_data.get("top_meanings", [])
            if top_meanings:
                st.markdown("### Sensuri Principale")
                
                # Create tabs for each top meaning
                if len(top_meanings) > 0:
                    tabs = st.tabs([f"Sens {i+1} ({m.get('confidence', 0):.2f})" for i, m in enumerate(top_meanings)])
                    
                    for i, (tab, meaning) in enumerate(zip(tabs, top_meanings)):
                        with tab:
                            display_meaning(meaning, is_primary=(i==0))
            
            # Display other meanings using a checkbox
            other_meanings = word_data.get("other_meanings", [])
            if other_meanings:
                # Checkbox to toggle visibility - less disruptive than a button
                show_other = st.checkbox(f"Arată alte sensuri posibile ({len(other_meanings)})", key=f"show_other_{word_idx}")
                
                # Only show other meanings if checkbox is checked
                if show_other:
                    st.markdown("### Alte Sensuri Posibile")
                    for i, meaning in enumerate(other_meanings):
                        st.markdown(f"#### Sens alternativ {i+1} - Încredere: {meaning.get('confidence', 0):.2f}")
                        display_meaning(meaning, is_primary=False)
                        # Add a separator between meanings except for the last one
                        if i < len(other_meanings) - 1:
                            st.markdown("---")


def display_meaning(meaning: Dict[str, Any], is_primary: bool = False):
    """
    Display a single word meaning with its enrichment
    
    Args:
        meaning: The meaning dictionary
        is_primary: Whether this is the primary meaning
    """
    definition = meaning.get("definition", "")
    synonyms = meaning.get("synonyms", [])
    enrichment = meaning.get("enrichment", {})    
    
    if is_primary:
        st.markdown("#### Sensul cel mai probabil în acest context")
        
    st.markdown(f"**Definiție:** {definition}")
        
    if synonyms:
        st.markdown(f"**Sinonime:** {', '.join(synonyms)}")
    
    
    # Display enrichment
    if enrichment:
        st.markdown("#### Îmbogățire")
        
        # Display explanation
        explanation = enrichment.get("explanation", "")
        if explanation:
            st.markdown(f"**Explicație:**\n{explanation}")
        
        # Display examples
        examples = enrichment.get("examples", [])
        if examples:
            st.markdown("**Exemple:**")
            for i, example in enumerate(examples):
                st.markdown(f"{i+1}. *{example}*")


def format_pos(pos: str) -> str:
    """Format part of speech tag to human-readable form"""
    pos_map = {
        "NOUN": "Substantiv",
        "VERB": "Verb",
        "ADJ": "Adjectiv",
        "ADV": "Adverb",
        "PRON": "Pronume",
        "DET": "Determinant",
        "ADP": "Prepoziție",
        "CONJ": "Conjuncție",
        "NUM": "Numeral",
        "PART": "Particulă",
        "INTJ": "Interjecție"
    }
    return pos_map.get(pos, pos)


if __name__ == "__main__":
    main() 