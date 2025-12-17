# 简易作业提交系统 (Assignment Submission System)

## 1. 项目概述
本项目是一个基于 Python Flask 和 SQLite 的轻量级作业管理系统。旨在解决师生之间作业发布、提交与评分的交互需求。系统采用前后端分离的设计思想（单页应用），无需安装复杂的数据库软件，可在 Windows/Linux 环境下即开即用。

## 2. 需求分析
- **角色划分**：
  - **教师**：发布作业（标题、描述、截止日期）、查看所有学生提交、对提交进行评分（0-100分）。
  - **学生**：查看所有作业列表、提交作业内容（文本）、查看老师给出的分数。
- **登录控制**：系统需要登录才能访问，区分角色权限。

## 3. 总体设计
采用经典的三层架构：
1. **展示层 (Frontend)**：HTML5 + TailwindCSS + JavaScript (Fetch API)。单页应用设计，响应式布局。
2. **业务层 (Backend)**：Flask 框架处理路由、权限验证（Session）、业务逻辑。
3. **数据层 (Database)**：SQLite 关系型数据库，存储用户、作业及提交信息。

## 4. 详细设计 (Database & API)
### 数据库设计
包含 `users` (用户), `assignments` (作业), `submissions` (提交) 三张表，通过外键关联。密码经过 PBKDF2 哈希加密存储。

### 核心 API
- `POST /api/login`: 用户登录
- `GET /api/assignments`: 获取作业列表（根据角色返回不同数据）
- `POST /api/assignments`: 教师发布作业
- `POST /api/submissions`: 学生提交作业
- `POST /api/grade`: 教师评分

## 5. 项目实现与运行
### 环境要求
- Python 3.8+

### 运行步骤 (Windows/Linux)
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 初始化数据库（生成示例数据）：
   ```bash
   python init_db.py
   ```
3. 启动系统：
   ```bash
   python app.py
   ```
4. 浏览器访问：`http://127.0.0.1:80`

### 测试账号
- **老师**: `teacher1` / `123456`
- **学生**: `student1` / `123456`

## 6. 功能测试
1. 登录 teacher1，点击"发布新作业"，填写信息后发布，列表应更新。
2. 登录 student1，看到新作业，输入内容点击"提交"，提示成功。
3. 登录 teacher1，点击该作业的"查看提交"，给 student1 打分 90，点击打分。
4. 登录 student1，作业卡片上应显示"得分: 90"。

## 7. 改进展望
- 增加文件上传功能。
- 增加作业截止日期自动封网功能。
- 引入 Redis 替代文件系统 Session 以提升并发性能。