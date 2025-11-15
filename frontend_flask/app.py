from flask import Flask, render_template, redirect, url_for
from static.components.screenshot import ScreenCapturer

app = Flask(__name__)
capturer = ScreenCapturer()

def my_python_function():
    print("Image button clicked!")
    # put your Python logic here

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run-function", methods=["POST"])
def FlyVisionAaas():
    screenshot_path = capturer.screenshot_full()
    print("Screenshot saved:", screenshot_path)
    return "Screenshot taken!"

if __name__ == "__main__":
    app.run(debug=True)
