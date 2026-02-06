# AI提示词设计原则

## 核心原则

1. **明确角色**: 中国象棋教练
2. **输出格式**: 结构化JSON（棋步+解释）
3. **解释语言**: 通俗易懂，适合初学者
4. **思考链**: 展示战术考虑
5. **局面分析**: 每步后评估优势

## 系统提示词模板

```python
SYSTEM_PROMPT = """你是一位经验丰富的中国象棋教练，擅长用通俗易懂的语言解释象棋策略。

你的任务是：
1. 分析当前棋局态势
2. 给出最佳棋步
3. 用初学者能理解的语言解释这个棋步的战术目的

输出格式（JSON）：
{
  "move": "炮二平五",
  "explanation": "这一步的战术考虑...",
  "position_eval": "红方略微优势"
}

注意事项：
- 解释要具体，避免空泛
- 用比喻帮助理解（如"控制咽喉要道"）
- 指出关键战术（如"牵制"、"弃子"）
- 评估局面时给出具体理由"""
```

## 用户提示词构建

```python
def build_prompt(game_state: GameState) -> str:
    """构建AI提示词。"""
    return f"""当前棋局：

【棋盘状态】
{format_board(game_state.board)}

【历史着法】
{' '.join(game_state.move_history)}

【轮到】{'红方' if game_state.current_player == 'red' else '黑方'}

请分析当前局面，给出最佳着法并解释战术意图。"""
```

## 提示词优化技巧

### 1. 添加战术提示

```python
tactical_hints = {
    "under_attack": "注意：你的{piece}正在被攻击",
    "checking": "当前可以将军",
    "endgame": "已进入残局阶段",
}
```

### 2. 层级化解释

```python
EXPLANATION_LEVELS = {
    "beginner": "重点解释基本规则和简单战术",
    "intermediate": "分析战术组合和中局战略",
    "advanced": "深度计算和复杂战术分析",
}
```

### 3. 情境感知

```python
def get_contextual_hints(game_state: GameState) -> List[str]:
    """获取情境提示。"""
    hints = []
    
    if len(game_state.move_history) < 10:
        hints.append("开局阶段，注重出子效率")
    elif len(game_state.move_history) > 80:
        hints.append("残局阶段，兵卒价值上升")
    
    if game_state.material_difference < -3:
        hints.append("对方子力占优，寻找防守反击机会")
    
    return hints
```

## 输出验证

```python
def validate_ai_response(response: dict) -> bool:
    """验证AI响应格式。"""
    required_fields = ["move", "explanation", "position_eval"]
    
    if not all(field in response for field in required_fields):
        return False
    
    if not isinstance(response["move"], str) or len(response["move"]) < 3:
        return False
    
    if not isinstance(response["explanation"], str) or len(response["explanation"]) < 10:
        return False
    
    return True
```

## 常见问题处理

### 问题1: 输出格式错误

```python
# 添加重试机制
@retry(max_attempts=3)
def get_ai_move(game_state: GameState) -> Optional[dict]:
    response = ai_client.chat.completions.create(
        messages=[...],
        response_format={"type": "json_object"}
    )
    
    try:
        parsed = json.loads(response.choices[0].message.content)
        if validate_ai_response(parsed):
            return parsed
    except (json.JSONDecodeError, KeyError):
        pass
    
    return None
```

### 问题2: 解释过于抽象

```python
# 在提示词中添加具体要求
prompt += """
解释要求：
- 用具体位置（如"河沿"、"九宫"）
- 说明攻击/防御目标
- 给出后续可能的变着"""
```

### 问题3: 棋步非法

```python
# 验证棋步合法性
def is_legal_move(move: str, game_state: GameState) -> bool:
    try:
        from_pos, to_pos = parse_move(move)
        return game_state.board.is_valid_move(from_pos, to_pos)
    except:
        return False
```
