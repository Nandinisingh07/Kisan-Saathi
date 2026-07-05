"""
CIBRC Registered Pesticide Reference Database
==============================================

HONEST DATA PROVENANCE STATEMENT
----------------------------------
This file contains 25 entries. Their source status is explicitly marked per
entry using the "source_verified" field:

  "illustrative -- not independently verified"
    The product name, company, and active ingredient are real and well-known in
    Indian agriculture, but the specific registration number used here was
    constructed to be plausible (matching real CIB&RC number formats) and has
    NOT been independently verified against a specific traceable government
    document (gazette notification, PPQS annual report page, etc.).
    These entries exist so the demo has scannable QR codes. Do not treat the
    registration number as authoritative.

  "PPQS/ICAR public literature -- product and company verified, reg no illustrative"
    The product name and manufacturer are well-established and appear in ICAR
    crop protection recommendations and PPQS-linked materials, but the specific
    numeric registration number has not been traced to a specific gazette page.

  "PPQS crop protection schedule -- product class verified"
    The product's pesticide class and approval for listed crops appears in PPQS
    IPM schedules, but the specific trade-name registration number is not
    independently confirmed here.

SCOPE LIMITATION (also displayed in UI):
  This lookup checks whether the scanned product+company+reg combination
  appears in this reference set. It does NOT:
    - Query the live CROP portal (login required: cropuser.cgg.gov.in)
    - Guarantee any physical unit is genuine (no serialisation)
    - Cover the ~10,000+ registered products in the full CROP database

  A match means: "This combination is in our reference set."
  No match means: "Could not verify against this partial list."
  No-match does NOT mean confirmed counterfeit.
"""

# Format per entry:
#   key: "PRODUCT_NAME|||COMPANY_NAME|||REG_NO"  (all UPPERCASE, stripped)
#   value: dict with display-ready fields
#
# QR payload format: "product=<name>|company=<company>|reg=<reg_no>"

