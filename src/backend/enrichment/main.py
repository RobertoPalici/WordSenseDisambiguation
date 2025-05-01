"""
Main entry point for testing the enrichment functionality.

This module creates dummy input data in the same format used by the API,
calls the enrichment function, and prints the results.
"""

import json
import logging
from typing_extensions import List

from ..utils.config import settings
from ..ambiguity.types import (
    AmbiguousWordDict, 
    RecommendationDict, 
    ResultDict,
)
from .enrichment import enrich_top_meanings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("backend.enrichment.main")


def main():
    """
    Main function to test the enrichment functionality
    """
    logger.info("Starting enrichment test")
    
    # Check OpenAI API status
    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY is not set in settings. Using dummy client.")
    else:
        logger.info(f"Using OpenAI API with model: {settings.OPENAI_MODEL}")
    
    result_dict = create_test_data()
    
    enrich_top_meanings(result_dict)    
    
    # Also print some statistics about API usage
    total_ambiguous_words = len(result_dict.get("ambiguous_words", []))
    total_meanings = sum(len(word.get("potential_meanings", [])) for word in result_dict.get("ambiguous_words", []))
    max_meanings_per_word = max(len(word.get("potential_meanings", [])) for word in result_dict.get("ambiguous_words", []))
    
    print("\n===== ENRICHMENT STATISTICS =====")
    print(f"Total ambiguous words: {total_ambiguous_words}")
    print(f"Total potential meanings: {total_meanings}")
    print(f"Max meanings per word: {max_meanings_per_word}")

