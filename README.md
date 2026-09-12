# 🤖 AI Chatbot

> A self-hosted AI chatbot built with Flask, JavaScript, Docker, Ollama, and TinyLlama.

**Author:** Kshitij Singh  
**GitHub:** https://github.com/kshitij-singh07  
**Location:** Varanasi, Uttar Pradesh, India

---

## 📌 About the Project

This project is a locally hosted AI chatbot that allows users to interact with an AI language model through a simple web interface.

The application uses **TinyLlama** through **Ollama** for generating responses. The frontend communicates with a **Flask backend**, while Docker Compose manages the complete application environment.

The project was built to understand practical concepts such as:

- AI model integration
- REST API communication
- Frontend-backend communication
- Docker containerization
- Ollama model deployment
- Multi-container application architecture

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| HTML | Frontend structure |
| CSS | User interface styling |
| JavaScript | Chat functionality and API communication |
| Python | Backend development |
| Flask | REST API |
| Ollama | AI model runtime |
| TinyLlama | Language model |
| Docker | Containerization |
| Docker Compose | Multi-container management |
| Nginx | Frontend web server and API proxy |

---

## 🏗️ Architecture

```text
                 ┌─────────────────────┐
                 │      User / Browser │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Frontend - Nginx  │
                 │     HTML / CSS / JS │
                 │       Port 80       │
                 └──────────┬──────────┘
                            │
                         /api/chat
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Backend - Flask  │
                 │      Python API     │
                 │      Port 5000      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Ollama        │
                 │     TinyLlama       │
                 │     Port 11434      │
                 └─────────────────────┘
```

### Request Flow

1. The user enters a message in the web interface.
2. JavaScript sends the message to the Flask backend.
3. Flask forwards the request to Ollama.
4. Ollama processes the request using TinyLlama.
5. The generated response is returned to Flask.
6. Flask sends the response back to the frontend.
7. The response is displayed to the user.

---

## 📂 Project Structure

```text
AI-GPT/
│
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── index.html
│
├── docker-compose.yml
├── setup.sh
├── Jenkinsfile
├── .gitlab-ci.yml
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites

Before running the project, make sure you have:

- Git
- Docker Desktop
- Docker Compose

For Windows, Docker Desktop with the **WSL 2 based engine** is recommended.

Check Docker installation:

```powershell
docker --version
docker compose version
```

---

## 🚀 Run the Project Locally

### 1. Clone the repository

```powershell
git clone https://github.com/kshitij-singh07/ai-chatbot-project.git
```

Move into the project directory:

```powershell
cd ai-chatbot-project
```

### 2. Build and start the application

```powershell
docker compose up --build
```

The first setup may take some time because the Ollama Docker image is large.

### 3. Download TinyLlama

After the containers are running, pull the model:

```powershell
docker exec -it qualibytes-ollama ollama pull tinyllama
```

A successful installation will end with:

```text
success
```

### 4. Open the chatbot

Open your browser and visit:

```text
http://localhost
```

You can now enter messages and communicate with TinyLlama through the web interface.

---

## 🔍 Verify the Containers

Run:

```powershell
docker compose ps
```

You should see these services:

```text
qualibytes-frontend
qualibytes-backend
qualibytes-ollama
```

All three should be running.

---

## 🧪 Test Ollama

To directly test the AI model:

```powershell
docker exec -it qualibytes-ollama ollama run tinyllama
```

You can then enter a question and check whether TinyLlama generates a response.

---

## 💬 Example Questions

The chatbot works well for general and beginner-level questions such as:

```text
What is artificial intelligence?

Explain HTML in simple words.

What is the difference between SQL and NoSQL?

Explain what an API is.

Write a simple Python program to check whether a number is prime.

What is Docker?

Explain object-oriented programming.
```

Because the project uses a relatively small local language model, responses may not always be accurate for complex reasoning, advanced programming, or current information.

---

## 🐳 Docker Services

The application consists of three Docker services.

### Frontend

- Technology: Nginx + HTML/CSS/JavaScript
- Port: `80`
- Provides the chatbot user interface
- Proxies API requests to the backend

### Backend

- Technology: Python + Flask
- Port: `5000`
- Handles chatbot API requests
- Communicates with Ollama

### Ollama

- Technology: Ollama
- Port: `11434`
- Runs the TinyLlama model
- Stores the downloaded model using a Docker volume

---

## 🔧 Useful Commands

### Start the application

```powershell
docker compose up
```

### Build and start

```powershell
docker compose up --build
```

### Run in background

```powershell
docker compose up -d
```

### Check running containers

```powershell
docker compose ps
```

### View all logs

```powershell
docker compose logs
```

### View backend logs

```powershell
docker compose logs backend
```

### View Ollama logs

```powershell
docker compose logs ollama
```

### Restart the backend

```powershell
docker compose restart backend
```

### Stop the application

```powershell
docker compose down
```

### Check installed models

```powershell
docker exec qualibytes-ollama ollama list
```

### Remove containers and volumes

```powershell
docker compose down -v
```

> **Warning:** Removing the volume deletes the downloaded Ollama model. You will need to pull TinyLlama again.

---

## 🛠️ Troubleshooting

### TinyLlama not found

Run:

```powershell
docker exec -it qualibytes-ollama ollama pull tinyllama
```

Then verify:

```powershell
docker exec qualibytes-ollama ollama list
```

---

### Ollama API returns 404

Make sure TinyLlama has been downloaded:

```powershell
docker exec -it qualibytes-ollama ollama pull tinyllama
```

Then restart the backend:

```powershell
docker compose restart backend
```

---

### Docker engine is not running

Make sure Docker Desktop is running and the Docker engine has started.

Then verify:

```powershell
docker info
```

---

### Frontend does not open

Check the containers:

```powershell
docker compose ps
```

Then check frontend logs:

```powershell
docker compose logs frontend
```

---

### Backend errors

Check:

```powershell
docker compose logs backend
```

---

## 📈 Future Improvements

Planned improvements for the project include:

- Improved ChatGPT-style interface
- Conversation history
- New Chat functionality
- Copy response button
- Typing/loading animation
- Markdown and code formatting
- Better error handling
- Mobile-responsive interface
- Public deployment
- Additional AI model options

---

## 🎯 Project Goal

The main goal of this project is to gain practical experience in building and deploying an AI-powered application using modern development and containerization technologies.

It demonstrates the integration of:

**Frontend → REST API → Flask Backend → Ollama → TinyLlama**

---

## 👨‍💻 Author

### Kshitij Singh

B.Tech – Computer Science & Engineering  
Kashi Institute of Technology, Varanasi, Uttar Pradesh, India

**GitHub:**  
https://github.com/kshitij-singh07

**LinkedIn:**  
https://www.linkedin.com/in/kshitij-singh-57a248337

---

## 📄 License

This project is intended for educational and personal development purposes.