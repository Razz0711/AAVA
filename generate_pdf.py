# generate_pdf.py - Generate PDF documentation for AAVA

from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, 'AAVA - Authorised Address Validation Agency', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')
    
    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(2)
    
    def section_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT", align='L')
        self.ln(1)
    
    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(2)
    
    def bullet_point(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.cell(10, 6, "  *")
        self.multi_cell(0, 6, text)
    
    def table_row(self, col1, col2, col3="", header=False):
        if header:
            self.set_font('Helvetica', 'B', 9)
            self.set_fill_color(102, 126, 234)
            self.set_text_color(255, 255, 255)
        else:
            self.set_font('Helvetica', '', 9)
            self.set_fill_color(245, 245, 245)
            self.set_text_color(0, 0, 0)
        
        if col3:
            self.cell(50, 7, col1, 1, 0, 'L', True)
            self.cell(70, 7, col2, 1, 0, 'L', True)
            self.cell(60, 7, col3, 1, 1, 'L', True)
        else:
            self.cell(60, 7, col1, 1, 0, 'L', True)
            self.cell(120, 7, col2, 1, 1, 'L', True)

# Create PDF
pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)

# Title Page
pdf.add_page()
pdf.set_font('Helvetica', 'B', 28)
pdf.set_text_color(102, 126, 234)
pdf.ln(60)
pdf.cell(0, 15, 'AAVA', 0, 1, 'C')
pdf.set_font('Helvetica', '', 16)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 10, 'Authorised Address Validation Agency', 0, 1, 'C')
pdf.ln(10)
pdf.set_font('Helvetica', 'I', 12)
pdf.set_text_color(128, 128, 128)
pdf.cell(0, 8, 'Part of DHRUVA Digital Address Ecosystem', 0, 1, 'C')
pdf.cell(0, 8, 'Government of India Initiative', 0, 1, 'C')
pdf.cell(0, 8, 'Department of Posts', 0, 1, 'C')
pdf.ln(20)
pdf.set_font('Helvetica', 'B', 12)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 8, 'Smart India Hackathon 2024', 0, 1, 'C')
pdf.ln(30)
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(128, 128, 128)
pdf.cell(0, 8, 'Documentation Version 1.0', 0, 1, 'C')
pdf.cell(0, 8, 'November 30, 2025', 0, 1, 'C')

# Table of Contents
pdf.add_page()
pdf.chapter_title('Table of Contents')
pdf.ln(5)
toc = [
    ('1. Overview', 3),
    ('2. Problem Statement', 3),
    ('3. DHRUVA Ecosystem', 4),
    ('4. Technology Stack', 5),
    ('5. Project Structure', 6),
    ('6. Application Pages', 7),
    ('7. DIGIPIN Specifications', 9),
    ('8. Confidence Score Algorithm', 11),
    ('9. Database Schema', 13),
    ('10. Installation & Setup', 14),
    ('11. Deployment', 15),
    ('12. AI Chat Features', 16),
    ('13. Security', 17),
    ('14. Compliance Status', 17),
]
for item, page in toc:
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(150, 8, item, 0, 0)
    pdf.cell(30, 8, str(page), 0, 1, 'R')

# 1. Overview
pdf.add_page()
pdf.chapter_title('1. Overview')
pdf.body_text('AAVA (Authorised Address Validation Agency) is a comprehensive web application built for the Smart India Hackathon 2024. It is part of India\'s DHRUVA Digital Address Ecosystem - a Government of India initiative by the Department of Posts.')
pdf.body_text('The application provides a unified digital addressing system with address validation, DIGIPIN geocoding, confidence scoring, and AI-powered assistance.')

# 2. Problem Statement
pdf.chapter_title('2. Problem Statement')
pdf.body_text('India faces critical addressing challenges:')
pdf.bullet_point('60-80 million households lack formal addresses')
pdf.bullet_point('Rural areas have ambiguous landmark-based addresses')
pdf.bullet_point('Urban slums/informal settlements excluded from formal systems')
pdf.bullet_point('No standardized digital addressing infrastructure')
pdf.bullet_point('Delivery failures cost the economy billions annually')
pdf.ln(5)
pdf.body_text('AAVA addresses these challenges by providing a robust validation framework for the DHRUVA ecosystem.')

