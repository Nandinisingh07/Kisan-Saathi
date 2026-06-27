import os
import logging
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Blueprint, jsonify, request

logger = logging.getLogger("kisan_saathi")

firebase_bp = Blueprint("firebase", __name__)

# Initialize Firebase SDK
db = None
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase SDK initialized successfully.")
except Exception as e:
    logger.warning(f"Failed to initialize Firebase Admin SDK (Local mock fallback will be used): {e}")

@firebase_bp.route("/api/verify-qr", methods=["POST"])
def verify_qr():
    req_data = request.get_json()
    if not req_data or "qr_data" not in req_data:
        return jsonify({"success": False, "error": "No QR data provided", "verified": False})
        
    product_id = req_data["qr_data"].strip()
    warnings = []
    
    # 1. Fallback to local mock db if Firebase SDK could not initialize
    if db is None:
        logger.warning("Firebase DB not initialized. Simulating verification.")
        # Local verification simulation
        if product_id in ["1234567890123", "9876543210986"]:
            return jsonify({
                "success": True,
                "verified": True,
                "product_id": product_id,
                "name": "Super Urea Premium 50KG",
                "manufacturer": "Kisan Fertilizers Ltd",
                "batch": "B-2026-X9",
                "expiry": "2028-12-31",
                "warnings": []
            })
        else:
            return jsonify({
                "success": True,
                "verified": False,
                "product_id": product_id,
                "name": "Unknown Fake Product",
                "manufacturer": "Unregistered Manufacturer",
                "batch": "N/A",
                "expiry": "N/A",
                "warnings": ["Warning: This product is not registered in our database. It might be counterfeit!"]
            })
            
    try:
        # 2. Query Firestore collection "products" where document ID = product_id
        doc_ref = db.collection("products").document(product_id)
        doc = doc_ref.get()
        
        if doc.exists:
            product = doc.to_dict()
            name = product.get("name", "Agricultural Item")
            manufacturer = product.get("manufacturer", "Registered Manufacturer")
            batch = product.get("batch", "N/A")
            expiry = product.get("expiry", "")
            verified = product.get("verified", True)
            
            # Check expiry field
            if expiry:
                try:
                    expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
                    if datetime.date.today() > expiry_date:
                        verified = False
                        warnings.append("⚠️ चेतावनी: यह उत्पाद समाप्त हो चुका है! कृपया इसका उपयोग न करें। (This product has expired! Do not use.)")
                except ValueError:
                    logger.warning(f"Invalid expiry date format: {expiry} for product {product_id}")
            
            p_warnings = product.get("warnings", [])
            if isinstance(p_warnings, list):
                warnings.extend(p_warnings)
                
            return jsonify({
                "success": True,
                "verified": verified,
                "product_id": product_id,
                "name": name,
                "manufacturer": manufacturer,
                "batch": batch,
                "expiry": expiry,
                "warnings": warnings
            })
        else:
            return jsonify({
                "success": True,
                "verified": False,
                "product_id": product_id,
                "name": "Unknown Fake Product",
                "manufacturer": "Unregistered Manufacturer",
                "batch": "N/A",
                "expiry": "N/A",
                "warnings": ["⚠️ चेतावनी: यह उत्पाद हमारे डेटाबेस में पंजीकृत नहीं है। यह नकली हो सकता है! (Warning: This product is not registered in our database.)"]
            })
            
    except Exception as e:
        logger.error(f"Error querying Firestore database: {e}")
        return jsonify({"success": False, "error": str(e), "verified": False})
