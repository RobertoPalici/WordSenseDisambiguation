# wdisambiguation/ner_utils.py

import spacy
from typing import List, Tuple

# Load the Romanian spaCy model
nlp = spacy.load("ro_core_news_sm")

def get_named_entities(text: str) -> List[Tuple[str, str]]:
    """
    Returnează o listă de entități numite (text, tip) din textul dat.
    """
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

def is_named_entity(token: str, ner_list: List[Tuple[str, str]]) -> bool:
    """
    Verifică dacă un token apare în lista de entități NER.
    """
    token_lower = token.lower()
    return any(token_lower == ent[0].lower() for ent in ner_list)
