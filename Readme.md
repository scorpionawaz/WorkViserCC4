# 🧠 WorkViser: AI-Powered Productivity Platform for Remote Teams

WorkViser is a cross-platform AI-powered software tool designed to **enhance the productivity and efficiency** of **remotely working employees and managers**. It uses voice automation, real-time notifications, and smart task orchestration to streamline communication and work management.


---

## 🏗️ Architecture Diagram

![Screenshot](./Screenshot%202025-06-30%20181622.png)

<!-- Replace the above path with your actual diagram image or external link -->

---

WorkViser is designed to optimize remote workflows with a modular architecture:

- 🎙️ **Voice Agent (OmniDimension)**: Users can access the AI agent by simply calling a phone number. The voice assistant is hosted and managed via OmniDimension, providing task assistance and conversational support without requiring local setup.
- ⚙️ **Backend**: FastAPI handles business logic, authentication, and API endpoints.
- 💼 **Manager Frontend**: A Next.js dashboard for assigning, tracking, and evaluating employee tasks.
- 🖥️ **Employee Desktop Client**: Built with C# .NET for notifications, check-ins, and voice triggers.
- 📡 **MongoDB**: NoSQL database for efficient storage of task, user, and interaction data.

---

## 🧰 Tech Stack


| Component            | Technology/Service                               |
|----------------------|---------------------------------------------------|
| 🧠 Voice Agent        | **OmniDimension** – Accessible via phone call    |
| 🤖 Language Model     | **LLaMA (Meta AI)** – Locally hosted LLM         |
| 🖥️ Employee App       | **C# .NET** – Windows desktop application         |
| 🌐 Manager Frontend   | **Next.js** – React, Tailwind CSS                 |
| ⚙️ Backend API        | **FastAPI (Python)** |
| 🗃️ Database           | **MongoDB** – Cloud/Local NoSQL datastore         |
| 🚀 Deployment         | **AWS EC2**, **GitHub Actions** (CI/CD)          |


---

## ⚙️ Backend Installation (FastAPI)

To set up and run the FastAPI backend locally:

```bash
# Step 1: Clone the repository
git clone https://github.com/workviser/workviser.git

# Step 2: (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Create a .env file with the following environment variables
GROQ_API_KEY=your-groq-api-key
DATABASE_NAME=workviser
HOST=localhost
PORT=8000
MONGO_URI=mongodb://localhost:27017

# Step 5: Run the FastAPI server
uvicorn main:app --reload



