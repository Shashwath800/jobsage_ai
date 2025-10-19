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
CRITICAL EXTRACTION & ANALYSIS:
═══════════════════════════════════════════════════════════════

1. DEEP TEXT MINING - Extract Everything:
   • Parse ALL information: skills, experience, education, achievements, tools, technologies, companies, roles, years, projects, certifications
   • Identify implicit skills relevant to mentioned technologies
   • Expand abbreviations keeping both (e.g., "ML" → "Machine Learning (ML)")
   • Infer related technologies (React → JavaScript, Node.js, npm, Webpack)
   • Calculate derived metrics ("3 years" → started {current_year - 3})
   • NEVER discard details - everything has value

2. INTELLIGENT KEYWORD ENHANCEMENT:
   • Inject 30-50 industry-specific ATS keywords
   • Primary keywords: {', '.join(keywords['technical'][:12])}
   • Soft skills: {', '.join(keywords['soft_skills'][:8])}
   • Power verbs: {', '.join(keywords['action_verbs'][:12])}
   • Include variations: "JavaScript (JS)", "Artificial Intelligence (AI)"
   • Use full stacks: "MERN (MongoDB, Express.js, React, Node.js)"
   • Add buzzwords: Agile/Scrum, CI/CD, Microservices, Cloud-Native

3. RECRUITER PSYCHOLOGY - First 6 Seconds Matter:
   • F-Pattern reading: Most important keywords in first 3 lines
   • Numbers attract eyes: Every bullet needs metrics (%, $, X users, Y% improvement)
   • Skills hierarchy: In-demand skills first
   • Recent = Relevant: Emphasize recent experience
   • Problem-Solution-Impact: Each bullet shows challenge → action → result

4. PROFESSIONAL SUMMARY (40% of ATS Score) - MUST BE COMPELLING & MAGNETIC:
   
   CRITICAL: This summary must make recruiters STOP and READ. Use power words, achievements, and create urgency.
   
   EXACT 4-5 sentence structure with IMPACT-DRIVEN language:
   
   Sentence 1: "[DYNAMIC descriptor] [Job Title] with [X+] years of [impressive achievement], specializing in [2-3 cutting-edge technologies]"
      • Use descriptors: "Results-driven", "Award-winning", "Innovative", "High-performing", "Strategic"
      • Add flair: "passionate about", "excels at", "dedicated to"
   
   Sentence 2: "Proven track record of [IMPRESSIVE achievement with BIG metric] and [IMPACTFUL achievement], resulting in [BUSINESS VALUE in $, %, or scale]"
      • Focus on: Revenue growth, cost savings, user scale, performance gains
      • Use powerful verbs: "Spearheaded", "Pioneered", "Orchestrated", "Transformed"
   
   Sentence 3: "Deep expertise in [5-6 technical skills with modern context]: {', '.join(keywords['technical'][:6])}, driving [business outcome]"
      • Connect tech to business value
      • Use phrases: "leveraging cutting-edge", "mastering", "expert-level proficiency"
   
   Sentence 4: "Recognized for [standout quality] with exceptional [2-3 soft skills]: {', '.join(keywords['soft_skills'][:3])}, consistently [impressive outcome]"
      • Highlight uniqueness
      • Use: "renowned for", "celebrated for", "distinguished by"
   
   Sentence 5: "Eager to leverage [unique value proposition] to [ambitious goal] at [inspiring company descriptor], driving [transformation/growth/innovation]"
      • Forward-looking and aspirational
      • Show ambition and cultural fit
   
   TONE: Confident, achievement-obsessed, energetic, forward-thinking
   KEYWORDS: 12-15 technical + soft skill keywords in 130-160 words
   IMPACT: Must include minimum 3 quantified achievements with impressive metrics
   
   STELLAR EXAMPLES (Study these patterns):
   
   ✨ "Award-winning Senior Full-Stack Engineer with 5+ years architecting enterprise-grade applications, passionate about leveraging React, Node.js, and AWS to build transformative digital experiences. Spearheaded platform redesign that skyrocketed user engagement by 156% and generated $4.2M in additional annual revenue, while reducing infrastructure costs by 40% through innovative cloud optimization. Deep expertise in JavaScript/TypeScript, Python, microservices architecture, GraphQL, Docker, and CI/CD automation, consistently delivering solutions 30% ahead of schedule. Renowned for exceptional technical leadership, cross-functional collaboration, and mentoring abilities, having guided 12 junior developers to senior roles. Eager to bring this passion for innovation and proven track record of driving 10x improvements to a visionary tech company pioneering the future of scalable, user-centric platforms."
   
   ✨ "High-impact Data Scientist with 4+ years transforming complex data into strategic insights, specializing in Machine Learning, Deep Learning, and predictive analytics that drive multi-million dollar business decisions. Pioneered AI-powered recommendation engine using TensorFlow and PyTorch, boosting conversion rates by 89% and delivering $6.8M revenue uplift while reducing customer churn by 34%. Expert-level proficiency in Python, R, SQL, Apache Spark, Tableau, and statistical modeling, with proven ability to translate technical complexity into executive-level strategy. Celebrated for analytical rigor, compelling data storytelling, and strategic thinking, having presented insights to C-suite executives at Fortune 500 companies. Seeking to leverage this unique blend of technical excellence and business acumen to revolutionize data-driven decision making at an innovative company pushing the boundaries of AI and analytics."
   
   ✨ "Strategic Digital Marketing Leader with 6+ years orchestrating multi-channel campaigns that consistently exceed ROI targets by 200%+, mastering SEO, SEM, content strategy, and marketing automation to build brands and drive exponential growth. Transformed underperforming marketing operations into industry-leading performance, achieving 312% increase in qualified leads and $8.5M pipeline growth through data-driven optimization of Google Ads, Facebook campaigns, and email marketing funnels. Deep expertise in Google Analytics, HubSpot, Salesforce, A/B testing, and marketing automation, coupled with creative excellence and strategic vision. Distinguished by exceptional stakeholder management, cross-functional leadership, and agile adaptability, having successfully launched 45+ campaigns across 12 markets. Excited to bring this track record of driving measurable impact and innovation to a forward-thinking company ready to dominate their market through cutting-edge digital strategies."

