import streamlit as st
import json
import re
from datetime import datetime
import requests
import os

# Page config
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
# CONFIGURATION & TEMPLATES (ORIGINAL CODE)
# -----------------------------

class ResumeTemplates:
    @staticmethod
    def get_fallback_template(user_name):
        """Generate a basic template when API fails"""
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
            "professional_summary": "Motivated professional with strong technical skills and passion for innovation. Seeking opportunities to contribute to challenging projects and grow professionally.",
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University Name",
                    "location": "City, State",
                    "graduation": "May 2024",
                    "gpa": "3.7/4.0",
                    "relevant_coursework": ["Data Structures", "Algorithms", "Database Systems",
                                            "Software Engineering"],
                    "honors": ["Dean's List"]
                }
            ],
            "technical_skills": {
                "Programming Languages": ["Python", "JavaScript", "Java", "SQL"],
                "Frameworks & Tools": ["React", "Node.js", "Git", "Docker"],
                "Databases & Cloud": ["PostgreSQL", "MongoDB", "AWS"]
            },
            "experience": [
                {
                    "title": "Software Developer Intern",
                    "company": "Tech Company",
                    "location": "City, State",
                    "duration": "June 2023 - August 2023",
                    "achievements": [
                        "Developed and deployed web applications serving 1000+ users daily",
                        "Collaborated with cross-functional teams to deliver features on schedule"
                    ]
                }
            ],
            "projects": [
                {
                    "title": "Portfolio Website",
                    "technologies": "React, Node.js, MongoDB",
                    "duration": "January 2024 - March 2024",
                    "description": [
                        "Built responsive portfolio website with modern UI/UX design",
                        "Implemented contact form with email integration and analytics tracking"
                    ],
                    "github": f"github.com/{user_name.lower().replace(' ', '')}/portfolio",
                    "demo": "portfolio-demo.com"
                }
            ],
            "certifications": [
                "AWS Certified Cloud Practitioner (2024)"
            ],
            "achievements": [
                "Hackathon Winner - Built innovative solution in 24 hours",
                "Open Source Contributor - 50+ contributions to popular projects"
            ]
        }

    @staticmethod
    def get_enhanced_prompt(user_input):
        current_year = datetime.now().year
        return f"""Create a professional resume in JSON format for: "{user_input}"

Generate realistic content. Keep it concise for one page. Return ONLY valid JSON with this structure:

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
  "professional_summary": "2-3 line compelling summary highlighting key strengths, experience, and career goals",
  "education": [
    {{
      "degree": "Full degree name",
      "institution": "University/College Name",
      "location": "City, State",
      "graduation": "Month Year",
      "gpa": "3.X/4.0 (only if 3.5+)",
      "relevant_coursework": ["Course 1", "Course 2", "Course 3"],
      "honors": ["Dean's List", "Academic Scholarship"]
    }}
  ],
  "technical_skills": {{
    "Programming Languages": ["Language1", "Language2", "Language3"],
    "Frameworks & Tools": ["Framework1", "Tool1", "Tool2"],
    "Databases & Cloud": ["Database1", "AWS/Azure/GCP"]
  }},
  "experience": [
    {{
      "title": "Job Title/Role",
      "company": "Company Name",
      "location": "City, State",
      "duration": "Month Year - Month Year",
      "achievements": [
        "Achievement with quantified impact (max 2 lines)",
        "Technical accomplishment with results (max 2 lines)"
      ]
    }}
  ],
  "projects": [
    {{
      "title": "Project Name",
      "technologies": "Tech Stack",
      "duration": "Month Year - Month Year",
      "description": [
        "Built/Developed [solution] achieving [result] (1-2 lines)",
        "Implemented [feature] improving [metric] by [amount] (1-2 lines)"
      ],
      "github": "github.com/username/project",
      "demo": "demo-url.com"
    }}
  ],
  "certifications": [
    "Certification Name (Organization, Year)"
  ],
  "achievements": [
    "Specific achievement with impact (1 line)"
  ]
}}

Make it professional and ATS-optimized for {current_year}. Keep all content concise (max 2 lines per bullet)."""

    @staticmethod
    def get_industry_defaults(field_keywords):
        """Generate industry-specific defaults based on detected field"""
        defaults = {
            "software_engineering": {
                "skills": {
                    "Programming Languages": ["Python", "JavaScript", "Java", "TypeScript"],
                    "Frameworks & Tools": ["React", "Node.js", "Django", "Git", "Docker"],
                    "Databases & Cloud": ["PostgreSQL", "MongoDB", "AWS", "Redis"]
                },
                "certifications": ["AWS Solutions Architect", "Google Cloud Professional"]
            },
            "data_science": {
                "skills": {
                    "Programming Languages": ["Python", "R", "SQL"],
                    "Frameworks & Tools": ["TensorFlow", "PyTorch", "Pandas", "Jupyter"],
                    "Databases & Cloud": ["PostgreSQL", "BigQuery", "AWS", "Spark"]
                },
                "certifications": ["Google Data Analytics", "AWS Machine Learning"]
            },
            "marketing": {
                "skills": {
                    "Digital Marketing": ["Google Ads", "SEO/SEM", "Content Marketing"],
                    "Analytics Tools": ["Google Analytics", "Tableau", "HubSpot"],
                    "Design & Content": ["Adobe Creative Suite", "Canva", "WordPress"]
                },
                "certifications": ["Google Ads Certified", "HubSpot Content Marketing"]
            }
        }

        field_lower = " ".join(field_keywords).lower()
        if any(word in field_lower for word in ["software", "programming", "developer", "engineer"]):
            return defaults["software_engineering"]
        elif any(word in field_lower for word in ["data", "analytics", "machine learning", "ai"]):
            return defaults["data_science"]
        elif any(word in field_lower for word in ["marketing", "digital", "seo", "social media"]):
            return defaults["marketing"]
        else:
            return defaults["software_engineering"]


