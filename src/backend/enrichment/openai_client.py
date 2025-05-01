"""
OpenAI API client module

This module handles interactions with the OpenAI API for generating
explanations and example sentences.
"""

import logging
import re
from typing_extensions import Dict, List

from openai import OpenAI
from ..utils.config import settings
from fastapi import HTTPException

logger = logging.getLogger('backend.enrichment.openai_client')

# Singleton instance of the OpenAI client
_openai_client_instance = None


def _get_openai_client() -> OpenAI:
    """
    Returns a singleton instance of the OpenAI client.
    """
    global _openai_client_instance
    
    if _openai_client_instance is None:
        api_key = settings.OPENAI_API_KEY
        logger.info(f"OpenAI API key: {api_key}")
        if not api_key:
            logger.error("OpenAI API key not configured in settings.")
            raise HTTPException(status_code=503, detail="Failed to initialize OpenAI client")
        
        try:
            _openai_client_instance = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise HTTPException(status_code=503, detail="Failed to initialize OpenAI client")
    
    return _openai_client_instance
    

# TODO: This 2 function can be optimized to extract the duplicated code.
def generate_batch_explanations(meanings: List[Dict]) -> Dict[int, str]:
    """
    Generate explanations for multiple word meanings in a single API call
    
    Args:
        meanings: List of dictionaries containing word meaning information
        
    Returns:
        Dictionary mapping index to explanation
    """
    # Use the singleton client
    client = _get_openai_client()
    
    # Create a batch prompt for multiple meanings
    prompts = []
    for i, meaning in enumerate(meanings):
        word = meaning["word"]
        sense_id = meaning["sense_id"]
        definition = meaning["definition"]
        pos = meaning["pos"]
        
        definition_text = f" Definiția din dicționar: {definition}" if definition else ""
        prompt = f"SENSUL {i+1}: Cuvântul \"{word}\" ({pos}) cu ID-ul sensului: {sense_id}.{definition_text}"
        prompts.append(prompt)
    
    batch_prompt = "\n\n".join(prompts)
    
    system_message = """
    Ești un expert lingvist specializat în limba română. Vei primi mai multe sensuri ale unor cuvinte românești.
    Pentru FIECARE sens, generează o explicație clară, detaliată și naturală.

    Fiecare explicație ar trebui să fie scrisă în română și să aibă 3-5 propoziții, fiind ușor de înțeles pentru o persoană care învață limba română.
    Concentrează-te pe contextul specific al fiecărui sens.

    Este ESENȚIAL să formatezi răspunsul tău exact așa:
    EXPLICAȚIA 1: [explicația pentru primul sens]

    EXPLICAȚIA 2: [explicația pentru al doilea sens]

    Și așa mai departe pentru fiecare sens. Folosește întoarceri de rând (newlines) între fiecare explicație.
    """
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": batch_prompt}
    ]
    
    try:
        if settings.ENRICHMENT_MOCK_API:
            raise Exception("Testing enrichment mock API")
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages
        )
        
        # Parse the response to extract individual explanations
        text = response.choices[0].message.content.strip()
        explanations = {}
        
        # Improved parsing - try multiple approaches
        # First try to split by the explicit markers
        pattern = r"EXPLICAȚIA\s+(\d+):\s*(.*?)(?=EXPLICAȚIA\s+\d+:|$)"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # If we found matches with regex
            for idx_str, content in matches:
                try:
                    idx = int(idx_str) - 1  # Convert to 0-based index
                    explanations[idx] = content.strip()
                except (ValueError, IndexError):
                    continue
        else:
            # Fallback to the original line-by-line parsing
            current_idx = None
            current_text = []
            
            # Add a newline at the end to ensure we process the last explanation
            for line in text.split('\n'):
                line = line.strip()
                
                # Check if this is a new explanation marker
                if line.startswith('EXPLICAȚIA ') and ':' in line:
                    # If we were building an explanation, save it
                    if current_idx is not None and current_text:
                        explanations[current_idx] = ' '.join(current_text).strip()
                        current_text = []
                    
                    # Extract the index from the marker
                    try:
                        idx_str = line.split('EXPLICAȚIA ')[1].split(':')[0].strip()
                        current_idx = int(idx_str) - 1  # Convert to 0-based index
                    except (IndexError, ValueError):
                        current_idx = len(explanations)  # Fallback if parsing fails
                
                # If not a marker and we have a current index, add to the current explanation
                elif current_idx is not None:
                    current_text.append(line)
            
            # Save the last explanation if there is one
            if current_idx is not None and current_text:
                explanations[current_idx] = ' '.join(current_text).strip()
        
        # Ensure we have explanations for all meanings
        for i in range(len(meanings)):
            if i not in explanations:
                word = meanings[i]["word"]
                explanations[i] = f"Nu am putut genera o explicație pentru sensul cuvântului '{word}'."
        
        return explanations
        
    except Exception as e:
        logger.error(f"Error generating batch explanations: {str(e)}")
        return {i: f"Nu am putut genera o explicație pentru sensul cuvântului '{meanings[i]['word']}'." 
                for i in range(len(meanings))}

