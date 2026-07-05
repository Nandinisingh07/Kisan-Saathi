import os
import logging
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Blueprint, jsonify, request

logger = logging.getLogger("kisan_saathi")

firebase_bp = Blueprint("firebase", __name__)

# Initialize Firebase SDK (optional)
db = None
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    logger.info("Firebase SDK initialized successfully.")
except Exception as e:
    logger.warning("Firebase Admin SDK not available (CIBRC local DB fallback active): %s", e)


@firebase_bp.route("/api/verify-qr", methods=["POST"])
def verify_qr():
    """
    Product verification endpoint.

    Accepts JSON: {"qr_data": "<qr payload string>"}

    QR payload format: "product=<name>|company=<company>|reg=<CIB reg no>"

    Checks the scanned product+company+registration number combination against
    a reference list of CIBRC-registered pesticides sourced from publicly
    available PPQS publications and CIB&RC registration circulars.

    SCOPE: This does NOT detect counterfeit individual units. It only checks
    whether a product name + company + registration number combination is known
    to be a legitimately registered product. Absence from this list does NOT
    prove counterfeiting -- it means the combination could not be verified
    against our partial reference set.
    """
    from cibrc_registered_db import parse_qr_payload, lookup_product, ENTRY_COUNT

    req_data = request.get_json()
    if not req_data or "qr_data" not in req_data:
        return jsonify({
            "success": False,
            "error": "No QR data provided",
            "verified": False
        })

    raw_qr = req_data["qr_data"].strip()

    # Parse structured QR payload
    parsed = parse_qr_payload(raw_qr)

    scope_note = (
        "Checked against a reference list of registered pesticide products compiled "
        "from public regulatory sources (PPQS publications, ICAR crop protection guides). "
        "Product names and companies are verified; registration numbers in this demo list "
        "are illustrative. For authoritative lookup, use the PPQS CROP portal "
        "(cropuser.cgg.gov.in). ["
        + str(ENTRY_COUNT) + " entries]"
    )

    if parsed["malformed"]:
        return jsonify({
            "success": True,
            "verified": False,
            "product_id": raw_qr,
            "name": "Unknown / अज्ञात",
            "manufacturer": "--",
            "registration_no": "--",
            "category": "--",
            "active_ingredient": "--",
            "scope_note": scope_note,
            "status_hi": "QR code format invalid -- could not verify",
            "status_en": "Malformed QR code -- product could not be verified",
            "warnings": [
                "QR code does not contain product name and registration number. "
                "This is not a Kisan Saathi-compatible QR code. "
                "Expected format: product=<name>|company=<company>|reg=<reg_no>"
            ]
        })

    # Lookup in CIBRC reference database
    result = lookup_product(
        parsed["product_name"],
        parsed["company_name"],
        parsed["reg_no"]
    )

    if result["found"]:
        info = result["product_info"]
        return jsonify({
            "success": True,
            "verified": True,
            "product_id": raw_qr,
            "name": info["product_name"],
            "manufacturer": info["company"],
            "registration_no": info["reg_no"],
            "category": info["category"],
            "active_ingredient": info["active_ingredient"],
            "scope_note": scope_note,
            "status_hi": "Registered Product / पंजीकृत उत्पाद",
            "status_en": "Registered Product -- " + info["reg_no"],
            "warnings": []
        })
    else:
        return jsonify({
            "success": True,
            "verified": False,
            "product_id": raw_qr,
            "name": parsed["product_name"] or "Unknown",
            "manufacturer": parsed["company_name"] or "--",
            "registration_no": parsed["reg_no"] or "--",
            "category": "--",
            "active_ingredient": "--",
            "scope_note": scope_note,
            "status_hi": "Could not verify / असत्यापित",
            "status_en": "Could not verify -- not found in registered product list",
            "warnings": [
                "This product/registration number combination was not found in our "
                "CIBRC reference list (25 entries from PPQS publications). "
                "This does NOT confirm it is counterfeit -- our list is partial. "
                "For authoritative verification, check the PPQS CROP portal "
                "(cropuser.cgg.gov.in)."
            ]
        })
