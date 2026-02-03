# ✈️ CMPE331 Flight Roster System

This project is a comprehensive web application designed with a microservices-like architecture to handle flight management, crew rostering, and intelligent passenger seating assignments.

## 🏗️ Project Architecture and Ports

The system consists of 4 distinct parts, and each must be run in its own terminal:

| Service Name | Directory Path | Port | Description |
| :--- | :--- | :--- | :--- |
| **Frontend** | `flight_roster_system` | **5173** | React (Vite) User Interface |
| **Flight API** | `passenger_flight` | **8000** | Flight and Passenger database service |
| **Main System** | `Main_System` | **8001** | Main Orchestrator and Auth (Login) service |
| **Crew API** | `pilot_cabin` | **8002** | Pilot and Cabin Crew database service |

---

## 🛠️ Installation

After downloading the project to your computer, follow these steps in order.

### 1. Backend Setup (Python)

Open a terminal in the root directory and install the required libraries:

```bash
# Create a virtual environment (Optional but recommended)
python3 -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
