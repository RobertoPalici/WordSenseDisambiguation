import logging
import re
import requests
from fastapi import HTTPException
from typing import Dict, List

from ..utils.config import settings

logger = logging.getLogger('backend.enrichment.openai_client')

API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


def _call_deepseek_api(messages: List[Dict[str, str]]) -> str:
    if not settings.OPENROUTER_API_KEY:
        logger.error("OpenRouter API key is not set.")
        raise HTTPException(status_code=503, detail="OpenRouter API key missing")

    payload = {
        "model": settings.ENRICHMENT_MODEL,
        "messages": messages
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=503, detail="Failed to fetch response from DeepSeek API")
    except Exception as e:
        logger.error(f"Exception during DeepSeek API call: {str(e)}")
        raise HTTPException(status_code=503, detail="Failed to call DeepSeek API")


def generate_batch_explanations(meanings: List[Dict]) -> Dict[int, str]:
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
    Fiecare explicație ar trebui să fie scrisă în română și să aibă 3-5 propoziții.
    Formatează astfel:
    EXPLICAȚIA 1: [explicația]
    EXPLICAȚIA 2: [explicația]
    ...
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": batch_prompt}
    ]

    try:
        if settings.ENRICHMENT_MOCK_API:
            raise Exception("Testing enrichment mock API")

        text = _call_deepseek_api(messages)
        explanations = {}
        pattern = r"EXPLICAȚIA\s+(\d+):\s*(.*?)(?=EXPLICAȚIA\s+\d+:|$)"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            for idx_str, content in matches:
                try:
                    idx = int(idx_str) - 1
                    explanations[idx] = content.strip()
                except Exception:
                    continue

        for i in range(len(meanings)):
            if i not in explanations:
                word = meanings[i]["word"]
                explanations[i] = f"Nu am putut genera o explicație pentru sensul cuvântului '{word}'."

        return explanations

    except Exception as e:
        logger.error(f"Error generating batch explanations: {str(e)}")
        return {i: f"Nu am putut genera o explicație pentru sensul cuvântului '{meanings[i]['word']}'." for i in range(len(meanings))}


def generate_batch_examples(meanings: List[Dict]) -> Dict[int, List[str]]:
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
    Formatează astfel:
    EXEMPLE PENTRU SENSUL 1:
    1. propoziție
    2. propoziție

    EXEMPLE PENTRU SENSUL 2:
    1. propoziție
    2. propoziție
    ...
    """

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": batch_prompt}
    ]

    try:
        if settings.ENRICHMENT_MOCK_API:
            raise Exception("Testing enrichment mock API")

        text = _call_deepseek_api(messages)
        examples_dict = {}
        pattern = r"EXEMPLE PENTRU SENSUL\s+(\d+):(.*?)(?=EXEMPLE PENTRU SENSUL\s+\d+:|$)"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            for idx_str, content in matches:
                idx = int(idx_str) - 1
                lines = [l.strip() for l in content.strip().split('\n') if l.strip()]
                examples = [re.sub(r"^\d+\.\s*", "", line) for line in lines]
                examples_dict[idx] = examples if examples else [f"Nu am putut genera exemple pentru sensul {idx+1}."]

        for i in range(len(meanings)):
            if i not in examples_dict or not examples_dict[i]:
                word = meanings[i]["word"]
                examples_dict[i] = [f"Nu am putut genera exemple pentru sensul cuvântului '{word}'."]
        return examples_dict

    except Exception as e:
        logger.error(f"Error generating batch examples: {str(e)}")
        return {i: [f"Nu am putut genera exemple pentru sensul cuvântului '{meanings[i]['word']}'."] for i in range(len(meanings))}