CIBRC_REGISTERED_PRODUCTS = {

    # --- Fungicides ---

    "SAAF|||UPL LIMITED|||FMC-341": {
        "product_name": "Saaf (Carbendazim 12% + Mancozeb 63% WP)",
        "company": "UPL Limited",
        "reg_no": "FMC-341",
        "category": "Fungicide",
        "active_ingredient": "Carbendazim 12% + Mancozeb 63% WP",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Saaf by UPL is a widely known and genuinely registered fungicide in India. "
            "The specific reg. no. FMC-341 is illustrative and has not been traced to "
            "a specific gazette notification or PPQS document page."
        ),
    },

    "KAVACH|||SYNGENTA INDIA LIMITED|||CR-428": {
        "product_name": "Kavach (Chlorothalonil 75% WP)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-428",
        "category": "Fungicide",
        "active_ingredient": "Chlorothalonil 75% WP",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Kavach (Chlorothalonil 75% WP) by Syngenta is a real, widely used registered "
            "fungicide in India. Reg. no. CR-428 is illustrative."
        ),
    },

    "CONTAF PLUS|||TATA RALLIS INDIA LIMITED|||CIB-1089": {
        "product_name": "Contaf Plus (Hexaconazole 5% SC)",
        "company": "Tata Rallis India Limited",
        "reg_no": "CIB-1089",
        "category": "Fungicide",
        "active_ingredient": "Hexaconazole 5% SC",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Contaf Plus by Tata Rallis (now Rallis India) is a real registered product. "
            "Reg. no. CIB-1089 is illustrative."
        ),
    },

    "TILT|||SYNGENTA INDIA LIMITED|||CR-216": {
        "product_name": "Tilt (Propiconazole 25% EC)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-216",
        "category": "Fungicide",
        "active_ingredient": "Propiconazole 25% EC",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Tilt (Propiconazole 25% EC) by Syngenta appears in ICAR crop protection "
            "recommendations for wheat and rice. Reg. no. CR-216 is illustrative."
        ),
    },

    "SCORE|||SYNGENTA INDIA LIMITED|||CR-507": {
        "product_name": "Score (Difenoconazole 25% EC)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-507",
        "category": "Fungicide",
        "active_ingredient": "Difenoconazole 25% EC",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Score (Difenoconazole 25% EC) by Syngenta is a real registered fungicide. "
            "Reg. no. CR-507 is illustrative."
        ),
    },

    "BAVISTIN|||BASF INDIA LIMITED|||GR-218": {
        "product_name": "Bavistin (Carbendazim 50% WP)",
        "company": "BASF India Limited",
        "reg_no": "GR-218",
        "category": "Fungicide",
        "active_ingredient": "Carbendazim 50% WP",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Bavistin (Carbendazim 50% WP) by BASF is one of the oldest registered "
            "systemic fungicides in India, referenced in ICAR and PPQS IPM schedules. "
            "Reg. no. GR-218 is illustrative."
        ),
    },

    "MANCOZEB 75 WP|||COROMANDEL INTERNATIONAL LIMITED|||CIB-882": {
        "product_name": "Mancozeb 75% WP",
        "company": "Coromandel International Limited",
        "reg_no": "CIB-882",
        "category": "Fungicide",
        "active_ingredient": "Mancozeb 75% WP",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Mancozeb 75% WP by Coromandel is a real registered product. "
            "Reg. no. CIB-882 is illustrative."
        ),
    },

    # --- Insecticides ---

    "SOLOMON|||BAYER CROPSCIENCE LIMITED|||BCL-1241": {
        "product_name": "Solomon (Imidacloprid 17.8% SL + Beta-Cyfluthrin)",
        "company": "Bayer CropScience Limited",
        "reg_no": "BCL-1241",
        "category": "Insecticide",
        "active_ingredient": "Imidacloprid 17.8% SL + Beta-Cyfluthrin",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Solomon by Bayer CropScience is a real combination insecticide registered "
            "in India. Reg. no. BCL-1241 is illustrative."
        ),
    },

    "CONFIDOR|||BAYER CROPSCIENCE LIMITED|||BCL-892": {
        "product_name": "Confidor (Imidacloprid 17.8% SL)",
        "company": "Bayer CropScience Limited",
        "reg_no": "BCL-892",
        "category": "Insecticide",
        "active_ingredient": "Imidacloprid 17.8% SL",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Confidor (Imidacloprid 17.8% SL) by Bayer is referenced in ICAR pest "
            "management recommendations and PPQS IPM schedules. "
            "Reg. no. BCL-892 is illustrative."
        ),
    },

    "ACTARA|||SYNGENTA INDIA LIMITED|||CR-621": {
        "product_name": "Actara (Thiamethoxam 25% WG)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-621",
        "category": "Insecticide",
        "active_ingredient": "Thiamethoxam 25% WG",
        "source_verified": "PPQS crop protection schedule -- product class verified",
        "source_note": (
            "Actara (Thiamethoxam 25% WG) by Syngenta is referenced in PPQS/ICAR "
            "IPM schedules for multiple crops including cotton and rice. "
            "Reg. no. CR-621 is illustrative."
        ),
    },

    "KARATE|||SYNGENTA INDIA LIMITED|||CR-385": {
        "product_name": "Karate (Lambda-Cyhalothrin 5% EC)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-385",
        "category": "Insecticide",
        "active_ingredient": "Lambda-Cyhalothrin 5% EC",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Karate (Lambda-Cyhalothrin 5% EC) by Syngenta is a real, widely used "
            "registered insecticide appearing in ICAR crop protection guides. "
            "Reg. no. CR-385 is illustrative."
        ),
    },

    "CHLORPYRIPHOS 20 EC|||UPL LIMITED|||FMC-102": {
        "product_name": "Chlorpyriphos 20% EC",
        "company": "UPL Limited",
        "reg_no": "FMC-102",
        "category": "Insecticide",
        "active_ingredient": "Chlorpyrifos 20% EC",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Chlorpyrifos 20% EC by UPL is one of the most widely registered "
            "insecticides in India, referenced in PPQS schedules and ICAR manuals. "
            "Reg. no. FMC-102 is illustrative."
        ),
    },

    "MONOCIL|||TATA RALLIS INDIA LIMITED|||CIB-344": {
        "product_name": "Monocil (Monocrotophos 36% SL)",
        "company": "Tata Rallis India Limited",
        "reg_no": "CIB-344",
        "category": "Insecticide",
        "active_ingredient": "Monocrotophos 36% SL",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Monocil (Monocrotophos 36% SL) by Rallis India is a real registered "
            "insecticide. Reg. no. CIB-344 is illustrative. "
            "Note: Monocrotophos is restricted/banned for certain uses under Insecticides Act."
        ),
    },

    "TRACER|||DOW AGROSCIENCES INDIA|||DAI-219": {
        "product_name": "Tracer (Spinosad 45% SC)",
        "company": "Dow AgroSciences India",
        "reg_no": "DAI-219",
        "category": "Insecticide",
        "active_ingredient": "Spinosad 45% SC",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Tracer (Spinosad 45% SC) by Dow AgroSciences is a real bio-derived "
            "insecticide registered in India. Reg. no. DAI-219 is illustrative."
        ),
    },

    "CORAGEN|||FMC INDIA LIMITED|||FMC-891": {
        "product_name": "Coragen (Chlorantraniliprole 18.5% SC)",
        "company": "FMC India Limited",
        "reg_no": "FMC-891",
        "category": "Insecticide",
        "active_ingredient": "Chlorantraniliprole 18.5% SC",
        "source_verified": "PPQS crop protection schedule -- product class verified",
        "source_note": (
            "Coragen (Chlorantraniliprole 18.5% SC) by FMC is referenced in PPQS/ICAR "
            "IPM schedules for rice and other crops. "
            "Reg. no. FMC-891 is illustrative."
        ),
    },

    # --- Herbicides ---

    "ROUNDUP|||MONSANTO INDIA LIMITED|||MIL-483": {
        "product_name": "Roundup (Glyphosate 41% SL)",
        "company": "Monsanto India Limited",
        "reg_no": "MIL-483",
        "category": "Herbicide",
        "active_ingredient": "Glyphosate 41% SL",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Roundup (Glyphosate 41% SL) by Monsanto India is a real, widely registered "
            "non-selective herbicide referenced in ICAR weed management guides. "
            "Reg. no. MIL-483 is illustrative."
        ),
    },

    "TARGA SUPER|||SYNGENTA INDIA LIMITED|||CR-298": {
        "product_name": "Targa Super (Quizalofop-p-ethyl 5% EC)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-298",
        "category": "Herbicide",
        "active_ingredient": "Quizalofop-p-ethyl 5% EC",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Targa Super by Syngenta is a real registered herbicide for soybean and "
            "other broadleaf crops. Reg. no. CR-298 is illustrative."
        ),
    },

    "NOMINEE GOLD|||BAYER CROPSCIENCE LIMITED|||BCL-1102": {
        "product_name": "Nominee Gold (Bispyribac-Sodium 10% SC)",
        "company": "Bayer CropScience Limited",
        "reg_no": "BCL-1102",
        "category": "Herbicide",
        "active_ingredient": "Bispyribac-Sodium 10% SC",
        "source_verified": "PPQS crop protection schedule -- product class verified",
        "source_note": (
            "Nominee Gold (Bispyribac-Sodium 10% SC) by Bayer is referenced in PPQS/ICAR "
            "weed management schedules for paddy. Reg. no. BCL-1102 is illustrative."
        ),
    },

    "2 4 D AMINE SALT|||UPL LIMITED|||FMC-067": {
        "product_name": "2,4-D Amine Salt 58% SL",
        "company": "UPL Limited",
        "reg_no": "FMC-067",
        "category": "Herbicide",
        "active_ingredient": "2,4-D Amine Salt 58% SL",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "2,4-D is one of the oldest registered selective herbicides in India; "
            "UPL's formulation is referenced in ICAR weed management guides. "
            "Reg. no. FMC-067 is illustrative."
        ),
    },

    # --- Systemic Fungicides (combined) ---

    "RIDOMIL GOLD|||SYNGENTA INDIA LIMITED|||CR-712": {
        "product_name": "Ridomil Gold (Metalaxyl-M 4% + Mancozeb 64% WP)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-712",
        "category": "Fungicide",
        "active_ingredient": "Metalaxyl-M 4% + Mancozeb 64% WP",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Ridomil Gold by Syngenta is a real, registered systemic+contact fungicide "
            "widely used in India for downy mildew control. Reg. no. CR-712 is illustrative."
        ),
    },

    "DITHANE M-45|||DOW AGROSCIENCES INDIA|||DAI-087": {
        "product_name": "Dithane M-45 (Mancozeb 75% WP)",
        "company": "Dow AgroSciences India",
        "reg_no": "DAI-087",
        "category": "Fungicide",
        "active_ingredient": "Mancozeb 75% WP",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Dithane M-45 (Mancozeb 75% WP) by Dow is referenced in numerous ICAR crop "
            "protection manuals and PPQS publications. Reg. no. DAI-087 is illustrative."
        ),
    },

    "AMPLIGO|||SYNGENTA INDIA LIMITED|||CR-1087": {
        "product_name": "Ampligo (Chlorantraniliprole 10% + Lambda-Cyhalothrin 5% ZC)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-1087",
        "category": "Insecticide",
        "active_ingredient": "Chlorantraniliprole 10% + Lambda-Cyhalothrin 5% ZC",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Ampligo by Syngenta is a real registered combination insecticide used in "
            "India for lepidopteran pests. Reg. no. CR-1087 is illustrative."
        ),
    },

    "REEVA 5|||PI INDUSTRIES LIMITED|||PI-446": {
        "product_name": "Reeva 5 (Lambda-Cyhalothrin 5% EC)",
        "company": "PI Industries Limited",
        "reg_no": "PI-446",
        "category": "Insecticide",
        "active_ingredient": "Lambda-Cyhalothrin 5% EC",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Reeva 5 by PI Industries is a real registered pyrethroid insecticide in India. "
            "Reg. no. PI-446 is illustrative."
        ),
    },

    "AMISTAR|||SYNGENTA INDIA LIMITED|||CR-543": {
        "product_name": "Amistar (Azoxystrobin 23% SC)",
        "company": "Syngenta India Limited",
        "reg_no": "CR-543",
        "category": "Fungicide",
        "active_ingredient": "Azoxystrobin 23% SC",
        "source_verified": "PPQS/ICAR public literature -- product and company verified, reg no illustrative",
        "source_note": (
            "Amistar (Azoxystrobin 23% SC) by Syngenta is referenced in ICAR crop "
            "protection guides for rice and wheat. Reg. no. CR-543 is illustrative."
        ),
    },

    "PULSAR|||ATUL LIMITED|||ATL-331": {
        "product_name": "Pulsar (Imazethapyr 10% SL)",
        "company": "Atul Limited",
        "reg_no": "ATL-331",
        "category": "Herbicide",
        "active_ingredient": "Imazethapyr 10% SL",
        "source_verified": "illustrative -- not independently verified",
        "source_note": (
            "Pulsar (Imazethapyr 10% SL) by Atul Ltd is a real registered legume "
            "herbicide in India. Reg. no. ATL-331 is illustrative."
        ),
    },
}

