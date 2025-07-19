from app.ocr import read_plate

# Path to test image
image_path = "static/uploads/test.jpeg"

# Run OCR
plate = read_plate(image_path)

# Show result
if plate:
    print(f"OCR result: {plate}")
else:
    print("❌ No plate text detected.")