def create_test_data() -> ResultDict:
    """
    Create dummy test data in ResultDict format with multiple ambiguous words and meanings
    
    Returns:
        A ResultDict object with ambiguous_words and recommendations
    """
    # Create ambiguous words
    ambiguous_words: List[AmbiguousWordDict] = [
        # Word 1: bancă - 4 potential meanings
        {
            "word": "bancă",
            "pos": "NOUN",
            "position": 0,
            "potential_meanings": [
                {
                    "id": "ENG30-08227335-n",
                    "definition": "Instituție financiară care acceptă depozite și oferă împrumuturi",
                    "pos": "NOUN",
                    "synonyms": ["bancă", "instituție financiară", "instituție bancară"],
                    "confidence": 0.85
                },
                {
                    "id": "ENG30-03219135-n",
                    "definition": "Un obiect lung pe care oamenii pot să stea",
                    "pos": "NOUN",
                    "synonyms": ["bancă", "banchetă", "laviță"],
                    "confidence": 0.35
                },
                {
                    "id": "ENG30-09618957-n",
                    "definition": "O formațiune naturală asemănătoare unui banc subacvatic",
                    "pos": "NOUN",
                    "synonyms": ["bancă", "banc", "recif"],
                    "confidence": 0.12
                },
                {
                    "id": "ENG30-08033385-n",
                    "definition": "Un grup sau o instituție de donare și stocare a unor materiale biologice",
                    "pos": "NOUN",
                    "synonyms": ["bancă", "depozit", "bancă biologică"],
                    "confidence": 0.09
                }
            ],
            "best_meaning": {
                "id": "ENG30-08227335-n",
                "definition": "Instituție financiară care acceptă depozite și oferă împrumuturi",
                "pos": "NOUN",
                "synonyms": ["bancă", "instituție financiară", "instituție bancară"],
                "confidence": 0.85
            },
            "ambiguity_score": 0.62
        },
        
        # Word 2: refuzat - 3 potential meanings
        {
            "word": "refuzat",
            "pos": "VERB",
            "position": 2,
            "potential_meanings": [
                {
                    "id": "ENG30-02546031-v",
                    "definition": "A respinge, a nu accepta ceva oferit",
                    "pos": "VERB",
                    "synonyms": ["refuza", "respinge", "nega"],
                    "confidence": 0.92
                },
                {
                    "id": "ENG30-02557299-v",
                    "definition": "A nu permite cuiva să facă ceva",
                    "pos": "VERB",
                    "synonyms": ["refuza", "interzice", "opri"],
                    "confidence": 0.45
                },
                {
                    "id": "ENG30-02549488-v",
                    "definition": "A da un răspuns negativ la o cerere sau propunere",
                    "pos": "VERB",
                    "synonyms": ["refuza", "declina", "respinge"],
                    "confidence": 0.38
                }
            ],
            "best_meaning": {
                "id": "ENG30-02546031-v",
                "definition": "A respinge, a nu accepta ceva oferit",
                "pos": "VERB",
                "synonyms": ["refuza", "respinge", "nega"],
                "confidence": 0.92
            },
            "ambiguity_score": 0.47
        },
        
        # Word 3: operație - 5 potential meanings
        {
            "word": "operație",
            "pos": "NOUN",
            "position": 10,
            "potential_meanings": [
                {
                    "id": "ENG30-01061805-n",
                    "definition": "Procedură medicală chirurgicală",
                    "pos": "NOUN",
                    "synonyms": ["operație", "intervenție chirurgicală", "procedură medicală"],
                    "confidence": 0.78
                },
                {
                    "id": "ENG30-00947128-n",
                    "definition": "Acțiune militară planificată",
                    "pos": "NOUN",
                    "synonyms": ["operație", "operațiune", "acțiune militară"],
                    "confidence": 0.65
                },
                {
                    "id": "ENG30-05616246-n",
                    "definition": "Acțiune matematică între numere sau expresii",
                    "pos": "NOUN",
                    "synonyms": ["operație", "operație matematică", "calcul"],
                    "confidence": 0.51
                },
                {
                    "id": "ENG30-00974107-n",
                    "definition": "Proces sau acțiune într-un sistem organizat",
                    "pos": "NOUN",
                    "synonyms": ["operație", "proces", "activitate"],
                    "confidence": 0.43
                },
                {
                    "id": "ENG30-00912677-n",
                    "definition": "Tranzacție comercială sau financiară",
                    "pos": "NOUN",
                    "synonyms": ["operație", "tranzacție", "operațiune financiară"],
                    "confidence": 0.28
                }
            ],
            "best_meaning": {
                "id": "ENG30-01061805-n",
                "definition": "Procedură medicală chirurgicală",
                "pos": "NOUN",
                "synonyms": ["operație", "intervenție chirurgicală", "procedură medicală"],
                "confidence": 0.78
            },
            "ambiguity_score": 0.75
        },
        
        # Word 4: masă - 6 potential meanings
        {
            "word": "masă",
            "pos": "NOUN",
            "position": 15,
            "potential_meanings": [
                {
                    "id": "ENG30-04379243-n",
                    "definition": "Mobilier format dintr-un blat susținut de picioare, folosit pentru a așeza obiecte",
                    "pos": "NOUN",
                    "synonyms": ["masă", "birou", "mobilă"],
                    "confidence": 0.72
                },
                {
                    "id": "ENG30-07566340-n",
                    "definition": "Alimente servite și consumate la o anumită oră a zilei",
                    "pos": "NOUN",
                    "synonyms": ["masă", "prânz", "cină", "mic-dejun"],
                    "confidence": 0.69
                },
                {
                    "id": "ENG30-13267111-n",
                    "definition": "Mulțime de persoane care formează un grup nedefinit",
                    "pos": "NOUN",
                    "synonyms": ["masă", "mulțime", "majoritate"],
                    "confidence": 0.54
                },
                {
                    "id": "ENG30-05240896-n",
                    "definition": "Cantitate de materie dintr-un obiect, măsură fizică fundamentală",
                    "pos": "NOUN",
                    "synonyms": ["masă", "greutate", "volum"],
                    "confidence": 0.42
                },
                {
                    "id": "ENG30-04149232-n",
                    "definition": "Materie densă și compactă, formă nedefinită",
                    "pos": "NOUN",
                    "synonyms": ["masă", "bloc", "materie"],
                    "confidence": 0.37
                },
                {
                    "id": "ENG30-08509711-n",
                    "definition": "Slujbă religioasă în ritul catolic",
                    "pos": "NOUN",
                    "synonyms": ["masă", "liturghie", "slujbă"],
                    "confidence": 0.15
                }
            ],
            "best_meaning": {
                "id": "ENG30-04379243-n",
                "definition": "Mobilier format dintr-un blat susținut de picioare, folosit pentru a așeza obiecte",
                "pos": "NOUN",
                "synonyms": ["masă", "birou", "mobilă"],
                "confidence": 0.72
            },
            "ambiguity_score": 0.88
        },
        
        # Word 5: calc - 3 potential meanings
        {
            "word": "calc",
            "pos": "NOUN",
            "position": 20,
            "potential_meanings": [
                {
                    "id": "ENG30-14653265-n",
                    "definition": "Element chimic, metal alcalino-pământos cu simbolul Ca",
                    "pos": "NOUN",
                    "synonyms": ["calciu", "Ca", "element chimic"],
                    "confidence": 0.81
                },
                {
                    "id": "ENG30-14941900-n",
                    "definition": "Compus mineral, carbonat de calciu folosit în construcții",
                    "pos": "NOUN",
                    "synonyms": ["calc", "var", "piatră de var"],
                    "confidence": 0.75
                },
                {
                    "id": "ENG30-03082979-n",
                    "definition": "Formă de reproducere a unui desen prin presare",
                    "pos": "NOUN",
                    "synonyms": ["calc", "copie", "reproducere"],
                    "confidence": 0.32
                }
            ],
            "best_meaning": {
                "id": "ENG30-14653265-n",
                "definition": "Element chimic, metal alcalino-pământos cu simbolul Ca",
                "pos": "NOUN",
                "synonyms": ["calciu", "Ca", "element chimic"],
                "confidence": 0.81
            },
            "ambiguity_score": 0.56
        }
    ]
    
    # Create recommendations for all ambiguous words
    recommendations: List[RecommendationDict] = [
        # Recommendation for "bancă"
        {
            "word": "bancă",
            "pos": "NOUN",
            "recommendation": "Cuvântul 'bancă' este ambiguu. Considerați utilizarea unui sinonim mai specific în funcție de sensul intenționat:",
            "options": [
                {
                    "meaning": "Instituție financiară care acceptă depozite și oferă împrumuturi",
                    "synonyms": ["instituție financiară", "instituție bancară"]
                },
                {
                    "meaning": "Un obiect lung pe care oamenii pot să stea",
                    "synonyms": ["banchetă", "laviță"]
                },
                {
                    "meaning": "O formațiune naturală asemănătoare unui banc subacvatic",
                    "synonyms": ["banc", "recif"]
                },
            ]
        },
        # Recommendation for "refuzat"
        {
            "word": "refuzat",
            "pos": "VERB",
            "recommendation": "Forma 'refuzat' a verbului 'refuza' este ambiguă. Considerați utilizarea unui sinonim mai specific:",
            "options": [
                {
                    "meaning": "A respinge, a nu accepta ceva oferit",
                    "synonyms": ["respinge", "nega"]
                },
                {
                    "meaning": "A nu permite cuiva să facă ceva",
                    "synonyms": ["interzice", "opri"]
                },
                {
                    "meaning": "A da un răspuns negativ la o cerere sau propunere",
                    "synonyms": ["declina", "respinge"]
                }
            ]
        },
        # Recommendation for "operație"
        {
            "word": "operație",
            "pos": "NOUN",
            "recommendation": "Cuvântul 'operație' are mai multe sensuri. Considerați utilizarea unui termen mai specific:",
            "options": [
                {
                    "meaning": "Procedură medicală chirurgicală",
                    "synonyms": ["intervenție chirurgicală", "procedură medicală"]
                },
                {
                    "meaning": "Acțiune militară planificată",
                    "synonyms": ["operațiune", "acțiune militară"]
                },
                {
                    "meaning": "Acțiune matematică între numere sau expresii",
                    "synonyms": ["operație matematică", "calcul"]
                },
            ]
        },
        # Recommendation for "masă"
        {
            "word": "masă",
            "pos": "NOUN",
            "recommendation": "Cuvântul 'masă' este foarte ambiguu. Folosiți un termen mai precis pentru contextul dorit:",
            "options": [
                {
                    "meaning": "Mobilier format dintr-un blat susținut de picioare, folosit pentru a așeza obiecte",
                    "synonyms": ["birou", "mobilă"]
                },
                {
                    "meaning": "Alimente servite și consumate la o anumită oră a zilei",
                    "synonyms": ["prânz", "cină", "mic-dejun"]
                },
                {
                    "meaning": "Mulțime de persoane care formează un grup nedefinit",
                    "synonyms": ["mulțime", "majoritate"]
                },
            ]
        },
        # Recommendation for "calc"
        {
            "word": "calc",
            "pos": "NOUN",
            "recommendation": "Cuvântul 'calc' poate avea mai multe sensuri. Folosiți un termen mai specific:",
            "options": [
                {
                    "meaning": "Element chimic, metal alcalino-pământos cu simbolul Ca",
                    "synonyms": ["calciu", "Ca", "element chimic"]
                },
                {
                    "meaning": "Compus mineral, carbonat de calciu folosit în construcții",
                    "synonyms": ["var", "piatră de var"]
                },
                {
                    "meaning": "Formă de reproducere a unui desen prin presare",
                    "synonyms": ["copie", "reproducere"]
                }
            ]
        }
    ]
    
    # Create result dictionary with a more complex example text
    return {
        "text": "Banca a refuzat împrumutul deoarece au considerat că planul de operație al afacerii nu era clar, iar masa de potențiali clienți nu era suficient analizată. Chiar și fără finanțare, am continuat să calculez șansele de succes.",
        "ambiguous_words": ambiguous_words,
        "recommendations": recommendations
    }

if __name__ == "__main__":
    main() 