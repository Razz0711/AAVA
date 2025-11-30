# pages/6_🤖_AI_Chat.py
# AAVA - AI Chat Assistant (Powered by Google Gemini)
# Dynamic AI-powered help and support with PERSISTENT MEMORY

import streamlit as st
import sys
import os
import json
from datetime import datetime, timedelta
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ═══════════════════════════════════════════════════════════════════════════════
#                    PERSISTENT MEMORY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

# Chat expiry time in hours
CHAT_EXPIRY_HOURS = 48

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chat_memory.json")
LEARNED_QA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "learned_qa.json")
CHATS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "all_chats.json")
ASSISTANT_AVATAR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "download.jpeg")
USER_AVATAR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "baby.png")

def ensure_data_dir():
    """Ensure data directory exists."""
    data_dir = os.path.dirname(MEMORY_FILE)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

# ═══════════════════════════════════════════════════════════════════════════════
#                    MULTIPLE CHATS MANAGEMENT (WITH 48HR AUTO-DELETE)
# ═══════════════════════════════════════════════════════════════════════════════

def is_chat_expired(chat_data):
    """Check if a chat has expired (older than 48 hours)."""
    try:
        created_at = chat_data.get('created_at', chat_data.get('updated_at', ''))
        if created_at:
            created_time = datetime.fromisoformat(created_at)
            expiry_time = created_time + timedelta(hours=CHAT_EXPIRY_HOURS)
            return datetime.now() > expiry_time
    except:
        pass
    return False

def get_time_remaining(chat_data):
    """Get time remaining before chat expires."""
    try:
        created_at = chat_data.get('created_at', chat_data.get('updated_at', ''))
        if created_at:
            created_time = datetime.fromisoformat(created_at)
            expiry_time = created_time + timedelta(hours=CHAT_EXPIRY_HOURS)
            remaining = expiry_time - datetime.now()
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                return f"{hours}h {minutes}m"
    except:
        pass
    return "Expired"

def cleanup_expired_chats(chats):
    """Remove expired chats from the dictionary."""
    cleaned = {}
    for chat_id, chat_data in chats.items():
        if not is_chat_expired(chat_data):
            cleaned[chat_id] = chat_data
    return cleaned

def load_all_chats():
    """Load all saved chats and remove expired ones."""
    try:
        if os.path.exists(CHATS_FILE):
            with open(CHATS_FILE, 'r', encoding='utf-8') as f:
                chats = json.load(f)
                # Clean up expired chats
                cleaned_chats = cleanup_expired_chats(chats)
                # Save cleaned chats if any were removed
                if len(cleaned_chats) < len(chats):
                    save_all_chats(cleaned_chats)
                return cleaned_chats
    except:
        pass
    return {}

