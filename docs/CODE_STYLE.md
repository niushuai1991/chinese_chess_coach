# 代码风格指南

## Python代码规范

### 导入顺序（PEP 8）

```python
# 标准库
import os
from typing import Optional, List, Dict
from datetime import datetime

# 第三方库
from fastapi import FastAPI, HTTPException
from openai import OpenAI

# 本地模块
from backend.game.chess import ChineseChess
from backend.ai.explainer import MoveExplainer
```

### 格式化规则

- **4空格**缩进（禁止Tab）
- **100字符**最大行宽
- 使用**f-string**格式化字符串
- 使用**双引号**包裹字符串
- 函数间空**2行**，类内方法间空**1行**

### 类型注解

所有函数必须包含类型注解：

```python
from typing import Optional, List, Dict

def get_move_explanation(
    board: List[List[str]],
    move: str,
    language: str = "zh"
) -> Optional[str]:
    """获取棋步解释。
    
    Args:
        board: 当前棋盘状态
        move: 棋步（如'炮二平五'）
        language: 语言，默认中文
        
    Returns:
        棋步解释文本，失败返回None
    """
    if not move:
        return None
    # 实现逻辑...
```

### 命名规范

- 函数/变量：`snake_case`
- 类：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有方法：`_leading_underscore`
- 异常类：`PascalCaseError`

```python
MAX_HISTORY_LENGTH = 200
API_TIMEOUT = 30

class ChineseChess:
    def __init__(self, board_size: int = 10):
        self.board_size = board_size
        self._validate_board()
    
    def _validate_board(self) -> None:
        """验证棋盘配置。"""
        pass
    
    def make_move(self, from_pos: str, to_pos: str) -> bool:
        """执行棋步。"""
        pass
```

### 错误处理

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

def make_ai_move(session_id: str) -> Dict:
    """AI下棋。
    
    Raises:
        HTTPException: 400参数错误，500服务器错误
    """
    try:
        game_state = get_game_state(session_id)
        if not game_state:
            raise HTTPException(status_code=404, detail="游戏不存在")
            
        move = await ai_engine.suggest_move(game_state)
        if not move:
            raise HTTPException(status_code=500, detail="AI生成棋步失败")
            
        return {"move": move, "explanation": move.explanation}
        
    except ValueError as e:
        logger.error(f"无效参数: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("AI下棋失败")
        raise HTTPException(status_code=500, detail="服务器内部错误")
```

### API路由规范

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/api/game", tags=["game"])

class MoveRequest(BaseModel):
    session_id: str
    from_pos: str
    to_pos: str

@router.post("/move")
async def make_move(request: MoveRequest) -> Dict:
    """玩家下棋。"""
    pass

@router.post("/ai-move")
async def ai_move(session_id: str) -> Dict:
    """AI下棋并返回解释。"""
    pass

@router.post("/undo")
async def undo_move(session_id: str) -> Dict:
    """悔棋。"""
    pass
```

### 环境变量

```python
# .env 文件
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.example.com/v1
MODEL_NAME=gpt-4
LOG_LEVEL=INFO

# 代码中加载
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY环境变量未设置")
```

## 前端代码规范

```javascript
// 使用现代ES6+语法
const moveHistory = [];

async function makeAIMove() {
    try {
        const response = await fetch('/api/game/ai-move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_id: currentSession})
        });
        const data = await response.json();
        updateBoard(data.move);
        addExplanation(data.explanation);
    } catch (error) {
        console.error('AI下棋失败:', error);
        showError('AI下棋失败，请重试');
    }
}
```

## 最佳实践

1. **异步优先**: 所有IO操作使用async/await
2. **类型安全**: 严格使用mypy检查
3. **日志记录**: 使用logging模块，记录关键操作
4. **配置管理**: 敏感信息使用环境变量
5. **错误恢复**: 提供清晰的错误信息给用户
6. **文档**: 所有公共API添加docstring
7. **测试覆盖**: 核心逻辑覆盖率>80%
