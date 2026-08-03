# A股量化全景监控中心 - Tushare版

> 基于Tushare免费数据源的A股实时量化监控系统

## 数据源

- **Tushare** ([tushare.pro](https://tushare.pro)) - 免费注册获取Token
- 支持A股日线行情、指数数据
- 免费版限流：500次/分钟，注册即送120积分

## 快速部署到 Render

### 第1步：获取Tushare Token

1. 访问 [tushare.pro](https://tushare.pro)
2. 注册账号 → 登录 → 右上角 **"个人主页"**
3. 复制 **Token**（一串字母数字组合）

### 第2步：部署到Render

**方式A：Blueprint一键部署**

1. Fork本项目到你的GitHub
2. 登录 [dashboard.render.com](https://dashboard.render.com)
3. **New +** → **Blueprint** → 选择仓库
4. 点击 **Apply**

**方式B：手动创建**

1. **New +** → **Web Service**
2. 连接GitHub仓库
3. 配置：
   - Runtime: `Docker`
   - Plan: `Free`
   - Dockerfile Path: `./Dockerfile`
4. 环境变量：
   | Key | Value |
   |-----|-------|
   | `HOST` | `0.0.0.0` |
   | `PORT` | `10000` |
   | `TUSHARE_TOKEN` | `你的Token` |
   | `UPDATE_INTERVAL` | `300` |
5. 点击 **Create Web Service**

### 第3步：访问

部署完成后，访问分配的域名：
```
https://a-stock-quant-monitor.onrender.com
```

## 本地测试

```bash
# 1. 安装依赖
cd backend
pip install -r requirements.txt

# 2. 设置环境变量
export TUSHARE_TOKEN=你的Token
export PORT=10000

# 3. 启动
python app.py

# 4. 访问 http://localhost:10000
```

## 自定义标的

编辑 `backend/config.py` 中的 `STOCK_SYMBOLS`，添加你想监控的股票代码。

## 技术栈

- FastAPI + WebSocket
- Pandas/NumPy 量化计算
- Tushare 免费数据源
- 原生JS前端
- Docker + Render
