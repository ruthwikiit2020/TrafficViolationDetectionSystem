from paddleocr import PaddleOCR
import cv2
from groq import Groq

# Initialize PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# Set up Groq API
groq_client = Groq(api_key="") #GROQ API KEY


def correct_with_groq(plate_text):
    """
    Uses Groq API to correct the OCR-extracted license plate text,
    returning only the corrected license plate string.
    """
    response = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {
                "role": "system",
                "content": ("You are an expert in correcting OCR-extracted license plates. "
                            "Return only the corrected license plate in a single word or number, "
                            "without any additional explanation or commentary.")
            },
            {
                "role": "user",
                "content": f"The OCR detected license plate is: {plate_text}. Please return only the corrected license plate."
            }
        ],
        max_tokens=20
    )
    return response.choices[0].message.content.strip()


def predict_number_plate(image, confidence_threshold=0.7):
    """
    Extracts text from a license plate image using PaddleOCR and validates/corrects it using Groq if necessary.
    Returns a tuple (plate_text, average_confidence).
    """
    result = ocr.ocr(image, cls=True)
    if not result:
        return "", 0

    detected_texts = []
    confidences = []

    for line in result:
        if line is None:
            continue
        for word_info in line:
            if not word_info:
                continue
            try:
                text, conf = word_info[1]
            except Exception as e:
                continue
            if conf >= confidence_threshold:
                detected_texts.append(text)
                confidences.append(conf)
            else:
                print(f"Low confidence ({conf:.2f}) for: {text}, sending to Groq for correction...")
                corrected_text = correct_with_groq(text)
                detected_texts.append(corrected_text)
                confidences.append(1.0)  # Assume corrected text has high confidence

    if detected_texts:
        plate_text = " ".join(detected_texts)
        avg_conf = sum(confidences) / len(confidences)
    else:
        plate_text = ""
        avg_conf = 0

    return plate_text, avg_conf

