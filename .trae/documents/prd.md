# 产品需求文档（PRD）v1.2：招股说明书下载 CLI 工具（MVP）

---

## 1. 产品概述

**产品名称**：IPO Prospectus Fetcher（`ipofetch`）
**定位**：第一阶段 MVP 为轻量级 Python CLI 工具，**用户直接提供招股说明书所在网页的完整 URL**，工具自动解析页面并下载 PDF 文件。
**支持市场**：中国大陆（巨潮）、香港（HKEXnews）、美国（SEC EDGAR）三大交易所公开页面。
**核心价值**：一键从已知 URL 下载 PDF，为内部研究及未来 Agentic 系统提供可靠、可编程的数据获取能力。

---

## 2. 功能需求（第一阶段）

| 功能 | 描述 |
|------|------|
| **URL 输入下载** | 通过位置参数接收招股页面 URL（`ipofetch <URL>`） |
| **PDF 自动解析** | 自动识别页面中 PDF 下载链接（支持 `.pdf` 静态链接，简易处理 JS 触发） |
| **本地保存** | 保存 PDF 至指定目录（默认 `./prospectus/`），支持自定义文件名 |
| **基础元数据** | 同步生成 JSON 文件，含原始 URL、PDF URL、下载时间、文件哈希 |
| **Python API** | 提供 `download_prospectus_from_url(url, output_dir)` 函数，供 Agentic 系统调用 |

> **不包含**：股票代码识别、自动搜索、批量股票下载、浏览器自动化。

---

## 3. 技术实现要点

- **架构**：单解析器 + 可扩展接口。初始实现通用 PDF 链接提取器（基于 `httpx` + `lxml`）。
- **页面策略**：
  - A股/HK：提取含 `.pdf` 的 `<a>` 标签，优先匹配"招股说明书"文本。
  - 美股（EDGAR）：先解析 filing 详情页中的 `.htm` 链接，再二次请求提取 PDF。
- **限制**：仅处理公开、无需登录的页面；高度依赖 JS 渲染的页面将报错提示。
- **合规**：默认请求间隔 ≥1 秒，可配置 User-Agent。
- **错误处理**：清晰提示"未找到 PDF 链接"等常见失败原因，支持 `--verbose` 调试。

---

## 4. 代码质量要求

### 4.1 开发工具链
- **Ruff**: 代码格式化和静态检查（替代 flake8, isort, black）
- **MyPy**: 静态类型检查，强制类型注解覆盖
- **Pytest**: 单元测试和集成测试框架

### 4.2 代码规范
- **Python 版本**: 3.8+ 兼容性要求
- **类型提示**: 所有公共函数必须有完整类型注解
- **行长度**: 88 字符（Black 兼容）
- **文档字符串**: Google 风格文档字符串
- **导入风格**: 单行导入，按字母顺序排序
- **复杂度限制**: McCabe 复杂度不超过 10

### 4.3 依赖管理
- **核心依赖**: typer@0.9.0+, rich@13.0.0+, httpx@0.25.0+
- **配置管理**: pydantic-settings@2.0.0+（可选）
- **HTML解析**: lxml@4.9.0+
- **开发依赖**: ruff, mypy, pytest（在 pyproject.toml 中声明）

---

## 5. 命令行接口设计

### 5.1 基本用法
```bash
# 基本下载
ipofetch https://example.com/prospectus-page

# 指定输出目录
ipofetch https://example.com/prospectus-page --output ./downloads/

# 详细输出模式
ipofetch https://example.com/prospectus-page --verbose

# 显示帮助
ipofetch --help

# 显示版本
ipofetch --version
```

### 5.2 Python API
```python
from ipofetch import download_prospectus_from_url

result = download_prospectus_from_url(
    url="https://example.com/prospectus-page",
    output_dir="./prospectus/"
)

print(f"下载成功: {result['success']}")
print(f"PDF路径: {result['pdf_path']}")
print(f"元数据路径: {result['metadata_path']}")
```

---

## 6. 错误处理和用户体验

### 6.1 常见错误场景
- 网络连接失败
- 页面无法访问（404, 403等）
- 未找到PDF链接
- 下载失败或中断
- 磁盘空间不足

### 6.2 用户反馈
- 使用 Rich 库提供彩色终端输出
- 下载进度条显示
- 清晰的错误信息和建议
- 详细模式下的调试信息

---

## 7. 安全和合规考虑

### 7.1 网络请求
- 默认 User-Agent: "IPOFetch/1.0.0"
- 请求间隔: ≥1秒（可配置）
- 超时设置: 30秒（可配置）
- 重试机制: 最多3次，指数退避

### 7.2 数据安全
- 不记录敏感信息
- 文件哈希验证
- 安全的文件路径处理
- 输入验证和清理