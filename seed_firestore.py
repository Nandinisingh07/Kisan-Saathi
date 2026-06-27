import firebase_admin
from firebase_admin import credentials, firestore

def seed():
    print("Connecting to Firestore database...")
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        print(f"Failed to connect to Firebase. Make sure firebase_key.json is present and valid. Error: {e}")
        return

    # Seed 10 sample products
    products = {
        "1234567890123": {
            "name": "Super Urea Premium 50KG",
            "manufacturer": "Kisan Fertilizers Ltd",
            "batch": "B-2026-X9",
            "expiry": "2028-12-31",
            "verified": True,
            "warnings": []
        },
        "9876543210986": {
            "name": "Organic Neem Oil Pesticide (Concentrated)",
            "manufacturer": "Narmada Bio-Organics",
            "batch": "N-786-26",
            "expiry": "2027-06-30",
            "verified": True,
            "warnings": []
        },
        "1111111111111": {
            "name": "Mancozeb 75% WP Fungicide",
            "manufacturer": "Bharat Insecticides Ltd",
            "batch": "MNC-001",
            "expiry": "2026-12-31",
            "verified": True,
            "warnings": []
        },
        "2222222222222": {
            "name": "Potash Fertilizer NPK 0-0-50",
            "manufacturer": "IFFCO Group",
            "batch": "P-9988",
            "expiry": "2029-01-15",
            "verified": True,
            "warnings": []
        },
        "3333333333333": {
            "name": "Expired Ammonium Sulfate",
            "manufacturer": "Coromandel International",
            "batch": "AS-332",
            "expiry": "2024-05-01",  # Expired product
            "verified": True,
            "warnings": ["Expired: Do not apply to sensitive crops."]
        },
        "4444444444444": {
            "name": "DAP (Di-Ammonium Phosphate) Standard",
            "manufacturer": "NFL India",
            "batch": "DAP-8871",
            "expiry": "2027-09-20",
            "verified": True,
            "warnings": []
        },
        "5555555555555": {
            "name": "Imidacloprid 17.8% SL Insecticide",
            "manufacturer": "Tata Rallis India",
            "batch": "IMD-092",
            "expiry": "2027-03-10",
            "verified": True,
            "warnings": []
        },
        "6666666666666": {
            "name": "Glyphosate 41% SL Herbicide",
            "manufacturer": "Monsanto India Ltd",
            "batch": "GLY-441",
            "expiry": "2027-11-30",
            "verified": True,
            "warnings": ["Warning: Dangerous to aquatic environments. Keep away from water channels."]
        },
        "7777777777777": {
            "name": "Trichoderma Viride Bio-Fungicide",
            "manufacturer": "National Seeds Corp",
            "batch": "TV-776",
            "expiry": "2026-10-01",
            "verified": True,
            "warnings": []
        },
        "8888888888888": {
            "name": "Kalyan Sona Wheat Seeds Grade A",
            "manufacturer": "NSSC Seeds",
            "batch": "KSW-021",
            "expiry": "2026-08-30",
            "verified": True,
            "warnings": []
        }
    }

    print("Uploading sample products to Firestore...")
    for pid, data in products.items():
        try:
            db.collection("products").document(pid).set(data)
            print(f"Registered product {pid}: {data['name']}")
        except Exception as e:
            print(f"Failed to register product {pid}: {e}")
            
    print("Seed complete!")

if __name__ == "__main__":
    seed()
