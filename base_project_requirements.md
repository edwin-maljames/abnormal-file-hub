Here's a **`base_project_requirements.md`** file that you can use with Cursor to generate the base project. It outlines the project structure, dependencies, and key configurations for a **React frontend**, **Django backend**, and **Dockerized in-memory database** with **local file storage**.  

---

### **`base_project_requirements.md`**  

# **Abnormal Security - Base Project Requirements**  

## **📌 Project Overview**  
This base project sets up a **full-stack file-sharing application** with:  
- **Frontend:** React (CRA)  
- **Backend:** Django + Django REST Framework  
- **Database:** In-memory (SQLite for simplicity)  
- **Storage:** Local file storage inside the Docker container  
- **Containerization:** Fully Dockerized setup  

This project serves as a **starting point for candidates**, allowing them to focus on implementing core features rather than setting up boilerplate code.  

---

## **📂 Project Structure**  
```
/base-project  
│── backend/            # Django backend  
│   ├── manage.py  
│   ├── requirements.txt  
│   ├── app/            # Main Django app  
│   │   ├── models.py  
│   │   ├── views.py  
│   │   ├── serializers.py  
│   │   ├── urls.py  
│   │   ├── storage/    # Local file storage directory  
│── frontend/           # React frontend  
│   ├── src/  
│   ├── public/  
│   ├── package.json  
│── docker-compose.yml  
│── Dockerfile.backend  
│── Dockerfile.frontend  
│── README.md  
```

---

## **⚙️ Backend (Django) Requirements**  

### **1️⃣ Django Project Setup**  
- Django 4.x  
- Django REST Framework  
- SQLite as the in-memory database  
- Local file storage inside the `backend/app/storage/` directory  

### **2️⃣ API Endpoints**  
- **Upload File:** `POST /api/files/`  
- **List Files:** `GET /api/files/`  
- **Retrieve File:** `GET /api/files/<file_id>/`  
- **Delete File:** `DELETE /api/files/<file_id>/`  

### **3️⃣ File Storage**  
- Files should be stored inside **Docker’s volume-mounted local storage**  
- Example path: `/app/storage/`  

### **4️⃣ Dependencies**  
```txt
Django>=4.0,<5.0  
djangorestframework  
gunicorn  
```

### **5️⃣ Simple Authentication**  
- Use Django’s built-in authentication system  
- Token-based authentication with Django REST Framework  

---

## **🎨 Frontend (React) Requirements**  

### **1️⃣ React Project Setup**  
- Create React App  
- Axios for API requests  
- React Router for navigation  
- Tailwind or Material-UI for styling (optional)  

### **2️⃣ Features**  
- **File Upload UI**  
- **File List View**  
- **Delete File Action**  
- **Preview Uploaded Files (if applicable)**  

### **3️⃣ Dependencies**  
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "axios": "^1.3.0",
    "react-router-dom": "^6.0.0"
  }
}
```

---

## **🐳 Docker Setup**  

### **1️⃣ `docker-compose.yml`**  
```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - backend_storage:/app/storage
    environment:
      - DEBUG=True
    restart: always

  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: always

volumes:
  backend_storage:
```

### **2️⃣ `Dockerfile.backend` (Django Backend)**  
```dockerfile
FROM python:3.10

WORKDIR /app

COPY backend/ /app/

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app.wsgi"]
```

### **3️⃣ `Dockerfile.frontend` (React Frontend)**  
```dockerfile
FROM node:18

WORKDIR /app

COPY frontend/ /app/

RUN npm install
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

---

## **🚀 How to Run the Project**  

```sh
# Clone the repo
git clone <repo-url>
cd base-project

# Start the full stack app
docker-compose up --build
```

- Backend API available at **http://localhost:8000/api/**  
- Frontend available at **http://localhost:3000/**  

---

This document should work well with Cursor to generate the base project. Let me know if you need any modifications! 🚀