# 3. DHRUVA Ecosystem
pdf.add_page()
pdf.chapter_title('3. DHRUVA Ecosystem')
pdf.body_text('DHRUVA = Digital Hyperlocal Unique Reliable Verified Address')
pdf.body_text('A unified national digital addressing system with 4 core pillars:')
pdf.ln(3)
pdf.table_row('Component', 'Full Form', 'Role', header=True)
pdf.table_row('DIGIPIN', 'Digital Postal Index Number', 'Geocode system')
pdf.table_row('DARPAN', 'Digital Address Repository...', 'Central database')
pdf.table_row('DIVYA', 'Digital Interface for Verified...', 'Citizen portal')
pdf.table_row('AAVA', 'Authorised Address Validation...', 'Quality assurance')

pdf.ln(10)
pdf.section_title('Ecosystem Participants')
pdf.table_row('Entity', 'Role', header=True)
pdf.table_row('CM (Central Mapper)', 'Maintains DIGIPIN grid system')
pdf.table_row('AIP (Address Information Provider)', 'Creates/updates addresses')
pdf.table_row('AIA (Address Information Agent)', 'Field agents who verify')
pdf.table_row('AIU (Address Information User)', 'Consumers of address data')
pdf.table_row('AAVA', 'Validates address accuracy')

# 4. Technology Stack
pdf.add_page()
pdf.chapter_title('4. Technology Stack')
pdf.ln(3)
pdf.table_row('Layer', 'Technology', header=True)
pdf.table_row('Frontend', 'Streamlit (Python)')
pdf.table_row('Backend', 'Python 3.8+')
pdf.table_row('Database', 'SQLite')
pdf.table_row('Maps', 'Folium + Streamlit-Folium')
pdf.table_row('Charts', 'Plotly Express')
pdf.table_row('AI Chat', 'Google Gemini API')

pdf.ln(10)
pdf.section_title('Key Dependencies')
pdf.bullet_point('streamlit - Web application framework')
pdf.bullet_point('pandas, numpy - Data processing')
pdf.bullet_point('plotly - Interactive charts')
pdf.bullet_point('folium - Interactive maps')
pdf.bullet_point('google-generativeai - AI chat capabilities')
pdf.bullet_point('python-dotenv - Environment variable management')
pdf.bullet_point('Pillow - Image processing')

# 5. Project Structure
pdf.add_page()
pdf.chapter_title('5. Project Structure')
pdf.set_font('Courier', '', 9)
structure = """
Development of AAVA/
|-- app.py                    # Main application
|-- requirements.txt          # Dependencies
|-- .env                      # Environment variables
|-- .gitignore               # Git ignore rules
|-- README.md                # Project readme
|-- DOCUMENTATION.md         # Documentation
|
|-- pages/                   # Streamlit pages
|   |-- 1_Validation_Request.py
|   |-- 2_Agent_Portal.py
|   |-- 3_Confidence_Score.py
|   |-- 4_Admin_Panel.py
|   |-- 6_AI_Chat.py
|
|-- utils/                   # Utility modules
|   |-- database.py          # SQLite operations
|   |-- digipin.py           # DIGIPIN encode/decode
|   |-- confidence_score.py  # Score algorithm
|
|-- assets/                  # Static assets
|-- data/                    # Data storage
|-- .streamlit/              # Streamlit config
"""
pdf.multi_cell(0, 5, structure)

# 6. Application Pages
pdf.add_page()
pdf.chapter_title('6. Application Pages')

pdf.section_title('Home (Dashboard)')
pdf.body_text('System overview with metrics for total addresses, validations, agents. Displays recent activity feed and provides quick navigation to all features.')

pdf.section_title('Validation Request')
pdf.body_text('Submit new address validation requests. Enter address details with DIGIPIN, select validation type (Digital/Physical/Hybrid), collect consent, and track existing requests.')

