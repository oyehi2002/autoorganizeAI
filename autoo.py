import os
import re
import shutil
from pathlib import Path
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import PyPDF2
import concurrent.futures

print("Loading BLIP model...")
processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-large", use_fast=True)
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-large")
print("Model loaded successfully!")


class FileOrganizer:
    def __init__(self, processor, model):
        self.processor = processor
        self.model = model
        self.image_extensions = {'.jpg', '.jpeg',
                                 '.png', '.gif', '.bmp', '.tiff', '.webp'}
        self.pdf_extension = '.pdf'
        self.errorc = 0

    def generate_image_caption(self, image_path):
        """Generate caption for image file"""
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(images=image, return_tensors="pt")
            outputs = self.model.generate(
                **inputs,
                max_length=10,
                min_length=3,
                num_beams=3,
                do_sample=True,
                temperature=0.7
            )
            caption = self.processor.decode(
                outputs[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            print(f"Error generating caption for {image_path}: {str(e)}")
            return "unnamed_image"

    def extract_pdf_text(self, pdf_path, max_chars=100):
        """Extract first few lines of text from PDF for naming"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)

                # Check if PDF is encrypted first
                if reader.is_encrypted:
                    self.errorc += 1
                    return f"unable_to_read_{self.errorc}"

                # Check if PDF has pages
                if len(reader.pages) > 0:
                    text = reader.pages[0].extract_text()
                    text = ' '.join(text.split())
                    if len(text) > max_chars:
                        text = text[:max_chars]
                    return text if text.strip() else "pdf_document"
                else:
                    # PDF exists but has no pages
                    self.errorc += 1
                    return f"empty_pdf_{self.errorc}"

        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {str(e)}")
            self.errorc += 1
            return f"pdf_document_{self.errorc}"

    def sanitize_filename(self, text, max_length=50):
        """Convert text to safe filename"""
        text = re.sub(r'[<>:"/\\|?*]', '', text)
        text = text.replace(' ', '_')
        text = re.sub(r'_+', '_', text)
        text = text.strip('_')

        # Limit length
        if len(text) > max_length:
            text = text[:max_length]

        return text if text else "unnamed_file"

    def get_unique_filepath(self, directory, filename):
        """Generate unique filepath - simplified"""
        base = Path(directory) / filename
        counter = 1

        while base.exists():
            stem, ext = base.stem, base.suffix
            base = Path(directory) / f"{stem}_{counter}{ext}"
            counter += 1

        return str(base)

    def process_file(self, file_path, destination_folder, file_type):
        """Universal file processor"""
        try:
            print(f"Processing {file_type}: {os.path.basename(file_path)}")

            # Generate name based on file type
            if file_type == "image":
                content = self.generate_image_caption(file_path)
            else:  # PDF
                content = self.extract_pdf_text(file_path)

            safe_name = self.sanitize_filename(content)
            original_ext = Path(file_path).suffix.lower()
            new_filename = f"{safe_name}{original_ext}"
            new_path = self.get_unique_filepath(
                destination_folder, new_filename)

            shutil.move(file_path, new_path)
            print(
                f"✓ Moved to: {os.path.basename(new_path)} | Content: {content[:50]}...")

            return {"original": file_path, "new": new_path, "content": content}

        except Exception as e:
            print(f"✗ Error processing {file_type} {file_path}: {str(e)}")
            return None

    def organize_files(self, source_folder="Downloads", create_in_source=True):
        """Main function to organize files"""
        source_path = Path.home() / \
            source_folder if source_folder == "Downloads" else Path(
                source_folder)

        if not source_path.exists():
            print(f"Source folder {source_path} doesn't exist!")
            return

        # Setup destinations
        base = source_path if create_in_source else Path.cwd()
        images_folder = base / "Images"
        images_folder.mkdir(exist_ok=True)
        pdf_folder = base / "PDFs"
        pdf_folder.mkdir(exist_ok=True)
        # Collect files by type
        files_to_process = {
            "image": [f for f in source_path.iterdir() if f.is_file() and f.suffix.lower() in self.image_extensions],
            "pdf": [f for f in source_path.iterdir() if f.is_file() and f.suffix.lower() == '.pdf']
        }

        print(
            f"Found {len(files_to_process['image'])} images, {len(files_to_process['pdf'])} PDFs")

        for file_type, file_list in files_to_process.items():
            if not file_list:
                continue

            destination = images_folder if file_type == "image" else pdf_folder
            print(f"\n=== Processing {len(file_list)} {file_type}s ===")

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(self.process_file, str(
                    f), str(destination), file_type) for f in file_list]
                results = [future.result() for future in concurrent.futures.as_completed(
                    futures) if future.result()]

            print(f"Successfully processed {len(results)} {file_type}s")

        print("\n🎉 File organization complete!")


def main():
    organizer = FileOrganizer(processor, model)

    # You can change these settings as a user:
    # or provide full path like "/Users/yourname/Downloads" wherever you wanna organize
    source_folder = "Downloads"
    # True = create folders inside Downloads, False = create in current directory
    create_in_source = True

    print(f"Organizing files from: {source_folder}")
    organizer.organize_files(source_folder, create_in_source)


if __name__ == "__main__":
    main()
