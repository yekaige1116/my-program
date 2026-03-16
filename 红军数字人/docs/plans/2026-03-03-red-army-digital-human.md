# 长征小红军数字人实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建一个可交互的长征小红军数字人网页，支持AI对话、角色动画和长征知识展示

**Architecture:** 单HTML文件实现，使用Canvas绘制2D卡通角色，通过JavaScript实现动画系统和AI对话功能，CSS实现界面样式

**Tech Stack:** HTML5 Canvas, CSS3, JavaScript (ES6+), 国内AI API (通义千问/文心一言)

---

## Task 1: 创建基础HTML结构和样式

**Files:**
- Modify: `/Users/yekaige/红军数字人/网页交互.html`

**Step 1: 创建HTML基础结构**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>长征小红军数字人</title>
    <style>
        /* 样式将在后续步骤添加 */
    </style>
</head>
<body>
    <div class="container">
        <!-- 角色展示区 -->
        <div class="character-section">
            <canvas id="characterCanvas" width="400" height="500"></canvas>
        </div>

        <!-- 对话交互区 -->
        <div class="chat-section">
            <div class="chat-header">
                <h2>小红军</h2>
                <span class="status">在线</span>
            </div>
            <div class="chat-messages" id="chatMessages">
                <!-- 消息将动态添加 -->
            </div>
            <div class="chat-input">
                <input type="text" id="userInput" placeholder="请输入您的问题...">
                <button id="sendBtn">发送</button>
            </div>
        </div>
    </div>

    <!-- API配置面板 -->
    <div class="settings-panel" id="settingsPanel">
        <h3>API配置</h3>
        <select id="apiProvider">
            <option value="qwen">通义千问</option>
            <option value="wenxin">文心一言</option>
            <option value="xunfei">讯飞星火</option>
        </select>
        <input type="password" id="apiKey" placeholder="请输入API Key">
        <button id="saveSettings">保存配置</button>
    </div>

    <!-- 设置按钮 -->
    <button class="settings-btn" id="settingsBtn">⚙️</button>

    <script>
        // JavaScript代码将在后续步骤添加
    </script>
</body>
</html>
```

**Step 2: 添加CSS样式**

在`<style>`标签内添加：

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Microsoft YaHei', sans-serif;
    background: linear-gradient(135deg, #F5F0E1 0%, #E8E0C8 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.container {
    display: flex;
    gap: 30px;
    max-width: 1200px;
    width: 100%;
    background: white;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(196, 30, 58, 0.15);
    overflow: hidden;
}

/* 角色展示区 */
.character-section {
    flex: 0 0 400px;
    background: linear-gradient(180deg, #87CEEB 0%, #98FB98 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
}

#characterCanvas {
    display: block;
}

/* 对话交互区 */
.chat-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 600px;
}

.chat-header {
    padding: 20px;
    background: #C41E3A;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-header h2 {
    font-size: 24px;
}

.status {
    font-size: 14px;
    opacity: 0.9;
}

.chat-messages {
    flex: 1;
    padding: 20px;
    overflow-y: auto;
    background: #f9f9f9;
}

.message {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
}

.message.user {
    align-items: flex-end;
}

.message.assistant {
    align-items: flex-start;
}

.message-bubble {
    max-width: 80%;
    padding: 12px 18px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.5;
}

.message.user .message-bubble {
    background: #C41E3A;
    color: white;
    border-bottom-right-radius: 4px;
}

.message.assistant .message-bubble {
    background: white;
    color: #333;
    border: 1px solid #e0e0e0;
    border-bottom-left-radius: 4px;
}

.chat-input {
    padding: 20px;
    background: white;
    border-top: 1px solid #e0e0e0;
    display: flex;
    gap: 10px;
}

.chat-input input {
    flex: 1;
    padding: 12px 18px;
    border: 2px solid #e0e0e0;
    border-radius: 25px;
    font-size: 15px;
    outline: none;
    transition: border-color 0.3s;
}

.chat-input input:focus {
    border-color: #C41E3A;
}

.chat-input button {
    padding: 12px 25px;
    background: #C41E3A;
    color: white;
    border: none;
    border-radius: 25px;
    font-size: 15px;
    cursor: pointer;
    transition: background 0.3s;
}

.chat-input button:hover {
    background: #a01830;
}

/* 设置面板 */
.settings-panel {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    z-index: 1000;
    display: none;
    min-width: 300px;
}

.settings-panel.show {
    display: block;
}

.settings-panel h3 {
    margin-bottom: 20px;
    color: #C41E3A;
}

.settings-panel select,
.settings-panel input {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 14px;
}

.settings-panel button {
    width: 100%;
    padding: 12px;
    background: #C41E3A;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}

.settings-btn {
    position: fixed;
    top: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: #C41E3A;
    color: white;
    border: none;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    z-index: 999;
}

/* 快捷问题按钮 */
.quick-questions {
    padding: 10px 20px;
    background: #f5f5f5;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.quick-btn {
    padding: 8px 16px;
    background: white;
    border: 1px solid #C41E3A;
    color: #C41E3A;
    border-radius: 20px;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.3s;
}

.quick-btn:hover {
    background: #C41E3A;
    color: white;
}

/* 响应式设计 */
@media (max-width: 900px) {
    .container {
        flex-direction: column;
    }

    .character-section {
        flex: 0 0 300px;
    }
}
```

