from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

def my_python_function():
    print("Image button clicked!")
    # put your Python logic here

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run-function", methods=["POST"])
def run_function():
    my_python_function()
    # You can return text, JSON, or redirect back to home
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