pdf.section_title('Agent Portal')
pdf.body_text('Agent authentication and task management. View assigned tasks by priority, navigate to locations via map integration, capture photo/video evidence with GPS coordinates, submit verification reports, and view performance statistics.')

pdf.add_page()
pdf.section_title('Confidence Score')
pdf.body_text('Calculate and analyze confidence scores for any address. View component breakdown (DSR, SC, TF, PVS), see grade (A+ to F) with recommendations, and simulate score changes.')

pdf.section_title('Admin Panel')
pdf.body_text('System-wide administration. View statistics, manage validations and agents, generate sample data, view audit logs, configure settings, and export reports.')

pdf.section_title('AI Chat')
pdf.body_text('General-purpose AI assistant powered by Google Gemini. Answers any topic including academics, coding, and general knowledge. Has special expertise in AAVA/DIGIPIN. Features include DIGIPIN encode/decode commands, persistent chat memory with 48-hour retention, and multiple chat sessions with history.')

# 7. DIGIPIN Specifications
pdf.add_page()
pdf.chapter_title('7. DIGIPIN Technical Specifications')

pdf.section_title('What is DIGIPIN?')
pdf.body_text('DIGIPIN (Digital Postal Index Number) is a 10-character alphanumeric geocode that pinpoints any location in India to approximately 4m x 4m accuracy. Think of it as GPS coordinates compressed into a human-readable code.')

pdf.section_title('Character Set (16 characters)')
pdf.set_font('Courier', 'B', 12)
pdf.cell(0, 8, '2 3 4 5 6 7 8 9 C F J K L M P T', 0, 1, 'C')
pdf.set_font('Helvetica', '', 10)
pdf.ln(3)
pdf.body_text('These 16 characters avoid confusable pairs like 0/O, 1/I/L, B/8, S/5.')

pdf.section_title('Geographic Bounds (India)')
pdf.table_row('Parameter', 'Value', header=True)
pdf.table_row('MIN_LAT', '2.5 N (Southern tip)')
pdf.table_row('MAX_LAT', '38.5 N (Northern tip)')
pdf.table_row('MIN_LON', '63.5 E (Western tip)')
pdf.table_row('MAX_LON', '99.5 E (Eastern tip)')

pdf.add_page()
pdf.section_title('Grid Label Matrix (4x4)')
pdf.set_font('Courier', '', 10)
matrix = """
        Col 0   Col 1   Col 2   Col 3
       +-------+-------+-------+-------+
Row 0  |   F   |   C   |   9   |   8   |
       +-------+-------+-------+-------+
Row 1  |   J   |   3   |   2   |   7   |
       +-------+-------+-------+-------+
Row 2  |   K   |   4   |   5   |   6   |
       +-------+-------+-------+-------+
Row 3  |   L   |   M   |   P   |   T   |
       +-------+-------+-------+-------+
"""
pdf.multi_cell(0, 5, matrix)

pdf.ln(5)
pdf.section_title('Resolution by Level')
pdf.set_font('Helvetica', '', 10)
pdf.table_row('Level', 'Approximate Size', header=True)
pdf.table_row('Level 1', '~1000 km (Country zone)')
pdf.table_row('Level 5', '~4 km (Locality)')
pdf.table_row('Level 8', '~60 m (Building cluster)')
pdf.table_row('Level 10', '~4 m (Exact spot)')

pdf.ln(5)
pdf.section_title('Format')
pdf.bullet_point('Raw: 3PJK4M5L2T (10 characters)')
pdf.bullet_point('Display: 3PJ-K4M-5L2T (with hyphens)')
pdf.bullet_point('Case: Case-insensitive (stored uppercase)')

# 8. Confidence Score Algorithm
pdf.add_page()
pdf.chapter_title('8. Confidence Score Algorithm')

pdf.section_title('Formula')
pdf.set_font('Courier', 'B', 10)
pdf.cell(0, 8, 'SCORE = 100 x [(DSR x 0.30) + (SC x 0.30) + (TF x 0.20) + (PVS x 0.20)]', 0, 1, 'C')
pdf.set_font('Helvetica', '', 10)
pdf.ln(5)