**Step 3: 在浏览器中打开验证布局**

在浏览器中打开 `网页交互.html`，确认：
- 页面显示正常
- 左侧角色区域和右侧对话区域布局正确
- 设置按钮可见

**Step 4: 提交进度**

```bash
git add 网页交互.html
git commit -m "feat: 添加基础HTML结构和CSS样式"
```

---

## Task 2: 实现小红军角色绘制

**Files:**
- Modify: `/Users/yekaige/红军数字人/网页交互.html` (script部分)

**Step 1: 创建角色绘制类**

在`<script>`标签内添加：

```javascript
// 角色绘制类
class RedArmyCharacter {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.width = canvas.width;
        this.height = canvas.height;

        // 角色状态
        this.state = 'idle'; // idle, talking, happy, thinking, salute
        this.frame = 0;
        this.animationTime = 0;

        // 角色位置
        this.x = this.width / 2;
        this.y = this.height / 2 + 50;

        // 动画参数
        this.bobOffset = 0;
        this.blinkTimer = 0;
        this.isBlinking = false;
        this.mouthOpen = 0;
        this.armAngle = 0;

        // 启动动画循环
        this.animate();
    }

    // 绘制八角帽
    drawHat() {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(this.x, this.y - 120);

        // 帽子主体
        ctx.fillStyle = '#4A5D23';
        ctx.beginPath();
        ctx.moveTo(-40, 0);
        ctx.lineTo(-30, -40);
        ctx.lineTo(30, -40);
        ctx.lineTo(40, 0);
        ctx.closePath();
        ctx.fill();

        // 帽檐
        ctx.fillStyle = '#3D4D1C';
        ctx.beginPath();
        ctx.ellipse(0, 0, 50, 15, 0, 0, Math.PI * 2);
        ctx.fill();

        // 红五星
        this.drawStar(0, -25, 12, '#FFD700', '#C41E3A');

        ctx.restore();
    }

    // 绘制五角星
    drawStar(cx, cy, size, fillColor, strokeColor) {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(cx, cy);

        ctx.fillStyle = fillColor;
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = 2;

        ctx.beginPath();
        for (let i = 0; i < 5; i++) {
            const angle = (i * 4 * Math.PI) / 5 - Math.PI / 2;
            const x = Math.cos(angle) * size;
            const y = Math.sin(angle) * size;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        ctx.restore();
    }

    // 绘制脸部
    drawFace() {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(this.x, this.y - 60);

        // 脸型
        ctx.fillStyle = '#FFE4C4';
        ctx.beginPath();
        ctx.ellipse(0, 0, 45, 50, 0, 0, Math.PI * 2);
        ctx.fill();

        // 腮红
        ctx.fillStyle = 'rgba(255, 150, 150, 0.3)';
        ctx.beginPath();
        ctx.ellipse(-30, 15, 12, 8, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(30, 15, 12, 8, 0, 0, Math.PI * 2);
        ctx.fill();

        // 眼睛
        const eyeY = -5;
        const eyeHeight = this.isBlinking ? 2 : 10;

        // 左眼
        ctx.fillStyle = '#333';
        ctx.beginPath();
        ctx.ellipse(-15, eyeY, 8, eyeHeight, 0, 0, Math.PI * 2);
        ctx.fill();

        // 右眼
        ctx.beginPath();
        ctx.ellipse(15, eyeY, 8, eyeHeight, 0, 0, Math.PI * 2);
        ctx.fill();

        // 眼睛高光
        if (!this.isBlinking) {
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(-12, eyeY - 3, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(18, eyeY - 3, 3, 0, Math.PI * 2);
            ctx.fill();
        }

        // 眉毛
        ctx.strokeStyle = '#5D4037';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';

        ctx.beginPath();
        ctx.moveTo(-22, eyeY - 18);
        ctx.quadraticCurveTo(-15, eyeY - 22, -8, eyeY - 18);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(8, eyeY - 18);
        ctx.quadraticCurveTo(15, eyeY - 22, 22, eyeY - 18);
        ctx.stroke();

        // 嘴巴
        ctx.fillStyle = '#C41E3A';
        ctx.strokeStyle = '#8B0000';
        ctx.lineWidth = 2;

        if (this.state === 'talking') {
            // 说话时嘴巴张开
            const mouthHeight = 5 + this.mouthOpen * 10;
            ctx.beginPath();
            ctx.ellipse(0, 25, 12, mouthHeight, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        } else if (this.state === 'happy') {
            // 开心的笑容
            ctx.beginPath();
            ctx.arc(0, 20, 15, 0.1 * Math.PI, 0.9 * Math.PI);
            ctx.stroke();
        } else {
            // 普通表情
            ctx.beginPath();
            ctx.arc(0, 20, 10, 0.2 * Math.PI, 0.8 * Math.PI);
            ctx.stroke();
        }

        ctx.restore();
    }

    // 绘制身体
    drawBody() {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(this.x, this.y + 30);

        // 军装主体
        ctx.fillStyle = '#4A5D23';
        ctx.beginPath();
        ctx.moveTo(-35, -20);
        ctx.lineTo(-40, 80);
        ctx.lineTo(40, 80);
        ctx.lineTo(35, -20);
        ctx.closePath();
        ctx.fill();

        // 衣领
        ctx.fillStyle = '#3D4D1C';
        ctx.beginPath();
        ctx.moveTo(-20, -20);
        ctx.lineTo(0, 10);
        ctx.lineTo(20, -20);
        ctx.lineTo(15, -25);
        ctx.lineTo(0, 0);
        ctx.lineTo(-15, -25);
        ctx.closePath();
        ctx.fill();

        // 腰带
        ctx.fillStyle = '#8B4513';
        ctx.fillRect(-40, 40, 80, 12);

        // 腰带扣
        ctx.fillStyle = '#FFD700';
        ctx.fillRect(-8, 42, 16, 8);

        ctx.restore();
    }

    // 绘制手臂
    drawArms() {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(this.x, this.y + 20);

        // 左臂
        ctx.save();
        ctx.translate(-40, 0);
        ctx.rotate(-0.3 + Math.sin(this.armAngle) * 0.1);
        ctx.fillStyle = '#4A5D23';
        ctx.beginPath();
        ctx.ellipse(0, 30, 12, 35, 0, 0, Math.PI * 2);
        ctx.fill();
        // 手
        ctx.fillStyle = '#FFE4C4';
        ctx.beginPath();
        ctx.ellipse(0, 65, 10, 12, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // 右臂 (敬礼时抬起)
        ctx.save();
        ctx.translate(40, 0);

        if (this.state === 'salute') {
            // 敬礼姿势
            ctx.rotate(-1.5);
            ctx.fillStyle = '#4A5D23';
            ctx.beginPath();
            ctx.ellipse(0, -30, 12, 35, 0, 0, Math.PI * 2);
            ctx.fill();
            // 手
            ctx.fillStyle = '#FFE4C4';
            ctx.beginPath();
            ctx.ellipse(0, -65, 10, 12, 0, 0, Math.PI * 2);
            ctx.fill();
        } else {
            ctx.rotate(0.3 + Math.sin(this.armAngle) * 0.1);
            ctx.fillStyle = '#4A5D23';
            ctx.beginPath();
            ctx.ellipse(0, 30, 12, 35, 0, 0, Math.PI * 2);
            ctx.fill();
            // 手
            ctx.fillStyle = '#FFE4C4';
            ctx.beginPath();
            ctx.ellipse(0, 65, 10, 12, 0, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.restore();

        ctx.restore();
    }

    // 绘制腿脚
    drawLegs() {
        const ctx = this.ctx;
        ctx.save();
        ctx.translate(this.x, this.y + 110);

        // 裤腿
        ctx.fillStyle = '#3D4D1C';

        // 左腿
        ctx.fillRect(-25, 0, 20, 50);

        // 右腿
        ctx.fillRect(5, 0, 20, 50);

        // 草鞋
        ctx.fillStyle = '#D2691E';

        // 左脚
        ctx.beginPath();
        ctx.ellipse(-15, 55, 18, 8, 0, 0, Math.PI * 2);
        ctx.fill();

        // 右脚
        ctx.beginPath();
        ctx.ellipse(15, 55, 18, 8, 0, 0, Math.PI * 2);
        ctx.fill();

        // 草鞋绑带
        ctx.strokeStyle = '#8B4513';
        ctx.lineWidth = 2;

        ctx.beginPath();
        ctx.moveTo(-25, 45);
        ctx.lineTo(-5, 50);
        ctx.moveTo(-15, 40);
        ctx.lineTo(-15, 50);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(5, 45);
        ctx.lineTo(25, 50);
        ctx.moveTo(15, 40);
        ctx.lineTo(15, 50);
        ctx.stroke();

        ctx.restore();
    }

    // 更新动画状态
    updateAnimation(deltaTime) {
        this.animationTime += deltaTime;

        // 呼吸/晃动效果
        this.bobOffset = Math.sin(this.animationTime * 2) * 3;

        // 眨眼
        this.blinkTimer += deltaTime;
        if (this.blinkTimer > 3) {
            this.isBlinking = true;
            if (this.blinkTimer > 3.15) {
                this.isBlinking = false;
                this.blinkTimer = 0;
            }
        }

        // 说话时嘴巴动画
        if (this.state === 'talking') {
            this.mouthOpen = (Math.sin(this.animationTime * 10) + 1) / 2;
        } else {
            this.mouthOpen = 0;
        }

        // 手臂摆动
        this.armAngle = this.animationTime * 2;
    }

    // 绘制完整角色
    draw() {
        this.ctx.clearRect(0, 0, this.width, this.height);

        this.ctx.save();
        this.ctx.translate(0, this.bobOffset);

        this.drawLegs();
        this.drawBody();
        this.drawArms();
        this.drawFace();
        this.drawHat();

        this.ctx.restore();
    }

    // 动画循环
    animate() {
        const now = performance.now();
        const deltaTime = (now - (this.lastTime || now)) / 1000;
        this.lastTime = now;

        this.updateAnimation(deltaTime);
        this.draw();

        requestAnimationFrame(() => this.animate());
    }

    // 设置状态
    setState(state) {
        this.state = state;
    }
}
```

