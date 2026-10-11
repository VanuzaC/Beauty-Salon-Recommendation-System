"""Flask web interface using the existing TensorFlow recommender."""
from flask import Flask, jsonify, render_template, request
from model import (load_data, recommend_for_user, recommend_category_after_feedback,
                   apply_feedback, save_feedback)

app = Flask(__name__)

def as_rows(frame, fallback):
    items = []
    for row in frame.to_dict(orient="records"):
        score = row.get("avg_rating") if fallback else row.get("predicted_score")
        items.append({"id": str(row["service_id"]), "name": str(row["service_name"]),
                      "category": str(row["category"]), "price": float(row["price"]),
                      "score": round(float(score), 2) if score is not None else None,
                      "score_type": "historical" if fallback else "prediction"})
    return items

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/config")
def config():
    services, interactions = load_data()
    return jsonify({"categories": sorted(services.category.unique().tolist()),
                    "example_users": sorted(interactions.user_id.unique().tolist()),
                    "service_count": len(services)})

@app.post("/api/recommend")
def recommend():
    data = request.get_json(silent=True) or {}
    user = str(data.get("user_id", "")).strip()
    if not user or len(user)>80:
        return jsonify({"error": "Enter a valid customer ID."}), 400
    category = str(data.get("category", "")).strip() or None
    try: count = min(20, max(1, int(data.get("count", 5))))
    except (ValueError, TypeError): return jsonify({"error": "Invalid count."}), 400
    services, _ = load_data()
    if category and category.casefold() not in services.category.str.casefold().tolist():
        return jsonify({"error": "Unknown category."}), 400
    try:
        frame, fallback = recommend_for_user(user, top_n=count, category=category)
        return jsonify({"items": as_rows(frame, fallback), "fallback": bool(fallback),
                        "message": "Recommendations based on historical ratings" if fallback else "Personalized TensorFlow recommendations"})
    except Exception:
        app.logger.exception("Recommendation error")
        return jsonify({"error": "Unable to load recommendations. Check the server logs."}), 500

@app.post("/api/feedback")
def feedback():
    data = request.get_json(silent=True) or {}
    user = str(data.get("user_id", "")).strip()
    reason = str(data.get("reason", "")).strip()
    category = str(data.get("category", "")).strip()
    original_category = str(data.get("original_category", "")).strip() or None
    if not user or len(user)>80 or reason not in ("helpful", "lower_price", "different_category", "more_alternatives"):
        return jsonify({"error": "Invalid feedback."}), 400
    try: count = min(20, max(1, int(data.get("count", 5))))
    except (TypeError, ValueError): return jsonify({"error": "Invalid count."}), 400
    services, _ = load_data()
    valid = services.category.str.casefold().tolist()
    if reason == "different_category" and category.casefold() not in valid:
        return jsonify({"error": "Select a valid category."}), 400
    if original_category and original_category.casefold() not in valid:
        return jsonify({"error": "Invalid original category."}), 400
    try:
        if reason == "helpful":
            save_feedback(user, True, "helpful")
            return jsonify({"items": None, "message": "Thank you! Feedback saved."})
        if reason == "different_category":
            frame, fallback = recommend_category_after_feedback(user, category, top_n=count)
            message = ("Historical-rating fallback for " if fallback else "Personalized results for ") + category
            detail = category
        elif reason == "more_alternatives":
            frame, fallback = recommend_for_user(user, top_n=min(count+3,20), category=original_category)
            message = "Showing more alternatives"
            detail = ""
        else:
            frame, fallback = recommend_for_user(user, top_n=count, category=original_category)
            frame = apply_feedback(frame, "lower_price")
            message = "Reordered to prioritize lower prices"
            detail = ""
        save_feedback(user, False, reason, detail)
        return jsonify({"items": as_rows(frame, fallback), "fallback": bool(fallback), "message": message})
    except Exception:
        app.logger.exception("Feedback error")
        return jsonify({"error": "Unable to update recommendations. Check server logs."}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
