# 代码规范（后端 · Python）

> **规范来源：[PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)（Python 官方编码规范）**
>
> 补充参考：[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
>
> 本项目为 Python 3 项目，以 PEP 8 为基准规范；对 PEP 8 未覆盖的部分（如文档字符串格式）采用 Google Python Style Guide 的约定。

---

## 1. 文件与编码

1. 所有源文件使用 **UTF-8** 编码，不添加 BOM。
2. 文件顶部顺序：模块 docstring → `from __future__ import annotations` → 标准库导入 → 第三方库导入 → 本项目导入。三组导入之间空一行（PEP 8 的 Imports 章节）。
3. 每个模块、每个类、每个公开函数都必须有 docstring；docstring 使用中文，便于课程评审阅读。

## 2. 命名约定

| 对象 | 风格 | 示例 |
| --- | --- | --- |
| 模块 / 包 | `lowercase_with_underscores` | `history_repository.py` |
| 类 | `CapWords` | `CalculationHistory`、`HistoryRepository` |
| 函数 / 变量 | `lowercase_with_underscores` | `evaluate_expression`、`history_id` |
| 常量 | `UPPER_CASE_WITH_UNDERSCORES` | `MAX_EXPRESSION_LENGTH` |
| 私有方法 | 单个前导下划线 `_parse_term` | 仅供类内部使用 |
| 异常类 | `CapWords` + `Error` 后缀 | `DivisionByZeroError` |

## 3. 格式

1. **缩进**：4 个空格，禁止使用 Tab。
2. **行宽**：不超过 100 字符（PEP 8 建议 79，本项目在可读性前提下放宽到 100）。
3. 顶层函数 / 类之间空 **两行**，类内方法之间空 **一行**。
4. 二元运算符换行时，运算符置于**行首**（PEP 8 推荐写法）。
5. 字符串统一使用双引号 `"`；正则、SQL 等含大量引号的场景可用单引号。

## 4. 注释与文档

1. 注释解释「**为什么**」而不是「**做了什么**」；代码本身已表达清楚的不再重复注释。
2. 复杂算法（如递归下降文法）在模块 docstring 中给出文法定义。
3. 公开函数使用 Google 风格 docstring：一行摘要 + 必要的 `Args` / `Raises` / `Returns` 段落。
4. 禁止保留被注释掉的代码块；废弃代码直接删除，由版本控制系统负责追溯。

## 5. 设计约定

1. **分层职责**：`controller` 只处理 HTTP，`service` 编排用例，`repository` 只写 SQL，`calculator` 只做计算；禁止跨层调用（例如 controller 直接写 SQL）。
2. **禁止动态执行**：任何位置都不得使用 `eval` / `exec` 处理用户输入。
3. **参数化 SQL**：所有 SQL 一律使用 `?` 占位符传参，禁止字符串拼接 SQL。
4. **异常语义化**：失败路径抛出携带 `code` 与 `http_status` 的领域异常，由统一错误处理器翻译为 JSON，不在业务代码里拼装错误响应。
5. **类型标注**：公开函数签名必须有类型标注；`__init__` 返回类型标注为 `None`。

## 6. 工具

- 格式化：`pip install black && black src`
- 静态检查：`pip install flake8 && flake8 src --max-line-length=100`
- 导入排序：`pip install isort && isort src`
