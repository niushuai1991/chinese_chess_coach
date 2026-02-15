"""游戏状态管理"""

import logging
import uuid

from backend.game.rules import XiangqiRules
from backend.models.schemas import GameState, Move, Piece, PieceType, PlayerColor, Position

logger = logging.getLogger(__name__)


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
            # 获取起始位置的棋子信息，用于调试
            piece = game.board[from_pos.row][from_pos.col]
            piece_info = f"{piece.color.value} {piece.type.value}" if piece else "空"
            raise ValueError(
                f"无效的棋步: {from_pos.dict()} -> {to_pos.dict()}, "
                f"起始位置棋子: {piece_info}, "
                f"当前玩家: {game.current_player.value}"
            )

        # 执行棋步（保存起始棋子和被吃棋子）
        piece = game.board[from_pos.row][from_pos.col]
        target_piece = (
            game.board[to_pos.row][to_pos.col]
            if 0 <= to_pos.row < 10 and 0 <= to_pos.col < 9
            else None
        )
        if not piece:
            raise ValueError("起始位置没有棋子")

        captured = game.board[to_pos.row][to_pos.col]

        # 打印走棋信息
        player = "红方" if piece.color.value == "red" else "黑方"
        piece_name = self._get_piece_name(piece.type.value, piece.color.value)
        capture_info = (
            f" 吃掉 {self._get_piece_name(captured.type.value, captured.color.value)}"
            if captured
            else ""
        )

        logger.info(
            f"🎮 {player}走棋: {piece_name} ({from_pos.row},{from_pos.col}) -> ({to_pos.row},{to_pos.col}){capture_info}"
        )
        print(
            f"🎮 {player}走棋: {piece_name} ({from_pos.row},{from_pos.col}) -> ({to_pos.row},{to_pos.col}){capture_info}"
        )

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

        # 打印对局状态
        move_count = len(game.move_history)
        logger.info(
            f"📊 第{move_count}步完成 | 当前轮到: {'红方' if game.current_player.value == 'red' else '黑方'}"
        )
        if game.is_check:
            logger.warning(f"⚠️  将军！")
        if game.is_checkmate:
            logger.error(f"💀 将死！游戏结束")
        if game.is_stalemate:
            logger.info(f"🤝 困毙！和棋")

        return game

    def _get_piece_name(self, piece_type: str, color: str) -> str:
        """获取棋子中文名称"""
        names = {
            "k": "将" if color == "black" else "帅",
            "a": "士" if color == "black" else "仕",
            "e": "象" if color == "black" else "相",
            "h": "马",
            "r": "车",
            "c": "炮",
            "p": "卒" if color == "black" else "兵",
        }
        return names.get(piece_type, piece_type)

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
