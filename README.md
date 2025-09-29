# AI-Powered Resume Generator (A4 Optimized)

This project generates a **professional, ATS-optimized, one-page resume** from a brief 1-2 line description using AI (Ollama API).  
The resume is output as a **print-ready HTML file** optimized for A4 size.

---

## Features

- Generates a **complete professional resume** including:
  - Contact information
  - Professional summary
  - Education
  - Technical skills
  - Work experience
  - Projects
  - Certifications
  - Achievements & awards
- **A4-optimized HTML** layout
- Automatic browser preview
- Intelligent fallback if AI generation fails
- Industry-specific skill and certification defaults

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) account and Python package
- Optional: `pdfkit` to convert HTML to PDF (requires wkhtmltopdf)

Install Python dependencies:

```bash
pip install -r requirements.txt
