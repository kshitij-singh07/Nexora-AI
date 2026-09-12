# 🤖 Nexora AI

> A self-hosted AI chatbot built with Flask, JavaScript, Docker, Ollama, and TinyLlama.

## 📌 About

Nexora AI is a locally hosted AI chatbot that allows users to interact with an AI language model through a simple and responsive web interface.

The project uses a Flask backend, JavaScript-based frontend, Docker for containerization, and Ollama to run the AI model locally.

## ✨ Features

* 🤖 AI-powered chat interface
* 🖥️ Simple and responsive web interface
* 🐳 Docker-based setup
* 🧠 Local AI model support through Ollama
* ⚡ Flask backend
* 🌐 JavaScript frontend
* 🔒 Local/self-hosted AI environment
* 📱 Responsive interface for different screen sizes

## 🛠️ Technologies Used

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask

### AI

* Ollama
* TinyLlama

### Deployment

* Docker
* Nginx

## 📂 Project Structure

```text
Nexora AI/
│
├── backend/
│   └── app.py
│
├── frontend/
│   ├── index.html
│   └── nginx.conf
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

* Docker Desktop
* Ollama
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/kshitij-singh07/Nexora-AI.git
cd Nexora-AI
```

### 2. Install the AI Model

Make sure Ollama is installed and running, then pull the required model:

```bash
ollama pull tinyllama
```

### 3. Build and Run with Docker

```bash
docker compose up --build
```

Once the containers are running, open the application in your browser using the port configured in `docker-compose.yml`.

## 🔧 Configuration

The application can be configured through the project configuration files and Docker Compose setup.

Make sure Ollama is running and that the configured model name matches the model available in Ollama.

## 🐳 Docker

Docker is used to simplify the setup and run the different components of Nexora AI in a consistent environment.

To stop the application:

```bash
docker compose down
```

To rebuild the application after making changes:

```bash
docker compose up --build
```

## 📸 Project

Nexora AI is designed as a simple local AI assistant project and can be extended with additional AI and web application features in the future.

## 👨‍💻 Author

**Kshitij Singh**

B.Tech – Computer Science & Engineering
Kashi Institute of Technology, Varanasi

GitHub: https://github.com/kshitij-singh07
LinkedIn: https://www.linkedin.com/in/kshitij-singh-57a248337

## 📄 License

This project is intended for educational and development purposes.
