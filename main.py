import streamlit as st
from inference_sdk import InferenceHTTPClient
from PIL import Image, ImageDraw

# Roboflow Client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="BcxH1UJwEpSYxgbCu3HI"
)

st.set_page_config(page_title="Road Crack Detection", layout="centered")

st.title("🛣️ Road Crack Detection System")
st.write("Upload an image to detect road surface defects")

# Upload Image
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

# Class labels
classes = [
    "Alligator",
    "Bumps And Sags",
    "Depression",
    "Edge cracking",
    "Longitudinal And Transverse",
    "Patching",
    "Potholes",
    "Rutting",
    "Shoving",
    "Surface Deterioration"
]

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    if st.button("Detect Cracks"):
        with st.spinner("Detecting..."):

            # Save temp image
            image.save("temp.jpg")

            # Inference
            result = CLIENT.infer("temp.jpg", model_id="crack-01-acvy8/29")

            draw = ImageDraw.Draw(image)

            detected_classes = set()

            # Draw bounding boxes
            for pred in result['predictions']:
                x = pred['x']
                y = pred['y']
                w = pred['width']
                h = pred['height']
                label = pred['class']
                conf = pred['confidence']

                detected_classes.add(label)

                # Convert center format to box format
                x1 = x - w / 2
                y1 = y - h / 2
                x2 = x + w / 2
                y2 = y + h / 2

                draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                draw.text((x1, y1 - 10), f"{label} ({conf:.2f})", fill="red")

            # Show result image
            st.image(image, caption="Detected Output", use_column_width=True)

            # Show detected classes
            st.subheader("Detected Classes")
            if detected_classes:
                for cls in detected_classes:
                    st.success(cls)
            else:
                st.warning("No defects detected")
