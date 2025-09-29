import ollama
import json
import re
from datetime import datetime
import webbrowser
import os


# -----------------------------
# CONFIGURATION & TEMPLATES
# -----------------------------

class ResumeTemplates:
    @staticmethod
    def get_enhanced_prompt(user_input):
        current_year = datetime.now().year
        return f"""
You are an expert resume writer and career counselor. Create a comprehensive, ATS-optimized, professional resume from this brief input: "{user_input}"

CRITICAL INSTRUCTIONS:
1. Infer the person's career level, field, and goals from the input
2. Generate realistic, quantified achievements using industry standards
3. Create 2-3 substantial projects with measurable impacts (CONCISE - max 2 bullet points each)
4. Add relevant experience (1-2 entries, max 2-3 bullets each)
5. Include industry-appropriate technical skills and certifications
6. Write compelling, action-oriented descriptions using power verbs
7. Make everything hire-worthy and impressive but realistic
8. KEEP ALL CONTENT CONCISE - must fit on ONE A4 PAGE

CONTENT LIMITS (STRICT):
- Professional Summary: 2-3 lines maximum
- Each bullet point: 1-2 lines maximum
- Projects: 2-3 maximum with 2 bullets each
- Experience: 1-2 entries with 2-3 bullets each
- Skills: Group into 3-4 categories maximum
- Certifications: 2-3 maximum
- Achievements: 2-3 maximum

RETURN ONLY VALID JSON with this EXACT structure:

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

Generate concise, impressive content that MUST fit on ONE A4 PAGE. Use industry-specific terminology for {current_year}.
"""

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
            for achievement in exp.get('achievements', [])[:3]:  # Limit to 3 bullets
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
        for project in resume_data['projects'][:3]:  # Limit to 3 projects
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

            for desc in project.get('description', [])[:2]:  # Limit to 2 bullets per project
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
        for cert in resume_data['certifications'][:3]:  # Limit to 3
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
        for achievement in resume_data['achievements'][:3]:  # Limit to 3
            html_content += f"""            <div class="bullet">• {achievement}</div>\n"""

        html_content += """        </div>
    </div>
"""

    html_content += """
</body>
</html>"""

    return html_content


# -----------------------------
# MAIN RESUME GENERATOR
# -----------------------------