**Step 2: 初始化角色**

在角色类定义后添加：

```javascript
// 初始化角色
const canvas = document.getElementById('characterCanvas');
const character = new RedArmyCharacter(canvas);
```

**Step 3: 在浏览器中验证角色绘制**

刷新页面，确认：
- 小红军角色正确显示
- 角色有轻微的呼吸晃动效果
- 眨眼动画正常

**Step 4: 提交进度**

```bash
git add 网页交互.html
git commit -m "feat: 实现小红军角色Canvas绘制和动画"
```

---

## Task 3: 实现对话界面功能

**Files:**
- Modify: `/Users/yekaige/红军数字人/网页交互.html` (script部分)

**Step 1: 添加消息显示功能**

在初始化代码后添加：

```javascript
// 聊天管理器
class ChatManager {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');

        // 长征知识库 - 作为对话上下文
        this.knowledgeBase = `
你是长征小红军，一个可爱、亲切的红军小战士形象。你用生动、易懂的语言向用户介绍长征相关的知识。

关于长征的重要知识：

【历史事件】
1. 飞夺泸定桥（1935年5月）：红军22名勇士冒着枪林弹雨，攀踏铁索，夺取泸定桥，这是长征中最惊险的战斗之一。

2. 四渡赤水（1935年1-3月）：毛泽东指挥红军四次渡过赤水河，巧妙地调动敌人，是运动战的典范。

