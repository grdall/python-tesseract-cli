# python-tesseract-cli

CLI for Tesseract OCR.

Input a directory when scanning to scan all images. Hardcoded output directory to ./text from wherever the image folder was. If the different images in the directory are in multiple languages, split them up by language (better result when matching language in image, inputting "english" as language will not read swedish "ë" or similar, will just write "e" or "�"). 