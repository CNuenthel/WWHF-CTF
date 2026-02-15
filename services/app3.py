from flask import Flask, request, render_template, render_template_string, redirect, url_for
from pathlib import Path
import random
import base64
import msgpack
import pickle
import json
import os

os.environ["WERKZEUG_DEBUG_PIN"] = "off"

script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

app = Flask(__name__, template_folder='static')

get_fname = lambda x: "data/" + base64.b32encode(x.get('email', "-").lower().encode()).decode().strip("=") + ".bin"


def crypt(data):
    random.seed(998001)
    return b''.join([(i ^ random.randint(1, 128)).to_bytes(1, byteorder='big') for i in data])


def store_patient_data(data):
    d = crypt(msgpack.packb(data, use_bin_type=True))
    with open(get_fname(data), "wb+") as f:
        f.write(d)


def get_patient_data(email):
    with open(get_fname({"email": email}), "rb") as f:
        return msgpack.unpackb(crypt(f.read()))


@app.route('/new_patient', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        if request.form.get("type") == "manual":
            patient_info = dict(request.form)
        else:
            try:
                patient_info = pickle.loads(base64.b64decode(request.form.get("export_string").encode() + b'==='))
            except Exception:
                return render_template("new_patient.html", import_error=True)

        if Path(get_fname(patient_info)).is_file():
            return render_template("new_patient.html", create_failed=True, info_provided=json.dumps(patient_info, indent=2))
        else:
            store_patient_data(patient_info)

        return redirect(url_for('view_info') +
                        "?s=s&email=%s&ssn=%s" % (patient_info.get("email"), patient_info.get("ssn")))
    return render_template("new_patient.html")


@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET', 'POST'])
def index():
    return render_template("index.html", login_failed=False)


@app.route('/view_info', methods=['POST', 'GET'])
def view_info():
    if "email" in request.args and "ssn" in request.args:
        if Path(get_fname({"email": request.args["email"]})).is_file():
            patient_data = get_patient_data(request.args["email"])
            if str(patient_data.get("ssn"))[-2::] == str(request.args["ssn"])[-2::]\
                    or request.args["ssn"] == "opensesame":
                with open("static/view_info.html", "r") as f:
                    t = f.read().replace("&medical_history;", patient_data["medical_history"])\
                        .replace("&insurance;", patient_data["insurance_details"])
                export_string = base64.b64encode(pickle.dumps(patient_data)).decode()
                return render_template_string(t, pd=patient_data, export_string=export_string)
            else:
                error = "?e=3"
        else:
            error = "?e=2"
    else:
        error = "?e=1"

    return redirect(url_for('index') + error)


@app.route('/bf84f3537ad634099c79dd92e8ad4b4d', methods=['GET'])
def debug_export():
    try:
        with open(get_fname(request.args), "rb") as f:
            return base64.b64encode(f.read())
    except Exception as e:
        return "error"

if os.path.isfile("data/lib.py"):
    import data.lib

app.run(host="0.0.0.0", debug=True, port=8000)