3. 强渡大渡河（1935年5月）：17名勇士冒着敌人的炮火，强渡大渡河，为红军北上打开通道。

4. 爬雪山过草地（1935年6-8月）：红军翻越夹金山等雪山，穿越松潘草地，克服了极端恶劣的自然环境。

5. 遵义会议（1935年1月）：确立了毛泽东在党中央的领导地位，是长征的转折点。

6. 会宁会师（1936年10月）：红军三大主力在甘肃会宁会师，标志着长征的胜利结束。

【人物故事】
- 小红军的故事：很多和你一样的小战士，年纪虽小但意志坚定，他们相互帮助、共同前进。

- 红军将领：朱德、周恩来、刘伯承等将领身先士卒，与战士同甘共苦。

【地理路线】
长征从江西瑞金出发，途经湖南、贵州、四川、甘肃等省，最后到达陕北，全程约二万五千里。

【长征精神】
长征精神包括：不怕牺牲、坚韧不拔、团结互助、勇往直前。这种精神激励着一代又一代中国人。

请用亲切、生动的语言回答用户的问题，像讲故事一样介绍长征知识。回答要简洁，每次回复控制在100字以内。
`;

        this.init();
    }

    init() {
        // 绑定发送事件
        this.sendBtn.addEventListener('click', () => this.sendMessage());

        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // 显示欢迎消息
        this.addMessage('assistant', '你好呀！我是长征小红军！有什么想了解的长征故事吗？我可以给你讲讲飞夺泸定桥、爬雪山过草地的故事哦！');
    }

    // 添加消息到界面
    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = content;

        messageDiv.appendChild(bubbleDiv);
        this.messagesContainer.appendChild(messageDiv);

        // 滚动到底部
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;

        // 如果是助手消息，触发角色说话动画
        if (role === 'assistant') {
            character.setState('talking');
            setTimeout(() => character.setState('idle'), 3000);
        }
    }

    // 发送消息
    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;

        // 显示用户消息
        this.addMessage('user', message);
        this.userInput.value = '';

        // 显示加载状态
        this.sendBtn.disabled = true;
        this.sendBtn.textContent = '思考中...';
        character.setState('thinking');

        try {
            // 调用AI获取回复
            const response = await this.callAI(message);
            this.addMessage('assistant', response);
            character.setState('happy');
        } catch (error) {
            console.error('AI调用失败:', error);
            this.addMessage('assistant', '抱歉，我现在有点累了，请稍后再问我吧~');
            character.setState('idle');
        } finally {
            this.sendBtn.disabled = false;
            this.sendBtn.textContent = '发送';
        }
    }

    // 调用AI API
    async callAI(message) {
        const provider = localStorage.getItem('apiProvider') || 'qwen';
        const apiKey = localStorage.getItem('apiKey');

        if (!apiKey) {
            return '请先点击右上角的设置按钮，配置API Key哦！这样我才能更好地回答你的问题~';
        }

        // 根据不同服务商调用API
        switch (provider) {
            case 'qwen':
                return await this.callQwenAPI(message, apiKey);
            case 'wenxin':
                return await this.callWenxinAPI(message, apiKey);
            case 'xunfei':
                return await this.callXunfeiAPI(message, apiKey);
            default:
                return '请选择一个AI服务商~';
        }
    }

    // 通义千问API调用
    async callQwenAPI(message, apiKey) {
        const response = await fetch('https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: 'qwen-turbo',
                input: {
                    messages: [
                        { role: 'system', content: this.knowledgeBase },
                        { role: 'user', content: message }
                    ]
                }
            })
        });

        const data = await response.json();
        return data.output.text || data.output.choices[0].message.content;
    }

    // 文心一言API调用（简化版，实际需要获取access_token）
    async callWenxinAPI(message, apiKey) {
        // 注意：文心一言需要先获取access_token
        return '文心一言接口配置较复杂，建议使用通义千问~';
    }

    // 讯飞星火API调用（简化版）
    async callXunfeiAPI(message, apiKey) {
        return '讯飞星火接口需要WebSocket，建议使用通义千问~';
    }
}

// 初始化聊天管理器
const chatManager = new ChatManager();
```

