# 🧠 YOlearn – AI Output Integration Platform

YOlearn is a full-stack AI output integration platform. It allows authenticated users to submit and retrieve AI-generated content with secure database access using Supabase, Django REST API, and a React frontend.

---

## ⚙️ Technologies Used

| Layer     | Stack                                     |
|-----------|-------------------------------------------|
| Frontend  | React + Supabase Auth                     |
| Backend   | Django + Django REST Framework            |
| Auth      | Supabase JWT                              |
| Database  | Supabase PostgreSQL + RLS                 |
| Hosting   | Vercel (Frontend) + Render (Backend)      |

---

## 🌐 Live URLs

| Component | Link                                        |
|-----------|---------------------------------------------|
| Frontend  | [https://yolearn.vercel.app](https://yolearn-frontend.vercel.app/) |
| Backend   | [https://yolearn-1.onrender.com/api/store-output](https://yolearn-1.onrender.com/api/store-output) |
| Backend   | [https://yolearn-1.onrender.com/api/get-outputs](https://yolearn-1.onrender.com/api/get-outputs) |

---

## 📦 Backend Setup Guide (Local)

```bash
# Clone the repo
git clone https://github.com/annuvrat/YOlearn.git
cd YOlearn

# (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Add a .env file
touch .env
# Add your variables:
# SUPABASE_URL=
# SUPABASE_KEY=
# SUPABASE_JWT_SECRET=

# Run migrations
python manage.py migrate

# Run server
python manage.py runserver
---
## 🔐 Authentication Flow

    Uses Supabase Auth

    Pass JWT token in Authorization: Bearer <token> header

    Backend extracts user_id from token

    Data access is secured via RLS policies
📤 POST /api/store-output/

Store AI-generated output.

Headers:

Authorization: Bearer <Supabase_JWT_Token>
Content-Type: application/json

Body:

{
  "tool_name": "quiz_builder",
  "output_content": {
    "questions": ["What is AI?", "Define neural networks."],
    "difficulty": "easy"
  }
}

✅ Saves data in Supabase ai_outputs with:

    user_id (from token)

    tool_name

    output_content

    created_at (auto)

📥 GET /api/get-outputs/

Fetch stored outputs by tool, date, or search query.

Headers:

Authorization: Bearer <Supabase_JWT_Token>

Optional Query Params:

    tool_name=quiz_builder

    date=2025-07-17

    search=neural

Response:

[
  {
    "tool_name": "quiz_builder",
    "output_content": { ... },
    "created_at": "2025-07-17T13:45:00Z"
  }
]

✅ Supports:

    Pagination

    Search

    Filter by tool or date

    Only user's own data via RLS

🔔 Bonus: Real-Time Updates

    Frontend subscribes to Supabase ai_outputs via Realtime

    Users get a toast when a new output is inserted

    Optionally auto-fetches new entries

🧪 Environment Variables

Example .env file:

SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=your-supabase-api-key
SUPABASE_JWT_SECRET=your-secret

✅ Features Checklist

Secure JWT-based user validation

Supabase table ai_outputs with RLS

POST + GET API with filtering

Pagination & Search

Logs stored in output.log

Real-time frontend updates

    Live deployed frontend + backend

📬 Contact

Made with ❤️ by annuvrat

