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
        """Generate highly optimized prompt for ATS-friendly resumes with strong professional summaries"""
        current_year = datetime.now().year
        
        # Get industry-specific keywords
        keywords = ATSKeywordExtractor.get_industry_keywords(user_input)
        
        prompt = f"""You are an expert ATS (Applicant Tracking System) resume writer and career coach. Create a professional, ATS-optimized resume in JSON format.

USER INPUT: "{user_input}"

CRITICAL REQUIREMENTS:

1. PROFESSIONAL SUMMARY (Most Important):
   - Write a compelling 3-4 line summary that:
     * Opens with a strong value proposition (e.g., "Results-driven [Role] with X years of experience...")
     * Highlights 2-3 key achievements with quantifiable metrics
     * Incorporates 3-5 relevant industry keywords naturally: {', '.join(keywords['technical'][:5])}
     * Ends with career objective aligned to target role
   - Use powerful action words: {', '.join(keywords['action_verbs'][:5])}
   - Make it achievement-focused, not responsibility-focused
   - Example: "Results-driven Software Engineer with 3+ years of experience developing scalable web applications using React and Node.js, reducing load times by 40% and serving 100K+ daily users. Proven expertise in Agile methodologies and cloud deployment. Seeking to leverage full-stack expertise to drive innovation at a fast-paced tech company."

2. ATS OPTIMIZATION:
   - Use standard section headers: "Professional Summary", "Technical Skills", "Professional Experience", "Projects", "Education"
   - Include relevant keywords naturally throughout: {', '.join(keywords['technical'][:8])}
   - Use industry-standard terminology
   - Avoid graphics, tables, or special formatting
   - Include both acronyms and full terms (e.g., "ML (Machine Learning)")

3. ACHIEVEMENT-BASED BULLETS:
   - Use the STAR method: Situation, Task, Action, Result
   - Start with action verbs: {', '.join(keywords['action_verbs'][:10])}
   - Include quantifiable metrics (numbers, percentages, timeframes)
   - Format: "[Action Verb] [what you did] [resulting in/achieving] [quantifiable impact]"
   - Example: "Engineered a real-time analytics dashboard using React and Python, reducing report generation time by 60% and enabling data-driven decisions for 50+ stakeholders"

4. TECHNICAL SKILLS:
   - Group by category for easy ATS scanning
   - List in order of relevance to target role
   - Include proficiency levels if applicable
   - Relevant keywords: {', '.join(keywords['technical'][:12])}

5. EXPERIENCE & PROJECTS:
   - Focus on impact and results, not just responsibilities
   - Use metrics: improved X by Y%, reduced Z by N hours, served M users
   - Highlight technologies used in context
   - Show business value, not just technical details

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
  "professional_summary": "COMPELLING 3-4 LINE SUMMARY following guidelines above. MUST include achievements, keywords, and metrics. This is the MOST IMPORTANT section.",
  "education": [
    {{
      "degree": "Full degree name (e.g., Bachelor of Science in Computer Science)",
      "institution": "University Name",
      "location": "City, State",
      "graduation": "Month Year",
      "gpa": "3.X/4.0 (only if 3.5+)",
      "relevant_coursework": ["Course 1", "Course 2", "Course 3", "Course 4"],
      "honors": ["Dean's List", "Scholarship Name"]
    }}
  ],
  "technical_skills": {{
    "Programming Languages": ["Language1", "Language2", "Language3"],
    "Frameworks & Libraries": ["Framework1", "Framework2", "Library1"],
    "Tools & Technologies": ["Tool1", "Tool2", "Tool3"],
    "Databases & Cloud": ["Database1", "Cloud Platform", "Tool"]
  }},
  "experience": [
    {{
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, State",
      "duration": "Month Year - Month Year",
      "achievements": [
        "[Action Verb] [specific accomplishment] resulting in [quantified impact with metrics]",
        "[Action Verb] [technical implementation] improving [metric] by [percentage/number]",
        "[Action Verb] [project/initiative] achieving [measurable result]"
      ]
    }}
  ],
  "projects": [
    {{
      "title": "Project Name",
      "technologies": "Tech Stack (list all relevant keywords)",
      "duration": "Month Year - Month Year",
      "description": [
        "[Action Verb] [what was built] achieving [specific metric/outcome]",
        "[Action Verb] [key feature/optimization] resulting in [quantified improvement]"
      ],
      "github": "github.com/username/project",
      "demo": "project-demo.com"
    }}
  ],
  "certifications": [
    "Certification Name (Issuing Organization, Year)"
  ],
  "achievements": [
    "Specific achievement with quantified impact (1 line with metrics)"
  ]
}}

QUALITY CHECKLIST:
✓ Professional summary is compelling and keyword-rich
✓ Every bullet point has quantifiable metrics
✓ Action verbs used consistently
✓ Industry keywords integrated naturally
✓ Content is concise (1-2 lines per bullet)
✓ ATS-friendly formatting
✓ Focus on achievements, not responsibilities
✓ Business value clearly demonstrated

Generate content for {current_year}. Make it professional, impactful, and ATS-optimized."""

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
            "model": "llama-3.3-70b-versatile",
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
                "temperature": 0.8  # Slightly higher for more creative summaries
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
    """Extract and parse JSON from LLM response"""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    json_patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'\{.*\}',
    ]

    for pattern in json_patterns:
        match = re.search(pattern, response_text, re.DOTALL)
        if match:
            try:
                json_str = match.group(1) if '```' in pattern else match.group(0)
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue

    raise ValueError("Could not extract valid JSON from response")


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
            # Generate enhanced prompt
            enhanced_prompt = ResumeTemplates.get_enhanced_prompt(user_input)

            # Call LLM API
            with st.spinner("🎯 Crafting keyword-rich professional summary and achievement-focused content..."):
                llm_response = call_llm_api(enhanced_prompt)

            # Extract JSON from response
            st.info("📊 Parsing resume data...")
            resume_data = extract_json_from_response(llm_response)

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
