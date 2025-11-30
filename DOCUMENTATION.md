# AAVA - Authorised Address Validation Agency

## 📋 Project Documentation

---

## 🎯 Overview

**AAVA** (Authorised Address Validation Agency) is a comprehensive web application. It is part of India's **DHRUVA Digital Address Ecosystem** - a Government of India initiative by the Department of Posts.

### Problem Statement
- 60-80 million households in India lack formal addresses
- Rural areas have ambiguous landmark-based addresses
- Urban slums/informal settlements excluded from formal systems
- No standardized digital addressing infrastructure
- Delivery failures cost the economy billions annually

### Solution
AAVA provides a unified digital addressing system with address validation, DIGIPIN geocoding, confidence scoring, and AI-powered assistance.

---

## 🏗️ Architecture

### DHRUVA Ecosystem Components

| Component | Full Form | Role |
|-----------|-----------|------|
| **DIGIPIN** | Digital Postal Index Number | 10-character geocode system |
| **DARPAN** | Digital Address Repository for Precision Addressing Network | Central address database |
| **DIVYA** | Digital Interface for Verified and Yielded Addresses | Citizen portal |
| **AAVA** | Authorised Address Validation Agency | Third-party validation |

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Streamlit (Python) |
| **Backend** | Python 3.8+ |
| **Database** | SQLite |
| **Maps** | Folium + Streamlit-Folium |
| **Charts** | Plotly Express |
| **AI Chat** | Google Gemini API |

---

## 📁 Project Structure

```
Development of AAVA/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (API keys)
├── .gitignore                  # Git ignore rules
├── README.md                   # Project readme
├── DOCUMENTATION.md            # This file
├── COMPLIANCE_REPORT.md        # Compliance status report
│
├── pages/                      # Streamlit multi-page app
│   ├── 1_✅_Validation_Request.py
│   ├── 2_📱_Agent_Portal.py
│   ├── 3_📊_Confidence_Score.py
│   ├── 4_⚙️_Admin_Panel.py
│   └── 6_🤖_AI_Chat.py
│
├── utils/                      # Utility modules
│   ├── database.py             # SQLite CRUD operations
│   ├── digipin.py              # DIGIPIN encode/decode
│   └── confidence_score.py     # Score algorithm
│
├── assets/                     # Static assets
│   ├── download.jpeg           # AI assistant avatar
│   └── baby.png                # User avatar
│
├── data/                       # Data storage
│   ├── aava.db                 # SQLite database
│   ├── chat_memory.json        # AI chat history
│   ├── learned_qa.json         # Learned Q&A pairs
│   └── all_chats.json          # All chat sessions
│
└── .streamlit/
    └── secrets.toml            # Streamlit secrets (API keys)
```

---

## 📄 Pages Description

### 🏠 Home (app.py)
- System overview dashboard
- Total addresses, validations, agents metrics
- Recent activity feed
- Quick navigation to all features

### ✅ Validation Request
- Submit new address validation requests
- Enter address details + DIGIPIN
- Select validation type (Digital/Physical/Hybrid)
- Consent collection
- Track existing validation requests

### 📱 Agent Portal
- Agent login/authentication
- View assigned tasks by priority
- Navigate to location (map integration)
- Capture photo/video evidence
- GPS coordinate capture
- Submit verification reports
- View performance statistics

### 📊 Confidence Score
- Calculate confidence score for any address
- View component breakdown:
  - DSR (Delivery Success Rate) - 30%
  - SC (Spatial Consistency) - 30%
  - TF (Temporal Freshness) - 20%
  - PVS (Physical Verification Status) - 20%
- See grade (A+ to F) and recommendations
- Simulate score changes

### ⚙️ Admin Panel
- System-wide statistics
- Manage validations and agents
- Generate sample data
- View audit logs
- Configuration settings
- Export reports

### 🤖 AI Chat
- General-purpose AI assistant (Gemini-powered)
- Answers ANY topic (academics, coding, general knowledge)
- Special expertise in AAVA/DIGIPIN
- DIGIPIN encode/decode commands
- Persistent chat memory (48-hour retention)
- Multiple chat sessions with history

---

## 🔢 DIGIPIN Technical Specifications

### What is DIGIPIN?
A **10-character alphanumeric geocode** that pinpoints any location in India to approximately **4m × 4m** accuracy.

### Character Set (16 characters)
```
2 3 4 5 6 7 8 9 C F J K L M P T
```

### Geographic Bounds (India)
| Parameter | Value |
|-----------|-------|
| MIN_LAT | 2.5°N |
| MAX_LAT | 38.5°N |
| MIN_LON | 63.5°E |
| MAX_LON | 99.5°E |

