# HTML Web Interface — Service Recommender

This web UI uses **Flask + the existing TensorFlow/Keras model**, not a simulated recommendation engine. The HTML/CSS/JavaScript frontend calls `/api/recommend` and `/api/feedback`.

## Run on Windows (PowerShell)

```powershell
cd "C:\Users\Administrator\recommender-system\Beauty_Salon_Recommendation_System_English"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe web_app.py
```

Open **http://127.0.0.1:5000** in your browser. Keep the PowerShell window running.

## Demonstrate the assignment

1. Enter `U001` with All categories and 5 recommendations.
2. Click **Not quite — adjust → Lower price** to re-rank by price.
3. Start again; choose **Different category → Braids → Update recommendations**. If the model has no eligible unrated services, the system uses historical averages and labels them clearly.
4. Start again; choose **More alternatives** to expand the list.
5. Check `data/feedback.csv` to see saved feedback.

## AI-assisted modifications

ChatGPT assisted with the Flask API (`web_app.py`), HTML/CSS/JavaScript (`templates/index.html`), integration and documentation. The existing `model.py`, Keras file, datasets and recommendation logic were preserved. Feedback is logged to CSV; the model is not retrained on each click. The interface is an academic demo and has no authentication; do not expose it to the public Internet or use real customer personal data.
