from pydantic import BaseModel

from app.schemas.types import (EvaluationsCommentType,
                               EvaluationsGradeType)


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateEvaluationsRequest(BaseModel):
    comment_text: EvaluationsCommentType
    grade: EvaluationsGradeType


class GetAvgEvaluation(BaseModel):
    average_evaluation: float
