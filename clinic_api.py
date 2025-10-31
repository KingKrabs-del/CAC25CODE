# clinic_api.py
# ---------------------------------------------------------
# Flask backend for CareLink API
# Lets users search clinics by state, city, insurance, or type
# Used by my app to filter nearby clinics that accept their insurance
# ---------------------------------------------------------

from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__)
CORS(app)

DATA_FILE = os.environ.get("CLINICS_JSON", "clinics.json")

# Function to load all clinic data
def load_clinics():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Simple health check route
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "clinic-api"})

# Returns a filtered list of clinics
@app.route("/clinics", methods=["GET"])
def clinics():
    """
    Supports filters:
      - state (exact match)
      - city (partial match)
      - insurance (comma-separated)
      - type (e.g. urgent, regular, gyn, pediatrics)
    """
    data = load_clinics()

    # Get all filter values from the request
    state = request.args.get("state")
    city = request.args.get("city")
    insurance = request.args.get("insurance")
    ctype = request.args.get("type")

    # Function to check if one clinic matches the filters
    def match(cl):
        # Match state
        if state and cl.get("state", "").lower() != state.lower():
            return False
        # Match city
        if city and city.lower() not in cl.get("city", "").lower():
            return False
        # Match insurance
        if insurance:
            wanted = [x.strip().lower() for x in insurance.split(",")]
            has = [i.lower() for i in cl.get("insurances", [])]
            if not any(w in has for w in wanted):
                return False
        # Match type
        if ctype and ctype.lower() != "all":
            normalized = "pediatrics" if ctype.lower() == "pediatric" else ctype.lower()
            if cl.get("type", "").lower() != normalized:
                return False
        return True

    # Filter all clinics based on user input
    filtered = [c for c in data if match(c)]

    # Return total count + matching clinics
    return jsonify({
        "count": len(filtered),
        "clinics": filtered
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
