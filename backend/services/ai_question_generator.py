import os
import json
import time
import requests

from dotenv import load_dotenv


load_dotenv()


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


def generate_interview_questions(context):

    resume = context.get("candidate", {})
    job = context.get("job", {})
    matching = context.get("matching", {})

    prompt_data = {
        "resume": resume,
        "job_description": job,
        "resume_job_match": matching
    }

    prompt = f"""
You are an expert technical and HR interviewer.

Create a personalized interview for the candidate using
the resume and job description below.

The interview must work for ANY career domain.

Determine the career domain from the supplied resume
and job description.

Do not assume that the candidate has experience that
is not present in the resume.

Candidate and job information:

{json.dumps(prompt_data, indent=2)}

Generate exactly 10 interview questions.

Question distribution:

1. 2 Introduction / Background questions
2. 3 Resume / Project questions
3. 3 Technical questions relevant to the job
4. 1 Behavioral question
5. 1 question targeting a skill or requirement that
   needs further evaluation

Rules:

- Questions must be personalized.
- Use the candidate's actual projects and skills.
- Use the job description to select technical topics.
- Do not invent experience.
- Do not assume professional experience for a fresher.
- Questions should resemble real interview questions.
- Mix Easy, Medium, and Hard difficulty.
- Avoid repetitive questions.

Return ONLY valid JSON.

Do not use markdown.
Do not use ```json.
Do not add explanations before or after the JSON.

Use exactly this structure:

{{
    "domain": "detected career domain",
    "total_questions": 10,
    "questions": [
        {{
            "id": 1,
            "category": "Introduction",
            "difficulty": "Easy",
            "question": "Question text"
        }}
    ]
}}
"""

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
        ],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json"
        }
    }

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:

            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=90
            )

            print(
                f"Gemini response status: {response.status_code}"
            )

            # -----------------------------------------
            # SUCCESS
            # -----------------------------------------

            if response.status_code == 200:

                data = response.json()

                try:

                    answer = (
                        data["candidates"][0]
                        ["content"]
                        ["parts"][0]
                        ["text"]
                    )

                except (KeyError, IndexError, TypeError):

                    print("Unexpected Gemini response:")
                    print(json.dumps(data, indent=2))

                    raise RuntimeError(
                        "Gemini returned an unexpected response."
                    )

                answer = answer.strip()

                # Remove accidental markdown fences

                if answer.startswith("```json"):
                    answer = answer[7:]

                elif answer.startswith("```"):
                    answer = answer[3:]

                if answer.endswith("```"):
                    answer = answer[:-3]

                answer = answer.strip()

                try:

                    result = json.loads(answer)

                except json.JSONDecodeError:

                    print("Gemini returned:")
                    print(answer)

                    raise RuntimeError(
                        "Gemini returned invalid JSON."
                    )

                # Validate basic structure

                if "questions" not in result:

                    raise RuntimeError(
                        "Gemini response does not contain "
                        "'questions'."
                    )

                if not isinstance(result["questions"], list):

                    raise RuntimeError(
                        "Gemini 'questions' field is not a list."
                    )

                return result

            # -----------------------------------------
            # TEMPORARY SERVER ERROR
            # -----------------------------------------

            elif response.status_code in [500, 502, 503, 504]:

                print(
                    f"Gemini server error "
                    f"{response.status_code}:"
                )

                print(response.text)

                if attempt < max_attempts:

                    wait_time = attempt * 3

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue

                raise RuntimeError(
                    f"Gemini server is unavailable "
                    f"after {max_attempts} attempts. "
                    f"Last response: {response.text}"
                )

            # -----------------------------------------
            # RATE LIMIT
            # -----------------------------------------

            elif response.status_code == 429:

                print("Gemini rate limit response:")
                print(response.text)

                raise RuntimeError(
                    "Gemini rate limit reached. "
                    "Please wait and try again."
                )

            # -----------------------------------------
            # AUTHENTICATION
            # -----------------------------------------

            elif response.status_code in [401, 403]:

                print("Gemini authentication response:")
                print(response.text)

                raise RuntimeError(
                    "Gemini API authentication failed. "
                    "Check GEMINI_API_KEY in .env."
                )

            # -----------------------------------------
            # OTHER ERROR
            # -----------------------------------------

            else:

                print("Gemini API error:")
                print(response.text)

                raise RuntimeError(
                    f"Gemini API error "
                    f"{response.status_code}: "
                    f"{response.text}"
                )

        except requests.exceptions.Timeout:

            print("Gemini request timed out.")

            if attempt < max_attempts:

                wait_time = attempt * 3

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

                continue

            raise RuntimeError(
                "Gemini request timed out after "
                f"{max_attempts} attempts."
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