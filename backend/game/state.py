"""游戏状态管理"""

import uuid

from backend.game.rules import XiangqiRules
from backend.models.schemas import GameState, Move, Piece, PieceType, PlayerColor, Position


class GameManager:
    """游戏管理器"""

    def __init__(self) -> None:
        self.games: dict[str, GameState] = {}

    def create_game(self, player_color: PlayerColor) -> tuple[str, GameState]:
        """创建新游戏

        Args:
            player_color: 玩家选择的颜色

        Returns:
            (session_id, game_state)
        """
        session_id = str(uuid.uuid4())
        game_state = GameState(
            session_id=session_id,
            board=self._init_board(),
            current_player=PlayerColor.RED,
            player_color=player_color,
            move_history=[],
            is_check=False,
            is_checkmate=False,
            is_stalemate=False,
        )
        self.games[session_id] = game_state
        return session_id, game_state

    def get_game(self, session_id: str) -> GameState | None:
        """获取游戏状态"""
        return self.games.get(session_id)

    def make_move(self, session_id: str, from_pos: Position, to_pos: Position) -> GameState:
        """执行棋步

        Args:
            session_id: 游戏会话ID
            from_pos: 起始位置
            to_pos: 目标位置

        Returns:
            新的游戏状态

        Raises:
            ValueError: 无效的棋步
        """
        game = self.get_game(session_id)
        if not game:
            raise ValueError("游戏不存在")

        # 验证棋步合法性
        if not self._is_valid_move(game, from_pos, to_pos):
            raise ValueError("无效的棋步")

        # 执行棋步
        piece = game.board[from_pos.row][from_pos.col]
        if not piece:
            raise ValueError("起始位置没有棋子")

        captured = game.board[to_pos.row][to_pos.col]

        move = Move(from_pos=from_pos, to_pos=to_pos, piece=piece, captured=captured)

        # 更新棋盘
        game.board[to_pos.row][to_pos.col] = piece
        game.board[from_pos.row][from_pos.col] = None
        game.move_history.append(move)

        # 切换玩家
        game.current_player = (
            PlayerColor.BLACK if game.current_player == PlayerColor.RED else PlayerColor.RED
        )

        # 检查将军和将死（检查对手是否被将军）
        opponent = PlayerColor.BLACK if game.current_player == PlayerColor.RED else PlayerColor.RED
        game.is_check = XiangqiRules.is_in_check(game.board, opponent)
        game.is_checkmate = game.is_check and XiangqiRules.is_checkmate(game.board, opponent)
        game.is_stalemate = not game.is_check and XiangqiRules.is_stalemate(game.board, opponent)

        return game

    def undo_moves(self, session_id: str, moves: int) -> GameState:
        """悔棋

        Args:
            session_id: 游戏会话ID
            moves: 悔棋步数

        Returns:
            悔棋后的游戏状态

        Raises:
            ValueError: 悔棋步数过多
        """
        game = self.get_game(session_id)
        if not game:
            raise ValueError("游戏不存在")

        if moves > len(game.move_history):
            raise ValueError("悔棋步数过多")

        # 撤销棋步
        for _ in range(moves):
            move = game.move_history.pop()
            game.board[move.from_pos.row][move.from_pos.col] = move.piece
            game.board[move.to_pos.row][move.to_pos.col] = move.captured
            game.current_player = (
                PlayerColor.BLACK if game.current_player == PlayerColor.RED else PlayerColor.RED
            )

        game.is_check = self._is_in_check(game)
        game.is_checkmate = False
        game.is_stalemate = False

        return game

    def _init_board(self) -> list[list[Piece | None]]:
        """初始化棋盘"""
        board = [[None for _ in range(9)] for _ in range(10)]

        # 红方（下方）
        board[9][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)
        board[9][1] = Piece(type=PieceType.HORSE, color=PlayerColor.RED)
        board[9][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.RED)
        board[9][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)
        board[9][4] = Piece(type=PieceType.KING, color=PlayerColor.RED)
        board[9][5] = Piece(type=PieceType.ADVISOR, color=PlayerColor.RED)
        board[9][6] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.RED)
        board[9][7] = Piece(type=PieceType.HORSE, color=PlayerColor.RED)
        board[9][8] = Piece(type=PieceType.CHARIOT, color=PlayerColor.RED)

        board[7][1] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)
        board[7][7] = Piece(type=PieceType.CANNON, color=PlayerColor.RED)

        for i in range(0, 9, 2):
            board[6][i] = Piece(type=PieceType.PAWN, color=PlayerColor.RED)

        # 黑方（上方）
        board[0][0] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)
        board[0][1] = Piece(type=PieceType.HORSE, color=PlayerColor.BLACK)
        board[0][2] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)
        board[0][3] = Piece(type=PieceType.ADVISOR, color=PlayerColor.BLACK)
        board[0][4] = Piece(type=PieceType.KING, color=PlayerColor.BLACK)
        board[0][5] = Piece(type=PieceType.ADVISOR, color=PlayerColor.BLACK)
        board[0][6] = Piece(type=PieceType.ELEPHANT, color=PlayerColor.BLACK)
        board[0][7] = Piece(type=PieceType.HORSE, color=PlayerColor.BLACK)
        board[0][8] = Piece(type=PieceType.CHARIOT, color=PlayerColor.BLACK)

        board[2][1] = Piece(type=PieceType.CANNON, color=PlayerColor.BLACK)
        board[2][7] = Piece(type=PieceType.CANNON, color=PlayerColor.BLACK)

        for i in range(0, 9, 2):
            board[3][i] = Piece(type=PieceType.PAWN, color=PlayerColor.BLACK)

        return board

    def _is_valid_move(self, game: GameState, from_pos: Position, to_pos: Position) -> bool:
        """验证棋步合法性"""
        return XiangqiRules.validate_move(game.board, from_pos, to_pos)

    def _is_in_check(self, game: GameState) -> bool:
        """检查是否将军"""
        return XiangqiRules.is_in_check(game.board, game.current_player)

    def _is_checkmate(self, game: GameState) -> bool:
        """检查是否将死"""
        return XiangqiRules.is_checkmate(game.board, game.current_player)

    def _is_stalemate(self, game: GameState) -> bool:
        """检查是否困毙"""
        return XiangqiRules.is_stalemate(game.board, game.current_player)