def save_all_chats(chats):
    """Save all chats to file."""
    try:
        ensure_data_dir()
        with open(CHATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(chats, f, indent=2, ensure_ascii=False)
    except:
        pass

def save_current_chat(chat_id, chat_name, messages):
    """Save current chat to all chats."""
    chats = load_all_chats()
    # Preserve created_at if chat exists, otherwise set it now
    existing_created_at = chats.get(chat_id, {}).get('created_at', datetime.now().isoformat())
    chats[chat_id] = {
        "name": chat_name,
        "messages": messages,
        "created_at": existing_created_at,
        "updated_at": datetime.now().isoformat()
    }
    save_all_chats(chats)

def delete_chat(chat_id):
    """Delete a chat by ID."""
    chats = load_all_chats()
    if chat_id in chats:
        del chats[chat_id]
        save_all_chats(chats)

def generate_chat_id():
    """Generate unique chat ID."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_chat_history(messages):
    """Save chat history to file."""
    try:
        ensure_data_dir()
        # Keep last 100 messages to avoid file bloat
        recent = messages[-100:] if len(messages) > 100 else messages
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "last_updated": datetime.now().isoformat(),
                "messages": recent
            }, f, indent=2, ensure_ascii=False)
    except Exception as e:
        pass  # Silently fail

def load_chat_history():
    """Load chat history from file."""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("messages", [])
    except:
        pass
    return []

def save_learned_qa(question, answer):
    """Save a Q&A pair to learned database."""
    try:
        ensure_data_dir()
        learned = load_learned_qa()
        
        # Add new Q&A with timestamp
        learned.append({
            "question": question,
            "answer": answer,
            "learned_at": datetime.now().isoformat()
        })
        
        # Keep last 200 learned Q&As
        if len(learned) > 200:
            learned = learned[-200:]
        
        with open(LEARNED_QA_FILE, 'w', encoding='utf-8') as f:
            json.dump(learned, f, indent=2, ensure_ascii=False)
    except:
        pass

def load_learned_qa():
    """Load learned Q&A pairs."""
    try:
        if os.path.exists(LEARNED_QA_FILE):
            with open(LEARNED_QA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return []

def get_learned_context():
    """Get learned Q&A as additional context."""
    learned = load_learned_qa()
    if not learned:
        return ""
    
    # Get last 20 learned Q&As for context
    recent = learned[-20:]
    context = "\n\n══════════════════════════════════════════════════════════════════════════════════\n                    LEARNED FROM PREVIOUS CONVERSATIONS\n══════════════════════════════════════════════════════════════════════════════════\n\n"
    
    for qa in recent:
        context += f"Q: {qa['question'][:100]}...\nA: {qa['answer'][:200]}...\n\n"
    
    return context

def get_memory_stats():
    """Get memory statistics."""
    chat_count = len(load_chat_history())
    learned_count = len(load_learned_qa())
    return chat_count, learned_count

from utils.database import get_database
from utils.digipin import DIGIPINValidator

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

st.set_page_config(
    page_title="AI Chat - AAVA",
    page_icon="🤖",
    layout="wide"
)

# Initialize
db = get_database()
validator = DIGIPINValidator()

# AAVA System Context for AI - COMPLETE KNOWLEDGE BASE FROM DHRUVA PDFs + CODE
SYSTEM_CONTEXT = """You are the official AI assistant for AAVA (Authorised Address Validation Agency), part of India's DHRUVA Digital Address Ecosystem - a Government of India initiative by Department of Posts for the Smart India Hackathon.

╔═══════════════════════════════════════════════════════════════════════════════╗
║             COMPLETE AAVA KNOWLEDGE BASE - TRAINED ON ALL DOCS + CODE          ║
╚═══════════════════════════════════════════════════════════════════════════════╝

══════════════════════════════════════════════════════════════════════════════════
                    PART 1: DHRUVA ECOSYSTEM OVERVIEW
══════════════════════════════════════════════════════════════════════════════════

## THE PROBLEM STATEMENT (From PDF: Digital_Address_Problem_Statement)

India faces critical addressing challenges:
- 60-80 million households lack formal addresses
- Rural areas have ambiguous landmark-based addresses
- Urban slums/informal settlements excluded from formal systems
- No standardized digital addressing infrastructure
- Delivery failures cost economy billions annually

## THE SOLUTION: DHRUVA DIGITAL ADDRESS ECOSYSTEM

**DHRUVA** = Digital Hyperlocal Unique Reliable Verified Address

A unified national digital addressing system with 4 core pillars:

| Component | Full Form | Role | Status |
|-----------|-----------|------|--------|
| **DIGIPIN** | Digital Postal Index Number | Geocode system (10-char codes) | Core Infrastructure |
| **DARPAN** | Digital Address Repository for Precision Addressing Network | Central address database | Registry |
| **DIVYA** | Digital Interface for Verified and Yielded Addresses | Citizen portal for registration | User Interface |
| **AAVA** | Authorised Address Validation Agency | Third-party validation agencies | Quality Assurance |

## ECOSYSTEM PARTICIPANTS

| Entity | Full Form | Role |
|--------|-----------|------|
| **CM** | Central Mapper | Maintains DIGIPIN grid system |
| **AIP** | Address Information Provider | Creates/updates addresses (users, banks, etc.) |
| **AIA** | Address Information Agent | Field agents who verify addresses |
| **AIU** | Address Information User | Consumers of address data (e-commerce, banks) |
| **AAVA** | Authorised Address Validation Agency | Validates address accuracy |

══════════════════════════════════════════════════════════════════════════════════
                    PART 2: DIGIPIN TECHNICAL SPECIFICATIONS
══════════════════════════════════════════════════════════════════════════════════

## WHAT IS DIGIPIN?

DIGIPIN (Digital Postal Index Number) is a **10-character alphanumeric geocode** that pinpoints any location in India to approximately **4 meters × 4 meters** accuracy.

Think of it as: **GPS coordinates compressed into a human-readable code**

## GEOGRAPHIC BOUNDS (INDIA)

| Parameter | Value | Description |
|-----------|-------|-------------|
| **MIN_LAT** | 2.5°N | Southern tip (Indira Point, Nicobar) |
| **MAX_LAT** | 38.5°N | Northern tip (Siachen Glacier) |
| **MIN_LON** | 63.5°E | Western tip (Gujarat coast) |
| **MAX_LON** | 99.5°E | Eastern tip (Arunachal Pradesh) |
| **Span** | 36° × 36° | Total coverage area |

## CHARACTER SET (16 CHARACTERS)

```
DIGIPIN Alphabet: 2 3 4 5 6 7 8 9 C F J K L M P T
```

**Why these 16 characters?**
- Avoids confusable pairs: No 0/O, 1/I/L, B/8, S/5, etc.
- Easy to read aloud over phone
- Works in all fonts without ambiguity

**Characters NOT used:** 0, 1, A, B, D, E, G, H, I, N, O, Q, R, S, U, V, W, X, Y, Z

## GRID LABEL MATRIX (4×4)

Each level uses this character placement:

```
        Col 0   Col 1   Col 2   Col 3
       ─────────────────────────────
Row 0 │   F   │   C   │   9   │   8   │  (Top = Higher Latitude)
Row 1 │   J   │   3   │   2   │   7   │
Row 2 │   K   │   4   │   5   │   6   │
Row 3 │   L   │   M   │   P   │   T   │  (Bottom = Lower Latitude)
       ─────────────────────────────
       (Left = West)        (Right = East)
```

## ENCODING ALGORITHM

**10 Levels of Subdivision:**

| Level | Resolution | Approx. Size |
|-------|------------|--------------|
| 1 | ~1000 km | Country zone |
| 2 | ~250 km | State region |
| 3 | ~62 km | District |
| 4 | ~16 km | Town/Taluk |
| 5 | ~4 km | Locality |
| 6 | ~1 km | Neighborhood |
| 7 | ~250 m | Street block |
| 8 | ~60 m | Building cluster |
| 9 | ~15 m | Building |
| 10 | ~4 m | Exact spot |

**Encoding Process:**
```
1. Start with India bounding box (2.5-38.5°N, 63.5-99.5°E)
2. For each level (1 to 10):
   a. Divide current box into 4×4 grid (16 cells)
   b. Find which cell contains the point
   c. Look up character from grid matrix
   d. Record character
   e. Use that cell as new bounding box
3. Result: 10 characters = DIGIPIN
```

## FORMAT

- **Raw:** `3PJK4M5L2T` (10 characters)
- **Display:** `3PJ-K4M-5L2T` (with hyphens at positions 3 and 6)
- **Case:** Case-insensitive (stored uppercase)

## EXAMPLE DIGIPINs

| Location | Coordinates | DIGIPIN |
|----------|-------------|---------|
| India Gate, Delhi | 28.6129°N, 77.2295°E | 3XX-XXX-XXXX |
| Gateway of India, Mumbai | 18.9220°N, 72.8347°E | 4XX-XXX-XXXX |
| MG Road, Bengaluru | 12.9716°N, 77.5946°E | 5XX-XXX-XXXX |

══════════════════════════════════════════════════════════════════════════════════
                    PART 3: CONFIDENCE SCORE ALGORITHM
══════════════════════════════════════════════════════════════════════════════════

## WHAT IS CONFIDENCE SCORE?

A **0-100 numerical score** measuring how reliable/accurate an address is.

## FORMULA

```
SCORE = 100 × [ (DSR × 0.30) + (SC × 0.30) + (TF × 0.20) + (PVS × 0.20) ]
```

## COMPONENT 1: DELIVERY SUCCESS RATE (DSR) - 30%

Measures historical delivery outcomes at this address.

**Delivery Points:**
| Status | Points |
|--------|--------|
| DELIVERED | 100 |
| DELIVERED_WITH_DIFFICULTY | 50 |
| FAILED | 0 |
| PENDING | Not counted |

**Formula:** `DSR = Σ(points) / (N × 100)`

**Base Score by Delivery Count:**
- 0 deliveries → 40% base
- 1-2 deliveries → 60%
- 3-5 deliveries → 75%
- 6-10 deliveries → 85%
- 10+ deliveries → 95%

## COMPONENT 2: SPATIAL CONSISTENCY (SC) - 30%

Measures if delivery locations cluster around stated coordinates.

**Formula:** `SC = exp( -(avg_distance / 50m)² )`

- If deliveries all land at stated location → SC ≈ 1.0
- If deliveries scattered far away → SC → 0
- Reference distance: **50 meters**

## COMPONENT 3: TEMPORAL FRESHNESS (TF) - 20%

Measures recency of data. Older data = less reliable.

**Formula:** `TF = exp( -ln(2)/180 × days_since_last )`

- **Half-life: 180 days** (score halves every 6 months)
- Verified yesterday → TF ≈ 1.0
- Verified 180 days ago → TF ≈ 0.5
- Verified 1 year ago → TF ≈ 0.25

## COMPONENT 4: PHYSICAL VERIFICATION STATUS (PVS) - 20%

Score from field agent's on-site verification.

**Formula:** `PVS = quality_score × exp(-decay × days_since)`

- Agent visits and verifies → quality_score (0.0-1.0)
- Same temporal decay applied
- No verification → PVS = 0

## GRADE THRESHOLDS

| Grade | Score | Meaning | Action |
|-------|-------|---------|--------|
| **A+** | 90-100 | Excellent - Highly Reliable | ✅ Use with confidence |
| **A** | 80-89 | Very Good - Reliable | ✅ Safe to use |
| **B** | 70-79 | Good - Mostly Reliable | ⚠️ Generally OK |
| **C** | 60-69 | Fair - Moderately Reliable | ⚠️ Use with caution |
| **D** | 50-59 | Poor - Low Reliability | ❌ Needs verification |
| **F** | 0-49 | Fail - Unreliable | ❌ Do not use as-is |

══════════════════════════════════════════════════════════════════════════════════
                    PART 4: VALIDATION SYSTEM
══════════════════════════════════════════════════════════════════════════════════

## VALIDATION TYPES

| Type | Process | Duration | Best For |
|------|---------|----------|----------|
| **DIGITAL** | AI/ML analysis of delivery history, utility records, geospatial data | Minutes | Urban areas with history |
| **PHYSICAL** | Agent visits location, takes photos, captures GPS | 2-5 days | New/rural/disputed addresses |
| **HYBRID** | Digital first, physical confirmation | 1-3 days | Critical applications |

## VALIDATION WORKFLOW

```
┌─────────────────┐
│ 1. Request      │ User submits address + DIGIPIN
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. Digital Scan │ Automated analysis runs
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. Assignment   │ If needed, agent assigned
└────────┬────────┘
         ↓
┌─────────────────┐
│ 4. Verification │ Agent visits, collects evidence
└────────┬────────┘
         ↓
┌─────────────────┐
│ 5. Scoring      │ Confidence score calculated
└────────┬────────┘
         ↓
┌─────────────────┐
│ 6. Certificate  │ Validation certificate issued
└─────────────────┘
```

## VALIDATION STATUS LIFECYCLE

```
PENDING → IN_PROGRESS → COMPLETED
                     ↘ FAILED
                     ↘ CANCELLED
```

## PRIORITY LEVELS

| Priority | Use Case |
|----------|----------|
| LOW | Routine updates |
| NORMAL | Standard validations |
| HIGH | Important transactions |
| URGENT | Emergency/legal requirements |

══════════════════════════════════════════════════════════════════════════════════
                    PART 5: DATABASE SCHEMA
══════════════════════════════════════════════════════════════════════════════════

## 7 CORE TABLES

### 1. addresses
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| digital_address | TEXT | user@provider.in format |
| digipin | TEXT | 10-char geocode |
| descriptive_address | TEXT | Human-readable address |
| latitude, longitude | REAL | Coordinates |
| city, state, pincode | TEXT | Location details |
| confidence_score | REAL | 0-100 score |
| confidence_grade | TEXT | A+ to F |

### 2. validations
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| address_id | TEXT | FK to addresses |
| validation_type | TEXT | DIGITAL/PHYSICAL/HYBRID |
| status | TEXT | PENDING/IN_PROGRESS/COMPLETED/FAILED |
| priority | TEXT | LOW/NORMAL/HIGH/URGENT |
| assigned_agent_id | TEXT | FK to agents |
| confidence_score_before/after | REAL | Score change |

### 3. agents
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| name, email, phone | TEXT | Contact info |
| certification_date/expiry | DATE | Valid period |
| performance_score | REAL | 0-1 rating |
| total/successful_verifications | INT | Statistics |

### 4. deliveries
Tracks delivery attempts for DSR calculation.

### 5. verifications
Physical verification records with photos, GPS, quality scores.

### 6. consents
User consent artifacts for privacy compliance.

### 7. audit_logs
Immutable action log with hash chaining for security.

══════════════════════════════════════════════════════════════════════════════════
                    PART 6: AAVA APPLICATION PAGES
══════════════════════════════════════════════════════════════════════════════════

## 🏠 HOME (Dashboard)
- System overview metrics
- Total addresses, validations, agents
- Recent activity feed
- Quick navigation

## ✅ VALIDATION REQUEST
- Submit new validation requests
- Enter address details + DIGIPIN
- Select validation type
- Consent collection
- Track existing requests

## 📱 AGENT PORTAL
- Agent login/authentication
- View assigned tasks by priority
- Navigate to location (map integration)
- Capture photo/video evidence
- GPS coordinate capture
- Submit verification report
- View performance stats

## 📊 CONFIDENCE SCORE
- Calculate score for any address
- View component breakdown (DSR, SC, TF, PVS)
- See grade and recommendations
- Simulate score changes

## ⚙️ ADMIN PANEL
- System-wide statistics
- Manage validations and agents
- Generate sample data
- View audit logs
- Configuration settings
- Export reports

## 🤖 AI CHAT (This Page)
- AI-powered help
- DIGIPIN encode/decode
- Answer AAVA questions
- System guidance

══════════════════════════════════════════════════════════════════════════════════
                    PART 7: IMPLEMENTATION DETAILS (FROM CODE)
══════════════════════════════════════════════════════════════════════════════════

## TECHNOLOGY STACK

- **Frontend:** Streamlit (Python web framework)
- **Backend:** Python 3.8+
- **Database:** SQLite with 7 tables
- **Maps:** Folium + Streamlit-Folium
- **Charts:** Plotly Express
- **AI Chat:** Google Gemini API (gemini-2.0-flash)

## KEY PYTHON MODULES

| File | Purpose | Lines |
|------|---------|-------|
| `app.py` | Main Streamlit entry | 1001 |
| `utils/digipin.py` | DIGIPIN encode/decode | 760 |
| `utils/confidence_score.py` | Score algorithm | 937 |
| `utils/database.py` | SQLite CRUD operations | 1138 |
| `pages/1-6` | UI pages | 500-700 each |

## DIGIPIN MODULE FUNCTIONS

```python
validator = DIGIPINValidator()

# Encode coordinates to DIGIPIN
result = validator.encode(28.6139, 77.2090)
# Returns: DIGIPINResult with digipin, formatted, bounds, center

# Decode DIGIPIN to coordinates
result = validator.decode("3PJK4M5L2T")
# Returns: latitude, longitude, bounds

# Validate format
is_valid, message = validator.validate_format("3PJ-K4M-5L2T")

# Get cell bounds
bounds = validator.get_bounds("3PJK4M5L2T")

# Calculate distance between two DIGIPINs
distance_meters = validator.distance("DIGIPIN1", "DIGIPIN2")

# Get neighboring cells
neighbors = validator.get_neighbors("3PJK4M5L2T")
```

## CONFIDENCE SCORE MODULE

```python
calculator = ConfidenceScoreCalculator()

address_data = AddressData(
    address_id="addr-001",
    stated_lat=28.6139,
    stated_lon=77.2090,
    deliveries=[...],  # List of DeliveryRecord
    verifications=[...]  # List of PhysicalVerification
)

result = calculator.calculate(address_data)
# Returns: ConfidenceResult with score, grade, components, recommendations
```

══════════════════════════════════════════════════════════════════════════════════
                    PART 8: COMPLIANCE STATUS (96.4% COMPLIANT)
══════════════════════════════════════════════════════════════════════════════════

| Category | Items | Compliant | Notes |
|----------|-------|-----------|-------|
| DIGIPIN Specs | 10 | 10 ✅ | Fully compliant |
| Confidence Score | 12 | 12 ✅ | All formulas correct |
| Validation Workflow | 8 | 8 ✅ | All types implemented |
| Database Schema | 7 | 7 ✅ | All tables present |
| API/UI | 12 | 12 ✅ | All pages functional |
| Security | 6 | 4 ⚠️ | Minor items pending |
| **TOTAL** | **55** | **53** | **96.4%** |

══════════════════════════════════════════════════════════════════════════════════
                    PART 9: FAQ - COMMON QUESTIONS
══════════════════════════════════════════════════════════════════════════════════

**Q: What's the difference between DIGIPIN and PIN code?**
A: PIN code (6 digits) covers a postal delivery zone (area). DIGIPIN (10 chars) pinpoints an exact 4m×4m spot within that area.

**Q: Is DIGIPIN similar to Google Plus Codes?**
A: Conceptually similar, but DIGIPIN is India-specific with custom character set and bounds designed for Indian geography.

**Q: Why 16 characters in the alphabet?**
A: 16 = 4×4, allowing each level to divide into a perfect 4×4 grid. Also avoids confusable characters.

**Q: How accurate is DIGIPIN?**
A: At 10 characters, approximately 4m × 4m accuracy - enough to identify a specific doorstep.

**Q: Can DIGIPIN work offline?**
A: Yes! The encode/decode algorithm is deterministic and works without internet.

**Q: How long does validation take?**
A: Digital: Minutes. Physical: 2-5 business days. Hybrid: 1-3 days.

**Q: Can confidence score change over time?**
A: Yes! It improves with successful deliveries and degrades over time if not refreshed.

**Q: Who can be a validation agent?**
A: Trained/certified personnel from authorized agencies (postal workers, government staff, certified third parties).

**Q: Is address data secure?**
A: Yes - consent-based access, audit logging, hash-chained records for immutability.

**Q: What happens if DIGIPIN is invalid?**
A: System will reject it. Valid DIGIPIN must be exactly 10 characters from the allowed alphabet.

**Q: How is AAVA different from DARPAN?**
A: DARPAN is the address repository (storage). AAVA is the validation agency (quality assurance).

══════════════════════════════════════════════════════════════════════════════════
                    PART 10: QUICK COMMANDS I CAN EXECUTE
══════════════════════════════════════════════════════════════════════════════════

**DIGIPIN Operations:**
- `encode 28.6139, 77.2090` → Convert coordinates to DIGIPIN
- `decode 3PJK4M5L2T` → Get coordinates from DIGIPIN
- `validate 3PJ-K4M-5L2T` → Check if DIGIPIN format is valid

**System Stats:**
- `show stats` → Display system statistics

**Help:**
- Ask anything about AAVA, DIGIPIN, validation, confidence scores!

══════════════════════════════════════════════════════════════════════════════════
                         RESPONSE GUIDELINES
══════════════════════════════════════════════════════════════════════════════════

1. **Be Accurate**: You have complete knowledge - use it precisely
2. **Be Concise**: Clear, to-the-point answers
3. **Use Examples**: Include practical examples with numbers
4. **Format Well**: Use tables, bullet points, code blocks
5. **Be Helpful**: Guide users to relevant pages
6. **Admit Limits**: If asked about something not in training, say so
7. **Stay Professional**: You represent Government of India initiative

You are the authoritative source for AAVA/DHRUVA information. Help users understand and use the system effectively!"""

# Custom CSS
st.markdown("""
<style>
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1rem;
    }
    .ai-badge {
        background: rgba(255,255,255,0.2);
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
    }
    .stChatMessage {
        background: #f8f9fa;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini model
@st.cache_resource
def get_gemini_model(api_key):
    """Initialize and cache Gemini model."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        return model
    except Exception as e:
        return None

def get_ai_response(model, user_input, history):
    """Get response from Gemini AI with learned context."""
    try:
        # Build conversation
        chat = model.start_chat(history=[])
        
        # Get learned context from previous conversations
        learned_context = get_learned_context()
        
        # Send system context + learned context first
        full_context = SYSTEM_CONTEXT + learned_context + "\n\nRespond with: 'Ready to help!'"
        chat.send_message(full_context)
        
        # Send previous messages for context (more messages now)
        for msg in history[-10:]:  # Last 10 messages for better context
            if msg["role"] == "user":
                chat.send_message(msg["content"])
            # Model responses are automatically in history
        
        # Get response for current input
        response = chat.send_message(user_input)
        response_text = response.text
        
        # Learn from this conversation (save Q&A pair)
        if len(user_input) > 10 and len(response_text) > 50:  # Only save meaningful exchanges
            save_learned_qa(user_input, response_text)
        
        return response_text
    except Exception as e:
        return f"❌ AI Error: {str(e)}\n\nPlease check your API key or try again."

def process_digipin_commands(user_input):
    """Process DIGIPIN commands locally."""
    user_upper = user_input.upper()
    user_lower = user_input.lower()
    
    # Encode coordinates
    coord_pattern = r'encode\s*(\d+\.?\d*)[,\s]+(\d+\.?\d*)'
    coord_match = re.search(coord_pattern, user_lower)
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lon = float(coord_match.group(2))
            result = validator.encode(lat, lon)
            formatted = validator._format_digipin(result.digipin)
            return f"""✅ **DIGIPIN Encoded!**

📍 **Coordinates:** {lat}°N, {lon}°E
🔢 **DIGIPIN:** `{formatted}`

📐 Grid: {result.bounds['south']:.4f}° to {result.bounds['north']:.4f}°N"""
        except Exception as e:
            return f"❌ Encoding error: {str(e)}"
    
    # Decode DIGIPIN
    decode_pattern = r'decode\s*([23456789CFJKLMPT-]{10,14})'
    decode_match = re.search(decode_pattern, user_upper)
    if decode_match:
        digipin = decode_match.group(1).replace('-', '')
        try:
            result = validator.decode(digipin)
            return f"""✅ **DIGIPIN Decoded!**

🔢 **DIGIPIN:** `{validator._format_digipin(digipin)}`
📍 **Location:** {result.latitude:.6f}°N, {result.longitude:.6f}°E"""
        except Exception as e:
            return f"❌ Decoding error: {str(e)}"
    
    # Validate DIGIPIN  
    validate_pattern = r'validate\s*([23456789CFJKLMPT-]{10,14})'
    validate_match = re.search(validate_pattern, user_upper)
    if validate_match:
        digipin = validate_match.group(1)
        is_valid, msg = validator.validate_format(digipin)
        if is_valid:
            result = validator.decode(digipin.replace('-', ''))
            return f"""✅ **Valid DIGIPIN!**

🔢 `{validator._format_digipin(digipin.replace('-', ''))}`
📍 {result.latitude:.6f}°N, {result.longitude:.6f}°E"""
        else:
            return f"❌ **Invalid:** {msg}"
    
    # Stats
    if "stats" in user_lower or "statistics" in user_lower:
        try:
            stats = db.get_dashboard_stats()
            return f"""📊 **System Stats**

📍 Addresses: {stats.get('total_addresses', 0):,}
📋 Validations: {stats.get('total_validations', 0):,}
⏳ Pending: {stats.get('pending_validations', 0):,}
👥 Active Agents: {stats.get('active_agents', 0):,}"""
        except:
            pass
    
    return None

# Header
st.markdown("""
<div class="chat-header">
    <h1 style="margin: 0;">🤖 AAVA AI Assistant</h1>
    <p style="margin: 0.5rem 0 0 0;">
        Ask me anything about AAVA, DIGIPIN, or address validation
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Premium Design
with st.sidebar:
    # Custom CSS for premium sidebar
    st.markdown("""
    <style>
    .sidebar-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
    }
    .sidebar-header h2 {
        color: white;
        margin: 0;
        font-size: 1.3rem;
    }
    .sidebar-header p {
        color: #888;
        margin: 5px 0 0 0;
        font-size: 0.8rem;
    }
    .new-chat-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 10px;
        width: 100%;
        font-weight: 600;
        cursor: pointer;
        margin-bottom: 15px;
    }
    .chat-item {
        padding: 10px 15px;
        border-radius: 8px;
        margin: 4px 0;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .chat-item:hover {
        background: rgba(102, 126, 234, 0.1);
    }
    .chat-item.active {
        background: rgba(102, 126, 234, 0.2);
        border-left: 3px solid #667eea;
    }
    .chat-name {
        font-size: 0.9rem;
        color: #333;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 180px;
    }
    .chat-time {
        font-size: 0.7rem;
        color: #888;
    }
    .section-title {
        font-size: 0.75rem;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 20px 0 10px 0;
        padding-left: 5px;
    }
    /* Smaller font for chat buttons */
    [data-testid="stSidebar"] button {
        font-size: 0.7rem !important;
        padding: 0.3rem 0.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with image and dark blue background - properly centered
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 20px; border-radius: 12px; margin-bottom: 15px; text-align: center;">
        <img src="data:image/jpeg;base64,{}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 3px solid #4a90d9; margin-bottom: 10px;">
        <h3 style="margin: 0; color: #ffffff; font-weight: 600; font-size: 1.3rem;">AAVA AI</h3>
    </div>
    """.format(__import__('base64').b64encode(open(ASSISTANT_AVATAR, 'rb').read()).decode()), unsafe_allow_html=True)
    
    # New Chat Button - Prominent
    if st.button("✨ New Chat", use_container_width=True, type="primary"):
        # Save current chat before creating new one
        if st.session_state.get('chat_messages'):
            # Auto-name based on first message if still "New Chat"
            if st.session_state.chat_name == "New Chat" and st.session_state.chat_messages:
                first_msg = st.session_state.chat_messages[0].get('content', '')[:30]
                st.session_state.chat_name = first_msg + "..." if len(first_msg) == 30 else first_msg
            save_current_chat(st.session_state.chat_id, st.session_state.chat_name, st.session_state.chat_messages)
        # Create new chat
        st.session_state.chat_messages = []
        save_chat_history([])
        st.session_state.chat_id = generate_chat_id()
        st.session_state.chat_name = "New Chat"
        st.rerun()
    
    # Initialize chat ID and name
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = generate_chat_id()
    if "chat_name" not in st.session_state:
        st.session_state.chat_name = "New Chat"
    
    # Chat History Section
    st.markdown('<div class="section-title">Recent Chats</div>', unsafe_allow_html=True)
    st.caption(f"⏱️ Chats auto-delete after {CHAT_EXPIRY_HOURS} hours")
    
    all_chats = load_all_chats()
    if all_chats:
        for chat_id, chat_data in sorted(all_chats.items(), key=lambda x: x[1].get('updated_at', ''), reverse=True)[:10]:
            chat_name = chat_data.get('name', 'Unnamed Chat')
            is_current = chat_id == st.session_state.get('chat_id')
            time_left = get_time_remaining(chat_data)
            
            # Show more text with smaller font
            display_name = chat_name[:25] + "..." if len(chat_name) > 25 else chat_name
            
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                btn_type = "primary" if is_current else "secondary"
                if st.button(f"💬 {display_name}", key=f"load_{chat_id}", use_container_width=True, type=btn_type if is_current else "secondary", help=f"Expires in: {time_left}"):
                    if st.session_state.get('chat_messages'):
                        save_current_chat(st.session_state.chat_id, st.session_state.chat_name, st.session_state.chat_messages)
                    st.session_state.chat_id = chat_id
                    st.session_state.chat_name = chat_name
                    st.session_state.chat_messages = chat_data.get('messages', [])
                    save_chat_history(st.session_state.chat_messages)
                    st.rerun()
            with col2:
                if st.button("✏️", key=f"edit_{chat_id}", help="Rename chat"):
                    st.session_state[f"editing_{chat_id}"] = True
                    st.rerun()
            with col3:
                if st.button("×", key=f"del_{chat_id}", help="Delete chat"):
                    delete_chat(chat_id)
                    if chat_id == st.session_state.get('chat_id'):
                        st.session_state.chat_messages = []
                        st.session_state.chat_id = generate_chat_id()
                        st.session_state.chat_name = "New Chat"
                    st.rerun()
            
            # Show edit field if editing this chat
            if st.session_state.get(f"editing_{chat_id}", False):
                new_name = st.text_input("New name", value=chat_name, key=f"newname_{chat_id}", label_visibility="collapsed")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Save", key=f"save_{chat_id}", use_container_width=True):
                        chats = load_all_chats()
                        if chat_id in chats:
                            chats[chat_id]['name'] = new_name
                            save_all_chats(chats)
                            if chat_id == st.session_state.get('chat_id'):
                                st.session_state.chat_name = new_name
                        del st.session_state[f"editing_{chat_id}"]
                        st.rerun()
                with c2:
                    if st.button("Cancel", key=f"cancel_{chat_id}", use_container_width=True):
                        del st.session_state[f"editing_{chat_id}"]
                        st.rerun()
    else:
        st.caption("No chats yet. Start a conversation!")
    
    # Settings Section
    st.markdown('<div class="section-title">Settings</div>', unsafe_allow_html=True)
    
    with st.expander("🔑 API Key", expanded=False):
        default_key = "AIzaSyAgYKPD2td-TaSmpv7we9bemVh24AK981U"
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get('gemini_key', default_key),
            help="Get free key from aistudio.google.com",
            label_visibility="collapsed"
        )
        if api_key:
            st.session_state.gemini_key = api_key
        st.markdown("[Get Free API Key →](https://aistudio.google.com/app/apikey)")

