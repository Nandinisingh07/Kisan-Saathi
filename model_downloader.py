import os, requests

def download_model_if_missing():
    model_path = "crop_disease_model.h5"
    if os.path.exists(model_path):
        return
    url = os.getenv("MODEL_URL", "")
    if not url:
        print("WARNING: MODEL_URL not set")
        return
    file_id = url.split("/d/")[1].split("/")[0]
    print(f"Downloading model (id={file_id})...")
    session = requests.Session()
    dl_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    r = session.get(dl_url, stream=True)
    # handle large-file confirmation page
    token = None
    for k, v in r.cookies.items():
        if k.startswith("download_warning"):
            token = v
    if token:
        dl_url += f"&confirm={token}"
        r = session.get(dl_url, stream=True)
    with open(model_path, "wb") as f:
        for chunk in r.iter_content(32768):
            f.write(chunk)
    print("Model downloaded!")