**Step 2: 添加快捷问题按钮**

在HTML的chat-messages div后、chat-input div前添加：

```html
<div class="quick-questions">
    <button class="quick-btn" data-question="什么是长征？">什么是长征？</button>
    <button class="quick-btn" data-question="飞夺泸定桥的故事">飞夺泸定桥</button>
    <button class="quick-btn" data-question="爬雪山过草地">爬雪山过草地</button>
    <button class="quick-btn" data-question="长征精神是什么？">长征精神</button>
</div>
```

在ChatManager的init方法中添加：

```javascript
// 绑定快捷问题按钮
document.querySelectorAll('.quick-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        this.userInput.value = btn.dataset.question;
        this.sendMessage();
    });
});
```

**Step 3: 在浏览器中验证对话功能**

刷新页面，确认：
- 欢迎消息正确显示
- 输入框可以输入文字
- 点击发送按钮可以发送消息
- 快捷问题按钮可以点击

**Step 4: 提交进度**

```bash
git add 网页交互.html
git commit -m "feat: 实现对话界面和AI调用功能"
```

---

## Task 4: 实现设置面板功能

**Files:**
- Modify: `/Users/yekaige/红军数字人/网页交互.html` (script部分)

**Step 1: 添加设置面板逻辑**

在ChatManager类后添加：

