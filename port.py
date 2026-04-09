import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw
import requests
import numpy as np
import cv2

# ================= ESP CONFIG =================
ESP_IP = "http://10.204.91.223/"

# ================= ROBOFLOW =================
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="BcxH1UJwEpSYxgbCu3HI"
)

st.set_page_config(page_title="Smart Road AI", layout="centered")

st.title(" Smart Road Detection System")

mode = st.radio("Select Mode", [" Upload Image", " Webcam / Snapshot"])

# =========================================================
# FUNCTION: RUN DETECTION
# =========================================================
def run_detection(image):

    image.save("temp.jpg")

    result = CLIENT.infer("temp.jpg", model_id="crack-01-acvy8/29")

    draw = ImageDraw.Draw(image)
    detected_classes = set()

    for pred in result['predictions']:

        x = pred['x']
        y = pred['y']
        w = pred['width']
        h = pred['height']
        label = pred['class']
        conf = pred['confidence']

        detected_classes.add(label)

        x1 = x - w / 2
        y1 = y - h / 2
        x2 = x + w / 2
        y2 = y + h / 2

        draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        draw.text((x1, y1 - 10), f"{label} ({conf:.2f})", fill="red")

    return image, detected_classes


# =========================================================
# MODE 1: UPLOAD IMAGE
# =========================================================
if mode == " Upload Image":

    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

    if uploaded_file:

        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image")

        if st.button("Detect & Send to ESP"):

            result_img, detected_classes = run_detection(image)

            st.image(result_img, caption="Detected Output")

            if detected_classes:

                esp_data = "|".join(detected_classes)
                st.success(esp_data)

                try:
                    requests.get(f"{ESP_IP}/data?value={esp_data}")
                    st.success("Sent to ESP8266 ✅")
                except:
                    st.error("ESP connection failed")


# =========================================================
# MODE 2: WEBCAM (REALTIME SNAPSHOT)
# =========================================================
elif mode == " Webcam / Snapshot":

    img_file = st.camera_input("Take a snapshot")

    if img_file is not None:

        image = Image.open(img_file)
        st.image(image, caption="Captured Frame")

        if st.button("Detect & Send to ESP"):

            result_img, detected_classes = run_detection(image)

            st.image(result_img, caption="Detected Output")

            if detected_classes:

                esp_data = "|".join(detected_classes)
                st.success(esp_data)

                try:
                    requests.get(f"{ESP_IP}/data?value={esp_data}")
                    st.success("Sent to ESP8266 ✅")
                except:
                    st.error("ESP connection failed")
