# 港交所（HKEX）招股说明书下载规则

## 1. 概述

港交所招股说明书采用**章节式多PDF结构**，在 hkexnews.hk 网站上提供。每个招股说明书页面包含多个章节的PDF文件，需要特殊的解析和下载策略。

## 2. URL 结构分析

### 2.1 典型URL格式
```
https://www1.hkexnews.hk/listedco/listconews/sehk/YYYY/MM/DD/{document_id}_c.htm
```

其中：
- `YYYY/MM/DD`：发布日期（年/月/日）
- `{document_id}`：文档编号（可变长度，包含字母和数字）
- `_c.htm`：中文版本标识

### 2.2 文档ID格式分析
文档ID有两种主要格式：

1. **现代格式**（2020年后为主）：
   - 纯数字，通常12位
   - 示例：`2022120700981`, `2022072601437`
   
2. **传统格式**（2020年前）：
   - 以`ltn`开头 + 年月日 + 序列号
   - 示例：`ltn20100913006`, `ltn20131129074`, `ltn20040308000`

### 2.3 示例URL
```
# 现代格式
https://www1.hkexnews.hk/listedco/listconews/sehk/2022/1230/2022120700981_c.htm

# 传统格式
https://www1.hkexnews.hk/listedco/listconews/sehk/2010/0913/ltn20100913006_c.htm
```

## 3. 页面结构分析

### 3.1 HTML结构特征
港交所招股说明书页面具有以下特征：

1. **章节导航区域**：包含所有章节链接的表格或列表
2. **PDF链接格式**：相对路径，需要拼接基础URL
3. **章节命名规则**：使用中文章节名称
4. **编码格式**：可能是UTF-8或Big5（传统文档）

### 3.2 HTML结构类型
根据年份不同，HTML结构分为两类：

1. **现代结构**（2020年后）：
   - 使用UTF-8编码
   - 包含完整的HTML文档结构
   - PDF链接通常在表格或div中
   
2. **传统结构**（2020年前）：
   - 使用Big5编码（繁体中文）
   - HTML结构较简单
   - 可能在HTML注释中包含文件列表
   - 示例注释格式：
     ```
     <!--
     Multi-Files
     C
     Main Board
     D:\EPS\Working\Submit\20100913\353769\00853
     C101.pdf
     C102.pdf
     ...
     End
     -->
     ```

### 3.2 关键HTML元素
```html
<!-- 章节链接通常出现在这样的结构中 -->
<table>
  <tr>
    <td><a href="../2022120700981/2022120700981_1.pdf">警告</a></td>
    <td><a href="../2022120700981/2022120700981_2.pdf">重要提示</a></td>
    <!-- 更多章节... -->
  </tr>
</table>
```

## 4. PDF链接提取规则

### 4.1 链接格式规则
PDF链接有两种主要格式，取决于文档的发布年份和系统：

1. **现代格式**（2020年后）：
   ```
   ../{doc_id}/{doc_id}_{chapter_num}.pdf
   ```

2. **传统格式**（2020年前）：
   ```
   {prefix}{chapter_num}.pdf
   ```
   其中`{prefix}`可能是：`C`, `CWF`, `ltn`等

其中：
- `{doc_id}`：文档ID（从URL中提取）
- `{chapter_num}`：章节编号（1, 2, 3...或01, 02, 03...）

### 4.2 完整PDF URL构建
基础URL + 相对路径：

1. **现代格式**：
   ```
   https://www1.hkexnews.hk/listedco/listconews/sehk/YYYY/MM/DD/{doc_id}/{doc_id}_{chapter_num}.pdf
   ```

2. **传统格式**：
   ```
   https://www1.hkexnews.hk/listedco/listconews/sehk/YYYY/MM/DD/{prefix}{chapter_num}.pdf
   ```

注意：需要根据实际HTML中的相对路径进行拼接。

### 4.3 章节识别规则
1. **章节编号**：从1开始连续编号
2. **章节标题**：从链接文本中提取中文标题
3. **预期章节数量**：通常15-25个章节
4. **停止条件**：当某个章节编号返回404时停止

## 5. 下载策略

### 5.1 批量下载
1. **顺序下载**：按章节编号顺序下载
2. **并发限制**：最多3个并发连接，避免被封IP
3. **重试机制**：每个章节最多重试3次，指数退避

### 5.2 文件命名规则
```
{company}_{doc_id}_{chapter_num}_{title}.pdf
```

规则说明：
- `company`: 公司名称（自动简化为2-4字简称）
- `doc_id`: 12位文档编号
- `chapter_num`: 两位数章节序号（01, 02...）
- `title`: 章节标题（前10个字符，移除特殊符号）

示例：
```
腾讯_2022120700981_01_警告.pdf
腾讯_2022120700981_02_重要提示.pdf
```

### 5.3 元数据记录
为每个下载的章节记录：
```json
{
  "document_id": "2022120700981",
  "company_name": "腾讯控股有限公司",
  "chapter_number": 1,
  "chapter_title": "警告",
  "pdf_url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2022/1230/2022120700981_1.pdf",
  "local_path": "./downloads/腾讯控股_2022120700981_chapter_01_警告.pdf",
  "file_size": 524288,
  "download_time": "2024-12-01T10:30:00Z",
  "language": "zh-CN"
}
```

