import re


def clean_jd_text(text):
    """
    Clean extracted job description text.
    """

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def extract_section(text, start_heading, end_headings):
    """
    Extract text between one starting heading
    and the next known heading.
    """

    start_pattern = re.compile(
        rf"^\s*{re.escape(start_heading)}\s*:?\s*$",
        re.IGNORECASE | re.MULTILINE
    )

    start_match = start_pattern.search(text)

    if not start_match:
        return ""

    start_position = start_match.end()

    end_position = len(text)

    for heading in end_headings:

        pattern = re.compile(
            rf"^\s*{re.escape(heading)}\s*:?\s*$",
            re.IGNORECASE | re.MULTILINE
        )

        match = pattern.search(
            text,
            start_position
        )

        if match and match.start() < end_position:
            end_position = match.start()

    return text[start_position:end_position].strip()


def extract_list_items(section):
    """
    Convert a section into a list of clean items.
    """

    items = []

    for line in section.split("\n"):

        line = line.strip()

        # Remove bullet characters
        line = re.sub(
            r"^[•●▪\-*]\s*",
            "",
            line
        )

        if line:
            items.append(line)

    return items


def parse_job_description(text):
    """
    Convert raw JD text into structured data.
    """

    text = clean_jd_text(text)

    job_description = {
        "job_title": "",
        "required_skills": [],
        "responsibilities": [],
        "qualifications": []
    }

    # ----------------------------------------
    # JOB TITLE
    # ----------------------------------------

    title_match = re.search(
        r"^\s*(?:Job Title|Position|Role)\s*:\s*(.+)$",
        text,
        re.IGNORECASE | re.MULTILINE
    )

    if title_match:
        job_description["job_title"] = (
            title_match.group(1).strip()
        )

    # ----------------------------------------
    # REQUIRED SKILLS
    # ----------------------------------------

    skills_section = extract_section(
        text,
        "Requirements",
        [
            "Responsibilities",
            "Key Responsibilities",
            "What You'll Do",
            "What You Will Do",
            "Qualifications",
            "Preferred Qualifications"
        ]
    )

    job_description["required_skills"] = (
        extract_list_items(skills_section)
    )

    # ----------------------------------------
    # RESPONSIBILITIES
    # ----------------------------------------

    responsibilities_section = ""

    for heading in [
        "Responsibilities",
        "Key Responsibilities",
        "What You'll Do",
        "What You Will Do"
    ]:

        responsibilities_section = extract_section(
            text,
            heading,
            [
                "Responsibilities",
                "Key Responsibilities",
                "What You'll Do",
                "What You Will Do",
                "Qualifications",
                "Preferred Qualifications"
            ]
        )

        if responsibilities_section:
            break

    job_description["responsibilities"] = (
        extract_list_items(
            responsibilities_section
        )
    )

    # ----------------------------------------
    # QUALIFICATIONS
    # ----------------------------------------

    qualifications_section = ""

    for heading in [
        "Qualifications",
        "Preferred Qualifications"
    ]:

        qualifications_section = extract_section(
            text,
            heading,
            [
                "Qualifications",
                "Preferred Qualifications"
            ]
        )

        if qualifications_section:
            break

    job_description["qualifications"] = (
        extract_list_items(
            qualifications_section
        )
    )

    return job_description