from app.ocr import read_plate
from app.fine_logic import process_plate

plate = read_plate("static/uploads/TN42AB5460.jpg", debug=True)
print("Detected plate:", plate)
if plate:
    print(process_plate(plate)["message"])
else:
    print("❌ No valid plate recognized.")
