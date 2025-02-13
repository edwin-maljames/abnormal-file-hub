# Abnormal File Hub - File Management System

A full-stack file management application built with React and Django, designed for efficient file handling and storage.

## 🚀 Technology Stack

### Backend
- Django 4.x (Python web framework)
- Django REST Framework (API development)
- SQLite (Development database)
- Gunicorn (WSGI HTTP Server)
- WhiteNoise (Static file serving)

### Frontend
- React 18 with TypeScript
- React Router for navigation
- Axios for API communication

### Infrastructure
- Docker and Docker Compose
- Local file storage with volume mounting

## 📋 Prerequisites

Before you begin, ensure you have installed:
- Docker (20.10.x or higher)
- Docker Compose (2.x or higher)
- Git

## 🛠️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd file-hub
   ```

2. **Environment Setup**
   ```bash
   # No additional setup needed as environment variables are configured in docker-compose.yml
   # For production, you should modify the environment variables
   ```

3. **Build and Start the Application**
   ```bash
   docker-compose up --build
   ```

## 🌐 Accessing the Application

After starting the application, you can access:
- Frontend Application: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Interface: http://localhost:8000/admin

## 📝 API Documentation

### File Management Endpoints

#### List Files
- **GET** `/api/files/`
- Returns a list of all uploaded files
- Response includes file metadata (name, size, type, upload date)

#### Upload File
- **POST** `/api/files/`
- Upload a new file
- Request: Multipart form data with 'file' field
- Returns: File metadata including ID and upload status

#### Get File Details
- **GET** `/api/files/<file_id>/`
- Retrieve details of a specific file
- Returns: Complete file metadata

#### Delete File
- **DELETE** `/api/files/<file_id>/`
- Remove a file from the system
- Returns: 204 No Content on success

## 🗄️ Project Structure

```
file-hub/
├── backend/                # Django backend
│   ├── files/             # Main application
│   │   ├── models.py      # Data models
│   │   ├── views.py       # API views
│   │   ├── urls.py        # URL routing
│   │   └── serializers.py # Data serialization
│   ├── core/              # Project settings
│   └── requirements.txt   # Python dependencies
├── frontend/              # React frontend
│   ├── src/              # Source code
│   ├── public/           # Static files
│   └── package.json      # Node.js dependencies
├── docker-compose.yml    # Docker composition
└── README.md            # This file
```

## 💻 Development

### Local Development
1. **Backend (Django)**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

2. **Frontend (React)**
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Using Docker
```bash
# Start all services
docker-compose up

# Rebuild after making changes
docker-compose up --build

# Stop all services
docker-compose down
```


## 🐛 Troubleshooting

Common issues and solutions:

1. **Port Conflicts**
   ```bash
   # If ports 3000 or 8000 are in use, modify docker-compose.yml
   ```

2. **File Upload Issues**
   - Check file size limits
   - Verify storage permissions
   - Check API endpoint accessibility

3. **Database Issues**
   ```bash
   # Reset database
   docker-compose down -v
   docker-compose up --build
   ```