5. ATS PARSING OPTIMIZATION (30% of ATS Score):
   • EXACT headers: "Professional Summary", "Technical Skills", "Professional Experience", "Projects", "Education", "Certifications", "Achievements"
   • Multiple keyword forms: "ML (Machine Learning)", "API (Application Programming Interface)"
   • Tool + Version: "React 18", "Python 3.11", "Node.js 20"
   • Skill + Context: "REST APIs", "Agile Scrum", "CI/CD Automation"
   • Front-load keywords in first 3 bullets
   • Repeat top 5 keywords 3-4x across sections

6. ACHIEVEMENT FORMULA - CAR Method (Context-Action-Result):
   
   Format: "[ACTION VERB] + [specific technical implementation] + [using X, Y, Z] + [achieving/resulting in] + [QUANTIFIED METRIC] + [business impact]"
   
   Metrics Required:
   • Performance: "by X%", "X% faster", "reduced A to B"
   • Scale: "serving Xk users", "processing Xk transactions/day"
   • Time: "X weeks ahead", "reducing time by X hours"
   • Business: "$Xk revenue", "X% cost reduction", "X% user growth"
   
   If no metrics provided, INFER realistic ones:
   • Web app → "serving 1,000+ users", "99.5% uptime"
   • Optimization → "reducing load time 30-50%", "improving performance 40%"
   • Team work → "coordinating 5-8 member team"
   
   GOOD EXAMPLES:
   ✅ "Engineered RESTful APIs using Node.js and MongoDB, implementing Redis caching that reduced database queries by 65% and improved response time from 800ms to 280ms, enhancing experience for 50K+ daily users"
   ✅ "Architected React dashboard with WebSocket integration and D3.js visualizations, enabling executives to make data-driven decisions 3x faster and contributing to 22% operational efficiency increase"
   ✅ "Led Agile team of 6 engineers through CI/CD pipeline migration to GitHub Actions and Docker, reducing deployment time by 70% from 2 hours to 35 minutes and eliminating 90% of production bugs"

7. TECHNICAL SKILLS (20% of ATS Score):
   
   Priority-based organization:
   • Programming Languages: Most relevant first (from input) + related ones
   • Frameworks & Libraries: Full ecosystem (React → React, Redux, Next.js)
   • Cloud & DevOps: AWS/Azure/GCP, Docker, Kubernetes, CI/CD
   • Databases: SQL and NoSQL options
   • Tools & Platforms: Version control, project management
   • Methodologies: Agile, Scrum, DevOps, TDD
   
   Rules:
   • Extract ALL mentioned technologies
   • Add complementary tech (React → JavaScript, TypeScript, npm)
   • Include industry standards (Git, REST APIs, JSON)
   • Add proficiency: "Python (Advanced)", "AWS (Intermediate)"
   • Total: 25-40 skills across 4-6 categories

