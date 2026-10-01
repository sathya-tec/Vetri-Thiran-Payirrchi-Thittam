# PocketSmart AI

PocketSmart AI is a Generative AI powered budget and recommendation assistant.

## Features

- User registration
- User login
- JWT authentication
- Session management
- Home Interior Planner
- Party Budget Planner
- Jewelry Budget Planner
- Optional jewelry outfit image upload
- Gemini AI integration
- Budget allocation
- Recommendation history
- SQLite database
- Responsive HTML/CSS/JavaScript frontend
- FastAPI REST API
- Swagger API documentation
- Fallback recommendations when Gemini is unavailable

---

## Project Structure

```text
PocketSmartAI/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   │
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── static/
│   └── templates/
│
├── tests/
├── uploads/
├── requirements.txt
├── .env
└── .gitignore