pdf.section_title('Component 1: Delivery Success Rate (DSR) - 30%')
pdf.body_text('Measures historical delivery outcomes at this address.')
pdf.table_row('Status', 'Points', header=True)
pdf.table_row('DELIVERED', '100')
pdf.table_row('DELIVERED_WITH_DIFFICULTY', '50')
pdf.table_row('FAILED', '0')

pdf.ln(5)
pdf.section_title('Component 2: Spatial Consistency (SC) - 30%')
pdf.body_text('Measures if delivery locations cluster around stated coordinates.')
pdf.set_font('Courier', '', 10)
pdf.cell(0, 6, 'SC = exp(-(avg_distance / 50m)^2)', 0, 1)
pdf.set_font('Helvetica', '', 10)

pdf.ln(5)
pdf.section_title('Component 3: Temporal Freshness (TF) - 20%')
pdf.body_text('Measures recency of data. Half-life: 180 days.')
pdf.set_font('Courier', '', 10)
pdf.cell(0, 6, 'TF = exp(-ln(2)/180 x days_since_last)', 0, 1)
pdf.set_font('Helvetica', '', 10)

pdf.ln(5)
pdf.section_title('Component 4: Physical Verification Status (PVS) - 20%')
pdf.body_text('Score from field agent\'s on-site verification.')

pdf.add_page()
pdf.section_title('Grade Thresholds')
pdf.table_row('Grade', 'Score Range', 'Meaning', header=True)
pdf.table_row('A+', '90-100', 'Excellent - Highly Reliable')
pdf.table_row('A', '80-89', 'Very Good - Reliable')
pdf.table_row('B', '70-79', 'Good - Mostly Reliable')
pdf.table_row('C', '60-69', 'Fair - Moderately Reliable')
pdf.table_row('D', '50-59', 'Poor - Low Reliability')
pdf.table_row('F', '0-49', 'Fail - Unreliable')

# 9. Database Schema
pdf.add_page()
pdf.chapter_title('9. Database Schema')
pdf.body_text('The application uses SQLite with 7 core tables:')
pdf.ln(3)

tables = [
    ('addresses', 'Address records with DIGIPIN, coordinates, confidence scores'),
    ('validations', 'Validation requests with status tracking'),
    ('agents', 'Field agent information and performance metrics'),
    ('deliveries', 'Delivery attempt records for DSR calculation'),
    ('verifications', 'Physical verification records with evidence'),
    ('consents', 'User consent artifacts for privacy compliance'),
    ('audit_logs', 'Immutable action log with hash chaining'),
]

pdf.table_row('Table', 'Description', header=True)
for table, desc in tables:
    pdf.table_row(table, desc)

# 10. Installation & Setup
pdf.add_page()
pdf.chapter_title('10. Installation & Setup')

pdf.section_title('Prerequisites')
pdf.bullet_point('Python 3.8 or higher')
pdf.bullet_point('pip package manager')
pdf.bullet_point('Git (for cloning repository)')

pdf.ln(5)
pdf.section_title('Installation Steps')
pdf.set_font('Courier', '', 9)
steps = """
1. Clone the repository:
   git clone https://github.com/Razz0711/AAVA.git
   cd AAVA

2. Create virtual environment:
   python -m venv venv

3. Activate virtual environment:
   Windows: venv\\Scripts\\activate
   Linux/Mac: source venv/bin/activate

4. Install dependencies:
   pip install -r requirements.txt

5. Create .env file with API key:
   GEMINI_API_KEY=your_api_key_here

6. Run the application:
   streamlit run app.py

7. Open browser:
   http://localhost:8501
"""
pdf.multi_cell(0, 5, steps)

# 11. Deployment
pdf.add_page()
pdf.chapter_title('11. Deployment')

