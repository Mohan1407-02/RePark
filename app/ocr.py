import easyocr
import cv2
import numpy as np
import re

reader = easyocr.Reader(['en'], gpu=False)

def read_plate(image_path, debug=False):
    try:
        image = cv2.imread(image_path)
        if image is None:
            print("❌ Failed to load image.")
            return None

        image = cv2.resize(image, (800, 600))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        results = reader.readtext(thresh, detail=1)

        print("\n🧪 Raw OCR Results:")
        for box, text, conf in results:
            print(f"  Detected: '{text}' | Confidence: {conf:.2f}")

        # Combine and clean text
        combined_text = "".join([t.replace(" ", "").replace("-", "") for _, t, _ in results])
        combined_text = combined_text.upper()

        if combined_text.startswith("0"):
            combined_text = "K" + combined_text[1:]

        # Regex match
        match = re.search(r'[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}', combined_text)
        plate = match.group(0) if match else None

        if plate:
            print(f"\n✅ Selected Plate: {plate}")
        else:
            print("\n❌ No valid plate match found.")

        # 🔍 Show visual debug window if enabled
        if debug:
            for box, text, conf in results:
                pts = np.array(box).astype(int)
                cv2.polylines(image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)

            cv2.imshow("OCR Detection Debug", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return plate

    except Exception as e:
        print(f"❌ OCR error: {e}")
        return None
