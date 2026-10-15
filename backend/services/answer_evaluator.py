import os
import json
import time
import requests

from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()


# ---------------------------------------------------------
# Gemini configuration
# ---------------------------------------------------------

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file."
    )


MODEL = "gemini-3.8-flash"

API_URL = (
    f"https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)


# ---------------------------------------------------------
# Evaluate interview answer
# ---------------------------------------------------------

def evaluate_answer(question, answer, context):

    if not question or not question.strip():
        raise ValueError(
            "Question is required."
        )

    if not answer or not answer.strip():
        raise ValueError(
            "Answer is required."
        )

    # Extract information from context
    resume = context.get(
        "candidate",
        {}
    )

    job = context.get(
        "job",
        {}
    )

    matching = context.get(
        "matching",
        {}
    )

    # Data sent to Gemini
    evaluation_data = {
        "question": question,
        "candidate_answer": answer,
        "candidate_resume": resume,
        "job_description": job,
        "resume_job_match": matching
    }

    # -----------------------------------------------------
    # Prompt
    # -----------------------------------------------------

    prompt = f"""
You are an expert technical and HR interviewer.

Evaluate the candidate's answer to the interview question.

This system must work for ANY career domain, including:

- Software Engineering
- Machine Learning / AI
- Data Science
- Data Engineering
- Cybersecurity
- Cloud / DevOps
- Web Development
- Mobile Development
- Database roles
- Networking
- Electronics
- Mechanical Engineering
- Finance
- Marketing
- HR
- Business roles
- Other professional domains

Determine the expected knowledge from the question and
job description.

Evaluate the candidate based on:

1. Correctness
2. Relevance
3. Completeness
4. Clarity
5. Depth

Do NOT judge the candidate based on whether they have
professional experience if they are a student or fresher.

Do NOT invent facts about the candidate.

Do NOT assume that something is true just because it
appears in the job description.

Candidate and interview information:

{json.dumps(evaluation_data, indent=2)}

Give an overall score from 0 to 10.

Also provide:

- What the candidate did well
- What could be improved
- Important points the candidate missed
- A better sample answer
- Whether the answer is acceptable for an interview

Return ONLY valid JSON.

Use exactly this structure:

{{
    "score": 0,
    "rating": "Poor",
    "correctness": "Short evaluation",
    "relevance": "Short evaluation",
    "completeness": "Short evaluation",
    "clarity": "Short evaluation",
    "depth": "Short evaluation",
    "strengths": [
        "Strength 1",
        "Strength 2"
    ],
    "improvements": [
        "Improvement 1",
        "Improvement 2"
    ],
    "missed_points": [
        "Important point 1",
        "Important point 2"
    ],
    "better_answer": "A concise but strong sample answer.",
    "interview_ready": true
}}

Rating rules:

9-10 = Excellent
7-8 = Good
5-6 = Average
3-4 = Weak
0-2 = Poor

Important:

- Do not give a high score merely because the answer is long.
- Do not give a low score merely because the answer is short.
- Judge the actual content of the answer.
- Keep feedback constructive.
- Make the better answer realistic and concise.
- The evaluation should resemble feedback from a real interviewer.
"""

    # -----------------------------------------------------
    # Gemini request
    # -----------------------------------------------------

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": API_KEY
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    # -----------------------------------------------------
    # Retry configuration
    # -----------------------------------------------------

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

        except requests.exceptions.Timeout:

            if attempt < max_attempts:

                wait_time = attempt * 3

                print(
                    f"Gemini request timed out. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue

            raise RuntimeError(
                "Gemini request timed out. "
                "Please try again."
            )

        except requests.exceptions.ConnectionError as e:

            if attempt < max_attempts:

                wait_time = attempt * 3

                print(
                    f"Gemini connection error. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue

            raise RuntimeError(
                "Network error while contacting Gemini after "
                f"{max_attempts} attempts: {e}"
            ) from e

        except requests.exceptions.RequestException as e:

            raise RuntimeError(
                f"Network error while contacting Gemini: {e}"
            ) from e

        # -------------------------------------------------
        # Successful response
        # -------------------------------------------------

        if response.status_code == 200:

            try:

                data = response.json()

            except ValueError:

                raise RuntimeError(
                    "Gemini returned an invalid JSON response."
                )

            # Extract generated text
            try:

                result_text = (
                    data["candidates"][0]
                    ["content"]
                    ["parts"][0]
                    ["text"]
                )

            except (
                KeyError,
                IndexError,
                TypeError
            ):

                raise RuntimeError(
                    f"Unexpected Gemini response: {data}"
                )

            result_text = result_text.strip()

            # -------------------------------------------------
            # Remove Markdown code fences
            # -------------------------------------------------

            if result_text.startswith("```json"):

                result_text = result_text[7:]

            elif result_text.startswith("```"):

                result_text = result_text[3:]

            if result_text.endswith("```"):

                result_text = result_text[:-3]

            result_text = result_text.strip()

            # -------------------------------------------------
            # Convert Gemini response to Python dictionary
            # -------------------------------------------------

            try:

                result = json.loads(
                    result_text
                )

            except json.JSONDecodeError:

                raise RuntimeError(
                    "Gemini returned invalid JSON while "
                    "evaluating the candidate answer.\n\n"
                    f"Gemini response:\n{result_text}"
                )

            return result

        # -----------------------------------------------------
        # Temporary Gemini server/model error
        # -----------------------------------------------------

        elif response.status_code in [
            500,
            502,
            503,
            504
        ]:

            if attempt < max_attempts:

                wait_time = attempt * 3

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue

            raise RuntimeError(
                "Gemini is temporarily unavailable after "
                f"{max_attempts} attempts. "
                "Please try again."
            )

        # -----------------------------------------------------
        # Rate limit
        # -----------------------------------------------------

        elif response.status_code == 429:

            raise RuntimeError(
                "Gemini rate limit reached. "
                "Please wait a moment and try again."
            )

        # -----------------------------------------------------
        # Authentication error
        # -----------------------------------------------------

        elif response.status_code in [
            401,
            403
        ]:

            raise RuntimeError(
                "Gemini API authentication failed. "
                "Check GEMINI_API_KEY in your .env file."
            )

        # -----------------------------------------------------
        # Other Gemini API errors
        # -----------------------------------------------------

        else:

            raise RuntimeError(
                f"Gemini API error: "
                f"{response.status_code} - "
                f"{response.text}"
            )

    # This should normally never be reached.
    raise RuntimeError(
        "Unable to evaluate the answer."
    )