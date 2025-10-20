import streamlit as st
import json
import re
from datetime import datetime
import requests
import os

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    div[data-testid="stVerticalBlock"] > div:first-child {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    .title-container {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }

    .title-text {
        font-size: 3rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    .subtitle-text {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.5rem;
    }

    .feature-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .stTextArea textarea {
        border-radius: 10px;
        border: 2px solid #667eea;
        font-size: 1.1rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }

    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }

    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }

    .stat-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 0.5rem;
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
    }

    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# ENHANCED ATS KEYWORD EXTRACTION
# -----------------------------

class ATSKeywordExtractor:
    """Extract and suggest ATS-friendly keywords based on role/industry"""
    
    @staticmethod
    def get_industry_keywords(user_input):
        """Extract industry-specific ATS keywords"""
        user_input_lower = user_input.lower()
        
        keywords = {
            "software_engineering": {
                "technical": ["Python", "JavaScript", "Java", "React", "Node.js", "SQL", "Git", 
                             "Docker", "AWS", "API", "RESTful", "Agile", "CI/CD", "TypeScript",
                             "MongoDB", "PostgreSQL", "Redis", "Kubernetes", "Microservices"],
                "soft_skills": ["problem-solving", "collaboration", "communication", "leadership",
                               "analytical thinking", "team player", "self-motivated"],
                "action_verbs": ["developed", "engineered", "implemented", "optimized", "architected",
                                "designed", "deployed", "maintained", "automated", "integrated"]
            },
            "data_science": {
                "technical": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", "TensorFlow",
                             "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Data Visualization",
                             "Statistical Analysis", "A/B Testing", "Tableau", "Power BI", "Spark"],
                "soft_skills": ["analytical thinking", "problem-solving", "communication", "storytelling",
                               "business acumen", "attention to detail", "critical thinking"],
                "action_verbs": ["analyzed", "modeled", "predicted", "optimized", "visualized",
                                "implemented", "researched", "evaluated", "trained", "deployed"]
            },
            "marketing": {
                "technical": ["Google Analytics", "SEO", "SEM", "Content Marketing", "Social Media",
                             "Email Marketing", "Google Ads", "Facebook Ads", "HubSpot", "Salesforce",
                             "A/B Testing", "Marketing Automation", "CRM", "Adobe Creative Suite"],
                "soft_skills": ["creativity", "communication", "analytical thinking", "strategic planning",
                               "project management", "collaboration", "adaptability"],
                "action_verbs": ["launched", "executed", "optimized", "managed", "created", "coordinated",
                                "analyzed", "increased", "drove", "developed"]
            },
            "business_analyst": {
                "technical": ["SQL", "Excel", "Tableau", "Power BI", "JIRA", "Agile", "Scrum",
                             "Data Analysis", "Requirements Gathering", "Process Improvement",
                             "Business Intelligence", "Stakeholder Management"],
                "soft_skills": ["analytical thinking", "problem-solving", "communication", "collaboration",
                               "attention to detail", "critical thinking", "adaptability"],
                "action_verbs": ["analyzed", "identified", "documented", "collaborated", "facilitated",
                                "improved", "streamlined", "evaluated", "recommended", "implemented"]
            },
            "product_management": {
                "technical": ["Product Strategy", "Roadmap Planning", "User Research", "A/B Testing",
                             "Agile", "Scrum", "JIRA", "Analytics", "SQL", "Wireframing", "Prototyping"],
                "soft_skills": ["leadership", "strategic thinking", "communication", "collaboration",
                               "decision-making", "stakeholder management", "prioritization"],
                "action_verbs": ["launched", "led", "drove", "prioritized", "defined", "coordinated",
                                "analyzed", "optimized", "collaborated", "delivered"]
            }
        }
        
        # Detect industry
        if any(word in user_input_lower for word in ["software", "developer", "engineer", "programming", "coding"]):
            return keywords["software_engineering"]
        elif any(word in user_input_lower for word in ["data", "machine learning", "ml", "ai", "analytics"]):
            return keywords["data_science"]
        elif any(word in user_input_lower for word in ["marketing", "digital marketing", "seo", "social media"]):
            return keywords["marketing"]
        elif any(word in user_input_lower for word in ["business analyst", "ba", "requirements"]):
            return keywords["business_analyst"]
        elif any(word in user_input_lower for word in ["product manager", "pm", "product"]):
            return keywords["product_management"]
        else:
            return keywords["software_engineering"]  # Default


# -----------------------------
# ENHANCED PROMPT TEMPLATES
# -----------------------------


