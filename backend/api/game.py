"""游戏路由"""

from fastapi import APIRouter, HTTPException

from backend.game.state import GameManager
from backend.models.schemas import (
    MoveRequest,
    MoveResponse,
    NewGameRequest,
    NewGameResponse,
    UndoRequest,
    UndoResponse,
)

router = APIRouter()
game_manager = GameManager()


@router.post("/new", response_model=NewGameResponse)
async def new_game(request: NewGameRequest) -> NewGameResponse:
    """创建新游戏"""
    try:
        session_id, game_state = game_manager.create_game(request.player_color)
        return NewGameResponse(session_id=session_id, game_state=game_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/move", response_model=MoveResponse)
async def make_move(request: MoveRequest) -> MoveResponse:
    """玩家下棋"""
    try:
        game_state = game_manager.make_move(request.session_id, request.from_pos, request.to_pos)
        return MoveResponse(success=True, game_state=game_state)
    except ValueError as e:
        return MoveResponse(success=False, error=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/undo", response_model=UndoResponse)
async def undo_move(request: UndoRequest) -> UndoResponse:
    """悔棋"""
    try:
        game_state = game_manager.undo_moves(request.session_id, request.moves)
        return UndoResponse(success=True, game_state=game_state)
    except ValueError as e:
        return UndoResponse(success=False, error=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state/{session_id}")
async def get_game_state(session_id: str) -> dict:
    """获取游戏状态"""
    game_state = game_manager.get_game(session_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="游戏不存在")
    return game_state.model_dump()
