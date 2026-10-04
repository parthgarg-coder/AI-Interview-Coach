import re


def clean_resume_text(text):
    """
    Clean text extracted from a PDF.
    """

    # Fix words broken by PDF line wrapping
    text = text.replace("-\n", "")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive newlines
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def extract_section(text, start_heading, end_heading):
    """
    Extract text between two section headings.
    """

    start_index = text.find(start_heading)

    if start_index == -1:
        return ""

    start_index += len(start_heading)

    end_index = text.find(end_heading, start_index)

    if end_index == -1:
        return text[start_index:].strip()

    return text[start_index:end_index].strip()


def parse_contact_information(text, resume):
    """
    Extract name, email and phone.
    """

    lines = text.split("\n")

    if lines:
        resume["name"] = lines[0].strip()

    email_match = re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text
    )

    if email_match:
        resume["email"] = email_match.group()

    phone_match = re.search(
        r"\b\d{10}\b",
        text
    )

    if phone_match:
        resume["phone"] = phone_match.group()


def parse_skills(text):
    """
    Extract technical skills.
    """

    skills_section = extract_section(
        text,
        "Technical Skills",
        "Projects"
    )

    skills = []

    for line in skills_section.split("\n"):

        if ":" not in line:
            continue

        category, skill_text = line.split(":", 1)

        for skill in skill_text.split(","):

            skill = skill.strip()

            if skill:
                skills.append(skill)

    # Remove duplicates while preserving order
    skills = list(dict.fromkeys(skills))

    return skills


def parse_education(text):
    """
    Extract important education information.
    """

    education_section = extract_section(
        text,
        "Education",
        "Technical Skills"
    )

    education = {
        "college": "",
        "degree": "",
        "field": "",
        "graduation_year": "",
        "cgpa": "",
        "class_12": "",
        "class_10": ""
    }

    # College
    college_match = re.search(
        r"Inderprastha Engineering College",
        education_section,
        re.IGNORECASE
    )

    if college_match:
        education["college"] = college_match.group()

    # Graduation year
    year_match = re.search(
        r"Expected Graduation:\s*(\d{4})",
        education_section
    )

    if year_match:
        education["graduation_year"] = year_match.group(1)

    # Degree and field
    degree_match = re.search(
        r"B\.Tech\s*[–-]\s*(.*?)(?=CGPA:)",
        education_section
    )

    if degree_match:
        education["degree"] = "B.Tech"
        education["field"] = degree_match.group(1).strip()

    # CGPA
    cgpa_match = re.search(
        r"CGPA:\s*([\d.]+/\d+)",
        education_section
    )

    if cgpa_match:
        education["cgpa"] = cgpa_match.group(1)

    # Class 12
    class12_match = re.search(
        r"Class XII:\s*(\d+%)",
        education_section
    )

    if class12_match:
        education["class_12"] = class12_match.group(1)

    # Class 10
    class10_match = re.search(
        r"Class X:\s*(\d+%)",
        education_section
    )

    if class10_match:
        education["class_10"] = class10_match.group(1)

    return education

def clean_project_description(text):
    """
    Clean project description extracted from PDF.
    """

    # Remove GitHub / Live Demo labels
    text = re.sub(
        r"GitHub\|?Live Demo",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"GitHub",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove technology line at the beginning
    text = re.sub(
        r"^(Python|PostgreSQL|pytest|Scikit-learn|FastAPI|HTML/CSS/JS|,|\s)+",
        "",
        text
    )

    # Fix words broken across PDF lines
    text = text.replace("-\n", "")

    # Remove bullet characters
    text = text.replace("•", "")

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def parse_projects(text):
    """
    Extract projects from the resume.

    The current resume format contains two projects:
    1. Banking System (CLI)
    2. Mental Health Score Predictor
    """

    projects_section = extract_section(
        text,
        "Projects",
        "Achievements"
    )

    projects = []

    # -------------------------------------------------
    # Project 1: Banking System
    # -------------------------------------------------

    banking_match = re.search(
        r"Banking System \(CLI\)(.*?)(?=Mental Health Score Predictor)",
        projects_section,
        re.DOTALL
    )

    if banking_match:

        banking_text = banking_match.group(1).strip()

        projects.append({
            "name": "Banking System (CLI)",

            "technologies": [
                "Python",
                "PostgreSQL",
                "pytest"
            ],

            "description": clean_project_description(
                banking_text
            )
        })

    # -------------------------------------------------
    # Project 2: Mental Health Score Predictor
    # -------------------------------------------------

    mental_health_match = re.search(
        r"Mental Health Score Predictor(.*)",
        projects_section,
        re.DOTALL
    )

    if mental_health_match:

        mental_health_text = (
            mental_health_match.group(1).strip()
        )

        projects.append({
            "name": "Mental Health Score Predictor",

            "technologies": [
                "Python",
                "Scikit-learn",
                "FastAPI",
                "HTML/CSS/JS"
            ],

            "description": clean_project_description(
                mental_health_text
            )
        })

    return projects


def parse_achievements(text):
    """
    Extract achievements.
    """

    achievements_section = extract_section(
        text,
        "Achievements",
        "Coding / DSA"
    )

    achievements = []

    for line in achievements_section.split("\n"):

        line = line.strip()

        if line.startswith("•"):
            line = line[1:].strip()

        if line:
            achievements.append(line)

    return achievements


def parse_coding(text):
    """
    Extract coding/DSA information.
    """

    coding_section = extract_section(
        text,
        "Coding / DSA",
        "Languages"
    )

    coding = {
        "leetcode_problems": 0,
        "leetcode_rank": ""
    }

    problems_match = re.search(
        r"LeetCode:(\d+)",
        coding_section
    )

    rank_match = re.search(
        r"Global Rank:\s*([\d,]+)",
        coding_section
    )

    if problems_match:
        coding["leetcode_problems"] = int(
            problems_match.group(1)
        )

    if rank_match:
        coding["leetcode_rank"] = rank_match.group(1)

    return coding


def parse_resume(text):
    """
    Convert raw resume text into structured data.
    """

    text = clean_resume_text(text)

    resume = {
        "name": "",
        "email": "",
        "phone": "",
        "education": {},
        "skills": [],
        "projects": [],
        "achievements": [],
        "coding": {}
    }

    parse_contact_information(text, resume)

    resume["education"] = parse_education(text)

    resume["skills"] = parse_skills(text)

    resume["projects"] = parse_projects(text)

    resume["achievements"] = parse_achievements(text)

    resume["coding"] = parse_coding(text)

    return resume