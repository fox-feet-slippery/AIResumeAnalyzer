# 🤖 AI智能简历分析系统

一款基于人工智能技术的简历解析与岗位匹配平台，帮助招聘者快速筛选候选人，实现人岗精准匹配。

## 📋 项目概述

本系统采用前后端分离架构，集成百度千帆AI大模型实现智能分析。支持PDF简历自动解析、关键信息提取、智能岗位推荐、多维度匹配度评估等功能。

## ✨ 功能特性

### 模块一：简历上传与解析

- ✅ 支持PDF格式简历上传
- ✅ 多页简历解析（pdfplumber + PyPDF2）
- ✅ 文本清洗和结构化处理
- ✅ 保留特殊字符（如C++、C#）

### 模块二：AI智能信息提取

- ✅ **基本信息**：姓名、电话、邮箱、地址
- ✅ **求职信息**：求职意向、期望薪资
- ✅ **背景信息**：工作年限、学历背景、项目经历
- ✅ **技能提取**：自动识别技术栈

### 模块三：智能岗位推荐

- ✅ 根据简历内容智能推荐10+个匹配岗位
- ✅ 支持用户自主选择或手动输入
- ✅ 基于技能、经验、学历多维度推荐

### 模块四：匹配度分析

- ✅ 多维度匹配度评分：
  - 综合匹配度（0-100分）
  - 技能匹配率
  - 经验相关性
  - 学历匹配度
- ✅ AI智能分析匹配结果
- ✅ 个性化改进建议

### 模块五：缓存机制

- ✅ 内存缓存（无需Redis依赖）
- ✅ 避免重复解析，提升响应效率

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端应用                              │
│              React 18 + TypeScript + Ant Design             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        后端服务                              │
│                    FastAPI + Python 3.11                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  PDF解析    │  │  AI提取     │  │  匹配分析   │         │
│  │ pdfplumber  │  │ 百度千帆AI  │  │  本地规则   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        缓存层                                │
│                     内存缓存                                 │
└─────────────────────────────────────────────────────────────┘
```

### 后端技术栈

| 技术       | 说明               |
| ---------- | ------------------ |
| FastAPI    | 高性能异步Web框架  |
| pdfplumber | PDF文本提取        |
| PyPDF2     | PDF备用解析        |
| 百度千帆AI | ERNIE-3.5-8K大模型 |
| Pydantic   | 数据验证           |

### 前端技术栈

| 技术         | 说明       |
| ------------ | ---------- |
| React 18     | 前端框架   |
| TypeScript   | 类型安全   |
| Ant Design 5 | UI组件库   |
| Axios        | HTTP客户端 |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 16+
- 百度千帆API密钥

### 1. 克隆项目

```bash
git clone <repository-url>
cd AI智能简历分析系统
```

### 2. 后端配置与启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 编辑 .env 文件，配置百度千帆API密钥
# QIANFAN_API_KEY=your_api_key

# 启动服务
python -m uvicorn app.main:app --reload --port 8000
```

### 3. 前端配置与启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

### 4. 访问应用

打开浏览器访问：http://localhost:3000

## 📡 API文档

启动后端服务后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

#### 1. 上传简历

```http
POST /api/resume/upload
Content-Type: multipart/form-data

file: <PDF文件>
```

**响应示例：**

```json
{
  "success": true,
  "message": "简历解析成功",
  "data": {
    "basic": { "name": "张三", "phone": "13800138000" },
    "skills": ["C++", "Python"],
    "file_hash": "abc123..."
  }
}
```

#### 2. 推荐岗位

```http
POST /api/matching/recommend-job?resume_file_hash=xxx
```

**响应示例：**

```json
{
  "success": true,
  "message": "成功推荐10个岗位",
  "data": {
    "job_descriptions": [
      "C++开发工程师，熟悉C++11/14/17标准...",
      "C++后端开发工程师，精通STL..."
    ]
  }
}
```

#### 3. 计算匹配度

```http
POST /api/matching/score
Content-Type: application/json

{
  "resume_file_hash": "abc123...",
  "job_description": "C++开发工程师..."
}
```

**响应示例：**

```json
{
  "success": true,
  "message": "匹配度计算成功",
  "data": {
    "scores": {
      "overall_score": 85,
      "skill_match_rate": 90,
      "experience_relevance": 80,
      "education_match": 85
    },
    "analysis": {
      "matched_skills": ["C++", "STL"],
      "missing_skills": ["Linux"],
      "suggestions": ["建议补充Linux开发经验"]
    }
  }
}
```

## ⚙️ 环境变量配置

### 后端 (.env)

```env
# 百度千帆AI配置（必填）
QIANFAN_API_KEY=your_qianfan_api_key

# 阿里云DashScope配置（可选）
DASHSCOPE_API_KEY=your_dashscope_api_key

# 缓存配置
CACHE_TTL=3600
```

### 获取百度千帆API密钥

1. 访问 [百度智能云](https://cloud.baidu.com/)
2. 开通千帆大模型服务
3. 创建应用获取API Key

## 📁 项目结构

```
AI智能简历分析系统/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── resume.py      # 简历接口
│   │   │   └── matching.py    # 匹配接口
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 配置管理
│   │   │   └── cache.py       # 缓存管理
│   │   ├── models/            # 数据模型
│   │   │   └── schemas.py     # Pydantic模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── pdf_parser.py  # PDF解析
│   │   │   ├── ai_extractor.py # AI提取
│   │   │   └── local_extractor.py # 本地提取
│   │   └── main.py            # 应用入口
│   ├── requirements.txt       # Python依赖
│   ├── Dockerfile             # Docker配置
│   └── .env                   # 环境变量
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   │   ├── ResumeUpload.tsx    # 上传组件
│   │   │   ├── ResumeInfo.tsx      # 信息展示
│   │   │   ├── JobMatching.tsx     # 岗位匹配
│   │   │   └── MatchingResult.tsx  # 结果展示
│   │   ├── services/          # API服务
│   │   │   └── api.ts         # Axios封装
│   │   ├── types/             # TypeScript类型
│   │   │   └── index.ts       # 类型定义
│   │   └── App.tsx            # 主应用
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## 🎯 使用流程

1. **上传简历**：拖拽或点击上传PDF格式简历
2. **查看解析结果**：系统自动提取关键信息
3. **进入岗位匹配**：点击"进入岗位匹配"
4. **获取推荐岗位**：点击"提取关键词"获取AI推荐的10+个岗位
5. **选择岗位**：点击感兴趣的岗位，自动填充到输入框
6. **开始匹配分析**：查看详细的匹配度评分和改进建议

## 📝 注意事项

1. **API密钥安全**：请勿将API密钥提交到代码仓库
2. **文件格式**：仅支持PDF格式简历
3. **文件大小**：默认限制10MB
4. **缓存策略**：解析结果默认缓存1小时
5. **网络要求**：需要访问百度千帆API服务

## 🔧 开发计划

- [x] 项目架构设计
- [x] PDF解析模块
- [x] AI信息提取
- [x] 智能岗位推荐
- [x] 匹配评分算法
- [x] 前端页面开发
- [ ] Docker容器化部署
- [ ] 批量简历处理
- [ ] 更多AI模型支持

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**Made with ❤️ by AI Developer**
