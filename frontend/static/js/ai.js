// AI交互模块
class AIInteraction {
    constructor() {}

    async getAIMove(sessionId) {
        try {
            const response = await fetch("/api/ai/move", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ session_id: sessionId })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error("获取AI棋步失败:", error);
            throw error;
        }
    }

    async getMoveExplanation(sessionId, move) {
        // 这个功能可以扩展，用于获取特定棋步的解释
        try {
            const response = await fetch("/api/ai/explain", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: sessionId,
                    move: move
                })
            });

            const data = await response.json();
            return data.explanation;
        } catch (error) {
            console.error("获取解释失败:", error);
            return null;
        }
    }

    displayExplanation(explanation) {
        const explanationDiv = document.getElementById("explanation");
        if (explanationDiv) {
            explanationDiv.textContent = explanation;
        }
    }

    addExplanationToHistory(move, explanation) {
        const history = document.getElementById("moveHistory");
        if (history) {
            const item = document.createElement("div");
            item.className = "history-item";
            item.innerHTML = `
                <div class="history-move">${move}</div>
                <div class="history-explanation">${explanation}</div>
            `;
            history.insertBefore(item, history.firstChild);
        }
    }
}

// 导出供其他模块使用
window.AIInteraction = AIInteraction;