pdf.section_title('Streamlit Cloud Deployment')
pdf.body_text('1. Push code to GitHub repository')
pdf.body_text('2. Go to share.streamlit.io')
pdf.body_text('3. Connect your GitHub repository')
pdf.body_text('4. Add secrets in Streamlit Cloud dashboard:')
pdf.set_font('Courier', '', 10)
pdf.cell(0, 6, '   GEMINI_API_KEY = "your_api_key"', 0, 1)
pdf.set_font('Helvetica', '', 10)
pdf.body_text('5. Deploy the application')

pdf.ln(5)
pdf.section_title('Live URL')
pdf.set_font('Courier', '', 11)
pdf.cell(0, 8, 'https://aava.streamlit.app', 0, 1)

# 12. AI Chat Features
pdf.add_page()
pdf.chapter_title('12. AI Chat Features')

pdf.section_title('Capabilities')
pdf.bullet_point('General Purpose AI: Answers any topic')
pdf.bullet_point('Academic Help: Syllabus questions, homework, exam prep')
pdf.bullet_point('AAVA Expertise: DIGIPIN operations, confidence scores')
pdf.bullet_point('Coding Help: Any programming language')

pdf.ln(5)
pdf.section_title('Special Commands')
pdf.set_font('Courier', '', 10)
commands = """
encode 28.6139, 77.2090  -> Convert coordinates to DIGIPIN
decode 3PJK4M5L2T        -> Get coordinates from DIGIPIN
validate 3PJ-K4M-5L2T    -> Check DIGIPIN validity
show stats               -> Display system statistics
"""
pdf.multi_cell(0, 5, commands)

pdf.ln(5)
pdf.section_title('Chat Management')
pdf.set_font('Helvetica', '', 10)
pdf.bullet_point('Multiple chat sessions supported')
pdf.bullet_point('48-hour auto-delete for privacy')
pdf.bullet_point('Edit/rename chat titles')
pdf.bullet_point('Persistent memory across sessions')

# 13. Security
pdf.add_page()
pdf.chapter_title('13. Security')

pdf.section_title('API Key Protection')
pdf.bullet_point('API keys stored in .env file (not committed to Git)')
pdf.bullet_point('Backup in .streamlit/secrets.toml')
pdf.bullet_point('Both files excluded via .gitignore')

pdf.ln(5)
pdf.section_title('Data Security')
pdf.bullet_point('Consent-based data access')
pdf.bullet_point('Audit logging with hash chains')
pdf.bullet_point('Immutable record keeping')

# 14. Compliance Status
pdf.ln(10)
pdf.chapter_title('14. Compliance Status')
pdf.body_text('Overall Compliance: 96.4%')
pdf.ln(3)

pdf.table_row('Category', 'Status', header=True)
pdf.table_row('DIGIPIN Specs', '10/10 Compliant')
pdf.table_row('Confidence Score', '12/12 Compliant')
pdf.table_row('Validation Workflow', '8/8 Compliant')
pdf.table_row('Database Schema', '7/7 Compliant')
pdf.table_row('API/UI', '12/12 Compliant')
pdf.table_row('Security', '4/6 (Minor items pending)')

# Final page
pdf.add_page()
pdf.ln(60)
pdf.set_font('Helvetica', 'B', 16)
pdf.set_text_color(102, 126, 234)
pdf.cell(0, 10, 'Thank You', 0, 1, 'C')
pdf.ln(10)
pdf.set_font('Helvetica', '', 12)
pdf.set_text_color(0, 0, 0)
pdf.cell(0, 8, 'AAVA - Authorised Address Validation Agency', 0, 1, 'C')
pdf.cell(0, 8, 'Smart India Hackathon 2024', 0, 1, 'C')
pdf.ln(20)
pdf.set_font('Helvetica', '', 10)
pdf.set_text_color(128, 128, 128)
pdf.cell(0, 8, 'GitHub: https://github.com/Razz0711/AAVA', 0, 1, 'C')
pdf.cell(0, 8, 'Documentation generated on November 30, 2025', 0, 1, 'C')

# Save PDF
pdf.output('AAVA_Documentation.pdf')
print("PDF generated successfully: AAVA_Documentation.pdf")
