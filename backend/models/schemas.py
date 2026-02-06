"""数据模型定义"""

from enum import StrEnum

from pydantic import BaseModel, Field


class PlayerColor(StrEnum):
    """玩家颜色"""

    RED = "red"
    BLACK = "black"


class PieceType(StrEnum):
    """棋子类型"""

    KING = "k"  # 帅/将
    ADVISOR = "a"  # 仕/士
    ELEPHANT = "e"  # 相/象
    HORSE = "h"  # 马
    CHARIOT = "r"  # 车
    CANNON = "c"  # 炮
    PAWN = "p"  # 兵/卒


class Piece(BaseModel):
    """棋子"""

    type: PieceType
    color: PlayerColor


class Position(BaseModel):
    """位置"""

    row: int = Field(ge=0, le=9)
    col: int = Field(ge=0, le=8)


class Move(BaseModel):
    """棋步"""

    from_pos: Position
    to_pos: Position
    piece: Piece
    captured: Piece | None = None


class GameState(BaseModel):
    """游戏状态"""

    session_id: str
    board: list[list[Piece | None]]
    current_player: PlayerColor
    player_color: PlayerColor
    move_history: list[Move]
    is_check: bool
    is_checkmate: bool
    is_stalemate: bool


class MoveRequest(BaseModel):
    """下棋请求"""

    session_id: str
    from_pos: Position
    to_pos: Position


class MoveResponse(BaseModel):
    """下棋响应"""

    success: bool
    game_state: GameState | None = None
    error: str | None = None


class AIMoveRequest(BaseModel):
    """AI下棋请求"""

    session_id: str


class AIMoveResponse(BaseModel):
    """AI下棋响应"""

    success: bool
    move: Move | None = None
    explanation: str | None = None
    game_state: GameState | None = None
    error: str | None = None


class NewGameRequest(BaseModel):
    """新游戏请求"""

    player_color: PlayerColor


class NewGameResponse(BaseModel):
    """新游戏响应"""

    session_id: str
    game_state: GameState


class UndoRequest(BaseModel):
    """悔棋请求"""

    session_id: str
    moves: int = Field(default=2, ge=1, le=10, description="悔棋步数")


class UndoResponse(BaseModel):
    """悔棋响应"""

    success: bool
    game_state: GameState | None = None
    error: str | None = None