def generate_comprehensive_resume():
    print("🎯 AI-Powered Professional Resume Generator (A4 Optimized)")
    print("=" * 50)
    print("Simply enter 1-2 lines about yourself and get a complete professional resume!")
    print("Examples:")
    print("  • 'CS student with Python skills seeking SWE internship'")
    print("  • 'Marketing graduate with social media experience'")
    print("  • 'Data analyst with 2 years experience in healthcare'")
    print("=" * 50)

    user_input = input("\n📝 Enter your brief description (1-2 lines): ").strip()

    if not user_input:
        print("❌ Please provide a description to generate your resume.")
        return

    print(f"\n🤖 Generating professional resume for: '{user_input}'")
    print("⏳ This may take 30-60 seconds...")

    enhanced_prompt = ResumeTemplates.get_enhanced_prompt(user_input)

    try:
        response = ollama.chat(
            model="gpt-oss:20b-cloud",
            messages=[{"role": "user", "content": enhanced_prompt}]
        )
        raw_output = response["message"]["content"].strip()

        resume_data = extract_and_validate_json(raw_output, user_input)

    except Exception as e:
        print(f"⚠️  AI generation failed: {e}")
        print("📋 Generating resume with intelligent defaults...")
        resume_data = generate_fallback_resume(user_input)

    # Generate HTML resume
    html_content = generate_html_resume(resume_data)

    html_filename = f"Professional_Resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    html_filepath = os.path.abspath(html_filename)

    with open(html_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ Professional A4 Resume Generated: {html_filename}")
    print("📄 Opening resume in your default browser...")

    # Automatically open the HTML file in the default browser
    try:
        # Use webbrowser.open with the file path directly (works cross-platform)
        webbrowser.open(html_filepath)
        print("🌐 Resume opened successfully!")
    except Exception as e:
        print(f"⚠️  Could not auto-open browser: {e}")
        print(f"📂 Please manually open: {html_filepath}")

    print("\n💡 Tips:")
    print("   • Use browser's Print → Save as PDF to create a PDF version")
    print("   • Ensure 'Background graphics' is enabled for best appearance")
    print("   • The resume is optimized for A4 size (210mm × 297mm)")
    print("\n🎉 Resume generation complete!")


def extract_and_validate_json(raw_output, user_input):
    """Enhanced JSON extraction"""

    def try_parse_json(text):
        try:
            return json.loads(text)
        except:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                json_str = text[start:end + 1]
                json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                return json.loads(json_str)
            except:
                pass

        return None

    parsed_data = try_parse_json(raw_output)

    if parsed_data:
        print("✅ Successfully parsed AI-generated content")
        return parsed_data
    else:
        print("⚠️  JSON parsing failed, generating intelligent fallback...")
        return generate_fallback_resume(user_input)


def generate_fallback_resume(user_input):
    """Generate intelligent fallback resume with A4-optimized content"""
    input_lower = user_input.lower()
    words = user_input.split()
    name = words[0].title() if words and words[0].isalpha() else "Alex Johnson"

    field_keywords = []
    if any(word in input_lower for word in
           ["cs", "computer science", "software", "programming", "developer", "engineer"]):
        field_keywords = ["software engineering"]
    elif any(word in input_lower for word in ["data", "analytics", "machine learning", "ai"]):
        field_keywords = ["data science"]
    elif any(word in input_lower for word in ["marketing", "digital", "social media"]):
        field_keywords = ["marketing"]
    else:
        field_keywords = ["technology"]

    industry_defaults = ResumeTemplates.get_industry_defaults(field_keywords)
    current_year = datetime.now().year

    return {
        "contact": {
            "name": name,
            "email": f"{name.lower().replace(' ', '.')}@email.com",
            "phone": "(555) 123-4567",
            "location": "City, State",
            "linkedin": f"linkedin.com/in/{name.lower().replace(' ', '')}",
            "github": f"github.com/{name.lower().replace(' ', '')}",
            "portfolio": f"www.{name.lower().replace(' ', '')}.dev"
        },
        "professional_summary": f"Results-driven {field_keywords[0]} professional with strong analytical and technical skills. Proven ability to develop innovative solutions and deliver high-quality results in fast-paced environments.",
        "education": [{
            "degree": f"Bachelor of Science in {field_keywords[0].title()}",
            "institution": "State University",
            "location": "City, State",
            "graduation": f"May {current_year}",
            "gpa": "3.7/4.0",
            "relevant_coursework": ["Data Structures", "Algorithms", "Database Systems"],
            "honors": ["Dean's List", "Academic Excellence Award"]
        }],
        "technical_skills": industry_defaults["skills"],
        "experience": [{
            "title": "Software Engineering Intern",
            "company": "Tech Solutions Inc.",
            "location": "Remote",
            "duration": f"Jun {current_year - 1} - Aug {current_year - 1}",
            "achievements": [
                "Developed RESTful APIs using Python and Flask, serving 1000+ daily requests with 99.9% uptime",
                "Implemented automated testing suite reducing bug detection time by 40% and deployment cycle by 25%"
            ]
        }],
        "projects": [
            {
                "title": "E-Commerce Analytics Platform",
                "technologies": "Python, Django, React, PostgreSQL, AWS",
                "duration": f"Mar {current_year} - Jul {current_year}",
                "description": [
                    "Built full-stack platform processing 10,000+ transactions daily with real-time analytics dashboard",
                    "Optimized database queries and caching, reducing page load time by 60% and improving UX"
                ],
                "github": "github.com/username/ecommerce-analytics"
            },
            {
                "title": "AI-Powered Chatbot",
                "technologies": "Python, TensorFlow, Flask, MongoDB",
                "duration": f"Jan {current_year} - Mar {current_year}",
                "description": [
                    "Developed NLP chatbot achieving 92% intent recognition accuracy using transformer models",
                    "Deployed scalable API handling 500+ concurrent users with 200ms average response time"
                ],
                "github": "github.com/username/ai-chatbot"
            }
        ],
        "certifications": industry_defaults["certifications"][:2],
        "achievements": [
            f"Winner, University Hackathon - Best Technical Innovation ({current_year})",
            "Dean's List for 3 consecutive semesters"
        ]
    }


# -----------------------------
# MAIN EXECUTION
# -----------------------------

if __name__ == "__main__":
    try:
        generate_comprehensive_resume()
    except KeyboardInterrupt:
        print("\n❌ Resume generation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

    print("\n🚀 Thank you for using AI-Powered Resume Generator!")