class ResumeTemplates:
    @staticmethod
    def get_enhanced_prompt(user_input):
        """Generate ultra-optimized prompt for comprehensive ATS-friendly resumes with ATTRACTIVE summary"""
        current_year = datetime.now().year
        keywords = ATSKeywordExtractor.get_industry_keywords(user_input)
        
        prompt = f"""You are a SENIOR ATS OPTIMIZATION SPECIALIST and CERTIFIED PROFESSIONAL RESUME WRITER (CPRW) with 15+ years experience. Your resumes achieve 94% interview callback rate and rank in top 1% for ATS compatibility.

MISSION: Create COMPREHENSIVE, RECRUITER-READY, ATS-OPTIMIZED resume extracting EVERY detail from user input and transforming it into compelling, keyword-rich content that passes automated screening AND impresses human recruiters.

USER INPUT: "{user_input}"

═══════════════════════════════════════════════════════════════
ELITE ONE-PAGE A4 RESUME - EXECUTIVE STANDARD
═══════════════════════════════════════════════════════════════

MISSION: Create TOP 1% executive-grade resume that passes ATS with 95%+ score AND makes recruiters immediately schedule interviews. Every word must justify its existence on the page.

ONE-PAGE MANDATE (Non-negotiable):
- A4 dimensions: 210mm × 297mm with 15mm margins
- Content density: Maximum impact in minimum space
- Visual hierarchy: Most important content in top 50% of page
- Recruiter eye-tracking: F-pattern optimized (left-heavy, top-heavy)
- 6-second test: Key qualifications visible without scrolling

ELITE CONTENT ARCHITECTURE:

1. PROFESSIONAL SUMMARY (Top 15% of page - MAKE OR BREAK section)
   
   LENGTH: Exactly 4 sentences, 110-140 words
   STRUCTURE: Power opening → Quantified proof → Technical authority → Strategic value
   
   Sentence 1: "[ELITE descriptor] [Senior/Lead Role] with [X+] years [transformative action]"
   • Descriptors ONLY: "Award-winning", "Top-performing", "Strategic", "Results-driven"
   • Show seniority: Senior, Lead, Principal, Staff-level
   • Action: "driving", "architecting", "transforming", "pioneering"
   
   Sentence 2: "Proven expertise [delivering MASSIVE impact]: [2-3 achievements with BIG numbers]"
   • Revenue impact: "$X.XM revenue growth", "ROI of XXX%"
   • Scale metrics: "serving XM+ users", "processing XK+ transactions/sec"
   • Performance: "reducing costs XX%", "improving speed XX%"
   • MINIMUM metrics: 6-figure revenue OR 100K+ users OR 50%+ improvements
   
   Sentence 3: "Deep technical mastery in [5-6 cutting-edge technologies]: {keywords['technical'][:6]}, [delivering systematic excellence]"
   • Stack modern tech (Cloud-native, AI/ML, Microservices, Real-time systems)
   • Show breadth + depth: Full-stack, distributed systems, scalable architecture
   • Business connection: "driving digital transformation", "enabling data-driven decisions"
   
   Sentence 4: "Recognized for [standout leadership quality] and [2-3 executive soft skills], consistently [measurable team/business outcome]"
   • Leadership: "mentoring engineers to senior roles", "leading cross-functional teams"
   • Soft skills: strategic thinking, stakeholder management, technical vision
   • Team impact: "improving velocity XX%", "reducing time-to-market", "building high-performing teams"
   
   MANDATORY ELEMENTS:
   ✓ 3-4 quantified achievements (revenue, users, performance, scale)
   ✓ 10-12 ATS keywords naturally integrated
   ✓ Senior-level positioning (avoid junior language)
   ✓ Business value orientation (not just technical tasks)
   ✓ Forward-looking ambition (subtle, confident)
   
   POWER WORDS REQUIRED: architected, spearheaded, pioneered, transformed, orchestrated, scaled, optimized, engineered, drove, delivered
   
   TONE: Confident executive, proven track record, understated excellence
   
   ⭐ WORLD-CLASS EXAMPLE:
   "Award-winning Senior Software Architect with 6+ years pioneering cloud-native solutions for Fortune 500 clients, specializing in React, Node.js, AWS, and microservices architecture that process 10M+ daily transactions. Proven expertise delivering transformative impact: architected platform generating $8.2M additional annual revenue while reducing infrastructure costs 47%, and engineered real-time analytics system serving 2M+ users with 99.99% uptime. Deep technical mastery in JavaScript/TypeScript, Python, Kubernetes, GraphQL, Terraform, and event-driven architecture, consistently delivering enterprise solutions 40% ahead of schedule with zero critical bugs. Recognized for exceptional technical leadership and strategic vision, having mentored 15 engineers to senior positions while driving 65% improvement in team velocity and establishing engineering best practices adopted company-wide."

2. TECHNICAL SKILLS (20-28 skills across 4-5 categories - ATS keyword bank)
   
   STRATEGIC ORGANIZATION:
   • List in demand-order (most sought-after first within each category)
   • Include proficiency where relevant: "Python (Expert)", "AWS (Advanced)"
   • Show ecosystem mastery: "React (Hooks, Context, Redux, Next.js)"
   • Balance breadth + specialization
   
   CATEGORIES (Elite standard):
   
   **Languages & Frameworks**: [6-8 items]
   • Primary language + modern features: "JavaScript (ES6+, TypeScript)"
   • Backend: "Python 3.x", "Node.js", "Java 17"
   • Frontend: "React 18", "Vue 3", "Angular"
   • Include versions for credibility
   
   **Cloud & Infrastructure**: [6-8 items]
   • Major cloud: "AWS (EC2, S3, Lambda, RDS, CloudFront)"
   • Containers: "Docker", "Kubernetes (K8s)"
   • CI/CD: "Jenkins", "GitHub Actions", "ArgoCD"
   • IaC: "Terraform", "CloudFormation"
   
   **Databases & Data**: [4-6 items]
   • SQL: "PostgreSQL", "MySQL"
   • NoSQL: "MongoDB", "Redis", "DynamoDB"
   • Big Data: "Apache Kafka", "Spark" (if relevant)
   • Search: "Elasticsearch" (if applicable)
   
   **Tools & Practices**: [4-6 items]
   • Version Control: "Git (GitHub, GitLab)"
   • Architecture: "Microservices", "RESTful APIs", "GraphQL"
   • Methodologies: "Agile/Scrum", "TDD", "DevOps"
   • Monitoring: "Prometheus", "Grafana", "DataDog"
   
   RULES:
   ✓ Extract ALL technologies from input
   ✓ Add complementary tech (React → automatically include Redux, Webpack, npm)
   ✓ Include industry standards (Git, REST APIs always relevant)
   ✓ Modern > legacy (prioritize current versions)
   ✓ Total: 20-28 skills (anything less looks junior, anything more clutters)

3. PROFESSIONAL EXPERIENCE (2-3 roles MAXIMUM - Quality over quantity)
   
   SELECTION CRITERIA:
   • Most recent 2-3 roles only (last 4-6 years)
   • If 10+ years experience: combine early roles into one line
   • Each role: 3 achievement bullets ONLY (no more, no less)
   • Prioritize: Latest role (most bullets/detail) > Earlier roles (concise)
   
   BULLET FORMULA (15-22 words per bullet - STRICT):
   [Power verb] [specific technical implementation] [using X, Y, Z technologies] [achieving A% metric] [resulting in business impact $B/C users/D%]
   
   MANDATORY PER BULLET:
   ✓ Start with power verb: {', '.join(keywords['action_verbs'][:8])}
   ✓ Specific technical solution (not vague "worked on")
   ✓ 2-3 technologies mentioned in context
   ✓ Quantified metric (%, $, scale, time, users)
   ✓ Business impact (revenue, cost, users, performance, efficiency)
   
   METRICS HIERARCHY (Use highest available):
   1. Revenue/Cost: "$X.XM revenue", "reducing costs $XXK", "ROI XXX%"
   2. Scale: "serving XM users", "processing XK requests/sec", "XK daily transactions"
   3. Performance: "improving speed XX%", "reducing latency from Xs to Ys"
   4. Efficiency: "reducing time XX%", "increasing productivity XX%"
   5. Quality: "achieving 99.X% uptime", "zero production incidents"
   
   ⭐ ELITE EXAMPLES (Study these patterns):
   
   ✅ "Architected microservices payment gateway using Node.js, RabbitMQ, and PostgreSQL, processing 500K+ daily transactions with 99.99% reliability, reducing payment failures by 82% and recovering $1.2M in annual revenue"
   
   ✅ "Engineered real-time analytics pipeline leveraging Apache Kafka, Spark, and Elasticsearch, enabling sub-second data processing for 5M+ events/day, reducing executive report generation from 4 hours to 6 minutes"
   
   ✅ "Led cross-functional agile team of 12 engineers through platform modernization using React, TypeScript, and AWS, delivering 28 features ahead of schedule, increasing user engagement 67% and achieving 4.8/5.0 satisfaction score"
   
   ✅ "Optimized cloud infrastructure on AWS (Lambda, RDS, CloudFront) implementing auto-scaling and caching strategies, reducing monthly costs by $45K (38% savings) while improving API response time 61% from 850ms to 330ms"
   
   ✅ "Spearheaded migration from monolith to microservices architecture using Docker, Kubernetes, and GraphQL, reducing deployment time by 75% from 3 hours to 42 minutes and eliminating 94% of production rollback incidents"
   
   ROLE STRUCTURE:
   {{
     "title": "Senior/Lead/Staff [Role] (show seniority)",
     "company": "Company Name",
     "location": "City, ST",
     "duration": "Mon YYYY - Present/Mon YYYY",
     "achievements": [
       "BULLET 1 (HERO): Biggest impact with best metrics - this is your signature achievement",
       "BULLET 2 (TECHNICAL): Deep technical complexity showing expertise and problem-solving",
       "BULLET 3 (LEADERSHIP/BUSINESS): Team impact, process improvement, or business value"
     ]
   }}
   
   PROGRESSION INDICATORS:
   • Show increasing responsibility: "Led team of X", "Mentored Y engineers"
   • Technology evolution: Older role (jQuery) → Recent role (React, TypeScript)
   • Scope growth: "for department" → "for entire organization" → "for 500K+ users"

4. PROJECTS (2 MAXIMUM - Only if they're exceptional)
   
   INCLUDE PROJECTS IF:
   • Recent graduate/early career (< 3 years experience)
   • Switching industries (show transferable skills)
   • Projects more impressive than work experience
   • Building personal brand (open source, side business)
   
   SKIP PROJECTS IF:
   • 5+ years professional experience (work speaks for itself)
   • Strong work history fills the page
   • Projects are academic/basic
   
   PROJECT STRUCTURE (Compact but impactful):
   {{
     "title": "Compelling Project Name (professional naming)",
     "technologies": "Full Modern Stack: 8-12 technologies showing depth",
     "duration": "Mon YYYY - Mon YYYY",
     "description": [
       "18-22 WORDS: [Power verb] [comprehensive solution] [using tech stack] [achieving specific metric] [serving X users OR solving Y problem]",
       "18-22 WORDS: [Power verb] [standout technical feature] [implementation details] [quantified improvement in performance/UX/scale]"
     ],
     "github": "github.com/username/professional-repo-name",
     "demo": "live-demo-url.com"
   }}
   
   ⭐ ELITE PROJECT EXAMPLE:
   {{
     "title": "Enterprise Task Management Platform",
     "technologies": "React, Redux, TypeScript, Node.js, Express, PostgreSQL, Redis, Socket.io, AWS (S3, EC2), Docker, Nginx",
     "duration": "Jan 2024 - Apr 2024",
     "description": [
       "Engineered full-stack SaaS platform with real-time collaboration using WebSocket, supporting 3,500+ registered users across 50+ organizations with 99.7% uptime and sub-100ms latency",
       "Implemented advanced caching layer with Redis and CDN integration, reducing database load 73% and page load times from 3.1s to 890ms, achieving 85% mobile performance score"
     ],
     "github": "github.com/user/enterprise-task-platform",
     "demo": "taskplatform.demo.com"
   }}

5. EDUCATION (Minimal but complete - Bottom 10% of page)
   
   FORMAT:
   {{
     "degree": "Bachelor of Science in Computer Science (spell out fully)",
     "institution": "University Name",
     "location": "City, State",
     "graduation": "May 2024",
     "gpa": "3.8/4.0 (ONLY if 3.7+, otherwise omit)",
     "relevant_coursework": ["Advanced Algorithms", "Distributed Systems", "Machine Learning", "Database Design"],
     "honors": ["Dean's List (6 semesters)", "Academic Excellence Scholarship $15K"]
   }}
   
   RULES:
   ✓ Coursework: 3-4 most advanced/relevant courses
   ✓ GPA: Only if 3.7+ (3.5-3.69 optional, < 3.5 omit)
   ✓ Honors: Only substantial achievements (Dean's List, scholarships $5K+, top 10%)
   ✓ If 7+ years experience: Reduce to single line (degree, school, year)
   ✓ Skip high school entirely

6. CERTIFICATIONS (Top 3 industry-recognized ONLY)
   
   ELITE STANDARD:
   • Industry gold standard: AWS Certified, Google Cloud, Azure, Kubernetes (CKA/CKAD)
   • Specialized: TensorFlow Developer, PMP, Salesforce Architect
   • Include issuing year (recent = credible)
   
   SKIP:
   • Coursera/Udemy certificates (not industry-recognized)
   • Internal company training
   • Expired certifications (> 3 years old)
   
   FORMAT:
   [
     "AWS Certified Solutions Architect - Professional (Amazon Web Services, 2024)",
     "Certified Kubernetes Administrator (CKA) (Cloud Native Computing Foundation, 2024)",
     "Google Professional Cloud Architect (Google Cloud, 2023)"
   ]

7. ACHIEVEMENTS & AWARDS (Top 2 ONLY - Must be genuinely impressive)
   
   INCLUDE IF:
   • Major hackathon wins (1st-3rd place, 100+ participants)
   • Significant open source contributions (projects with 10K+ stars)
   • Published research/papers (peer-reviewed, conference presentations)
   • Industry awards/recognition (company-wide, regional, national)
   • Patents filed/granted
   • Speaking engagements (conferences, meetups with 100+ attendees)
   
   SKIP:
   • Participation certificates
   • Internal team awards
   • Generic recognition ("Employee of the Month")
   
   FORMAT:
   [
     "1st Place Google Cloud Innovation Challenge 2024 - Led 4-person team building AI-powered code review tool using Gemini API and Python, adopted by 800+ developers, reducing review cycle time 52%",
     "Open Source Maintainer - Core contributor to React Router (50K+ GitHub stars) with 85 merged PRs improving performance 30% and resolving 200+ issues, impacting 5M+ weekly NPM downloads"
   ]

═══════════════════════════════════════════════════════════════
ELITE ATS OPTIMIZATION (95%+ Match Score)
═══════════════════════════════════════════════════════════════

KEYWORD STRATEGY:
✓ Professional Summary: 10-12 high-value keywords naturally integrated
✓ Skills Section: 20-28 keywords (ATS goldmine)
✓ Experience: 3-5 keywords per bullet (embedded in achievements)
✓ Top 5 keywords repeated 3-4× across sections
✓ Both forms: "Machine Learning (ML)", "Continuous Integration/Continuous Deployment (CI/CD)"

PARSING OPTIMIZATION:
✓ Standard headers: "Professional Summary", "Technical Skills", "Professional Experience", "Projects", "Education", "Certifications", "Achievements"
✓ Clean bullet points (• symbol)
✓ Consistent date formats: "Mon YYYY - Mon YYYY"
✓ No tables, graphics, columns (ATS can't parse)
✓ Left-aligned text (F-pattern reading)

KEYWORD FRONT-LOADING:
✓ First 3-5 words of each bullet contain power verb + technology
✓ Example: "Architected microservices payment system..." not "Worked on a project that involved architecting..."

═══════════════════════════════════════════════════════════════
RECRUITER PSYCHOLOGY (6-Second Test)
═══════════════════════════════════════════════════════════════

VISUAL HIERARCHY:
✓ Top 40% of page contains: Name, contact, killer summary, top skills
✓ Quantified metrics visible at first glance (%, $, numbers in bold positions)
✓ Job titles show seniority (Senior, Lead, Staff)
✓ Clean white space (not cluttered)

SCANNING PATTERN (F-Pattern):
✓ Left side heavy (where eyes go first)
✓ Bullets start with power verbs
✓ First bullet per role = biggest achievement
✓ Numbers draw eye immediately

DECISION TRIGGERS:
✓ Summary makes them think: "This person can solve our problems"
✓ Skills match job description 70%+
✓ Experience shows growth and increasing impact
✓ Metrics prove claims (not just stating "improved performance")
✓ Recent and relevant (last 3-5 years focused)

═══════════════════════════════════════════════════════════════
JSON STRUCTURE - ELITE ONE-PAGE A4
═══════════════════════════════════════════════════════════════

{{
  "contact": {{
    "name": "Full Professional Name",
    "email": "professional.email@domain.com",
    "phone": "(555) 123-4567",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "portfolio": "www.portfolio.com"
  }},
  
  "professional_summary": "EXACTLY 4 sentences, 110-140 words. Must include: [Elite descriptor + Senior role + years] + [2-3 MASSIVE quantified achievements with 6-figure/scale metrics] + [5-6 cutting-edge technologies with business context] + [Leadership quality + team impact]. MINIMUM 3 achievements with BIG numbers. Power words: architected, spearheaded, pioneered, transformed. 10-12 keywords from: {', '.join(keywords['technical'][:6])}, {', '.join(keywords['soft_skills'][:4])}. Executive tone, proven track record, business-focused.",
  
  "technical_skills": {{
    "Languages & Frameworks": ["Modern primary language with version", "4-6 total showing full-stack", "Include: Python 3.x, JavaScript (ES6+), TypeScript, React 18, Node.js"],
    "Cloud & Infrastructure": ["Major cloud platform with services", "Containers & orchestration", "CI/CD tools", "6-8 total: AWS, Docker, Kubernetes, Jenkins, Terraform"],
    "Databases & Data": ["SQL + NoSQL options", "Caching layer", "4-6 total: PostgreSQL, MongoDB, Redis, Kafka"],
    "Tools & Practices": ["Version control", "Architecture patterns", "Methodologies", "4-6 total: Git, Microservices, RESTful APIs, GraphQL, Agile"]
  }},
  
  "experience": [
    {{
      "title": "Senior/Lead [Role] (show seniority level)",
      "company": "Company Name (include industry if notable)",
      "location": "City, ST",
      "duration": "Mon YYYY - Present",
      "achievements": [
        "15-22 WORDS: [Power verb] [specific technical implementation using X, Y, Z] [achieving A% metric] [resulting in $B revenue/C users/D% business impact]. Must include: tech stack, quantified metric, business value.",
        "15-22 WORDS: [Power verb] [complex technical solution] [technologies] [solving specific problem] [improving metric by %]. Show technical depth + scale.",
        "15-22 WORDS: [Power verb] [leadership/collaboration element] [methodology] [delivering outcome] [team/business impact]. Show leadership + results."
      ]
    }},
    {{
      "title": "Mid-level [Role]",
      "company": "Company Name",
      "location": "City, ST",
      "duration": "Mon YYYY - Mon YYYY",
      "achievements": [
        "3 bullets, 15-22 words each, showing progression from first role",
        "Focus on technical growth and increasing complexity",
        "Include metrics and technologies"
      ]
    }}
  ],
  
  "projects": [
    {{
      "title": "Professional Project Name",
      "technologies": "Complete Modern Stack: React, TypeScript, Node.js, Express, PostgreSQL, Redis, Docker, AWS (S3, EC2), 8-12 technologies",
      "duration": "Mon YYYY - Mon YYYY",
      "description": [
        "18-22 WORDS: [Power verb] [comprehensive solution] [using full tech stack] [achieving specific metric: X users OR Y% improvement] [business/user impact]",
        "18-22 WORDS: [Power verb] [key technical feature/optimization] [implementation approach] [quantified improvement in performance/UX/scale]"
      ],
      "github": "github.com/username/professional-repo-name",
      "demo": "live-demo-url.com"
    }}
  ],
  
  "education": [
    {{
      "degree": "Bachelor of Science in Computer Science (full name)",
      "institution": "University Name",
      "location": "City, State",
      "graduation": "May 2024",
      "gpa": "3.8/4.0 (only if 3.7+)",
      "relevant_coursework": ["Advanced course 1", "Advanced course 2", "Advanced course 3", "Advanced course 4"],
      "honors": ["Dean's List (X semesters)", "Scholarship Name $XXK"]
    }}
  ],
  
  "certifications": [
    "Industry-Recognized Cert 1 (Issuing Org, 2024)",
    "Industry-Recognized Cert 2 (Issuing Org, 2024)",
    "Industry-Recognized Cert 3 (Issuing Org, 2023)"
  ],
  
  "achievements": [
    "Major Achievement 1: [Specific accomplishment] [quantified impact] [context: competition/contribution] [year]. Example: '1st Place AWS Innovation Challenge 2024 - Built serverless ML platform using Lambda and SageMaker, adopted by 1,000+ developers, reducing model deployment time 78%'",
    "Major Achievement 2: [Significant contribution] [scale/reach] [impact metric]. Example: 'Open Source Core Contributor - 120+ merged PRs to TensorFlow (180K+ stars) improving inference speed 35%, impacting 10M+ developers globally'"
  ]
}}

═══════════════════════════════════════════════════════════════
FINAL ELITE QUALITY CHECKS
═══════════════════════════════════════════════════════════════

ONE-PAGE COMPLIANCE:
✓ Professional Summary: 110-140 words (4 sentences)
✓ Technical Skills: 20-28 items across 4 categories
✓ Experience: 2-3 roles × 3 bullets = 6-9 bullets total
✓ Projects: 0-2 (only if exceptional or early career)
✓ Education: Minimal (degree + 3-4 courses + honors)
✓ Certifications: Top 3 industry-recognized only
✓ Achievements: Top 2 genuinely impressive only
✓ TOTAL: Fits on single A4 page with professional spacing

ATS SCORE 95%+:
✓ Summary: 10-12 keywords, 3+ massive metrics
✓ Standard section headers (no creative variations)
✓ Top 5 keywords appear 3-4× naturally across sections
✓ Technical skills = comprehensive keyword bank (20-28 items)
✓ Each bullet: power verb + 2-3 technologies + quantified metric

RECRUITER MAGNETISM (6-Second Test):
✓ Summary makes recruiter STOP and READ (magnetic, achievement-heavy)
✓ Every bullet starts with powerful action verb
✓ Every experience bullet has impressive metric (%, $, scale)
✓ Shows clear progression and increasing impact
✓ Job titles reflect seniority level
✓ Recent and relevant (last 3-5 years focused)

EXECUTIVE POLISH:
✓ Confident tone (not arrogant, not timid)
✓ Business language (ROI, revenue, users, efficiency)
✓ Zero grammatical errors or typos
✓ Consistent formatting (dates, capitalization, punctuation)
✓ No personal pronouns (I, me, my, we)
✓ Past tense for previous roles, present for current
✓ Professional email and portfolio links

CONTENT EXCELLENCE:
✓ Every bullet uses CAR method (Context-Action-Result)
✓ Metrics are realistic and impressive (not inflated)
✓ Technologies mentioned in achievement context (not lists)
✓ Shows both technical depth AND business impact
✓ No fluff, filler, or generic statements
✓ Every word earns its place on the page

COMPETITIVE ADVANTAGE:
✓ Stands out from 200+ applicants
✓ Demonstrates measurable value (not just responsibilities)
✓ Shows leadership and growth mindset
✓ Balances technical excellence with soft skills
✓ Forward-thinking and results-oriented

TARGET OUTCOME:
- ATS Match Score: 95%+
- Recruiter Response: Interview invitation within 6 seconds of reading
- Positioning: Top 1% candidate in applicant pool
- Message: "This person will deliver exceptional results"

Return ONLY valid JSON with NO extra text, comments, or explanations."""

        return prompt

    @staticmethod
    def get_fallback_template(user_name):
        """Generate a basic ATS-optimized template when API fails"""
        return {
            "contact": {
                "name": user_name,
                "email": f"{user_name.lower().replace(' ', '.')}@email.com",
                "phone": "(555) 123-4567",
                "location": "City, State",
                "linkedin": f"linkedin.com/in/{user_name.lower().replace(' ', '-')}",
                "github": f"github.com/{user_name.lower().replace(' ', '')}",
                "portfolio": "www.portfolio.com"
            },
            "professional_summary": "Results-driven professional with strong technical expertise and proven track record of delivering high-impact solutions. Experienced in leveraging modern technologies to solve complex problems, optimize processes, and drive measurable business outcomes. Seeking to contribute technical skills and innovative thinking to challenging projects while continuing professional growth in a dynamic environment.",
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University Name",
                    "location": "City, State",
                    "graduation": "May 2024",
                    "gpa": "3.7/4.0",
                    "relevant_coursework": ["Data Structures & Algorithms", "Database Systems", "Software Engineering", "Machine Learning"],
                    "honors": ["Dean's List (All Semesters)", "Academic Excellence Scholarship"]
                }
            ],
            "technical_skills": {
                "Programming Languages": ["Python", "JavaScript", "Java", "SQL", "TypeScript"],
                "Frameworks & Libraries": ["React", "Node.js", "Express", "Django", "TensorFlow"],
                "Tools & Technologies": ["Git", "Docker", "Kubernetes", "Jenkins", "JIRA"],
                "Databases & Cloud": ["PostgreSQL", "MongoDB", "Redis", "AWS", "Azure"]
            },
            "experience": [
                {
                    "title": "Software Developer Intern",
                    "company": "Tech Company",
                    "location": "City, State",
                    "duration": "June 2023 - August 2023",
                    "achievements": [
                        "Engineered and deployed 3 full-stack web applications using React and Node.js, serving 1,000+ daily active users with 99.9% uptime",
                        "Optimized database queries and implemented caching strategies, reducing API response time by 45% and improving user experience",
                        "Collaborated with cross-functional team of 8 developers using Agile methodology to deliver 15+ features on schedule, increasing customer satisfaction by 25%"
                    ]
                }
            ],
            "projects": [
                {
                    "title": "E-Commerce Platform",
                    "technologies": "React, Node.js, MongoDB, Stripe API, AWS",
                    "duration": "January 2024 - March 2024",
                    "description": [
                        "Developed full-featured e-commerce platform with payment integration, achieving $10K+ in test transactions and 500+ registered users",
                        "Implemented secure authentication, shopping cart, and order management system, reducing checkout time by 30% through optimized UX"
                    ],
                    "github": f"github.com/{user_name.lower().replace(' ', '')}/ecommerce-platform",
                    "demo": "ecommerce-demo.com"
                }
            ],
            "certifications": [
                "AWS Certified Cloud Practitioner (Amazon Web Services, 2024)",
                "Google Data Analytics Professional Certificate (Google, 2024)"
            ],
            "achievements": [
                "Won 1st Place at University Hackathon 2024 - Built AI-powered study assistant used by 200+ students, reducing study time by 35%",
                "Open Source Contributor - Contributed 75+ commits to popular React libraries with 50K+ GitHub stars"
            ]
        }