```javascript
// 设置管理器
class SettingsManager {
    constructor() {
        this.panel = document.getElementById('settingsPanel');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.saveBtn = document.getElementById('saveSettings');
        this.apiProviderSelect = document.getElementById('apiProvider');
        this.apiKeyInput = document.getElementById('apiKey');

        this.init();
    }

    init() {
        // 加载保存的设置
        this.loadSettings();

        // 绑定事件
        this.settingsBtn.addEventListener('click', () => this.togglePanel());
        this.saveBtn.addEventListener('click', () => this.saveSettings());

        // 点击面板外部关闭
        document.addEventListener('click', (e) => {
            if (!this.panel.contains(e.target) && !this.settingsBtn.contains(e.target)) {
                this.panel.classList.remove('show');
            }
        });
    }

    togglePanel() {
        this.panel.classList.toggle('show');
    }

    loadSettings() {
        const provider = localStorage.getItem('apiProvider');
        const apiKey = localStorage.getItem('apiKey');

        if (provider) {
            this.apiProviderSelect.value = provider;
        }
        if (apiKey) {
            this.apiKeyInput.value = apiKey;
        }
    }

    saveSettings() {
        const provider = this.apiProviderSelect.value;
        const apiKey = this.apiKeyInput.value;

        localStorage.setItem('apiProvider', provider);
        localStorage.setItem('apiKey', apiKey);

        // 显示保存成功提示
        this.saveBtn.textContent = '保存成功！';
        setTimeout(() => {
            this.saveBtn.textContent = '保存配置';
            this.panel.classList.remove('show');
        }, 1000);
    }
}

// 初始化设置管理器
const settingsManager = new SettingsManager();
```

