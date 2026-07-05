import qrcode

products = ["1234567890123", "9876543210986", "1111111111111"]

for pid in products:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(pid)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    filename = f"{pid}.png"
    img.save(filename)
    print(f"Generated QR code: {filename}")
