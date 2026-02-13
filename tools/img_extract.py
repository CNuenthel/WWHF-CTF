import pytesseract
from PIL import Image

# Point pytesseract to the Tesseract installation
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR on Windows
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text