# Number of entries
ENTRY_COUNT = len(CIBRC_REGISTERED_PRODUCTS)

# Source verification summary (for transparency reporting)
SOURCE_SUMMARY = {
    "total": ENTRY_COUNT,
    "ppqs_icar_verified": sum(
        1 for v in CIBRC_REGISTERED_PRODUCTS.values()
        if "PPQS" in v.get("source_verified", "") or "crop protection" in v.get("source_verified", "")
    ),
    "illustrative": sum(
        1 for v in CIBRC_REGISTERED_PRODUCTS.values()
        if "illustrative" in v.get("source_verified", "")
    ),
    "note": (
        "ALL registration numbers in this database are illustrative and have not been "
        "individually traced to a specific gazette notification page. The product names, "
        "companies, and active ingredients are real and well-established in Indian "
        "agriculture. Use the PPQS CROP portal (cropuser.cgg.gov.in) for authoritative "
        "registration number verification."
    ),
}


def lookup_product(product_name: str, company_name: str, reg_no: str) -> dict:
    """
    Look up a product in the CIBRC reference database.

    Args:
        product_name: Product trade name (case-insensitive)
        company_name: Manufacturer/registrant company name (case-insensitive)
        reg_no: CIB&RC registration number (case-insensitive)

    Returns:
        dict with keys: found (bool), product_info (dict or None)
    """
    def norm(s):
        return " ".join(str(s).upper().split())

    key = f"{norm(product_name)}|||{norm(company_name)}|||{norm(reg_no)}"

    if key in CIBRC_REGISTERED_PRODUCTS:
        return {"found": True, "product_info": CIBRC_REGISTERED_PRODUCTS[key]}

    # Fallback: match on product name + reg_no only (handles minor company name variants)
    pname_norm = norm(product_name)
    reg_norm = norm(reg_no)
    for db_key, db_val in CIBRC_REGISTERED_PRODUCTS.items():
        parts = db_key.split("|||")
        if len(parts) == 3 and norm(parts[0]) == pname_norm and norm(parts[2]) == reg_norm:
            return {"found": True, "product_info": db_val}

    return {"found": False, "product_info": None}


def parse_qr_payload(qr_string: str) -> dict:
    """
    Parse a QR code payload string into product name, company, reg_no.

    Expected format: "product=<name>|company=<company>|reg=<reg_no>"
    Returns: dict with keys product_name, company_name, reg_no (or None if malformed)
    """
    fields = {}
    if not qr_string:
        return {"product_name": None, "company_name": None, "reg_no": None, "malformed": True}

    for part in qr_string.split("|"):
        if "=" in part:
            k, _, v = part.partition("=")
            fields[k.strip().lower()] = v.strip()

    product_name = fields.get("product")
    company_name = fields.get("company")
    reg_no = fields.get("reg")

    malformed = not (product_name and reg_no)
    return {
        "product_name": product_name,
        "company_name": company_name or "",
        "reg_no": reg_no,
        "malformed": malformed
    }
