import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from googletrans import Translator
import os
import tempfile
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import pandas as pd
import cv2


model = load_model("crop_disease_model.h5")
df = pd.read_csv("C:/Users/Nandini singh/Downloads/archive (2)/Datasets/Pesticide_Dataset/Pesticides.csv")
df['Disease'] = df['Disease'].str.strip()

class_labels = sorted(os.listdir("C:/Users/Nandini singh/Downloads/archive (1)/PlantVillage"))
translator = Translator()
lang_dict = {"English": "en", "Hindi": "hi", "Marathi": "mr", "Gujarati": "gu"}


window = tk.Tk()
window.title("🌿 Crop Disease Detector & Pesticide Advisor")
window.geometry("500x400")

selected_lang = tk.StringVar()
selected_lang.set("Hindi")

def predict_image(img_path):
    try:
        
        img = image.load_img(img_path, target_size=(128, 128))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        
        prediction = model.predict(img_array)[0]
        predicted_class = class_labels[np.argmax(prediction)]

        if "_" in predicted_class:
            try:
                crop, disease = predicted_class.split("_")
            except ValueError:
                crop = predicted_class
                disease = "Unknown"
        else:
            crop = predicted_class
            disease = "Healthy"

        crop = crop.replace("_", " ").strip()
        disease = disease.replace("_", " ").strip()

        
        filtered = df[df["Disease"].str.lower() == disease.lower()]
        pesticide = filtered["Pesticide"].values[0] if not filtered.empty else "No recommendation found"

        message = f"Crop: {crop}, Disease: {disease}, Recommended Pesticide: {pesticide}"
        print("🧠", message)

        lang_code = lang_dict[selected_lang.get()]
        translated = translator.translate(message, src='en', dest=lang_code).text
        print("🌐 Translation:", translated)

        messagebox.showinfo("Prediction", translated)

    except Exception as e:
        print("❌ Error:", e)
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


def upload_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        predict_image(file_path)


def capture_image():
    try:
        cam = cv2.VideoCapture(0)  

        if not cam.isOpened():
            raise Exception("Internal camera not detected. Please ensure it is enabled.")

        cv2.namedWindow("📷 Press SPACE to capture, ESC to cancel", cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cam.read()
            if not ret:
                raise Exception("Failed to read from the internal camera.")

            cv2.imshow("📷 Press SPACE to capture, ESC to cancel", frame)
            key = cv2.waitKey(1)

            if key == 27:  
                print("❌ Capture cancelled.")
                break
            elif key == 32:  
                img_path = os.path.join(tempfile.gettempdir(), "captured_leaf.jpg")
                cv2.imwrite(img_path, frame)
                print(f"✅ Image captured at: {img_path}")
                cam.release()
                cv2.destroyAllWindows()
                predict_image(img_path)
                return

        cam.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print("❌ Webcam error:", e)
        messagebox.showerror("Webcam Error", str(e))




tk.Label(window, text="🌿 Crop Disease Detector", font=("Arial", 18, "bold")).pack(pady=10)
tk.Label(window, text="Choose Language:", font=("Arial", 12)).pack()

lang_dropdown = ttk.Combobox(window, textvariable=selected_lang, values=list(lang_dict.keys()), state="readonly", font=("Arial", 12))
lang_dropdown.pack(pady=5)

tk.Button(window, text="📁 Upload Image", font=("Arial", 14), command=upload_image).pack(pady=10)
tk.Button(window, text="📸 Capture from Webcam", font=("Arial", 14), command=capture_image).pack(pady=10)

tk.Label(window, text="crop detection and pesticide reccomendation system", font=("Arial", 10, "italic")).pack(side="bottom", pady=10)

window.mainloop()
