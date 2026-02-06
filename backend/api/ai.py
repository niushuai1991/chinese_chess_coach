"""AI路由"""

from fastapi import APIRouter, HTTPException

from backend.ai.engine import AIEngine
from backend.api.game import game_manager
from backend.models.schemas import AIMoveRequest, AIMoveResponse

router = APIRouter()
ai_engine = AIEngine(game_manager=game_manager)


@router.post("/move", response_model=AIMoveResponse)
async def ai_move(request: AIMoveRequest) -> AIMoveResponse:
    """AI下棋并返回解释"""
    try:
        result = await ai_engine.make_move_with_explanation(request.session_id)
        return AIMoveResponse(
            success=True,
            move=result["move"],
            explanation=result["explanation"],
            game_state=result["game_state"],
        )
    except ValueError as e:
        return AIMoveResponse(success=False, error=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
