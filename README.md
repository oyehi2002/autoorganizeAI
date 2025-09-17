# AutoOrganizeAI

A Python script that automatically organizes your PDFs and images by renaming them based on their content.

## What it does

- **PDFs**: Reads text from the first page and creates meaningful filenames
- **Images**: Uses AI to generate captions and rename files accordingly  
- **Smart handling**: Deals with encrypted/corrupted files gracefully
- **Batch processing**: Handles multiple files efficiently


## Usage

1. Put the script in any folder
2. Run it.
   
By default, it scans your Downloads folder and creates:
- `PDFs/` folder for organized PDF files
- `Images/` folder for organized image files

## Supported formats

- **Images**: JPG, JPEG, PNG, BMP, TIFF, WEBP
- **PDFs**: All types including password-protected ones

## Configuration

Edit these variables in the script to customize:
- `source_folder` - change from "Downloads" to any folder
- `create_in_source` - set to False to create folders in current directory

## How it works

The script extracts meaningful content from your files and uses that to create organized, readable filenames. Encrypted or unreadable files get safe fallback names.

## Requirements

- Python 3.7+
- ~2GB disk space for AI models (downloaded automatically)
- Internet connection for first run

---

*First run takes a few minutes to download the image recognition model.*