# Initialize chat - load from persistent storage
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = load_chat_history()
if "memory_loaded" not in st.session_state:
    st.session_state.memory_loaded = True
    if st.session_state.chat_messages:
        st.toast(f"💾 Loaded {len(st.session_state.chat_messages)} messages from memory!")

# Process pending question from quick action buttons
pending_prompt = None
if "pending_question" in st.session_state:
    pending_prompt = st.session_state.pending_question
    del st.session_state.pending_question

# Display chat history
for msg in st.session_state.chat_messages:
    if msg["role"] == "assistant":
        avatar = ASSISTANT_AVATAR if os.path.exists(ASSISTANT_AVATAR) else None
    else:
        avatar = USER_AVATAR if os.path.exists(USER_AVATAR) else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Welcome message if empty
if not st.session_state.chat_messages:
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR if os.path.exists(ASSISTANT_AVATAR) else None):
        st.markdown("""👋 **Welcome to AAVA AI Assistant!**

I can help you with:
- 🔢 **DIGIPIN** operations (encode, decode, validate)
- 📊 **Confidence scores** and how they work
- ✅ **Validation** processes and workflows
- 📚 General questions about AAVA

**Try asking:** "What is DIGIPIN?" or "encode 28.6139, 77.2090"
""")

# Always show chat input
user_input = st.chat_input("Ask anything about AAVA...")