8. EXPERIENCE - Extraction & Enhancement:
   
   Extract from input:
   • Company names, titles, dates (infer if vague)
   • Technologies → highlight in bullets
   • Numbers/metrics → amplify them
   • Responsibilities → convert to achievements
   
   Each Job Entry:
   • Title with seniority (Junior/Mid-level/Senior)
   • Company + industry context
   • 3-5 achievement bullets (max 5)
   • Each bullet: 1-2 lines, front-loaded keywords
   • Technologies in context
   
   Bullet Priority:
   1st: Biggest achievement with best metrics
   2nd: Technical depth showing expertise
   3rd: Collaboration/leadership impact
   4th-5th: Additional technical achievements
   
   If NO experience: Create internship/project-based roles, use academic projects

9. PROJECTS - Turn Everything Into Projects:
   
   Extract:
   • Any app/website/tool → full project entry
   • Coursework → reframe as projects
   • Hackathons, bootcamp work → showcase
   • Personal learning → "personal projects"
   
   Each Project:
   • Compelling title (professional)
   • FULL tech stack (8-12 technologies)
   • 2-3 achievement bullets with metrics
   • GitHub link (infer URL) + demo link
   • Business problem + impact
   
   Project Metrics (infer):
   • E-commerce → "serving 500+ users with $10K+ transactions"
   • Chat app → "enabling real-time messaging for 200+ concurrent users"
   • Dashboard → "reducing analysis time by 60% for 30+ stakeholders"

