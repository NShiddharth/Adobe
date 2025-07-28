import os
import json
from deep_translator import GoogleTranslator
import time
from pathlib import Path

INPUT_DIR = "output_jsons"
OUTPUT_DIR = "training_datasets"

SUPPORTED_LANG_MAP = {
    "afr": "af", "amh": "am", "ara": "ar", "asm": "as", "ben": "bn",
    "bul": "bg", "cat": "ca", "ceb": "ceb", "ces": "cs", "chi_sim": "zh-CN",
    "chi_tra": "zh-TW", "dan": "da", "deu": "de", "ell": "el", "eng": "en",
    "fas": "fa", "fin": "fi", "fra": "fr", "guj": "gu", "heb": "iw",
    "hin": "hi", "ind": "id", "ita": "it", "jpn": "ja", "kan": "kn",
    "kat": "ka", "kor": "ko", "lav": "lv", "mal": "ml", "mar": "mr",
    "msa": "ms", "nep": "ne", "nld": "nl", "pol": "pl", "por": "pt",
    "rus": "ru", "sin": "si", "spa": "es", "swe": "sv", "tam": "ta",
    "tel": "te", "tha": "th", "tur": "tr", "ukr": "uk", "urd": "ur",
    "vie": "vi", "yor": "yo"
}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    try:
        source_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
        if not source_files:
            print(f"No .json files found in the '{INPUT_DIR}' directory.")
            return
    except FileNotFoundError:
        print(f"Error: Input directory not found at '{INPUT_DIR}'")
        return

    for source_filename in source_files:
        input_filepath = os.path.join(INPUT_DIR, source_filename)
        pdf_name = Path(source_filename).stem

        try:
            with open(input_filepath, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
            print(f"Loaded {len(data_list)} records from {source_filename}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from '{source_filename}'. Skipping.")
            continue
        except Exception as e:
            print(f"Error loading '{source_filename}': {e}. Skipping.")
            continue

        for lang_key, google_code in SUPPORTED_LANG_MAP.items():
            print(f"Translating '{pdf_name}' to {lang_key.upper()}...")
            translated_data = []

            if lang_key == "eng":
                for item in data_list:
                    new_item = item.copy()
                    new_item["lang"] = lang_key
                    translated_data.append(new_item)
            else:
                translator = GoogleTranslator(source='en', target=google_code)
                for item in data_list:
                    new_item = item.copy()
                    original_text = item.get("text", "")
                    if original_text.strip():
                        try:
                            time.sleep(0.1)
                            new_item["text"] = translator.translate(original_text)
                        except Exception as e:
                            print(f"Translation error for '{original_text[:20]}...': {e}")
                            new_item["text"] = original_text
                    new_item["lang"] = lang_key
                    translated_data.append(new_item)

            output_filename = f"{lang_key}_{pdf_name}.jsonl"
            jsonl_file_path = os.path.join(OUTPUT_DIR, output_filename)

            with open(jsonl_file_path, "w", encoding="utf-8") as f:
                for entry in translated_data:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

            print(f"Saved: {jsonl_file_path}")

if __name__ == "__main__":
    main()