def generate_batch_examples(meanings: List[Dict]) -> Dict[int, List[str]]:
    """
    Generate example sentences for multiple word meanings in a single API call
    
    Args:
        meanings: List of dictionaries containing word meaning information
        
    Returns:
        Dictionary mapping index to list of examples
    """
    client = _get_openai_client()
    
    # Create a batch prompt for multiple meanings
    prompts = []
    for i, meaning in enumerate(meanings):
        word = meaning["word"]
        sense_id = meaning["sense_id"]
        definition = meaning["definition"]
        pos = meaning["pos"]
        
        definition_text = f" Definiția din dicționar: {definition}" if definition else ""
        prompt = f"SENSUL {i+1}: Cuvântul \"{word}\" ({pos}) cu ID-ul sensului: {sense_id}.{definition_text}"
        prompts.append(prompt)
    
    batch_prompt = "\n\n".join(prompts)
    
    system_message = """
    Ești un expert lingvist specializat în limba română. Vei primi mai multe sensuri ale unor cuvinte românești.
    Pentru FIECARE sens, generează 2-3 propoziții exemplu.

    Propozițiile ar trebui:
    1. Să fie naturale și autentice, nu artificiale
    2. Să reflecte uzul cotidian al limbii române contemporane
    3. Să ofere contexte diverse dar specifice pentru acest sens particular al cuvântului
    4. Să fie de complexitate medie (10-15 cuvinte)
    5. Să nu includă explicații, doar propozițiile în sine

    Este ESENȚIAL să formatezi răspunsul tău exact așa:
    EXEMPLE PENTRU SENSUL 1:
    1. [primul exemplu pentru sensul 1]
    2. [al doilea exemplu pentru sensul 1]

    EXEMPLE PENTRU SENSUL 2:
    1. [primul exemplu pentru sensul 2]
    2. [al doilea exemplu pentru sensul 2]

    Și așa mai departe pentru fiecare sens. Folosește întoarceri de rând (newlines) între fiecare set de exemple.
    """
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": batch_prompt}
    ]
    
    try:
        if settings.ENRICHMENT_MOCK_API:
            raise Exception("Testing enrichment mock API")
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages
        )
        
        # Parse the response to extract individual examples
        text = response.choices[0].message.content.strip()
        examples_dict = {}
        
        # Improved parsing - try multiple approaches
        # First try to split by the explicit markers using regex
        pattern = r"EXEMPLE PENTRU SENSUL\s+(\d+):(.*?)(?=EXEMPLE PENTRU SENSUL\s+\d+:|$)"
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            # If we found matches with regex
            for idx_str, content in matches:
                try:
                    idx = int(idx_str) - 1  # Convert to 0-based index
                    # Parse the examples from the content
                    examples = []
                    for line in content.strip().split('\n'):
                        line = line.strip()
                        if line and any(line.startswith(f"{i}") for i in range(1, 10)):
                            # Remove the numbering
                            if '.' in line[:3]:
                                example = line.split('.', 1)[1].strip()
                            elif ':' in line[:3]:
                                example = line.split(':', 1)[1].strip()
                            else:
                                example = line[2:].strip()
                            
                            if example:
                                examples.append(example)
                        elif line and not any(char.isdigit() for char in line[:2]):
                            examples.append(line)
                    
                    examples_dict[idx] = examples if examples else [f"Nu am putut genera exemple pentru sensul {idx+1}."]
                    
                except (ValueError, IndexError):
                    continue
        else:
            # Fallback to the original line-by-line parsing
            current_idx = None
            current_examples = []
            
            for line in text.split('\n'):
                line = line.strip()
                
                # Check if this is a new section marker
                if line.startswith('EXEMPLE PENTRU SENSUL '):
                    # If we were building examples, save them
                    if current_idx is not None and current_examples:
                        examples_dict[current_idx] = current_examples
                        current_examples = []
                    
                    # Extract the index from the marker
                    try:
                        idx_str = line.split('EXEMPLE PENTRU SENSUL ')[1].strip().rstrip(':')
                        current_idx = int(idx_str) - 1  # Convert to 0-based index
                    except (IndexError, ValueError):
                        current_idx = len(examples_dict)  # Fallback if parsing fails
                
                # If not a section marker and we have a current index, check if it's an example
                elif current_idx is not None:
                    # Check if it's a numbered example
                    if any(line.startswith(f"{i}") for i in range(1, 10)):
                        # Remove the numbering
                        if '.' in line[:3]:
                            example = line.split('.', 1)[1].strip()
                        elif ':' in line[:3]:
                            example = line.split(':', 1)[1].strip()
                        else:
                            example = line[2:].strip()
                        
                        if example:
                            current_examples.append(example)
                    # If it's not clearly numbered but isn't empty, it might be an example too
                    elif line and not line.startswith('EXEMPLE') and not any(char.isdigit() for char in line[:2]):
                        current_examples.append(line)
            
            # Save the last set of examples if there are any
            if current_idx is not None and current_examples:
                examples_dict[current_idx] = current_examples
        
        # Ensure we have examples for all meanings
        for i in range(len(meanings)):
            if i not in examples_dict or not examples_dict[i]:
                word = meanings[i]["word"]
                examples_dict[i] = [f"Nu am putut genera exemple pentru sensul cuvântului '{word}'."]
        
        return examples_dict
        
    except Exception as e:
        logger.error(f"Error generating batch examples: {str(e)}")
        return {i: [f"Nu am putut genera exemple pentru sensul cuvântului '{meanings[i]['word']}'."] 
                for i in range(len(meanings))}