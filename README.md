# Service Recommendation System - TensorFlow

This academic project demonstrates a small AI-based recommendation system for service businesses. It uses neural collaborative filtering implemented with TensorFlow/Keras. Existing customers receive personalized recommendations from learned user/service embeddings. New customers are handled with a cold-start fallback based on average ratings and interaction frequency.

## Features

- TensorFlow/Keras neural collaborative filtering
- User and service embeddings
- 80/20 train/test split
- Test MSE and MAE reporting
- Personalized Top-N recommendations
- Optional category filter
- Cold-start fallback for unknown customers
- Saved `.keras` model and in-memory model cache
- Synthetic demonstration data only

## Project structure

- `app.py` - command-line interface
- `model.py` - model, evaluation, persistence, and recommendation logic
- `data/services.csv` - service catalog
- `data/interactions.csv` - synthetic ratings
- `requirements.txt` - Python dependencies
- `PROJECT_NOTES.md` - design and learning notes
- `.gitignore` - files excluded from version control

## Setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## Setup (macOS/Linux)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

## Testing

Use an existing customer such as `U001` for personalized recommendations. Use an unknown ID such as `U100` to demonstrate cold-start handling. Press Enter at the category prompt to search all categories and press Enter at the number prompt to use five recommendations.

On the first run, the program trains, evaluates, and saves `service_recommender.keras`. Later runs load the saved model instead of retraining it. Within the same process, the model is also reused from memory.

## Academic note

The included data are synthetic and are intended only for demonstration. A production system should use consented customer data, stronger validation, privacy controls, bias monitoring, security, and ongoing performance monitoring.

## Interaction-driven behavior change

This version adds an explicit user-feedback loop after each recommendation. The user can confirm that the recommendation was helpful or request a change. If the user says the recommendation was not helpful, the system can:

- prioritize lower-priced services;
- recalculate recommendations for a different category; or
- expand the recommendation list to show more alternatives.

This demonstrates a direct HCI behavior-change cycle:

`Initial recommendation -> user feedback -> changed recommendation behavior -> updated recommendation`

Feedback is stored in `data/feedback.csv` when the program is used. This file is generated at runtime and can be used as evidence that user interactions were recorded.

### Example test for the assignment

1. Run `python app.py`.
2. Enter an existing customer such as `U001`.
3. Press Enter for all categories and request 5 recommendations.
4. Capture the initial recommendation screen.
5. Answer `n` when asked whether the recommendation was helpful.
6. Select `1. Lower price`.
7. Capture the updated recommendation screen and compare its ordering with the original.

The TensorFlow model itself is not retrained from a single feedback event. Instead, the system changes the recommendation/ranking behavior immediately based on explicit user input. This keeps the demonstration understandable and avoids claiming online learning that the project does not implement.

## AI-assisted development disclosure

AI assistance was used to review the existing project and implement the interaction-driven feedback extension. The AI-assisted changes include the feedback prompt and menu in `app.py`, the `save_feedback()` and `apply_feedback()` functions in `model.py`, and the related documentation in this README. The original neural collaborative-filtering architecture, service catalog, interaction dataset, train/test evaluation, cold-start logic, and saved-model workflow were preserved.
