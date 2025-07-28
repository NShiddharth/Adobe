import os
import json
import traceback

from app.modules.layout_parser import LayoutParser
from app.modules.ocr_handler import OcrHandler
from app.modules.heading_classifier import HeadingClassifier
from app.modules.postprocessor import Postprocessor
from app.utils.config import TESSERACT_CONFIG

def main():
    input_directory = '/app/input'
    output_directory = '/app/output'

    os.makedirs(output_directory, exist_ok=True)
    print(f"Input directory: {input_directory}")
    print(f"Output directory: {output_directory}")

    ocr_handler = OcrHandler()
    layout_parser = LayoutParser(ocr_handler)
    heading_classifier = HeadingClassifier()

    if not heading_classifier.pipeline:
        print("Error: Heading Classifier model failed to load. Cannot proceed.")
        return

    for filename in os.listdir(input_directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_directory, filename)
            json_output_filename = filename.replace('.pdf', '.json')
            json_output_path = os.path.join(output_directory, json_output_filename)

            print(f"\nProcessing PDF: {filename}")

            try:
                primary_lang_for_pdf = 'eng'

                extracted_blocks_with_features = layout_parser.extract_text_blocks_with_features(
                    pdf_path=pdf_path,
                    lang=primary_lang_for_pdf + '+eng'
                )

                classified_blocks = heading_classifier.predict(extracted_blocks_with_features)

                postprocessor = Postprocessor(classified_blocks)
                final_outline, document_title = postprocessor.create_outline()

                final_output_data = {
                    "title": document_title,
                    "outline": final_outline
                }

                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(final_output_data, f, ensure_ascii=False, indent=2)

                print(f"Successfully processed {filename}. Output saved to {json_output_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                traceback.print_exc()

if __name__ == "__main__":
    main()
