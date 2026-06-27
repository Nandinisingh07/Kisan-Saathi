import qrcode

# Product IDs
product_ids = ["1234567890123", "9876543210986"]

# Generate QR codes
for pid in product_ids:
    img = qrcode.make(pid)
    img.save(f"{pid}.png")  # Saves QR code image
    print(f"✅ QR Code generated: {pid}.png")
