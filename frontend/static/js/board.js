// 棋盘渲染模块
class ChessBoard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.selectedCell = null;
        this.validMoves = [];
        this.init();
    }

    init() {
        this.renderBoard();
    }

    renderBoard() {
        this.container.innerHTML = "";
        
        // 棋盘容器 - 10行×9列交叉点
        const board = document.createElement("div");
        board.className = "board";
        
        // 绘制棋盘线条
        this.drawBoardLines(board);
        
        // 添加楚河汉界
        const river = document.createElement("div");
        river.className = "river";
        river.innerHTML = "<span>楚河</span><span>汉界</span>";
        board.appendChild(river);
        
        // 创建10行9列的交叉点（棋子位置）
        for (let row = 0; row < 10; row++) {
            for (let col = 0; col < 9; col++) {
                const cell = document.createElement("div");
                cell.className = "cell";
                cell.dataset.row = row;
                cell.dataset.col = col;
                
                // 设置位置 - 棋子在交叉点上
                cell.style.left = `${col * 50 + 25}px`;
                cell.style.top = `${row * 50 + 25}px`;
                
                cell.addEventListener("click", () => this.handleCellClick(row, col));
                board.appendChild(cell);
            }
        }
        
        this.container.appendChild(board);
    }

    drawBoardLines(board) {
        // 横线 - 10条横线
        for (let i = 0; i < 10; i++) {
            const line = document.createElement("div");
            line.className = "h-line";
            line.style.top = `${i * 50 + 25}px`;
            board.appendChild(line);
        }
        
        // 边线竖线（第0列和第8列，贯通楚河汉界）
        [0, 8].forEach(i => {
            const line = document.createElement("div");
            line.className = "v-line-full";
            line.style.left = `${i * 50 + 25}px`;
            board.appendChild(line);
        });

        // 黑方竖线（上半部分，第1-7列，第0-4行）
        for (let i = 1; i < 8; i++) {
            const line = document.createElement("div");
            line.className = "v-line-top";
            line.style.left = `${i * 50 + 25}px`;
            board.appendChild(line);
        }

        // 红方竖线（下半部分，第1-7列，第5-9行）
        for (let i = 1; i < 8; i++) {
            const line = document.createElement("div");
            line.className = "v-line-bottom";
            line.style.left = `${i * 50 + 25}px`;
            board.appendChild(line);
        }
        
        // 九宫格斜线
        this.drawPalaceDiagonals(board);
    }

    drawPalaceDiagonals(board) {
        // 黑方九宫格（第0-2行，第3-5列）
        const blackPalaceTL = { x: 3 * 50 + 25, y: 0 * 50 + 25 };
        const blackPalaceBR = { x: 5 * 50 + 25, y: 2 * 50 + 25 };
        const blackPalaceTR = { x: 5 * 50 + 25, y: 0 * 50 + 25 };
        const blackPalaceBL = { x: 3 * 50 + 25, y: 2 * 50 + 25 };
        
        // 红方九宫格（第7-9行，第3-5列）
        const redPalaceTL = { x: 3 * 50 + 25, y: 7 * 50 + 25 };
        const redPalaceBR = { x: 5 * 50 + 25, y: 9 * 50 + 25 };
        const redPalaceTR = { x: 5 * 50 + 25, y: 7 * 50 + 25 };
        const redPalaceBL = { x: 3 * 50 + 25, y: 9 * 50 + 25 };
        
        // 绘制九宫格斜线
        this.createDiagonalLine(board, blackPalaceTL, blackPalaceBR);
        this.createDiagonalLine(board, blackPalaceTR, blackPalaceBL);
        this.createDiagonalLine(board, redPalaceTL, redPalaceBR);
        this.createDiagonalLine(board, redPalaceTR, redPalaceBL);
    }

    createDiagonalLine(board, start, end) {
        const length = Math.sqrt(Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2));
        const angle = Math.atan2(end.y - start.y, end.x - start.x) * 180 / Math.PI;
        
        const line = document.createElement("div");
        line.className = "diagonal-line";
        line.style.width = `${length}px`;
        line.style.left = `${start.x}px`;
        line.style.top = `${start.y}px`;
        line.style.transform = `rotate(${angle}deg)`;
        line.style.transformOrigin = "0 0";
        board.appendChild(line);
    }

    handleCellClick(row, col) {
        const event = new CustomEvent("cellClick", {
            detail: { row, col },
            bubbles: true
        });
        this.container.dispatchEvent(event);
    }

    updateBoard(boardData) {
        const cells = this.container.querySelectorAll(".cell");
        cells.forEach(cell => {
            const row = parseInt(cell.dataset.row);
            const col = parseInt(cell.dataset.col);
            const piece = boardData[row]?.[col];

            // 清除棋子
            const existingPiece = cell.querySelector(".piece");
            if (existingPiece) {
                existingPiece.remove();
            }

            // 添加新棋子
            if (piece) {
                const pieceEl = document.createElement("div");
                pieceEl.className = `piece ${piece.color}`;
                pieceEl.textContent = this.getPieceChar(piece.type, piece.color);
                cell.appendChild(pieceEl);
            }
        });
    }

    getPieceChar(type, color) {
        const chars = {
            red: {
                k: "帅",
                a: "仕",
                e: "相",
                h: "马",
                r: "车",
                c: "炮",
                p: "兵"
            },
            black: {
                k: "将",
                a: "士",
                e: "象",
                h: "马",
                r: "车",
                c: "炮",
                p: "卒"
            }
        };
        return chars[color][type];
    }

    selectCell(row, col) {
        this.clearSelection();
        const cell = this.getCell(row, col);
        if (cell) {
            cell.classList.add("selected");
            this.selectedCell = { row, col };
        }
    }

    highlightValidMoves(moves) {
        this.clearValidMoves();
        moves.forEach(move => {
            const cell = this.getCell(move.row, move.col);
            if (cell) {
                cell.classList.add("valid-move");
                this.validMoves.push(move);
            }
        });
    }

    clearSelection() {
        const selected = this.container.querySelector(".selected");
        if (selected) {
            selected.classList.remove("selected");
        }
        this.selectedCell = null;
    }

    clearValidMoves() {
        const validCells = this.container.querySelectorAll(".valid-move");
        validCells.forEach(cell => cell.classList.remove("valid-move"));
        this.validMoves = [];
    }

    getCell(row, col) {
        return this.container.querySelector(`.cell[data-row="${row}"][data-col="${col}"]`);
    }
}
