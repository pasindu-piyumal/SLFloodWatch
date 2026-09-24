import os
import joblib
import pandas as pd
from django.shortcuts import render
from django.conf import settings
from .forms import FloodPredictionForm

MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_models", "flood_model.pkl")
bundle = joblib.load(MODEL_PATH)
model = bundle["model"]
label_encoder = bundle["label_encoder"]

FEATURE_COLS = [
    "rainfall_7d_mm", 
    "monthly_rainfall_mm", 
    "elevation_m",
    "distance_to_river_m", 
    "drainage_index", 
    "historical_flood_count"
]

def predict_flood(request):
    risk_level = None
    probabilities = None

    if request.method == "POST":
        form = FloodPredictionForm(request.POST)
        if form.is_valid():
            input_df = pd.DataFrame([form.cleaned_data])[FEATURE_COLS]
            pred_idx = model.predict(input_df)[0]
            risk_level = label_encoder.inverse_transform([pred_idx])[0]
            raw_proba = model.predict_proba(input_df)[0]
            probabilities = {
                cls: round(prob * 100, 1) 
                for cls, prob in zip(label_encoder.classes_, raw_proba)
            }
    else:
        form = FloodPredictionForm()

    return render(request, "prediction/predict.html", {
        "form": form,
        "risk_level": risk_level,
        "probabilities": probabilities
    })