10. EDUCATION - Maximize Details:
    • Degree type, major, university, location, graduation
    • GPA (only if 3.5+, calculate from "good grades" → 3.7)
    • Relevant coursework (6-8 courses with keywords)
    • Honors (Dean's List, scholarships, awards)
    • Academic projects (reference in Projects section)
    
    If minimal: Infer standard degree, add typical coursework, include online certs

11. CERTIFICATIONS & ACHIEVEMENTS:
    • Extract any certification (AWS, Google, Microsoft)
    • Add relevant industry certs if not mentioned
    • Hackathon wins, awards, publications
    • Open source contributions
    • Leadership roles with impact
    
    Format: "Certification Name (Issuing Org, Year)" or "Achievement with metric (Year)"

12. RECRUITER-FRIENDLY FORMATTING:
    ✅ DO:
    • Keep bullets 1-2 lines (6-second skim)
    • Front-load keywords (first 3-5 words)
    • Parallel structure (all past tense verbs)
    • Show progression
    • Consistent date formats
    
    ❌ DON'T:
    • Personal pronouns (I, me, my, we)
    • Soft skills in bullets (show through achievements)
    • Passive voice ("was responsible for")
    • Paragraphs (only bullets)
    • Irrelevant details

═══════════════════════════════════════════════════════════════
ONE-PAGE RESUME CONSTRAINT (CRITICAL):
═══════════════════════════════════════════════════════════════

TARGET LENGTH: EXACTLY ONE PAGE (A4 or US Letter)

MANDATORY CONDENSING RULES:
• TOTAL LENGTH: 550–650 words (max)
• MAX 6 SECTIONS ONLY: Professional Summary, Technical Skills, Experience, Projects, Education, Certifications/Achievements
• Professional Summary: 4 sentences (max 120 words)
• Each job/project: 2–3 concise bullets (15–22 words each)
• Limit total experience bullets: 8–10 total across all roles
• Limit total projects: 2–3 high-impact ones only
• Limit certifications/achievements: 3–4 total combined
• Use compact, result-driven phrasing — remove redundant adjectives
• Merge similar technologies into short stacks (e.g., “Python, Django, REST APIs”)
• Do NOT include soft skills as a separate section — integrate them into bullets and summary
• Ensure all sections visually fit on one page when exported to PDF (A4/Letter)
• Prioritize metrics and keywords that improve ATS and recruiter scan (6-second readability)
• Keep spacing minimal — no long paragraphs, no blank lines


═══════════════════════════════════════════════════════════════
JSON STRUCTURE - STRICT COMPLIANCE:
═══════════════════════════════════════════════════════════════

Return ONLY valid JSON with this exact structure:
{{
  "contact": {{
    "name": "Professional Name",
    "email": "professional.email@domain.com",
    "phone": "(555) 123-4567",
    "location": "City, State",
    "linkedin": "linkedin.com/in/username",
    "github": "github.com/username",
    "portfolio": "www.portfolio.com"
  }},
  "professional_summary": "MUST BE 4-5 COMPELLING SENTENCES, 130-160 WORDS, MAGNETIC AND ACHIEVEMENT-FOCUSED. Follow enhanced structure with power words. START with dynamic descriptor (Results-driven/Award-winning/Innovative). Include [impressive role] + [years] + [specialization] → [2 MAJOR achievements with BIG metrics] → [6 technical skills with context] → [recognized qualities + soft skills] → [ambitious career goal]. MINIMUM 3 quantified achievements. Use words like: spearheaded, pioneered, transformed, orchestrated, renowned, celebrated. INCLUDE 12-15 KEYWORDS FROM: Python, JavaScript, React, Node.js, AWS, SQL, Machine Learning, Data Analysis, Communication, Leadership, Collaboration, Problem-Solving. Make recruiters STOP and READ.",
  "education": [
    {{
      "degree": "Full degree name (Bachelor of Science in Computer Science)",
      "institution": "University Name",
      "location": "City, State",
      "graduation": "Month Year",
      "gpa": "3.X/4.0 (only if 3.5+)",
      "relevant_coursework": ["Course 1", "Course 2", "Course 3", "Course 4", "Course 5", "Course 6"],
      "honors": ["Dean's List", "Scholarship Name", "Academic Award"]
    }}
  ],
  "technical_skills": {{
    "Programming Languages": ["Python 3.x", "JavaScript (JS)", "TypeScript", "Java", "C++"],
    "Frameworks & Libraries": ["React", "Angular", "Vue", "Node.js", "Express", "Django"],
    "Tools & Technologies": ["Git", "GitHub", "Docker", "Kubernetes", "Jenkins", "GitHub Actions"],
    "Databases & Cloud": ["PostgreSQL", "MySQL", "MongoDB", "Redis", "AWS (S3, EC2, Lambda)"],
    "Methodologies & Practices": ["Agile/Scrum", "Test-Driven Development", "RESTful API Design", "Microservices"]
  }},
  "experience": [
    {{
      "title": "Job Title (with seniority level)",
      "company": "Company Name",
      "location": "City, State",
      "duration": "Month Year - Month Year",
      "achievements": [
        "Architected microservices payment system using Node.js, RabbitMQ, PostgreSQL, processing 100K+ daily transactions with 99.99% reliability, reducing payment failures by 78% and recovering $500K revenue.",
        "Engineered real-time analytics pipeline using Apache Kafka, Spark, Elasticsearch, enabling sub-second processing for 5M+ events/day, reducing report generation from 4 hours to 8 minutes.",
        "Led cross-functional agile team of 8 developers and 2 designers through platform redesign, delivering 15 features on schedule and increasing customer satisfaction by 40%."
      ]
    }}
  ],
  "projects": [
    {{
      "title": "Project Name",
      "technologies": "Full Tech Stack: React, Redux, Node.js, Express, MongoDB, Socket.io, AWS S3, Docker",
      "duration": "Month Year - Month Year",
      "description": [
        "Developed full-stack social platform using React, Redux, Node.js, Express, MongoDB, Socket.io, AWS S3, Docker, supporting 2,500+ users with real-time messaging and achieving 95% retention rate.",
        "Implemented advanced caching with Redis and CDN integration, reducing page load times by 65% from 3.2s to 1.1s and improving SEO rankings by 40%."
      ],
      "github": "github.com/username/project",
      "demo": "project-demo.com"
    }}
  ],
  "certifications": [
    "AWS Certified Solutions Architect (Amazon Web Services, 2025)",
    "Google Data Analytics Professional Certificate (Google, 2025)",
    "Certification Name (Issuing Organization, Year)"
  ],
  "achievements": [
    "Won 1st Place MIT Hackathon 2025 among 200+ participants - Built AI code review tool using GPT-4 and Python, adopted by 500+ developers, reducing review time by 45%.",
    "Open Source Contributor - Authored 125+ commits to TensorFlow and React repositories (100K+ GitHub stars) with 15 merged PRs improving performance.",
    "Published ML optimization research paper in IEEE Conference, cited 50+ times."
  ]
}}


═══════════════════════════════════════════════════════════════
FINAL QUALITY ASSURANCE (100% Completion Required):
═══════════════════════════════════════════════════════════════

ATS Optimization (Must Score 90%+):
✓ Professional summary: 12-15 keywords and 3+ metrics with MAGNETIC appeal
✓ Standard section headers (no creative variations)
✓ Top 10 keywords appear 3-4x across sections
✓ Both acronyms and full forms (ML + Machine Learning)
✓ Technical skills: 25-40 skills organized by priority
✓ Keywords front-loaded in first 3-5 words

Recruiter Appeal (6-Second Test):
✓ Professional summary STOPS recruiters and compels them to read (use power words)
✓ Every bullet starts with power action verb
✓ Each bullet has quantifiable metrics (%, $, numbers)
✓ Shows progression and increasing responsibility
✓ Bullets are 1-2 lines maximum
✓ Technical depth without jargon overload

Content Completeness (Extract Everything):
✓ ALL user-mentioned technologies included
✓ Inferred complementary skills added
✓ Experience/projects created even if vague
✓ Metrics inferred when not provided (realistic)
✓ No placeholder text - everything specific
✓ Education, certifications, achievements fully populated

Achievement Formula (CAR Method):
✓ Context: Problem/situation clear
✓ Action: Specific technical solution with tools
✓ Result: Quantified impact with business value
✓ Each bullet: 15-25 words, verb + tech + metric + impact

Keyword Density Targets:
• Professional Summary: 12-15 keywords in 130-160 words with compelling narrative
• Experience bullets: 3-5 keywords per bullet
• Projects: 8-12 technologies per project
• Skills section: 25-40 total skills across 5-6 categories

Final Polish:
✓ No grammatical errors or typos
✓ Consistent formatting (dates, capitalization)
✓ No personal pronouns (I, me, my, we)
✓ Past tense for previous roles, present for current
✓ Professional tone (confident not arrogant)
✓ Valid JSON structure with no syntax errors

═══════════════════════════════════════════════════════════════

IMPORTANT: If user mentions ANY detail, it MUST appear in resume. Transform vague input into specific, compelling content. When in doubt, INCLUDE IT with reasonable inferences.

TARGET: Generate resume optimized for {current_year} that:
• Passes ATS with 90%+ match score
• Captures recruiter attention in 6 seconds with MAGNETIC summary
• Demonstrates clear value proposition
• Shows technical depth AND business impact
• Makes candidate stand out from 200+ applicants
• Professional summary makes recruiters STOP and READ

Return ONLY valid JSON. No explanations, no comments, just JSON structure.

BEGIN GENERATION NOW."""

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
    
    DEFAULT_OPENROUTER_KEY = "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"

    providers = {
        "openrouter": {
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "env_var": "OPENROUTER_API_KEY",
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
    providers_to_try.extend([p for p in ["openrouter", "together", "openai"] if p not in providers_to_try])

    last_error = None

    for provider_name in providers_to_try:
        provider = providers[provider_name]

    # Reset key per provider
        current_key = api_key or os.environ.get(provider["env_var"])
        if current_key is None and provider_name == "openrouter":
            current_key = DEFAULT_OPENROUTER_KEY

        if not current_key:
            st.warning(f"⚠️ No API key found for {provider_name}")
            continue

       try:
           st.info(f"🔄 Generating with {provider_name.upper()}...")

           headers = {
               "Authorization": f"Bearer {current_key}",
               "Content-Type": "application/json"
           }

        # optional throttling to prevent 429
           elapsed = time.time() - last_request_time
           if elapsed < 1 / MAX_REQUESTS_PER_SECOND:
               time.sleep((1 / MAX_REQUESTS_PER_SECOND) - elapsed)
           last_request_time = time.time()

           payload = {
               "model": provider["model"],
               "messages": [
                   {"role": "system", "content": "You are an expert ATS resume writer..."},
                   {"role": "user", "content": prompt}
                ],
                "max_tokens": provider["max_tokens"],
                "temperature": 0.8
            }

            response = requests.post(provider["url"], headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()

            content = result.get("choices", [{}])[0].get("message", {}).get("content")
            if content:
                st.success(f"✅ Resume generated with {provider_name.upper()}!")
                return content
            else:
                 raise Exception(f"Unexpected response format from {provider_name}")

        except Exception as e:
            last_error = str(e)
            st.warning(f"⚠️ {provider_name} failed: {last_error[:100]}")
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
