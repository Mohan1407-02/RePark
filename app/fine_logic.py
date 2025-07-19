import re
from app.db import get_db_connection, get_phone_by_plate
from app.sms import send_sms

def check_if_fine(plate, conn):
    """
    Check if a vehicle is exempt. If not, issue fine and log it in the database.
    """
    # 🧼 Clean and standardize plate input
    cleaned_plate = plate.replace(" ", "").upper()

    # ✅ Exemption rule: Must be 10 chars, "G" at 5th position, starts with TN
    if cleaned_plate.startswith("TN") and len(cleaned_plate) == 10 and cleaned_plate[4] == "G":
        return "✅ Exempt (Government Vehicle)"

    # 🔍 Get phone number from database
    phone = get_phone_by_plate(cleaned_plate)

    if not phone:
        return "❌ Plate not found in database"

    # 🚨 Log the fine in the 'fines' table
    conn.execute("""
        INSERT INTO fines (plate, status, sms_sent, rto_result, timestamp)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (cleaned_plate, "🚨 Fine Issued", "Yes", "Valid"))  # You can modify rto_result as needed

    conn.commit()
    return "🚨 Fine Issued"

def process_plate(plate):
    conn = get_db_connection()
    cursor = conn.cursor()

    plate = plate.replace(" ", "").upper()
    row = cursor.execute("SELECT * FROM vehicles WHERE plate = ?", (plate,)).fetchone()

    if not row:
        status = "Plate not found in database."
        result = {
            "status": "not_found",
            "message": f"✅ Result: Plate {plate} not found in database."
        }
        sms_status = "No"
    else:
        is_exempt = re.match(r'^[A-Z]{2}[0-9]{2}G[0-9]{4}$', plate)
        if is_exempt:
            status = "Exempt - Government Vehicle"
            result = {
                "status": "exempt",
                "message": f"✅ Result: {plate} is exempt from fines (Govt Vehicle)."
            }
            sms_status = "No"
        else:
            status = "Fined - Non-Govt Vehicle"
            result = {
                "status": "fined",
                "message": f"🚨 Fine Issued: {plate} is not exempt."
            }
            phone = get_phone_by_plate(plate)
            sms_status = "No"
            if phone:
                try:
                    message = f"🚨 Fine Alert: Your vehicle {plate} has been fined at the airport."
                    send_sms(phone, message)
                    sms_status = "Yes"
                except Exception as e:
                    print(f"❌ SMS failed: {e}")

    cursor.execute(
        "INSERT INTO fines (plate, status, sms_sent) VALUES (?, ?, ?)",
        (plate, status, sms_status)
    )
    conn.commit()
    conn.close()

    return result
