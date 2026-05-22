import json
from urllib import error, request

from fastapi import HTTPException, status

from src.core.settings import settings
from src.persons.schemas.human_intake_schemas import CandidateInput, EvaluationResponse


class GroqEvaluationService:
    @staticmethod
    def evaluate_candidate(candidate: CandidateInput, role_counts: dict[str, int]) -> EvaluationResponse:
        if not settings.groq_api_key:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GROQ_API_KEY is not configured.",
            )

        candidate_for_ai = candidate.model_copy(update={"photo_url": None})

        payload = {
            "model": settings.groq_model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an intake evaluator for a survival camp. "
                        "Return only JSON with this exact schema: "
                        "{decision, score, explanation, suggested_profession, score_breakdown, applied_rules}. "
                        "Allowed decision values: APROBADO or RECHAZADO. "
                        "Allowed suggested_profession values: MEDIC, EXPLORER, FARMER, NOT_ASSIGNED. "
                        "score_breakdown must include integers for resilience, medical_experience, defense_experience, context. "
                        "score must be an integer between 0 and 100."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "candidate": candidate_for_ai.model_dump(),
                            "role_coverage": role_counts,
                            "evaluation_goal": "Assess survival suitability and recommend role assignment.",
                        }
                    ),
                },
            ],
        }

        req = request.Request(
            url=settings.groq_base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "shelter-logistics-api/1.0",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=settings.groq_timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Groq API request failed: {detail or exc.reason}",
            ) from exc
        except error.URLError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Could not reach Groq API: {exc.reason}",
            ) from exc
        except TimeoutError as exc:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Groq API request timed out.",
            ) from exc

        try:
            groq_payload = json.loads(response_body)
            content = groq_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Groq API returned an invalid response structure.",
            ) from exc

        parsed_content = GroqEvaluationService._parse_content_json(content)
        
        try:
            if "score_breakdown" in parsed_content:
                parsed_content["score_breakdown"] = GroqEvaluationService._scale_breakdown_to_total(
                    parsed_content["score_breakdown"], int(parsed_content.get("score", 0))
                )
        except Exception:
            pass

        try:
            return EvaluationResponse.model_validate(parsed_content)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Groq API response does not match evaluation schema.",
            ) from exc

    @staticmethod
    def _parse_content_json(content: str) -> dict:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find("{")
            end = content.rfind("}")
            if start == -1 or end == -1 or end <= start:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Groq API returned non-JSON content.",
                )

            snippet = content[start : end + 1]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Groq API JSON content could not be parsed.",
                ) from exc
        
    @staticmethod
    def _scale_breakdown_to_total(breakdown: dict, total_score: int) -> dict:
        keys = ["resilience", "medical_experience", "defense_experience", "context"]
        vals = [max(0, min(100, int(breakdown.get(k, 0) or 0))) for k in keys]
        s = sum(vals)
        if s == 0:
            if total_score and total_score > 0:
                base = total_score // 4
                scaled = [base] * 4
                rem = total_score - sum(scaled)
                scaled[0] += rem
                return dict(zip(keys, scaled))
            return dict(zip(keys, [0, 0, 0, 0]))
        target = total_score if total_score and total_score > 0 else 100
        scaled = [int(round(v * target / s)) for v in vals]
        diff = target - sum(scaled)
        scaled[0] += diff

        scaled = [max(0, min(100, int(v))) for v in scaled]
        return dict(zip(keys, scaled))