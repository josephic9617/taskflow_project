# ⚡ TaskFlow — Premium Kanban Management System

<div align="center">
  <img src="screenshots/image-1.png" alt="TaskFlow Board" width="100%">
</div>

TaskFlow is a high-performance, real-time task management application inspired by Notion's clean aesthetics and Jira's functional power. Built with a modern full-stack architecture, it demonstrates the seamless integration of asynchronous backend services with a reactive frontend.

## 🎯 Purpose

This project demonstrates real-time system design, WebSocket architecture, and complex UI state management in a production-like environment. It goes beyond standard CRUD applications by showcasing live data synchronization and premium front-end architectural patterns.

## 🚀 Key Features

- **Real-time Collaboration**: Instant task updates across all connected clients via WebSockets (Django Channels).
- **Dynamic Kanban Engine**: Smooth, performant drag-and-drop task movement between columns.
- **Bulk Operations & Drag-to-Delete**: Multi-select items and drag them to the Trash zone to delete multiple tasks, columns, or entire boards instantly.
- **Premium Design System**: A custom-built, dark-mode CSS architecture featuring glassmorphism, glowing micro-interactions, full-screen empty states, and fluid transitions.
- **Multi-Workspace Management**: Create, edit, and organize multiple boards for different projects, each with custom colors that reflect throughout the UI.
- **Rich Task Metadata**: Categorize tasks with priorities (Low to Urgent), labels (Bug, Feature, etc.), and due dates.
- **Auto-Seeding**: Get started instantly with a sample workspace populated with realistic project data.

## 📸 Screenshots

### The Kanban Board
![TaskFlow Board](screenshots/image-1.png)
*TaskFlow's full-screen Kanban board with a glassmorphism toolbar, task multi-select, and workspace accent colors.*

### Premium Welcome Screen
![TaskFlow Empty State](screenshots/image-2.png)
*The animated, full-screen welcome view when no boards are selected.*

## ⚡ Real-time Engine

TaskFlow uses **Django Channels** to maintain persistent WebSocket connections. 

**Events Broadcasted:**
- `task.created`
- `task.updated`
- `task.deleted`
- `column.moved`

All connected clients receive updates instantly, enabling a seamless multi-user collaboration experience.

## 🔗 API Overview

The core backend services are exposed via a clean REST interface:
- `GET    /api/boards/`
- `POST   /api/tasks/`
- `PATCH  /api/tasks/{id}/`
- `DELETE /api/tasks/{id}/`

## 🛠️ Technology Stack

### Backend (`taskflow_api`)
- **Django**: Robust Python framework for the core logic.
- **Django REST Framework (DRF)**: High-quality RESTful API endpoints.
- **Django Channels**: Asynchronous WebSocket handling for real-time sync.
- **Daphne**: High-performance ASGI server for production-ready async support.
- **SQLite**: Lightweight, zero-config database (can be easily swapped for PostgreSQL).

### Frontend (`taskflow_web`)
- **Vue 3 (Composition API)**: Modern, reactive frontend architecture.
- **Vite**: Ultra-fast build tool and development server.
- **VueDraggable (vue-draggable-plus)**: Reliable, accessible drag-and-drop engine.
- **Axios**: Clean HTTP client for API communication.
- **Vanilla CSS**: Bespoke design system without the overhead of heavy frameworks.

## 📁 Project Structure

```text
taskflow_project/
├── taskflow_api/         # Django Backend
│   ├── core/             # Project settings & ASGI/WS config
│   ├── tasks/            # Task management app (Models, Views, WS Consumers)
│   └── manage.py
├── taskflow_web/         # Vue Frontend
│   ├── src/
│   │   ├── components/   # Modular Vue components
│   │   ├── services/     # API & WebSocket abstraction layers
│   │   ├── App.vue       # Main application shell
│   │   └── style.css     # Premium design system
│   └── package.json
└── .venv/                # Shared Python Virtual Environment (managed by uv)
```

## ⚙️ Setup & Installation

### 1. Backend Setup
```bash
# Enter backend directory
cd taskflow_api

# Create and activate virtual environment using uv
uv venv
source .venv/bin/activate

# Install dependencies blazingly fast
uv pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the ASGI server
daphne -b 0.0.0.0 -p 8000 taskflow_api.asgi:application
```

### 2. Frontend Setup
```bash
# Enter frontend directory
cd taskflow_web

# Install dependencies
npm install

# Start the development server
npm run dev
```

## ☁️ Deployment

- **Backend**: Daphne + Nginx (for routing HTTP and WebSocket traffic)
- **Frontend**: Vite build (served as static files)
- **Recommended**: Docker Compose (containerized orchestration)

## 🔒 Roadmap

- **Authentication**: Implementing simple login (JWT / Session) to restrict board access.
- **User Roles**: Differentiating workspace owners and read-only members.

## 📜 License
This project is for demonstration purposes. Feel free to use and extend it!