### Grid Label Matrix (4×4)
```
      Col 0   Col 1   Col 2   Col 3
     ─────────────────────────────
Row 0 │   F   │   C   │   9   │   8   │
Row 1 │   J   │   3   │   2   │   7   │
Row 2 │   K   │   4   │   5   │   6   │
Row 3 │   L   │   M   │   P   │   T   │
```

### Resolution by Level
| Level | Approx. Size |
|-------|--------------|
| 1 | ~1000 km |
| 5 | ~4 km |
| 10 | ~4 m |

### Format
- Raw: `3PJK4M5L2T`
- Display: `3PJ-K4M-5L2T`

---

## 📊 Confidence Score Algorithm

### Formula
```
SCORE = 100 × [(DSR × 0.30) + (SC × 0.30) + (TF × 0.20) + (PVS × 0.20)]
```

### Components

#### 1. Delivery Success Rate (DSR) - 30%
| Status | Points |
|--------|--------|
| DELIVERED | 100 |
| DELIVERED_WITH_DIFFICULTY | 50 |
| FAILED | 0 |

#### 2. Spatial Consistency (SC) - 30%
```
SC = exp(-(avg_distance / 50m)²)
```

#### 3. Temporal Freshness (TF) - 20%
```
TF = exp(-ln(2)/180 × days_since_last)
```
Half-life: 180 days

#### 4. Physical Verification Status (PVS) - 20%
```
PVS = quality_score × exp(-decay × days_since)
```

### Grade Thresholds
| Grade | Score | Meaning |
|-------|-------|---------|
| A+ | 90-100 | Excellent |
| A | 80-89 | Very Good |
| B | 70-79 | Good |
| C | 60-69 | Fair |
| D | 50-59 | Poor |
| F | 0-49 | Fail |

---

## 🗄️ Database Schema

### 7 Core Tables

1. **addresses** - Address records with DIGIPIN, coordinates, confidence scores
2. **validations** - Validation requests with status tracking
3. **agents** - Field agent information and performance
4. **deliveries** - Delivery attempt records for DSR calculation
5. **verifications** - Physical verification records with evidence
6. **consents** - User consent artifacts
7. **audit_logs** - Immutable action log with hash chaining

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/Razz0711/AAVA.git
cd AAVA
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Set up environment variables**
Create `.env` file:
```
GEMINI_API_KEY=your_api_key_here
```

6. **Run the application**
```bash
streamlit run app.py
```

7. **Open in browser**
```
http://localhost:8501
```

---

## 📦 Dependencies

```
streamlit
pandas
numpy
plotly
folium
streamlit-folium
Pillow
python-dateutil
google-generativeai
python-dotenv
```

---

## 🔐 Security

### API Key Protection
- API keys stored in `.env` file (not committed to Git)
- Backup in `.streamlit/secrets.toml`
- Both files excluded via `.gitignore`

### Data Security
- Consent-based data access
- Audit logging with hash chains
- Immutable record keeping

---

## 🌐 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets in Streamlit Cloud dashboard:
   - `GEMINI_API_KEY = "your_api_key"`
5. Deploy

### Live URL
```
https://aava-app.streamlit.app
```

---

## 🤖 AI Chat Features

### Capabilities
- **General Purpose AI**: Answers any topic
- **Academic Help**: Syllabus questions, homework, exam prep
- **AAVA Expertise**: DIGIPIN operations, confidence scores
- **Coding Help**: Any programming language

### Special Commands
```
encode 28.6139, 77.2090    → Convert coordinates to DIGIPIN
decode 3PJK4M5L2T          → Get coordinates from DIGIPIN
validate 3PJ-K4M-5L2T      → Check DIGIPIN validity
show stats                  → Display system statistics
```

### Chat Management
- Multiple chat sessions
- 48-hour auto-delete for privacy
- Edit/rename chat titles
- Persistent memory across sessions

---

## 📈 Compliance Status

**Overall Compliance: 96.4%**

| Category | Compliant |
|----------|-----------|
| DIGIPIN Specs | 10/10 ✅ |
| Confidence Score | 12/12 ✅ |
| Validation Workflow | 8/8 ✅ |
| Database Schema | 7/7 ✅ |
| API/UI | 12/12 ✅ |
| Security | 4/6 ⚠️ |

---

## 👥 Team

- Project: AAVA - Authorised Address Validation Agency
- Problem Statement: Digital Address Ecosystem
- Organization: Department of Posts, Government of India

---

## 📄 License

This project is developed as part of the DHRUVA Digital Address Ecosystem initiative.

---

## 📞 Support

For issues or questions:
- GitHub Issues: [AAVA Repository](https://github.com/Razz0711/AAVA/issues)

---

*Last Updated: November 30, 2025*
