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

    # Seed real CIB&RC registered products
    products = {
        "1234567890123": {
            "name": "Saaf Fungicide (Carbendazim 12% + Mancozeb 63% WP)",
            "manufacturer": "UPL Limited",
            "batch": "sample batch — illustrative",
            "expiry": "2028-12-31",
            "verified": True,
            "warnings": []
        },
        "9876543210986": {
            "name": "Contaf Plus (Hexaconazole 5% SC)",
            "manufacturer": "Tata Rallis India",
            "batch": "sample batch — illustrative",
            "expiry": "2027-06-30",
            "verified": True,
            "warnings": []
        },
        "1111111111111": {
            "name": "Solomon Insecticide (Beta-cyfluthrin + Imidacloprid)",
            "manufacturer": "Bayer CropScience India",
            "batch": "sample batch — illustrative",
            "expiry": "2026-12-31",
            "verified": True,
            "warnings": []
        },
        "2222222222222": {
            "name": "IFFCO NPK 12-32-16 Fertilizer",
            "manufacturer": "IFFCO Group",
            "batch": "sample batch — illustrative",
            "expiry": "2029-01-15",
            "verified": True,
            "warnings": []
        },
        "3333333333333": {
            "name": "Gromor NPK 14-35-14 Fertilizer",
            "manufacturer": "Coromandel International",
            "batch": "sample batch — illustrative",
            "expiry": "2024-05-01",  # Expired product
            "verified": True,
            "warnings": ["Expired: Do not apply to sensitive crops."]
        }
    }

    print("Uploading real products to Firestore...")
    for pid, data in products.items():
        try:
            db.collection("products").document(pid).set(data)
            print(f"Registered product {pid}: {data['name']}")
        except Exception as e:
            print(f"Failed to register product {pid}: {e}")
            
    print("Seed complete!")

if __name__ == "__main__":
    seed()
