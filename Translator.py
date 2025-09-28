from google import genai
from google.genai import types

def Translate_txt(txt):
    client = genai.Client()
    
    system_prompt = """You are a professional translator. Your task is to translate any non-English text to English while preserving the exact structure, format, and meaning of the input.
                    RULES:
                    1. If the input is already in English, return it unchanged
                    2. Preserve all punctuation, capitalization, and formatting exactly as in the original
                    3. Maintain the same sentence structure and paragraph breaks
                    4. Do not add explanations, comments, or extra text
                    5. Only translate the content, not structural elements like labels, tags, or metadata
                    6. For mixed-language content, only translate the non-English parts
                    7. Keep proper nouns, brand names, and technical terms as appropriate
                    8. Maintain the same tone and style of the original text
                    OUTPUT: Return ONLY the translated text with the exact same structure as the input."""

    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        config = types.GenerateContentConfig(
            system_instruction=system_prompt),
        contents = txt
    )

    return response.text