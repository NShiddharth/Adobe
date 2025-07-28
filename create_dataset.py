import fitz
import re
import statistics
import json
import os
from pathlib import Path

PDF_INPUT_DIR = "input_pdf"
JSON_OUTPUT_DIR = "output_jsons"


class LayoutParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc_id = os.path.basename(pdf_path)

    def _get_page_avg_font_size(self, page):
        font_sizes = [
            span['size']
            for block in page.get_text("dict")["blocks"]
            for line in block.get("lines", [])
            for span in line.get("spans", []) if span['size'] > 0
        ]
        return statistics.mean(font_sizes) if font_sizes else 12.0

    def extract_text_blocks(self, max_pages=50):
        doc = fitz.open(self.pdf_path)
        all_blocks = []
        for page_num, page in enumerate(doc):
            if page_num >= max_pages:
                break

            avg_page_font_size = self._get_page_avg_font_size(page)
            page_blocks = page.get_text("dict")["blocks"]
            page_width = page.rect.width or 1
            page_height = page.rect.height or 1

            for i, block in enumerate(page_blocks):
                block_text = ""
                font_sizes, span_fonts = [], []

                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        block_text += span['text'] + " "
                        font_sizes.append(span['size'])
                        span_fonts.append(span['font'].lower())

                block_text = re.sub(r'\s+', ' ', block_text).strip()
                if not block_text:
                    continue

                avg_font_size = statistics.mean(font_sizes) if font_sizes else 0
                word_count = len(block_text.split())
                stripped_text = block_text.lstrip()
                first_char = stripped_text[0] if stripped_text else ''

                features = {
                    'font_size': avg_font_size,
                    'is_centered': float(abs((block['bbox'][0] + block['bbox'][2]) / 2 / page_width - 0.5) < 0.1),
                    'char_count': float(len(block_text)),
                    'x0_norm': block['bbox'][0] / page_width,
                    'height_norm': (block['bbox'][3] - block['bbox'][1]) / page_height,
                    'has_leading_digit_or_bullet': float(
                        first_char.isdigit() or first_char in ['•', '●', '☆', '-', '*']),
                    'relative_font_size_to_page_avg': avg_font_size / avg_page_font_size if avg_page_font_size > 0 else 1.0,
                    'is_bold': float(any("bold" in font for font in span_fonts)),
                    'is_italic': float(any("italic" in font or "oblique" in font for font in span_fonts)),
                    'line_count': float(len(block.get("lines", []))),
                    'y0_norm': block['bbox'][1] / page_height,
                    'line_gap_above_norm': 0.0,
                    'line_gap_below_norm': 0.0,
                    'contains_number': float(any(char.isdigit() for char in block_text)),
                    'ends_with_punctuation': float(block_text.endswith(('.', '?', '!'))),
                    'all_caps': float(block_text.isupper() and len(block_text) > 1),
                    'indentation': block['bbox'][0] / page_width,
                    'avg_word_length': sum(
                        len(word) for word in block_text.split()) / word_count if word_count > 0 else 0.0
                }

                all_blocks.append({
                    'doc_id': self.doc_id,
                    'page_num': page_num + 1,
                    'block_id': f"p{page_num + 1}_b{i}",
                    'text': block_text,
                    'lang': 'eng',
                    'features': features,
                    'label': 'UNLABELED'
                })
        doc.close()
        return all_blocks


def main():
    Path(PDF_INPUT_DIR).mkdir(exist_ok=True)
    Path(JSON_OUTPUT_DIR).mkdir(exist_ok=True)

    pdf_files = [f for f in os.listdir(PDF_INPUT_DIR) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in the '{PDF_INPUT_DIR}' directory. Please add some PDFs and run again.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process...")

    for pdf_file in pdf_files:
        pdf_input_path = os.path.join(PDF_INPUT_DIR, pdf_file)
        json_output_path = os.path.join(JSON_OUTPUT_DIR, f"{Path(pdf_file).stem}.json")

        print(f"\nProcessing '{pdf_input_path}'...")

        try:
            parser = LayoutParser(pdf_input_path)
            dataset = parser.extract_text_blocks()

            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(dataset, f, indent=2, ensure_ascii=False)

            print(f"Successfully created dataset with {len(dataset)} blocks.")
            print(f"Saved to: '{json_output_path}'")
        except Exception as e:
            print(f"Failed to process '{pdf_input_path}': {e}")

    print("Open the generated JSON files and manually change the 'UNLABELED' values to the correct labels (H1, H2, H3, Body).")


if __name__ == "__main__":
    main()