**Step 2: 添加敬礼彩蛋**

在ChatManager的addMessage方法中，检测特定关键词触发敬礼：

```javascript
// 在addMessage方法中添加
if (role === 'assistant' && (content.includes('红军') || content.includes('同志'))) {
    // 随机触发敬礼动画
    if (Math.random() > 0.5) {
        setTimeout(() => {
            character.setState('salute');
            setTimeout(() => character.setState('idle'), 2000);
        }, 1000);
    }
}
```

**Step 3: 在浏览器中验证设置功能**

刷新页面，确认：
- 点击设置按钮可以打开设置面板
- 可以选择AI服务商
- 可以保存API Key
- 刷新页面后设置仍然保留

**Step 4: 提交进度**

```bash
git add 网页交互.html
git commit -m "feat: 实现设置面板和配置保存功能"
```

---

## Task 5: 优化和完善

**Files:**
- Modify: `/Users/yekaige/红军数字人/网页交互.html`

**Step 1: 添加打字效果**

在ChatManager中添加打字效果方法：

```javascript
// 打字效果显示消息
async addMessageWithTyping(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    messageDiv.appendChild(bubbleDiv);
    this.messagesContainer.appendChild(messageDiv);

    // 打字效果
    character.setState('talking');
    for (let i = 0; i < content.length; i++) {
        bubbleDiv.textContent += content[i];
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        await new Promise(resolve => setTimeout(resolve, 30));
    }

    character.setState('idle');
}
```

**Step 2: 添加加载动画**

在CSS中添加：

```css
/* 加载动画 */
.typing-indicator {
    display: flex;
    gap: 5px;
    padding: 10px;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: #C41E3A;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}
```

**Step 3: 添加页面加载动画**

在HTML的container div前添加：

```html
<!-- 加载动画 -->
<div class="loading-screen" id="loadingScreen">
    <div class="loading-content">
        <div class="loading-star">⭐</div>
        <p>长征小红军正在准备...</p>
    </div>
</div>
```

在CSS中添加：

```css
.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #F5F0E1;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
    transition: opacity 0.5s;
}

.loading-screen.hidden {
    opacity: 0;
    pointer-events: none;
}

.loading-content {
    text-align: center;
}

.loading-star {
    font-size: 60px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
```

在JavaScript初始化代码最后添加：

```javascript
// 隐藏加载动画
setTimeout(() => {
    document.getElementById('loadingScreen').classList.add('hidden');
}, 1500);
```

**Step 4: 最终测试**

在浏览器中测试所有功能：
- 页面加载动画正常
- 角色动画流畅
- 对话功能正常
- 设置保存功能正常
- 快捷问题按钮正常

**Step 5: 提交最终版本**

```bash
git add 网页交互.html
git commit -m "feat: 完成长征小红军数字人功能实现"
```

---

## 完成检查清单

- [ ] 页面布局正确显示
- [ ] 小红军角色正确绘制
- [ ] 角色动画效果正常（呼吸、眨眼、说话）
- [ ] 对话界面可以正常输入和显示
- [ ] 快捷问题按钮可以正常工作
- [ ] 设置面板可以保存配置
- [ ] API调用功能正常（需要配置API Key）
- [ ] 页面加载动画正常
- [ ] 响应式布局在移动端正常显示
