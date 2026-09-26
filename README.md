# 832401224_calculator_backend

前后端分离计算器系统的**后端**服务（学号：832401224 / 谢宇城）。

前端仓库：[`832401224_calculator_frontend`](https://github.com/xie-yu520/832401224_calculator_frontend)

---

## 1. 项目介绍

本项目是「第一次作业——前后端分离计算器系统」的后端部分，对外提供一组 REST API：

- 接收前端传来的**数学表达式字符串**，在服务端完成解析与计算后返回结果；
- 把每一次成功的计算**持久化写入 SQLite 数据库**；
- 提供计算历史的查询（分页 + 关键字搜索）、删除、清空与收藏；
- 提供统计总览与进制转换（扩展功能）。

**核心计算 100% 在后端完成**，前端只负责展示。后端停止时，前端无法获得任何新的计算结果。
表达式解析采用自研的**词法分析 + 递归下降语法分析 + AST 求值**方案，**不使用 `eval` / `exec`**。

## 2. 技术栈

| 类别 | 选型 | 说明 |
| --- | --- | --- |
| 语言 | Python 3.9+ | 仅在 3.13 上做过完整测试 |
| Web 框架 | Flask 3.x | 轻量，路由清晰 |
| 跨域 | Flask-CORS | 支持前后端分离部署 |
| 数据库 | SQLite 3 | 标准库 `sqlite3`，无需安装数据库服务 |
| 表达式解析 | 自研（`src/calculator/`） | 词法 → 语法 → AST 求值，零第三方依赖 |

## 3. 运行环境

- Python 3.9 及以上（推荐 3.11+）
- pip
- 无需数据库服务，数据文件为项目内 `data/calculator.db`（首次启动自动创建）

## 4. 安装方法

```bash
# 1) 进入项目目录
cd 832401224_calculator_backend

# 2)（推荐）创建虚拟环境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3) 安装依赖
pip install -r requirements.txt
```

依赖只有两个：`Flask`、`Flask-CORS`。

## 5. 启动方法

```bash
python run.py
```

默认监听 `http://0.0.0.0:5000`。启动时会**自动建表**（幂等），无需手工执行 SQL。

验证是否启动成功：

```bash
curl http://127.0.0.1:5000/api/health
# {"service":"calculator-backend","status":"ok","success":true}
```

## 6. 配置说明

全部配置通过环境变量注入，未设置时使用默认值：

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PORT` / `CALCULATOR_PORT` | `5000` | 监听端口（云平台通常注入 `PORT`） |
| `CALCULATOR_HOST` | `0.0.0.0` | 监听地址 |
| `CALCULATOR_DB_PATH` | `<项目根>/data/calculator.db` | SQLite 文件路径 |
| `CALCULATOR_CORS_ORIGINS` | `*` | 允许的跨域来源 |
| `CALCULATOR_DEBUG` | `false` | 是否开启调试模式 |

Windows PowerShell 示例：

```powershell
$env:CALCULATOR_PORT=8000
python run.py
```

## 7. 数据库初始化方式

**无需手动初始化。** `create_app()` 启动时会调用 `init_database()` 执行 `CREATE TABLE IF NOT EXISTS`。

若希望手动建表或重置数据：

```bash
# 手动建表（幂等）
python -c "from src.app import create_app; create_app()"

# 重置数据：直接删除数据库文件即可，下次启动会重建
# Windows:
del data\calculator.db
# macOS / Linux:
rm -f data/calculator.db
```

表结构：

```sql
CREATE TABLE IF NOT EXISTS calculation_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    expression  TEXT    NOT NULL,   -- 计算表达式
    result      REAL    NOT NULL,   -- 计算结果
    created_at  TEXT    NOT NULL,   -- 计算时间（UTC+8，格式 YYYY-MM-DD HH:MM:SS）
    is_favorite INTEGER NOT NULL DEFAULT 0  -- 是否收藏（扩展功能）
);
CREATE INDEX IF NOT EXISTS idx_history_created_at
    ON calculation_history (created_at DESC);
