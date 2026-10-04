from services.matcher import match_resume_with_job


resume = {
    "skills": [
        "C++",
        "Python",
        "Machine Learning",
        "Deep Learning",
        "Scikit-learn",
        "PyTorch",
        "Random Forest",
        "Decision Tree",
        "Pandas",
        "NumPy",
        "Matplotlib",
        "FastAPI",
        "PostgreSQL",
        "SQL",
        "REST APIs",
        "Git",
        "pytest",
        "Data Structures & Algorithms",
        "Object-Oriented Programming",
        "Database Management"
    ]
}


job_description = {
    "job_title": "Machine Learning Engineer",

    "required_skills": [
        "Python",
        "Machine Learning",
        "PyTorch",
        "Scikit-learn",
        "SQL",
        "FastAPI",
        "REST APIs",
        "Data Structures and Algorithms"
    ]
}


result = match_resume_with_job(
    resume,
    job_description
)


print(result)