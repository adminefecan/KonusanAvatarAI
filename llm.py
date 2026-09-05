"""Ollama chat integration with Turkish-only response controls."""
import json
import os
import re
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
SYSTEM_PROMPT = (
    "Sen yalnızca Türkçe konuşan bir avatarsın. Cevabın yüzde yüz Türkçe olmalı. "
    "İngilizce, İspanyolca, Kürtçe veya başka hiçbir yabancı dilde kelime kullanma. "
    "ç, ğ, ı, İ, ö, ş ve ü harflerini normal Türkçe kelimelerde kullan; "
    "harfleri açıklama veya 'yumuşak g' diye yazma. "
    "Cümle sonunda rastgele yabancı kelime, ünlem veya anlamsız ek yazma. "
    "Kullanıcı ne sorarsa sorsun kısa, doğal ve anlaşılır Türkçeyle cevap ver. "
    "1-2 kısa cümle yeterli. Emoji, madde işareti, açıklama veya rol etiketi kullanma. "
    "Cevabını göndermeden önce son kelimenin Türkçe ve anlamlı olduğundan emin ol."
)


def _clean_response(text: str) -> str:
    text = text.strip().strip('"“”')
    text = re.sub(r"^(Avatar|Asistan)\s*:\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def answer(text: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": text,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0.2,
            "top_p": 0.8,
            "num_predict": 80,
            "repeat_penalty": 1.1,
        },
    }).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))
    return _clean_response(data.get("response", ""))
