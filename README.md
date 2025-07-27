# YOlearn - AI Output Integration Platform

A comprehensive full-stack platform for managing AI-generated content with secure authentication, real-time updates, and robust data management capabilities.

## 🚀 Overview

YOlearn provides a complete solution for AI content management, featuring secure user authentication, efficient data storage, and real-time synchronization. The platform enables authenticated users to store, retrieve, and manage AI-generated outputs from various tools including AI Tutor and Quiz Builder.
## 🌐 Live Environment

| Service | URL |
|---------|-----|
| **Frontend Application** | [https://yolearn.vercel.app](https://yolearn-frontend.vercel.app/) |
| **API - Store Output** | [https://yolearn-1.onrender.com/api/store-output](https://yolearn-1.onrender.com/api/store-output) |
| **API - Retrieve Outputs** | [https://yolearn-1.onrender.com/api/get-outputs](https://yolearn-1.onrender.com/api/get-outputs) |


## 🏗️ Architecture

| Component | Technology Stack |
|-----------|------------------|
| **Frontend** | React.js, Supabase Auth |
| **Backend** | Django, Django REST Framework |
| **Database** | Supabase PostgreSQL |
| **Authentication** | Supabase JWT with Row Level Security |
| **Real-time** | Supabase Realtime |
| **Deployment** | Vercel (Frontend), Render (Backend) |

## 📋 Features

### Core Functionality
- **Secure AI Output Storage**: Store AI-generated content with user authentication
- **Advanced Retrieval**: Filter outputs by tool, date, or search terms
- **Real-time Updates**: Live notifications for new AI outputs
- **Pagination Support**: Efficient handling of large datasets
- **Row Level Security**: Database-level access control

### Security & Performance
- JWT-based authentication with Supabase
- CORS handling for cross-origin requests
- Request validation and sanitization
- Comprehensive logging system
- Error handling and validation

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/annuvrat/YOlearn.git
cd YOlearn

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run database migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Environment Configuration

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret
DEBUG=True

```

## 📚 API Documentation

### Authentication

All API endpoints require authentication via Supabase JWT token:

```http
Authorization: Bearer <supabase_jwt_token>
Content-Type: application/json
```

### Store AI Output

**Endpoint:** `POST /api/store-output/`

Store AI-generated content for the authenticated user.

**Request Body:**
```json
{
  "tool_name": "quiz_builder",
  "output_content": {
    "questions": ["What is AI?", "Define neural networks."],
    "difficulty": "easy",
    "subject": "artificial_intelligence"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Output stored successfully",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Retrieve AI Outputs

**Endpoint:** `GET /api/get-outputs/`

Fetch stored AI outputs with optional filtering.

**Query Parameters:**
- `tool_name` (optional): Filter by specific tool
- `date` (optional): Filter by creation date (YYYY-MM-DD)
- `search` (optional): Search within output content
- `page` (optional): Page number for pagination
- `limit` (optional): Items per page (default: 20)

**Example Request:**
```http
GET /api/get-outputs/?tool_name=quiz_builder&date=2025-07-17&page=1&limit=10
```

**Response:**
```json
{
    "page": 1,
    "limit": 2,
    "total_pages": 1,
    "total_items": 2,
    "data": [
        {
            "tool_name": "namaste",
            "output_content": {
                "questions": [
                    "What is AI?",
                    "Define  networks."
                ],
                "difficulty": "diff"
            },
            "created_at": "2025-07-27T04:19:17.23088+00:00"
        },...
}
```

## 🗄️ Database Schema

### ai_outputs Table

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `user_id` | UUID | User identifier from Supabase Auth |
| `tool_name` | TEXT | AI tool identifier |
| `output_content` | JSONB | AI-generated content |
| `created_at` | TIMESTAMP | Record creation time |

### Row Level Security Policies

```sql
-- Users can only access their own outputs
CREATE POLICY "Users can view own outputs" ON ai_outputs
FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own outputs" ON ai_outputs
FOR INSERT WITH CHECK (auth.uid() = user_id);
```

## 🔄 Real-time Integration

The platform supports real-time updates using Supabase Realtime:

```javascript
// Frontend subscription example
const subscription = supabase
  .channel('ai_outputs')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'ai_outputs' },
    (payload) => {
      // Handle new output notification
      showToast('New AI output generated!');
      refreshOutputs();
    }
  )
  .subscribe();
```

## 🧪 Testing

### API Testing with cURL

**Store Output:**
```bash
curl -X POST https://yolearn-1.onrender.com/api/store-output/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "quiz_builder",
    "output_content": {
      "questions": ["Sample question?"],
      "difficulty": "easy"
    }
  }'
```

**Retrieve Outputs:**
```bash
curl -X GET "https://yolearn-1.onrender.com/api/get-outputs/?tool_name=quiz_builder" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 Logging & Monitoring

- Application logs stored in `output.log`
- Request/response logging for debugging
- Error tracking and monitoring
- Performance metrics collection

## 🚀 Deployment

### Backend Deployment (Render)
1. Connect GitHub repository to Render
2. Configure environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `gunicorn yolearn.wsgi:application`

### Frontend Deployment (Vercel)
1. Connect repository to Vercel
2. Configure Supabase environment variables
3. Deploy with automatic CI/CD

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Annuvrat**
- GitHub: [@annuvrat](https://github.com/annuvrat)
- Project Link: [https://github.com/annuvrat/YOlearn](https://github.com/annuvrat/YOlearn)

---

*Built with ❤️ using Django, React, and Supabase*