```

## 8. 前后端连接方式

后端已开启 CORS（`Access-Control-Allow-Origin` 放行 `/api/*`），前端只需把 API 地址指向后端即可：

1. 启动后端（`python run.py`，默认 `http://127.0.0.1:5000`）；
2. 打开前端页面，页面底部「后端地址」输入框填写 `http://127.0.0.1:5000`，点击保存；
   - 也可以在前端页面 URL 后追加 `?api=http://127.0.0.1:5000` 临时覆盖；
3. 页面右上角的状态指示灯变绿即表示连通。

> 若前端通过 `https://` 访问，后端也必须部署为 `https://`，否则浏览器会因混合内容策略拦截请求。

## 9. 目录结构

```
832401224_calculator_backend/
├── src/
│   ├── app.py                      # Flask 应用工厂、CORS、统一异常处理
│   ├── config.py                   # 配置（全部支持环境变量覆盖）
│   ├── calculator/                 # 表达式计算核心（无第三方依赖）
│   │   ├── tokenizer.py            #   词法分析
│   │   ├── parser.py               #   递归下降语法分析，产出 AST
│   │   ├── evaluator.py            #   AST 求值，函数表与常量表
│   │   ├── expression.py           #   门面：校验→词法→语法→求值
│   │   ├── tokens.py               #   Token 定义
│   │   └── exceptions.py           #   领域异常（携带 code / http_status）
│   ├── controller/
│   │   └── api_controller.py       # HTTP 路由，不含业务逻辑
│   ├── service/
│   │   ├── calculator_service.py   # 计算用例（先算后存）
│   │   ├── history_service.py      # 历史查询/删除/清空/收藏
│   │   ├── statistics_service.py   # 统计总览
│   │   └── conversion_service.py   # 进制转换
│   ├── model/
│   │   ├── calculation_history.py  # 历史领域模型
│   │   └── api_response.py         # 统一响应信封
│   └── repository/
│       ├── database.py             # 连接管理与建表
│       └── history_repository.py   # 唯一书写 SQL 的地方
├── run.py                          # 启动入口
├── requirements.txt
├── codestyle.md                    # 代码规范（基于 PEP 8）
├── web/                            # 部署副本：前端静态页面（不入库，见下方说明）
└── data/                           # SQLite 数据文件（首次启动生成）
```

> **关于 `web/` 目录**：这是部署时从 `832401224_calculator_frontend/src` 拷贝过来的前端静态文件副本，
> 仅用于让部署环境用一个地址同时访问前后端。它已写入 `.gitignore`，**前端代码以后端仓库之外的前端仓库为唯一来源**。
> 若该目录不存在（例如本地只做接口调试），Flask 不会注册静态路由，后端行为不变。
> 前端依旧通过 HTTP 接口 `/api/*` 获取结果，不做本地计算，前后端分离架构不变。

## 10. API 文档

统一响应信封：

```json
{ "success": true,  "...": "业务字段" }
{ "success": false, "code": "ERROR_CODE", "message": "English message" }
```

| 方法 | 路径 | 说明 | 成功状态码 |
| --- | --- | --- | --- |
| GET | `/api/health` | 健康检查 | 200 |
| POST | `/api/calculate` | 计算表达式并落库 | 200 |
| GET | `/api/history` | 分页查询历史 | 200 |
| DELETE | `/api/history/{id}` | 删除指定记录 | **204 No Content** |
| DELETE | `/api/history` | 清空全部历史 | 200 |
| PATCH | `/api/history/{id}/favorite` | 切换收藏 | 200 |
| GET | `/api/statistics` | 统计总览 | 200 |
| POST | `/api/convert` | 进制转换 | 200 |

**计算示例**

```bash
curl -X POST http://127.0.0.1:5000/api/calculate \
     -H "Content-Type: application/json" \
     -d '{"expression":"(1+2)*3"}'
```

```json
{
  "success": true,
  "id": 1,
  "expression": "(1+2)*3",
  "result": 9.0,
  "created_at": "2026-09-27 00:32:31",
  "is_favorite": false
}
```

**错误示例**

```json
{ "success": false, "code": "INVALID_EXPRESSION", "message": "Invalid expression" }
{ "success": false, "code": "DIVISION_BY_ZERO",   "message": "Division by zero" }
```

**查询历史参数**：`limit`（默认 20，最大 100）、`offset`（默认 0）、`keyword`（按表达式或结果模糊搜索）、`favorite=true`（只看收藏）。

**错误码**：`EMPTY_EXPRESSION`、`EXPRESSION_TOO_LONG`、`INVALID_CHARACTER`、`INVALID_EXPRESSION`、`DIVISION_BY_ZERO`、`MATH_DOMAIN_ERROR`、`RESULT_OVERFLOW`、`UNKNOWN_FUNCTION`、`UNKNOWN_CONSTANT`、`HISTORY_NOT_FOUND`(404)、`INVALID_PARAMETER`、`CONVERSION_ERROR`。

## 11. 支持的表达式语法

- 四则运算 `+ - * /`、取模 `%`、乘方 `^`
- 括号 `()`、一元正负号 `-5` / `3 * -2` / `-(1+2)` / `2^-3`
- 小数 `3.14` / `.5` / `5.`，科学计数法 `1e3` / `2.5e-4`
- 常量 `pi` / `π` / `e` / `tau`
- 函数：`sin cos tan asin acos atan sinh cosh tanh ln log log2 exp sqrt cbrt pow fact factorial abs floor ceil round sign rad deg max min mod`
- 三角函数参数为**弧度**；`ln` 为自然对数，`log` 为常用对数（底 10）
- 界面上的 `×` `÷` 与全角括号会被自动归一化为 `* / ( )`

安全策略：输入先过**长度上限（256）+ 字符白名单**，再进入解析器；全程不调用 `eval` / `exec`。

## 12. 代码规范

见 [`codestyle.md`](./codestyle.md)，以 **PEP 8** 为基准。