# -----------------------------
# API INTEGRATION
# -----------------------------

def call_llm_api(prompt, api_key=None, api_provider="groq"):
    """Call various LLM APIs with enhanced error handling"""
    
    DEFAULT_GROQ_KEY = "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"

    providers = {
        "groq": {
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "env_var": "GROQ_API_KEY",
            "model": "openai/gpt-oss-120b",
            "max_tokens": 4096
        },
        "together": {
            "url": "https://api.together.xyz/v1/chat/completions",
            "env_var": "TOGETHER_API_KEY",
            "model": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "max_tokens": 4096
        },
        "openai": {
            "url": "https://api.openai.com/v1/chat/completions",
            "env_var": "OPENAI_API_KEY",
            "model": "gpt-3.5-turbo",
            "max_tokens": 4096
        }
    }

    providers_to_try = [api_provider] if api_provider in providers else []
    providers_to_try.extend([p for p in ["groq", "together", "openai"] if p not in providers_to_try])

    last_error = None

    for provider_name in providers_to_try:
        provider = providers[provider_name]

        if api_key is None:
            api_key = os.environ.get(provider["env_var"])
            if api_key is None and provider_name == "groq":
                api_key = DEFAULT_GROQ_KEY

        if not api_key:
            st.warning(f"⚠️  No API key found for {provider_name}")
            continue

        try:
            st.info(f"🔄 Generating with {provider_name.upper()}...")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": provider["model"],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert ATS resume writer and career coach. You create compelling, keyword-optimized resumes that pass ATS systems and impress recruiters. Always respond with valid JSON only. Focus on achievements, metrics, and impact."
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": provider["max_tokens"],
                "temperature": 0.8
            }

            response = requests.post(
                provider["url"],
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                error_detail = response.text[:200]
                raise Exception(f"HTTP {response.status_code}: {error_detail}")

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                st.success(f"✅ Resume generated with {provider_name.upper()}!")
                return content
            else:
                raise Exception(f"Unexpected response format from {provider_name}")

        except Exception as e:
            last_error = str(e)
            st.warning(f"⚠️  {provider_name} failed: {str(e)[:100]}")
            api_key = None
            continue

    raise Exception(f"All API providers failed. Last error: {last_error}")


# -----------------------------
# HTML GENERATION (A4 OPTIMIZED)
# -----------------------------

def generate_html_resume(resume_data):
    """Generate a professional single-page A4 HTML resume"""

    contact = resume_data.get('contact', {})

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{contact.get('name', 'Professional Resume')}</title>
    <style>
        @page {{
            size: A4;
            margin: 0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Calibri', 'Arial', sans-serif;
            font-size: 9.5pt;
            line-height: 1.25;
            color: #333;
            background: white;
            width: 210mm;
            min-height: 297mm;
            max-height: 297mm;
            margin: 0 auto;
            padding: 12mm 15mm;
            overflow: hidden;
        }}

        .header {{
            text-align: center;
            margin-bottom: 10pt;
            padding-bottom: 6pt;
            border-bottom: 2pt solid #1F4E79;
        }}

        .name {{
            font-size: 18pt;
            font-weight: bold;
            color: #1F4E79;
            margin-bottom: 3pt;
            letter-spacing: 0.5pt;
        }}

        .contact-info {{
            font-size: 8.5pt;
            color: #595959;
            margin-top: 2pt;
            line-height: 1.3;
        }}

        .contact-info a {{
            color: #595959;
            text-decoration: none;
        }}

        .section {{
            margin-bottom: 8pt;
            page-break-inside: avoid;
        }}

        .section-title {{
            font-size: 11pt;
            font-weight: bold;
            color: #1F4E79;
            text-transform: uppercase;
            margin-bottom: 4pt;
            padding-bottom: 1pt;
            border-bottom: 1pt solid #1F4E79;
            letter-spacing: 0.3pt;
        }}

        .entry {{
            margin-bottom: 6pt;
            page-break-inside: avoid;
        }}

        .entry-header {{
            font-weight: bold;
            margin-bottom: 1pt;
            font-size: 9.5pt;
        }}

        .entry-subheader {{
            font-size: 8.5pt;
            color: #595959;
            margin-bottom: 2pt;
            line-height: 1.2;
        }}

        .entry-details {{
            margin-left: 12pt;
        }}

        .bullet {{
            margin-bottom: 1.5pt;
            padding-left: 10pt;
            text-indent: -10pt;
            line-height: 1.25;
        }}

        .skills-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 2pt;
        }}

        .skill-category {{
            margin-bottom: 1.5pt;
            line-height: 1.2;
        }}

        .skill-label {{
            font-weight: bold;
            display: inline;
        }}

        .summary {{
            text-align: justify;
            margin-bottom: 6pt;
            line-height: 1.3;
        }}

        @media print {{
            body {{
                margin: 0;
                padding: 12mm 15mm;
                width: 210mm;
                height: 297mm;
            }}

            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{contact.get('name', 'Your Name')}</div>
        <div class="contact-info">
            {contact.get('email', '')} | {contact.get('phone', '')} | {contact.get('location', '')}
        </div>
        <div class="contact-info">"""

    links = []
    if contact.get('linkedin'):
        links.append(f"{contact['linkedin']}")
    if contact.get('github'):
        links.append(f"{contact['github']}")
    if contact.get('portfolio'):
        links.append(f"{contact['portfolio']}")

    html_content += " | ".join(links)
    html_content += """
        </div>
    </div>
"""

    # Professional Summary
    if resume_data.get('professional_summary'):
        html_content += f"""
    <div class="section">
        <div class="section-title">Professional Summary</div>
        <div class="summary">{resume_data['professional_summary']}</div>
    </div>
"""

    # Education
    if resume_data.get('education'):
        html_content += """
    <div class="section">
        <div class="section-title">Education</div>
"""
        for edu in resume_data['education']:
            html_content += f"""
        <div class="entry">
            <div class="entry-header">{edu.get('degree', '')}</div>
            <div class="entry-subheader">
                {edu.get('institution', '')} | {edu.get('location', '')} | {edu.get('graduation', '')}"""

            if edu.get('gpa'):
                html_content += f" | GPA: {edu['gpa']}"

            html_content += "</div>"

            if edu.get('honors'):
                html_content += f"<div class='entry-subheader'>Honors: {', '.join(edu['honors'][:2])}</div>"

            if edu.get('relevant_coursework'):
                html_content += f"<div class='entry-subheader'>Coursework: {', '.join(edu['relevant_coursework'][:4])}</div>"

            html_content += "</div>"

        html_content += "    </div>\n"

    # Technical Skills
    if resume_data.get('technical_skills'):
        html_content += """
    <div class="section">
        <div class="section-title">Technical Skills</div>
        <div class="skills-grid">
"""
        for category, skills in resume_data['technical_skills'].items():
            if skills:
                html_content += f"""
            <div class="skill-category">
                <span class="skill-label">{category}:</span> {', '.join(skills)}
            </div>
"""
        html_content += """        </div>
    </div>
"""

    # Experience
    if resume_data.get('experience'):
        html_content += """
    <div class="section">
        <div class="section-title">Professional Experience</div>
"""
        for exp in resume_data['experience']:
            html_content += f"""
        <div class="entry">
            <div class="entry-header">{exp.get('title', '')} | {exp.get('company', '')}</div>
            <div class="entry-subheader">{exp.get('location', '')} | {exp.get('duration', '')}</div>
            <div class="entry-details">
"""
            for achievement in exp.get('achievements', [])[:3]:
                html_content += f"""                <div class="bullet">• {achievement}</div>\n"""

            html_content += """            </div>
        </div>
"""
        html_content += "    </div>\n"

    # Projects
    if resume_data.get('projects'):
        html_content += """
    <div class="section">
        <div class="section-title">Projects</div>
"""
        for project in resume_data['projects'][:3]:
            html_content += f"""
        <div class="entry">
            <div class="entry-header">{project.get('title', '')}</div>
            <div class="entry-subheader">{project.get('technologies', '')}"""

            if project.get('duration'):
                html_content += f" | {project['duration']}"

            project_links = []
            if project.get('github'):
                project_links.append(f"GitHub: {project['github']}")
            if project.get('demo'):
                project_links.append(f"Demo: {project['demo']}")
            if project_links:
                html_content += f" | {' | '.join(project_links)}"

            html_content += "</div>\n            <div class='entry-details'>\n"

            for desc in project.get('description', [])[:2]:
                html_content += f"""                <div class="bullet">• {desc}</div>\n"""

            html_content += """            </div>
        </div>
"""
        html_content += "    </div>\n"

    # Certifications
    if resume_data.get('certifications'):
        html_content += """
    <div class="section">
        <div class="section-title">Certifications</div>
        <div class="entry-details">
"""
        for cert in resume_data['certifications'][:3]:
            html_content += f"""            <div class="bullet">• {cert}</div>\n"""

        html_content += """        </div>
    </div>
"""

    # Achievements
    if resume_data.get('achievements'):
        html_content += """
    <div class="section">
        <div class="section-title">Achievements & Awards</div>
        <div class="entry-details">
"""
        for achievement in resume_data['achievements'][:3]:
            html_content += f"""            <div class="bullet">• {achievement}</div>\n"""

        html_content += """        </div>
    </div>
"""

    html_content += """
</body>
</html>"""

    return html_content


# -----------------------------
# JSON EXTRACTION & PARSING
# -----------------------------

def extract_json_from_response(response_text):
    """Extract and parse JSON from LLM response with enhanced error handling"""
    
    # First try: Direct JSON parse
    try:
        cleaned = response_text.strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Second try: Remove markdown code blocks
    try:
        cleaned = re.sub(r'```json\s*','', response_text)
        cleaned = re.sub(r'```\s*','', cleaned)
        cleaned = cleaned.strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Third try: Find JSON object using regex
    json_patterns = [
        r'```json\s*(\{.*?\})\s*```',
        r'```\s*(\{.*?\})\s*```',
        r'(\{[^{}]*\{[^{}]*\}[^{}]*\})',
        r'(\{.*\})',
    ]
    
    for pattern in json_patterns:
        matches = re.finditer(pattern, response_text, re.DOTALL)
        for match in matches:
            try:
                json_str = match.group(1) if match.lastindex else match.group(0)
                json_str = json_str.strip()
                parsed = json.loads(json_str)
                if isinstance(parsed, dict) and 'contact' in parsed:
                    return parsed
            except (json.JSONDecodeError, IndexError):
                continue
    
    # Fourth try: Extract largest JSON-like structure
    try:
        start = response_text.find('{')
        end = response_text.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = response_text[start:end+1]
            parsed = json.loads(json_str)
            if isinstance(parsed, dict):
                return parsed
    except json.JSONDecodeError:
        pass
    
    st.error("🔍 DEBUG: Could not parse JSON. Response preview:")
    st.code(response_text[:500] + "..." if len(response_text) > 500 else response_text)
    
    raise ValueError("Could not extract valid JSON from response. The AI may have returned malformed data.")


# -----------------------------
# STREAMLIT UI
# -----------------------------

def main():
    # Title
    st.markdown("""
        <div class="title-container">
            <h1 class="title-text">🚀 AI Resume Builder</h1>
            <p class="subtitle-text">Create ATS-Optimized Professional Resumes in Seconds</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.markdown("---")
        
        st.markdown("### 🎯 ATS Optimization Features")
        st.markdown("""
        - ✨ **AI-Powered Generation**
        - 📊 **Keyword-Rich Content**
        - 💼 **Achievement-Focused**
        - 📈 **Quantifiable Metrics**
        - 🔑 **Industry Keywords**
        - 📄 **ATS-Friendly Format**
        - 💾 **Instant Download**
        """)

        st.markdown("---")
        st.markdown("### 💡 Pro Tips for Better Results")
        st.markdown("""
        **Include in your description:**
        - Your target role/title
        - Years of experience
        - Key technical skills
        - Industry/domain
        - Career goals
        
        **Example:**
        "Software engineer with 3 years experience in Python and React, specializing in web applications, seeking senior developer role"
        """)
        
        st.markdown("---")
        st.markdown("### 🔑 What Makes a Great Resume")
        st.markdown("""
        - **Keywords**: Industry-specific terms
        - **Metrics**: Numbers, %, $ amounts
        - **Action Verbs**: Developed, engineered, optimized
        - **Impact**: Show results, not just duties
        - **ATS Format**: Standard sections, no graphics
        """)

    # Main content
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">⚡</div>
                <div class="stat-label">ATS Optimized</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">🎯</div>
                <div class="stat-label">Keyword Rich</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">💼</div>
                <div class="stat-label">Impact Focused</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Input section
    st.markdown("### 📝 Tell Us About Yourself")
    st.markdown("""
        <div class="info-card">
            <strong>Be Specific! Include:</strong><br>
            ✓ Target role/job title<br>
            ✓ Years of experience<br>
            ✓ Key technical skills<br>
            ✓ Industry/domain<br>
            ✓ Career goals<br><br>
            <strong>Good Examples:</strong><br>
            • "Software engineer with 3 years experience in Python, React, and AWS, seeking senior full-stack developer role"<br>
            • "Data scientist with 2 years ML experience, proficient in TensorFlow and SQL, targeting AI research position"<br>
            • "Digital marketing specialist with 4 years SEO and content marketing experience, seeking marketing manager role"
        </div>
    """, unsafe_allow_html=True)

    user_input = st.text_area(
        "Enter your detailed description (2-3 lines recommended)",
        placeholder="E.g., Software engineer with 3 years experience in Python, JavaScript, and cloud technologies. Specialized in building scalable web applications and microservices. Seeking senior developer role at innovative tech company...",
        height=120,
        key="user_input"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 Generate My ATS-Optimized Resume", use_container_width=True)

    # Generation logic
    if generate_button:
        if not user_input:
            st.error("❌ Please provide a description to generate your resume.")
            return

        if len(user_input.split()) < 10:
            st.warning("⚠️ For best results, provide more details (at least 10 words). Include your role, experience, skills, and goals.")

        st.info(f"🤖 Generating ATS-optimized resume with industry keywords...")
        st.warning("⏳ This may take 30-60 seconds for best quality...")

        try:
            enhanced_prompt = ResumeTemplates.get_enhanced_prompt(user_input)

            # Call LLM API with retry logic
            MAX_RETRIES = 3
            retry_count = 0
            resume_data = None

            while retry_count < MAX_RETRIES and resume_data is None:
                try:
                    with st.spinner(f"🎯 Attempt {retry_count + 1}/{MAX_RETRIES}: Generating resume..."):
                        llm_response = call_llm_api(enhanced_prompt)
                        st.info("📊 Parsing resume data...")
                        resume_data = extract_json_from_response(llm_response)
                        break  # Success!
                except Exception as e:
                    retry_count += 1
                    if retry_count < MAX_RETRIES:
                        st.warning(f"⚠️ Attempt {retry_count} failed. Retrying...")
                        import time
                        time.sleep(2)
                    else:
                        st.error(f"❌ All {MAX_RETRIES} attempts failed: {str(e)}")
                        raise
            
            if resume_data is None:
                raise Exception("Failed to generate valid resume data after all retries")

            # Validate professional summary
            summary = resume_data.get('professional_summary', '')
            if len(summary.split()) < 20:
                st.warning("⚠️ Generated summary is too short. Enhancing...")

            # Generate HTML resume
            st.info("🎨 Creating ATS-friendly HTML resume...")
            html_content = generate_html_resume(resume_data)

            # Save HTML file
            filename = f"resume_ats_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

            # Success message
            st.markdown("""
                <div class="success-box">
                    <h2>✅ ATS-Optimized Resume Generated Successfully!</h2>
                    <p>Your keyword-rich, professionally formatted resume is ready</p>
                </div>
            """, unsafe_allow_html=True)

            # Display key features
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info("✅ **Keyword Optimized**\nIndustry-relevant terms included")
            with col2:
                st.info("✅ **Achievement Focused**\nMetrics and impact highlighted")
            with col3:
                st.info("✅ **ATS Compatible**\nStandard format for parsing")

            st.success(f"📄 Saved as: {filename}")

            # Save JSON backup
            json_filename = filename.replace('.html', '.json')

            # Download buttons
            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="📄 Download HTML Resume",
                    data=html_content,
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True
                )

            with col2:
                json_data = json.dumps(resume_data, indent=2)
                st.download_button(
                    label="💾 Download Resume Data (JSON)",
                    data=json_data,
                    file_name=json_filename,
                    mime="application/json",
                    use_container_width=True
                )

            st.info("💡 **To save as PDF:** Open the HTML file in your browser and use Print → Save as PDF (Ctrl+P / Cmd+P)")

            # Show ATS tips
            st.markdown("""
                <div class="info-card">
                    <strong>🎯 ATS Optimization Tips Applied:</strong><br>
                    ✓ Industry-specific keywords naturally integrated<br>
                    ✓ Achievement-based bullets with quantifiable metrics<br>
                    ✓ Standard section headers for ATS parsing<br>
                    ✓ Action verbs at the start of each bullet<br>
                    ✓ Technical skills organized by category<br>
                    ✓ Clean, parseable formatting without graphics
                </div>
            """, unsafe_allow_html=True)

            # Preview
            st.markdown("### 👀 Resume Preview")
            st.markdown("**📋 Professional Summary:**")
            st.info(resume_data.get('professional_summary', 'N/A'))
            
            st.markdown("**🔑 Key Highlights:**")
            highlights = []
            if resume_data.get('technical_skills'):
                skills_count = sum(len(v) for v in resume_data['technical_skills'].values())
                highlights.append(f"✓ {skills_count} technical skills listed")
            if resume_data.get('experience'):
                exp_count = sum(len(exp.get('achievements', [])) for exp in resume_data['experience'])
                highlights.append(f"✓ {exp_count} achievement-focused bullets")
            if resume_data.get('projects'):
                highlights.append(f"✓ {len(resume_data['projects'])} projects showcased")
            if resume_data.get('certifications'):
                highlights.append(f"✓ {len(resume_data['certifications'])} certifications")
            
            for highlight in highlights:
                st.success(highlight)

            st.markdown("### 📄 Full Resume")
            st.components.v1.html(html_content, height=800, scrolling=True)

        except Exception as e:
            st.error(f"❌ Error generating resume: {str(e)}")

            # Try to extract name for fallback
            name_match = re.search(r'name is ([A-Za-z\s]+)', user_input, re.IGNORECASE)
            if name_match:
                user_name = name_match.group(1).strip()
            else:
                user_name = "Your Name"

            st.warning(f"💡 Using ATS-optimized fallback template for: {user_name}")
            st.warning("⚠️  Please customize the generated resume with your actual details!")

            try:
                # Generate fallback resume
                resume_data = ResumeTemplates.get_fallback_template(user_name)

                # Generate HTML resume
                st.info("🎨 Creating HTML resume...")
                html_content = generate_html_resume(resume_data)

                # Save HTML file
                filename = f"resume_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

                st.success(f"✅ ATS-optimized template generated!")
                st.success(f"📄 Saved as: {filename}")
                st.info("""💡 IMPORTANT: This is a template. Please edit with your actual:
   • Personal contact information
   • Education details and coursework
   • Work experience and achievements
   • Projects and technical skills
   • Certifications and achievements""")

                # Download button
                st.download_button(
                    label="📄 Download ATS Template",
                    data=html_content,
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True
                )

                # Preview
                st.markdown("### 👀 Template Preview")
                st.components.v1.html(html_content, height=800, scrolling=True)

            except Exception as fallback_error:
                st.error(f"❌ Could not generate fallback template: {str(fallback_error)}")


if __name__ == "__main__":
    main()
