def build_interview_context(
    resume,
    job_description,
    match_result
):
    """
    Build a generic context object for the
    interview question generator.

    This function is independent of any
    particular resume or career domain.
    """

    context = {
        "candidate": {
            "name": resume.get("name", ""),
            "education": resume.get("education", {}),
            "skills": resume.get("skills", []),
            "projects": resume.get("projects", []),
            "achievements": resume.get(
                "achievements", []
            ),
            "coding": resume.get(
                "coding", {}
            )
        },

        "job": {
            "title": job_description.get(
                "job_title",
                ""
            ),
            "required_skills": job_description.get(
                "required_skills",
                []
            ),
            "responsibilities": job_description.get(
                "responsibilities",
                []
            ),
            "qualifications": job_description.get(
                "qualifications",
                []
            )
        },

        "matching": {
            "matched_skills": match_result.get(
                "matched_skills",
                []
            ),
            "missing_skills": match_result.get(
                "missing_skills",
                []
            ),
            "match_percentage": match_result.get(
                "match_percentage",
                0
            )
        }
    }

    return context