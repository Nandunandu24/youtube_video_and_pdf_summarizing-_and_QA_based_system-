

# 📌 AI-Powered YouTube & PDF Summarization System

---

## 1️⃣ Problem Statement

With the exponential growth of online video content and digital documents, users often struggle to consume long YouTube videos and large PDF files efficiently. Manually watching hours of videos or reading lengthy documents is time-consuming and impractical, especially for students, researchers, and professionals.

There is a need for an intelligent system that can:

* Automatically transcribe YouTube videos
* Summarize long-form content
* Enable users to extract meaningful insights quickly
* Provide a simple and user-friendly interface

---

## 2️⃣ Project Overview

This project is a **full-stack AI-powered application** that allows users to:

* Input a YouTube video URL or upload a PDF file
* Automatically transcribe audio content using Whisper
* Generate concise summaries using NLP and vector-based retrieval
* Ask questions over the content using a Retrieval-Augmented Generation (RAG) pipeline

The system is built using **FastAPI for backend**, **React for frontend**, and deployed using **Vercel (frontend)** and **Railway (backend)**.

---

## 3️⃣ Objectives

* Automate YouTube video transcription
* Enable summarization of long videos and PDFs
* Implement semantic search using vector embeddings
* Provide question-answering capability over content
* Build an end-to-end deployable AI system
* Ensure scalability and modular design
* Deliver a clean and intuitive user interface

---

## 4️⃣ Proposed System

The proposed system consists of two major components:

### 🔹 Backend (AI Engine)

* Handles YouTube audio download
* Transcribes audio using Whisper
* Processes PDFs for text extraction
* Generates embeddings using sentence-transformers
* Stores embeddings in FAISS for fast retrieval
* Performs summarization and Q&A via RAG pipeline

### 🔹 Frontend (User Interface)

* Accepts YouTube URLs and PDF uploads
* Displays summaries and responses
* Communicates with backend APIs
* Provides real-time feedback to users

---

## 5️⃣ Working Flow of the System

1. User enters a YouTube URL or uploads a PDF file
2. Backend downloads YouTube audio (if applicable)
3. Whisper transcribes the audio into text
4. PDF content is extracted and cleaned
5. Text is chunked and converted into vector embeddings
6. Embeddings are stored in FAISS index
7. User requests summary or asks a question
8. Relevant chunks are retrieved using similarity search
9. Final response is generated and returned to frontend
10. Output is displayed to the user

---

## 6️⃣ Tools and Technologies Used

### 🔹 Technology Stack Table

| Category              | Tools / Technologies           | Purpose                             |
| --------------------- | ------------------------------ | ----------------------------------- |
| Programming Language  | Python, JavaScript             | Core backend & frontend development |
| Backend Framework     | FastAPI                        | API development                     |
| Frontend Framework    | React + Vite                   | User interface                      |
| AI / NLP              | Whisper, Sentence-Transformers | Transcription & embeddings          |
| Vector Database       | FAISS                          | Semantic search                     |
| Video Processing      | yt-dlp, ffmpeg                 | Audio extraction                    |
| PDF Processing        | pdfplumber                     | Text extraction                     |
| ML Framework          | PyTorch                        | Model execution                     |
| API Server            | Uvicorn                        | ASGI server                         |
| Deployment (Frontend) | Vercel                         | Hosting frontend                    |
| Deployment (Backend)  | Railway                        | Hosting backend                     |
| Version Control       | Git, GitHub                    | Source code management              |

---

## 7️⃣ Steps to Execute the Project

### 🔹 Backend Execution (Local)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Access API documentation:

```
http://localhost:8000/docs
```

---

### 🔹 Frontend Execution (Local)

```bash
cd frontend
npm install
npm run dev
```

Access frontend:

```
http://localhost:5173
```

---

## 8️⃣ Deployment Details

### 🔹 Frontend Deployment (Vercel)

* Connected GitHub repository
* Deployed `frontend/` folder
* Environment variable added:

```
VITE_BACKEND_URL = https://your-backend-url.up.railway.app
```

### 🔹 Backend Deployment (Railway)

* Deployed `backend/` folder
* Environment variable:

```
PORT = 8000
```

---

## 9️⃣ Output

* Successful transcription of YouTube videos
* Accurate summaries of long videos and PDFs
* Fast semantic search and Q&A responses
* Fully functional deployed web application
* Public URLs for frontend and backend services

---

## 🔟 Conclusion

This project demonstrates a complete **end-to-end AI application**, integrating NLP, vector search, and full-stack deployment. It effectively solves the problem of information overload by providing users with summarized insights and intelligent querying over multimedia content.

The system is scalable, modular, and suitable for real-world use cases in education, research, and professional knowledge management.

---


Just tell me what you want next.
