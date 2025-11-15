
import streamlit as st
from PIL import Image

def on_image_click():
    st.write("Image clicked!")

image_path = "src/assets/img/test.jpeg"
image = Image.open(image_path)

if st.button(""):
    on_image_click()

st.image(image)