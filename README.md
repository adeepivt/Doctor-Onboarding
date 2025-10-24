# 🏥 Doctor Onboarding API

A comprehensive GraphQL API built with FastAPI and Strawberry GraphQL for managing a multi-step doctor onboarding process. This API supports progressive data saving, allowing doctors to complete their registration across multiple sessions.

---

## 🔗 Live Demo

- **API Endpoint:** `https://doctor-onboarding-api.onrender.com/graphql`
- **API Documentation:** `https://doctor-onboarding-api.onrender.com/docs`

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **GraphQL:** Strawberry GraphQL
- **Database:** PostgreSQL
- **Database Driver:** psycopg2
- **Server:** Uvicorn
- **Deployment:** Render
- **Container:** Docker (Optional)

---

## 📁 Project Structure

```
doctor-onboarding-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database connection and query handlers
│   ├── models.py               # Strawberry GraphQL types and input types
│   └── schema/
│       ├── __init__.py
│       ├── helpers.py          # Helper functions for data fetching
│       ├── mutations.py        # GraphQL mutations
│       └── queries.py          # GraphQL queries
├── init.sql                    # Database schema initialization
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose setup
└── README.md                   # Project documentation
```

---

## 🗄️ Database Schema

### Main Tables

- **doctors** - Core doctor information with onboarding status tracking
- **doctor_mobile_numbers** - Multiple mobile numbers per doctor (supports adding multiple contact numbers)
- **departments** - Medical departments (pre-seeded with 10 departments)
- **doctor_departments** - Many-to-many relationship between doctors and departments
- **qualifications** - Doctor's educational qualifications (MBBS, MD, etc.)
- **specializations** - Medical specializations (Cardiology, Surgery, etc.)
- **addresses** - Practice address with geo-coordinates for map integration
- **appointment_settings** - Consultation charges and availability settings
- **schedules** - Weekly availability schedule (day-wise time slots)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 14+
- Docker & Docker Compose (for local development)

### Option 1: Local Setup with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/adeepivt/Doctor-Onboarding.git
cd doctor-onboarding-api

# Start services
docker-compose up --build
```

The API will be available at:
- **GraphQL Playground:** http://localhost:8000/graphql
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/adeepivt/Doctor-Onboarding.git
cd doctor-onboarding-api

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/docdb"
export PORT=8000

# Initialize database
psql -U your_user -d your_database -f init.sql

# Run the application
uvicorn app.main:app --reload
```

Access the API at http://localhost:8000

---

## 🎯 Design Decisions and Assumptions


**1:** Used raw SQL with psycopg2 instead of an ORM.

**2:** Implemented independent step-based mutations that can be completed in any order.

**3:** Created a separate `doctor_mobile_numbers` table instead of a single mobile field.


### Key Assumptions

- **Multiple Departments:** Doctors can practice in multiple departments (many-to-many)
- **Single Address:** Each doctor has one primary practice address (one-to-one)
- **Weekly Schedule:** Repeating weekly schedule (not date-specific appointments)
- **Day of Week:** Integers 0-6 (0=Sunday, 6=Saturday)

---

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and available endpoints |
| `/graphql` | GET/POST | GraphQL playground and API |
| `/docs` | GET | Interactive API documentation (Swagger) |
| `/health` | GET | Health check endpoint |

---

## 📚 Example Queries/Mutations

### Query: Get All Departments

```graphql
query {
  departments {
    id
    name
    iconName
  }
}
```

### Mutation: Start Onboarding

```graphql
mutation {
  startOnboarding(
    registerNo: "REG12345"
    email: "doctor@example.com"
    mobile: "+919876543210"
  ) {
    id
    email
    currentStep
    onboardingStatus
  }
}
```

### Mutation: Update Doctor Name (Step 2)

```graphql
mutation {
  updateDoctorName(doctorId: 1, name: "Dr. John Doe") {
    id
    name
    currentStep
  }
}
```

### Mutation: Update Schedule

```graphql
mutation {
  updateSchedule(
    doctorId: 1
    schedules: [
      {
        dayOfWeek: 1
        startTime: "09:00:00"
        endTime: "17:00:00"
        isAvailable: true
      }
      {
        dayOfWeek: 3
        startTime: "09:00:00"
        endTime: "17:00:00"
        isAvailable: true
      }
    ]
  ) {
    id
    schedules {
      dayOfWeek
      startTime
      endTime
    }
    currentStep
  }
}
```

### Mutation: Add Departments 

```graphql
mutation {
  addDepartments(doctorId: 1, departmentIds: [1, 2]) {
    id
    departments {
      id
      name
    }
    currentStep
  }
}
```

### Mutation: Complete Onboarding

```graphql
mutation {
  completeOnboarding(doctorId: 1) {
    id
    onboardingStatus
    currentStep
  }
}
```

### Query: Get Doctor with All Information

```graphql
query {
  doctor(id: 1) {
    id
    name
    email
    mobile
    registerNo
    bio
    profileImageUrl
    onboardingStatus
    currentStep
    departments {
      name
    }
    qualifications
    specializations
    address {
      country
      state
      city
      pincode
    }
    appointmentSettings {
      consultationCharge
      followUpCharge
    }
    schedules {
      dayOfWeek
      startTime
      endTime
    }
  }
}
```

### Query: Check if Already Registered

```graphql
query {
  checkRegistration(email: "doctor@example.com") {
    id
    name
    email
    registerNo
  }
}
```

### Query: Get Onboarding Progress Metadata

```graphql
query {
  onboardingMetadata(doctorId: 1) {
    totalSteps
    completedSteps
    currentStep
    isComplete
  }
}
```

### Query: Get All Doctors

```graphql
query {
  allDoctors {
    id
    name
    email
    onboardingStatus
    currentStep
  }
}
```

**Filter by status:**

```graphql
query {
  allDoctors(status: "completed") {
    id
    name
    email
  }
}
```

---


---

## 🔧 Environment Variables

Configure these in your `.env` file or docker-compose.yml:

```env
DATABASE_URL=postgresql://docuser:docpass@db:5432/docdb
PORT=8000
```

---

## 👤 Author

**ADEEP I V T**  
📧 Email: adeepivt@gmail.com  
🐙 GitHub: [@adeepivt](https://github.com/adeepivt)

---