# -----------------------------
# API INTEGRATION (ORIGINAL CODE)
# -----------------------------

def call_llm_api(prompt, api_key=None, api_provider="groq"):
    """
    Call various LLM APIs (OpenAI-compatible)

    Supported providers:
    1. Groq (FREE, FAST) - Get key from: https://console.groq.com/
    2. Together AI (FREE tier) - Get key from: https://api.together.xyz/
    3. OpenAI - Get key from: https://platform.openai.com/

    Environment variables:
    - GROQ_API_KEY
    - TOGETHER_API_KEY
    - OPENAI_API_KEY
    """

    # Hardcoded API key (can be overridden by environment variable)
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

    # Try providers in order of preference
    providers_to_try = [api_provider] if api_provider in providers else []
    providers_to_try.extend([p for p in ["groq", "together", "openai"] if p not in providers_to_try])

    last_error = None

    for provider_name in providers_to_try:
        provider = providers[provider_name]

        # Get API key (check environment variable, then use default for Groq)
        if api_key is None:
            api_key = os.environ.get(provider["env_var"])
            if api_key is None and provider_name == "groq":
                api_key = DEFAULT_GROQ_KEY

        if not api_key:
            st.warning(f"⚠️  No API key found for {provider_name} (set {provider['env_var']})")
            continue

        try:
            st.info(f"🔄 Trying {provider_name.upper()}...")

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": provider["model"],
                "messages": [
                    {"role": "system",
                     "content": "You are a professional resume writer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": provider["max_tokens"],
                "temperature": 0.7
            }

            response = requests.post(
                provider["url"],
                headers=headers,
                json=payload,
                timeout=120
            )

            # Better error handling
            if response.status_code != 200:
                error_detail = response.text[:200]
                raise Exception(f"HTTP {response.status_code}: {error_detail}")

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                st.success(f"✅ Successfully generated with {provider_name.upper()}!")
                return content
            else:
                raise Exception(f"Unexpected response format from {provider_name}")

        except Exception as e:
            last_error = str(e)
            st.warning(f"⚠️  {provider_name} failed: {str(e)[:100]}")
            api_key = None  # Reset for next provider
            continue

    raise Exception(
        f"All API providers failed. Last error: {last_error}\n\n"
        "Please set one of these API keys:\n"
        "1. GROQ_API_KEY (FREE, recommended) - https://console.groq.com/\n"
        "2. TOGETHER_API_KEY (FREE tier) - https://api.together.xyz/\n"
        "3. OPENAI_API_KEY - https://platform.openai.com/"
    )


# -----------------------------
# HTML GENERATION (ORIGINAL CODE - A4 OPTIMIZED)
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
# JSON EXTRACTION & PARSING (ORIGINAL CODE)
# -----------------------------

def extract_json_from_response(response_text):
    """Extract and parse JSON from LLM response"""
    try:
        # Try direct JSON parsing first
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON between code blocks
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
# STREAMLIT UI (WRAPPER)
# -----------------------------

def main():
    # Title
    st.markdown("""
        <div class="title-container">
            <h1 class="title-text">🚀 AI Resume Builder</h1>
            <p class="subtitle-text">Create Your Professional Resume in Seconds</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Settings")

        st.markdown("---")
        st.markdown("### 📊 Features")
        st.markdown("""
        - ✨ AI-Powered Generation
        - 📄 ATS-Optimized Format
        - 🎨 Professional Design
        - 💾 Instant Download
        - 🔄 Multiple API Providers
        """)

        st.markdown("---")
        st.markdown("### 💡 Pro Tips")
        st.markdown("""
        - Be specific about your skills
        - Mention years of experience
        - Include relevant keywords
        - State your career goals
        """)

    # Main content
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">⚡</div>
                <div class="stat-label">Fast Generation</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">🎯</div>
                <div class="stat-label">ATS Optimized</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="stat-card">
                <div class="stat-number">💼</div>
                <div class="stat-label">Professional</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Input section
    st.markdown("### 📝 Tell Us About Yourself")
    st.markdown("""
        <div class="info-card">
            <strong>Examples:</strong><br>
            • "CS student with Python skills seeking SWE internship"<br>
            • "Marketing graduate with social media experience"<br>
            • "Data analyst with 2 years experience in healthcare"
        </div>
    """, unsafe_allow_html=True)

    user_input = st.text_area(
        "Enter your brief description (1-2 lines)",
        placeholder="E.g., Computer Science student with Python and machine learning skills seeking a data science internship...",
        height=100,
        key="user_input"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("🚀 Generate My Resume", use_container_width=True)

    # Generation logic (ORIGINAL FUNCTIONALITY)
    if generate_button:
        if not user_input:
            st.error("❌ Please provide a description to generate your resume.")
            return

        st.info(f"🤖 Generating professional resume for: '{user_input}'")
        st.warning("⏳ This may take 30-60 seconds...")

        try:
            # Generate enhanced prompt
            enhanced_prompt = ResumeTemplates.get_enhanced_prompt(user_input)

            # Call LLM API
            with st.spinner("📊 Parsing resume data..."):
                llm_response = call_llm_api(enhanced_prompt)

            # Extract JSON from response
            st.info("📊 Parsing resume data...")
            resume_data = extract_json_from_response(llm_response)

            # Generate HTML resume
            st.info("🎨 Creating HTML resume...")
            html_content = generate_html_resume(resume_data)

            # Save HTML file
            filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

            # Success message
            st.markdown("""
                <div class="success-box">
                    <h2>✅ Resume Generated Successfully!</h2>
                    <p>Your professional resume is ready to download</p>
                </div>
            """, unsafe_allow_html=True)

            st.success(f"📄 Saved as: {filename}")

            # Save JSON backup
            json_filename = filename.replace('.html', '.json')
            st.success(f"💾 Resume data saved as: {json_filename}")

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

            st.info("💡 Use your browser's Print function (Ctrl+P / Cmd+P) to save as PDF")

            # Preview
            st.markdown("### 👀 Preview")
            st.components.v1.html(html_content, height=800, scrolling=True)

        except Exception as e:
            st.error(f"❌ Error generating resume: {str(e)}")

            # Try to extract name for fallback
            name_match = re.search(r'name is ([A-Za-z\s]+)', user_input, re.IGNORECASE)
            if name_match:
                user_name = name_match.group(1).strip()
            else:
                user_name = "Your Name"

            st.warning(f"💡 Using fallback template for: {user_name}")
            st.warning("⚠️  Please customize the generated resume with your actual details!")

            try:
                # Generate fallback resume
                resume_data = ResumeTemplates.get_fallback_template(user_name)

                # Generate HTML resume
                st.info("🎨 Creating HTML resume...")
                html_content = generate_html_resume(resume_data)

                # Save HTML file
                filename = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

                st.success(f"✅ Basic resume template generated!")
                st.success(f"📄 Saved as: {filename}")
                st.info("""💡 IMPORTANT: This is a template. Please edit with your actual:
   • Education details
   • Work experience
   • Skills and projects
   • Contact information""")

                # Download button
                st.download_button(
                    label="📄 Download Template",
                    data=html_content,
                    file_name=filename,
                    mime="text/html",
                    use_container_width=True
                )

                # Preview
                st.markdown("### 👀 Preview")
                st.components.v1.html(html_content, height=800, scrolling=True)

            except Exception as fallback_error:
                st.error(f"❌ Could not generate fallback template: {str(fallback_error)}")


if __name__ == "__main__":
    main()
