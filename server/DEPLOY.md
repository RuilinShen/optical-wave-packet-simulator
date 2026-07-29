===========================
光学模拟器 — 验证服务器部署
===========================

方式一：Render（推荐）
--------------------
1. 打开 https://dashboard.render.com
2. 点 "New +" → "Web Service"
3. 连接你的 GitHub 仓库（或直接上传）
4. 设置：
   - Name: optical-simulator-api
   - Environment: Python 3
   - Root Directory: server（重要！）
   - Build Command: （留空，无依赖）
   - Start Command: python app.py
   - Plan: Free
5. 点 "Create Web Service"
6. 部署完成后得到 URL，如：
   https://optical-simulator-api.onrender.com

方式二：Railway
--------------
1. 打开 https://railway.app
2. New Project → Deploy from GitHub
3. 选择 server 目录
4. Start Command: python app.py
5. Railway 会自动分配域名

部署后修改客户端
----------------
1. 打开 src/io/sponsor.py
2. 找到 VALIDATION_SERVER = "http://localhost:5000"
3. 改为部署后的真实 URL

测试赞助码生成
--------------
部署后，在浏览器访问：
  {你的URL}/admin/register?secret=admin_oqp38se2&tier=full&days=30
（或在代码里用 POST 调用）

免费方案限制
------------
- Render 免费实例 15 分钟无访问会休眠
- 唤醒需要 30-60 秒（客户端 5 秒超时可以改为 15 秒）
- Railway 免费实例不休眠，更适合
- SQLite 数据存储在临时磁盘，重启后会丢失
  → 建议定期导出赞助码列表备份
