# GPAFP - 黄金价格分析与预测平台

GPAFP (Gold Price Analysis & Forecast Platform) 是一个端到端的黄金价格趋势分析与预测系统。它集成了数据采集、清洗、实时监控、技术指标分析及价格预测功能，为分析师和交易员提供决策支持。

## 🛠 技术栈

### 后端 (Backend)
- **核心框架**: FastAPI (Python 3.10+)
- **数据库**: MySQL 8.0 + SQLAlchemy ORM
- **任务调度**: APScheduler (数据采集与定时任务)
- **认证安全**: OAuth2 + JWT

### 前端 (Frontend)
- **核心框架**: Vue 3 + TypeScript + Vite
- **UI 组件库**: Element Plus
- **图表可视化**: ECharts 5
- **状态管理**: Pinia

---

## 🚀 快速开始

### 1. 环境准备
确保您的开发环境已安装以下软件：
- Python 3.10+
- Node.js 16+
- MySQL 8.0+
- Git

### 2. 获取代码
```bash
git clone https://github.com/bzgz-tech/GPAFP.git
cd GPAFP
```

### 3. 数据库配置
1. 登录 MySQL 并创建一个新的数据库（例如 `gpafp`）：
   ```sql
   CREATE DATABASE gpafp CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
   ```
2. 在 `backend` 目录下创建一个 `.env` 文件，配置数据库连接信息：
   ```ini
   # backend/.env
   DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/gpafp
   SECRET_KEY=your_secret_key_here
   ```

### 4. 后端启动
```bash
cd backend

# 创建并激活虚拟环境 (Windows)
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动服务 (自动创建表结构)
python -m uvicorn app.main:app --reload --port 8000
```
后端启动成功后，API 文档地址：http://localhost:8000/docs

### 5. 前端启动
打开一个新的终端窗口：
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```
前端页面地址：http://localhost:5173

---

## 🔑 默认账号
系统初始化后，您可以通过注册页面创建新账号，或直接使用管理员功能（如有预设）。
*(注：如果数据库为空，请直接注册第一个用户)*

## 📄 许可证
[MIT License](LICENSE)
