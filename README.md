# AAVA - Authorised Address Validation Agency

> A Streamlit-based demonstration of the Address Validation system for India's DHRUVA Digital Address Ecosystem

![AAVA Banner](https://img.shields.io/badge/AAVA-Address%20Validation%20Agency-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)

## 🎯 Overview

AAVA (Authorised Address Validation Agency) is a comprehensive address validation system designed for the DHRUVA digital address ecosystem. It provides:

- **DIGIPIN Integration**: Full support for India's 10-character geocode system
- **Multi-Modal Validation**: Physical, Digital, and Hybrid validation workflows
- **Confidence Scoring**: Algorithmic scoring based on delivery history, spatial consistency, temporal freshness, and physical verification
- **Field Agent Management**: Complete agent lifecycle and task management
- **Consent Management**: Privacy-first approach with explicit consent handling
- **Audit Trail**: Immutable logging for all operations

## 🏗️ Architecture

```
AAVA System
├── Frontend (Streamlit)
│   ├── Dashboard
│   ├── Validation Request Portal
│   ├── Agent Portal
│   ├── Confidence Score Viewer
│   └── Admin Panel
│
├── Backend (Python)
│   ├── DIGIPIN Encoder/Decoder
│   ├── Confidence Score Calculator
│   └── Database Manager
│
└── Storage (SQLite)
    ├── Addresses
    ├── Validations
    ├── Agents
    ├── Deliveries
    ├── Verifications
    └── Audit Logs
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or extract the project**
   ```bash
   cd "Development of AAVA"
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate sample data** (optional but recommended)
   ```bash
   python utils/sample_data.py
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   - The app will automatically open at `http://localhost:8501`

## 📁 Project Structure

```
Development of AAVA/
├── app.py                          # Main Streamlit entry point
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── pages/                          # Multi-page Streamlit pages
│   ├── 1_🏠_Home.py               # Landing page
│   ├── 2_✅_Validation_Request.py # Request validation
│   ├── 3_📱_Agent_Portal.py       # Field agent interface
│   ├── 4_📊_Confidence_Score.py   # Score viewer
│   └── 5_⚙️_Admin_Panel.py        # Administration
│
├── utils/                          # Core utilities
│   ├── __init__.py
│   ├── digipin.py                 # DIGIPIN encode/decode
│   ├── confidence_score.py        # Scoring algorithm
│   ├── database.py                # SQLite operations
│   └── sample_data.py             # Sample data generator
│
└── data/                          # Auto-created data folder
    └── aava.db                    # SQLite database
```

## 🔧 Features

### 1. DIGIPIN System

The DIGIPIN (Digital Postal Index Number) system is a 10-character geocode:

- **Format**: `XXX-XXX-XXXX` (e.g., `3PJ-K4M-5L2T`)
- **Coverage**: All of India (Lat 2.5°N - 38.5°N, Lon 63.5°E - 99.5°E)
- **Precision**: 4m × 4m at highest resolution (Level 10)
- **Alphabet**: `2, 3, 4, 5, 6, 7, 8, 9, C, F, J, K, L, M, P, T`

### 2. Confidence Scoring

The confidence score (0-100) is calculated from four components:

| Component | Weight | Description |
|-----------|--------|-------------|
| Delivery Success Rate | 30% | Historical delivery outcomes |
| Spatial Consistency | 30% | GPS accuracy across deliveries |
| Temporal Freshness | 20% | Recency of data |
| Physical Verification | 20% | Agent verification status |

**Grades**:
- **A+**: 90-100 (Excellent)
- **A**: 80-89 (Good)
- **B**: 70-79 (Satisfactory)
- **C**: 60-69 (Acceptable)
- **D**: 50-59 (Poor)
- **F**: Below 50 (Unreliable)

### 3. Validation Workflows

#### Physical Validation
```
Request → Agent Assignment → Field Visit → Evidence Collection → Verification
```

#### Digital Validation
```
Request → Delivery History Analysis → Confidence Calculation → Result
```

#### Hybrid Validation
```
Digital Analysis + Physical Verification → Combined Score
```

### 4. Agent Portal

Field agents can:
- View assigned tasks sorted by priority
- Navigate to locations using integrated maps
- Upload photo/video evidence
- Capture GPS coordinates
- Submit verification results

### 5. Admin Panel

Administrators can:
- View system-wide statistics
- Manage validations and agents
- Generate sample data for testing
- View audit logs
- Export reports

## 📊 API Reference

### DIGIPIN Validator

```python
from utils.digipin import DIGIPINValidator

validator = DIGIPINValidator()

# Encode coordinates to DIGIPIN
result = validator.encode(28.6139, 77.2090)
print(result.digipin)  # e.g., "3PJK4M5L2T"

# Decode DIGIPIN to coordinates
result = validator.decode("3PJK4M5L2T")
print(result.latitude, result.longitude)

# Validate format
is_valid = validator.validate_format("3PJ-K4M-5L2T")
```

### Confidence Score Calculator

```python
from utils.confidence_score import ConfidenceScoreCalculator

calculator = ConfidenceScoreCalculator()

# Calculate score
deliveries = [...]  # List of delivery records
verifications = [...]  # List of verification records

score = calculator.calculate_confidence(
    deliveries=deliveries,
    verifications=verifications
)

print(f"Score: {score['total_score']}")
print(f"Grade: {score['grade']}")
```

### Database Operations

```python
from utils.database import get_database

db = get_database()

# Create validation
validation_id = db.create_validation({
    'digipin': '3PJK4M5L2T',
    'validation_type': 'HYBRID',
    'priority': 'NORMAL'
})

# Get validation
validation = db.get_validation(validation_id)

# Get statistics
stats = db.get_dashboard_stats()
```

## 🔒 Security & Privacy

- **Consent Management**: Explicit consent required before validation
- **Data Minimization**: Only necessary data collected
- **Audit Trail**: All operations logged with cryptographic chaining
- **Access Control**: Role-based access (Agent, Admin, API)

## 🧪 Testing

Run the database tests:
```bash
python utils/database.py
```

Run DIGIPIN tests:
```bash
python utils/digipin.py
```

## 📝 License

This project is developed for the DHRUVA hackathon demonstration purposes.

## 🤝 Contributing

This is a hackathon project. For production deployment, please contact the AAVA team.

## 📞 Support

For questions or issues, please refer to the DHRUVA documentation or contact the development team.

---

**Built with ❤️ for India's Digital Address Ecosystem**
