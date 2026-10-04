import re


def normalize(text):
    """
    Normalize text for comparison.
    """

    text = text.lower().strip()

    # Treat common variations as the same
    text = text.replace("&", "and")
    text = text.replace("-", " ")
    text = text.replace("/", " ")

    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def skill_matches(resume_skill, jd_skill):
    """
    Check whether a resume skill matches a JD skill.
    """

    resume_skill = normalize(resume_skill)
    jd_skill = normalize(jd_skill)

    # Exact match
    if resume_skill == jd_skill:
        return True

    # One contains the other
    if resume_skill in jd_skill:
        return True

    if jd_skill in resume_skill:
        return True

    return False


def match_skills(resume_skills, jd_skills):
    """
    Compare resume skills with required JD skills.
    """

    matched = []
    missing = []

    for jd_skill in jd_skills:

        found = False

        for resume_skill in resume_skills:

            if skill_matches(
                resume_skill,
                jd_skill
            ):
                found = True
                matched.append(jd_skill)
                break

        if not found:
            missing.append(jd_skill)

    return matched, missing


def calculate_match_percentage(
    matched_count,
    total_jd_skills
):
    """
    Calculate percentage of JD skills
    found in the resume.
    """

    if total_jd_skills == 0:
        return 0

    percentage = (
        matched_count / total_jd_skills
    ) * 100

    return round(percentage, 2)


def match_resume_with_job(
    resume,
    job_description
):
    """
    Main resume-JD matching function.
    """

    resume_skills = resume.get(
        "skills",
        []
    )

    jd_skills = job_description.get(
        "required_skills",
        []
    )

    matched_skills, missing_skills = (
        match_skills(
            resume_skills,
            jd_skills
        )
    )

    match_percentage = calculate_match_percentage(
        len(matched_skills),
        len(jd_skills)
    )

    return {
        "job_title": job_description.get(
            "job_title",
            ""
        ),

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "match_percentage": match_percentage
    }