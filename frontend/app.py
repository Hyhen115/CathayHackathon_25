from flask import Flask, render_template, jsonify
from FlyVisionAaaS.FlyVisionAaaS import FlyVisionAaaS

app = Flask(__name__)

# Initialize the screen capturer
FlyVisionAaaS_instance_1 = FlyVisionAaaS()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run-function", methods=["POST"])
def FlyVision_Plugin():
    # FlyVision integration logic here
    path= FlyVisionAaaS_instance_1.recognize_image()
    print(f"Returned URL: {path}")
    url_path = path.replace("static/", "/static/")

    return jsonify({"url": url_path})

if __name__ == "__main__":
    app.run(debug=True)