## 6. 错误处理

### 6.1 网络错误
- **连接超时**：30秒超时设置
- **HTTP错误**：
  - 404：章节不存在，停止下载
  - 429：请求过多，等待60秒后重试
  - 5xx：服务器错误，等待30秒后重试

### 6.2 解析错误
- **HTML结构变化**：记录错误日志，跳过该文档
- **链接提取失败**：尝试备用解析策略
- **编码问题**：
  - 现代文档：使用UTF-8编码
  - 传统文档：使用Big5编码（繁体中文）
  - 自动检测编码或根据文档年份判断

### 6.3 文件系统错误
- **磁盘空间不足**：检查可用空间，小于100MB时停止
- **权限错误**：记录错误，继续处理其他章节
- **文件已存在**：跳过或覆盖（根据用户设置）

## 7. 性能优化

### 7.1 连接池复用
使用httpx的连接池复用TCP连接

### 7.2 缓存策略
- **已下载文件缓存**：避免重复下载
- **失败记录缓存**：避免重复尝试失败的章节

### 7.3 进度显示
使用Rich库显示：
- 总体进度（已完成章节数/总章节数）
- 当前下载速度
- 预计剩余时间
- 失败章节列表

## 8. 特殊处理

### 8.1 版本处理
- 仅处理中文版本（`_c.htm`）
- 文件名中包含中文标识

### 8.2 更新文档
- 检测文档版本更新
- 增量下载新章节
- 保留历史版本

### 8.3 大文件处理
- 分块下载大PDF文件（>50MB）
- 显示下载进度条
- 支持断点续传

## 9. 合规要求

### 9.1 用户代理
使用合规的用户代理字符串：
```
IPOFetch/1.0.0 (Research Tool; Contact: research@example.com)
```

### 9.2 请求频率
- 章节间延迟：1-3秒随机延迟
- 文档间延迟：5-10秒随机延迟
- 尊重robots.txt（如果存在）

### 9.3 数据使用
- 仅用于研究目的
- 不用于商业用途
- 遵守港交所使用条款

## 10. 实现接口

### 10.1 解析器接口
```python
class HKEXNewsParser(BaseParser):
    def extract_pdf_links(self, url: str, html_content: str) -> List[HKEXChapter]:
        """提取港交所招股说明书所有章节PDF链接"""

    def extract_company_name(self, html_content: str) -> str:
        """从HTML中提取公司名称"""

    def get_document_type(self, url: str) -> str:
        """判断文档类型：modern或traditional"""

    def detect_encoding(self, html_content: str) -> str:
        """检测HTML编码：UTF-8或Big5"""

    def parse_comment_file_list(self, html_content: str) -> List[str]:
        """解析HTML注释中的文件列表（传统格式）"""
```

### 10.2 下载器接口
```python
class HKEXDownloader:
    def download_chapter(self, chapter: HKEXChapter, output_dir: str) -> DownloadResult:
        """下载单个章节"""

    def download_all_chapters(self, chapters: List[HKEXChapter], output_dir: str) -> BatchResult:
        """批量下载所有章节"""
```

### 10.3 元数据生成器
```python
class HKEXMetadataGenerator:
    def generate_document_metadata(self, chapters: List[HKEXChapter]) -> DocumentMetadata:
        """生成文档级元数据"""

    def generate_chapter_metadata(self, chapter: HKEXChapter) -> ChapterMetadata:
        """生成章节级元数据"""
```

## 11. 解析策略

### 11.1 现代文档解析（2020年后）
1. 检测UTF-8编码
2. 解析完整HTML结构
3. 提取表格或div中的PDF链接
4. 使用标准相对路径拼接

### 11.2 传统文档解析（2020年前）
1. 检测Big5编码
2. 检查HTML注释中的文件列表
3. 解析简化的HTML结构
4. 处理不同的文件前缀（C, CWF, ltn等）

### 11.3 混合解析策略
1. **自动检测**：根据URL年份或HTML特征自动选择解析器
2. **回退机制**：主解析失败时尝试备用解析器
3. **编码自适应**：根据meta标签或内容特征检测编码

## 13. 测试用例

### 13.1 单元测试
- URL解析测试（现代和传统格式）
- HTML解析测试（不同编码和结构）
- 文件命名测试（验证简化格式）
- 元数据生成测试
- 错误处理测试
- 编码检测测试

### 13.2 集成测试
- 完整文档下载测试（现代和传统）
- 网络异常测试
- 并发下载测试
- 大文件下载测试
- 编码转换测试
- 元数据完整性测试

### 13.3 示例测试URL
```
# 现代格式（2020年后）
https://www1.hkexnews.hk/listedco/listconews/sehk/2022/1230/2022120700981_c.htm
https://www1.hkexnews.hk/listedco/listconews/sehk/2022/0905/2022072601437_c.htm

# 传统格式（2020年前）
https://www1.hkexnews.hk/listedco/listconews/sehk/2010/0913/ltn20100913006_c.htm
https://www1.hkexnews.hk/listedco/listconews/sehk/2013/1129/ltn20131129074_c.htm
https://www1.hkexnews.hk/listedco/listconews/sehk/2004/0308/ltn20040308000_c.htm
```