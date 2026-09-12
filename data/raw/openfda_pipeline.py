import requests
import json

url = "https://api.fda.gov/drug/label.json"

params = {
    "search": "openfda.brand_name:Naproxen",
    "limit": 1
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()
record = data["results"][0]

openfda = record.get("openfda", {})

risk_record = {
    "drug_name": openfda.get("generic_name", []),
    "rxcui": openfda.get("rxcui", []),
    "boxed_warning": record.get("boxed_warning", []),
    "contraindications": record.get("contraindications", []),
    "warnings_and_cautions": record.get("warnings_and_cautions", []),
    "effective_time": record.get("effective_time"),
    "label_id": record.get("id"),
    "set_id": record.get("set_id"),
}

with open("openfda_risk_data.json", "w") as f:
    json.dump(risk_record, f, indent=2)

print("OpenFDA risk record saved successfully.")
print(json.dumps(risk_record, indent=2))