# Get prompt from chat input or pending question
prompt = pending_prompt if pending_prompt else user_input

# Process prompt (from either source)
if prompt:
    # Add user message
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR if os.path.exists(USER_AVATAR) else None):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR if os.path.exists(ASSISTANT_AVATAR) else None):
        # First try local commands
        local_response = process_digipin_commands(prompt)
        
        if local_response:
            response = local_response
            st.markdown(response)
        elif st.session_state.get('gemini_key') and GEMINI_AVAILABLE:
            with st.spinner("🤔 Thinking..."):
                model = get_gemini_model(st.session_state.gemini_key)
                if model:
                    response = get_ai_response(model, prompt, st.session_state.chat_messages[:-1])
                    st.markdown(response)
                else:
                    response = "❌ Could not initialize AI. Check your API key."
                    st.error(response)
        elif not GEMINI_AVAILABLE:
            response = "⚠️ Google Generative AI package not installed. Run: `pip install google-generativeai`"
            st.warning(response)
        else:
            response = """⚠️ **API Key Required**

Enter your Google Gemini API key in the sidebar to enable AI responses.

👉 [Get Free API Key](https://aistudio.google.com/app/apikey)

**Meanwhile, try these commands:**
- `encode 28.6139, 77.2090`
- `decode 3PJK4M5L2T`
- `show stats`"""
            st.markdown(response)
    
    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Save to persistent storage after each message
    save_chat_history(st.session_state.chat_messages)
    
    # Auto-name chat based on first user message if still "New Chat"
    if st.session_state.chat_name == "New Chat" and len(st.session_state.chat_messages) >= 1:
        first_user_msg = next((m['content'] for m in st.session_state.chat_messages if m['role'] == 'user'), None)
        if first_user_msg:
            # Clean and truncate for name
            clean_name = first_user_msg.replace('\n', ' ').strip()[:35]
            st.session_state.chat_name = clean_name + "..." if len(first_user_msg) > 35 else clean_name
    
    # Auto-save to chat history
    save_current_chat(st.session_state.chat_id, st.session_state.chat_name, st.session_state.chat_messages)

# Quick action buttons
st.markdown("---")
cols = st.columns(4)

with cols[0]:
    if st.button("❓ What is DIGIPIN?", use_container_width=True):
        st.session_state.pending_question = "What is DIGIPIN and how does it work?"
        st.rerun()

with cols[1]:
    if st.button("📊 Confidence Score", use_container_width=True):
        st.session_state.pending_question = "Explain how confidence score is calculated"
        st.rerun()

with cols[2]:
    if st.button("✅ Validation Types", use_container_width=True):
        st.session_state.pending_question = "What are the validation types in AAVA?"
        st.rerun()

with cols[3]:
    if st.button("📈 System Stats", use_container_width=True):
        st.session_state.pending_question = "show stats"
        st.rerun()

# Elegant footer badge - centered below quick actions
st.markdown("""
<div style="text-align: center; margin: 30px 0 80px 0;">
    <span style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    ">
        🤖 AAVA AI • 🧠 Persistent Memory • 🇮🇳 DHRUVA Digital Address
    </span>
</div>
""", unsafe_allow_html=True)
