// 游戏逻辑模块
class ChessGame {
    constructor() {
        this.sessionId = null;
        this.gameState = null;
        this.playerColor = "red";
        this.board = new ChessBoard("chessboard");
        this.isPlayerTurn = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // 新游戏按钮
        document.getElementById("newGameBtn").addEventListener("click", () => {
            this.startNewGame();
        });

        // 悔棋按钮
        document.getElementById("undoBtn").addEventListener("click", () => {
            this.undoMove();
        });

        // 颜色选择
        document.getElementById("colorSelect").addEventListener("change", (e) => {
            this.playerColor = e.target.value;
        });

        // 难度选择
        document.getElementById("difficultySelect").addEventListener("change", async (e) => {
            await this.changeDifficulty(e.target.value);
        });

        // 棋盘点击
        this.board.container.addEventListener("cellClick", (e) => {
            this.handleCellClick(e.detail.row, e.detail.col);
        });
    }

    async changeDifficulty(difficulty) {
        try {
            const response = await fetch("/api/settings/difficulty", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ difficulty: parseInt(difficulty) })
            });

            const data = await response.json();

            // 更新难度指示器
            const difficultyNames = { 3: "中等", 4: "困难", 5: "大师" };
            document.getElementById("difficultyIndicator").textContent = `难度：${difficultyNames[difficulty]}`;

            console.log("难度设置成功:", data);
        } catch (error) {
            console.error("设置难度失败:", error);
            this.showError("设置难度失败");
        }
    }

    async startNewGame() {
        try {
            const response = await fetch("/api/game/new", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ player_color: this.playerColor })
            });

            const data = await response.json();
            this.sessionId = data.session_id;
            this.gameState = data.game_state;

            this.updateUI();
            document.getElementById("undoBtn").disabled = true;

            // 初始化解说面板
            if (this.playerColor === "red") {
                this.updateExplanation("游戏开始！你执红先行，请点击棋子下棋。");
            } else {
                this.updateExplanation("游戏开始！你执黑，AI执红先行，请稍候...");
            }

            // 如果玩家执黑，AI先手
            if (this.playerColor === "black") {
                this.isPlayerTurn = false;
                setTimeout(() => this.makeAIMove(), 500);
            } else {
                this.isPlayerTurn = true;
            }

        } catch (error) {
            console.error("创建游戏失败:", error);
            this.showError("创建游戏失败，请重试");
        }
    }

    async handleCellClick(row, col) {
        if (!this.sessionId) return;

        // 检查游戏是否已结束（提前检查）
        if (this.gameState.is_checkmate || this.gameState.is_stalemate) {
            this.showError("游戏已结束，请开始新游戏");
            return;
        }

        if (!this.isPlayerTurn) return;

        const selected = this.board.selectedCell;

        if (selected) {
            // 尝试移动
            try {
                const response = await fetch("/api/game/move", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: this.sessionId,
                        from_pos: { row: selected.row, col: selected.col },
                        to_pos: { row, col }
                    })
                });

                const data = await response.json();

                if (data.success) {
                    this.gameState = data.game_state;
                    this.board.clearSelection();
                    this.board.clearValidMoves();
                    this.updateUI();
                    document.getElementById("undoBtn").disabled = false;

                    // 检查游戏是否结束
                    if (this.gameState.is_checkmate || this.gameState.is_stalemate) {
                        // 游戏结束，AI不再走棋
                        return;
                    }

                    // 显示玩家下棋提示
                    this.updateExplanation("你已下棋，正在等待AI回应...");

                    // AI回合
                    this.isPlayerTurn = false;
                    setTimeout(() => this.makeAIMove(), 500);
                } else {
                    this.showError(data.error || "无效的棋步");
                    this.board.clearSelection();
                    this.board.clearValidMoves();
                }

            } catch (error) {
                console.error("下棋失败:", error);
                this.showError("下棋失败，请重试");
            }
        } else {
            // 选择棋子
            const piece = this.gameState.board[row]?.[col];
            if (piece && piece.color === this.playerColor) {
                this.board.selectCell(row, col);
                // TODO: 计算并显示可行棋步
            }
        }
    }

    async makeAIMove() {
        if (!this.sessionId) return;

        // 检查游戏是否已结束
        if (this.gameState.is_checkmate || this.gameState.is_stalemate) {
            return; // 游戏已结束，AI不再走棋
        }

        try {
            const response = await fetch("/api/ai/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: this.sessionId })
            });

            const data = await response.json();

            if (data.success) {
                this.gameState = data.game_state;
                this.updateUI();

                // 检查游戏是否结束
                if (this.gameState.is_checkmate || this.gameState.is_stalemate) {
                    // 游戏结束，玩家无法继续走棋
                    return;
                }

                // 更新AI解说面板
                console.log("AI解说内容:", data.explanation);
                this.updateExplanation(data.explanation);

                // 添加AI解释到历史
                this.addHistoryItem(data.move, data.explanation);

                // 继续游戏
                this.isPlayerTurn = true;
            } else {
                this.showError(data.error || "AI下棋失败");
                this.isPlayerTurn = true;
            }

        } catch (error) {
            console.error("AI下棋失败:", error);
            this.showError("AI下棋失败，请重试");
            this.isPlayerTurn = true;
        }
    }

    async undoMove() {
        if (!this.sessionId) return;

        try {
            const response = await fetch("/api/game/undo", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    moves: 2
                })
            });

            const data = await response.json();

            if (data.success) {
                this.gameState = data.game_state;
                this.updateUI();
                this.isPlayerTurn = true;
            } else {
                this.showError(data.error || "悔棋失败");
            }

        } catch (error) {
            console.error("悔棋失败:", error);
            this.showError("悔棋失败，请重试");
        }
    }

    updateUI() {
        this.board.updateBoard(this.gameState.board);

        // 更新状态
        if (this.gameState.is_checkmate) {
            this.showStatus("将死！");
            // 禁用棋盘交互
            this.board.container.style.pointerEvents = "none";
        } else if (this.gameState.is_stalemate) {
            this.showStatus("和棋！");
            // 禁用棋盘交互
            this.board.container.style.pointerEvents = "none";
        } else if (this.gameState.is_check) {
            this.showStatus("将军！");
            this.board.container.style.pointerEvents = "auto";
        } else {
            this.showStatus(
                this.gameState.current_player === "red" ? "红方走棋" : "黑方走棋"
            );
            this.board.container.style.pointerEvents = "auto";
        }

        // 更新回合指示器
        const turnIndicator = document.getElementById("turnIndicator");
        turnIndicator.textContent = `你执${this.playerColor === "red" ? "红" : "黑"}`;
    }

    addHistoryItem(move, explanation) {
        const history = document.getElementById("moveHistory");
        const item = document.createElement("div");
        item.className = "history-item";
        item.innerHTML = `
            <div class="history-move">第${this.gameState.move_history.length}步</div>
            <div class="history-explanation">${explanation || "玩家下棋"}</div>
        `;
        history.insertBefore(item, history.firstChild);
    }

    showStatus(message) {
        document.getElementById("gameStatus").textContent = message;
    }

    updateExplanation(explanation) {
        console.log("updateExplanation被调用，内容:", explanation);
        const explanationDiv = document.getElementById("explanation");
        if (explanationDiv) {
            console.log("找到explanation元素，更新内容");
            explanationDiv.textContent = explanation || "等待AI分析...";
        } else {
            console.error("未找到explanation元素！");
        }
    }

    showError(message) {
        const explanation = document.getElementById("explanation");
        explanation.innerHTML = `<span style="color: #c41e3a;">${message}</span>`;
        setTimeout(() => {
            explanation.textContent = "请继续游戏";
        }, 3000);
    }
}

// 初始化游戏
let game;
document.addEventListener("DOMContentLoaded", () => {
    game = new ChessGame();
});
