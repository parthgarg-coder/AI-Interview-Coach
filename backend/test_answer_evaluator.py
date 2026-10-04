from services.answer_evaluator import evaluate_answer


context = {
    "candidate": {
        "name": "Parth Garg",
        "skills": [
            "Python",
            "Machine Learning",
            "PyTorch",
            "Scikit-learn",
            "FastAPI",
            "SQL"
        ]
    },

    "job": {
        "job_title": "Machine Learning Engineer",
        "required_skills": [
            "Python",
            "Machine Learning",
            "PyTorch",
            "Scikit-learn",
            "SQL",
            "FastAPI"
        ]
    },

    "matching": {
        "matched_skills": [
            "Python",
            "Machine Learning",
            "PyTorch",
            "Scikit-learn",
            "SQL",
            "FastAPI"
        ],
        "missing_skills": [],
        "match_percentage": 100
    }
}


question = """
What is overfitting in machine learning, and what techniques
can you use to prevent it?
"""


answer = """
Overfitting happens when a machine learning model learns the
training data too closely, including noise, so it performs
very well on training data but poorly on unseen data.

We can reduce overfitting by using techniques such as
cross-validation, regularization, pruning for decision trees,
dropout for neural networks, and collecting more training data.
"""


print("Evaluating answer...\n")


result = evaluate_answer(
    question,
    answer,
    context
)


print("Evaluation Result:")
print(result)