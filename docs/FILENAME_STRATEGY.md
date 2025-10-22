# 文件命名策略说明

## 概述

为了解决中文文件名在不同操作系统和终端环境下可能出现的编码问题，IPOFetch 采用了双重命名策略：
- **文件系统层面**：使用英文文件名，确保跨平台兼容性
- **元数据层面**：保存原始中文名称，保持信息完整性

## 文件命名规则

### 1. 公司名称处理

**英文文件名生成规则**：
- 使用预定义的中英文映射表进行转换
- 移除特殊字符和标点符号
- 限制长度为50个字符以内
- 如果无法匹配，使用通用格式：`Company_[document_id]`

**常见映射示例**：
```
中国移动有限公司 → China_Mobile_Limited
阿里巴巴集团控股有限公司 → Alibaba_Group_Holding_Limited
腾讯控股有限公司 → Tencent_Holdings_Limited
```

### 2. 章节标题处理

**英文文件名生成规则**：
- 使用预定义的章节标题映射表
- 常见章节自动转换为标准英文名称
- 未匹配的章节使用格式：`Chapter_XX`

**常见映射示例**：
```
封面 → Cover
目录 → Table_of_Contents
概要 → Summary
风险因素 → Risk_Factors
业务 → Business
财务资料 → Financial_Information
```

## 元数据保存

### 原始名称保存位置

所有原始中文名称都保存在JSON元数据文件中：

```json
{
  "company_name": "China_Mobile_Limited",
  "company_name_original": "中国移动有限公司",
  "chapters": [
    {
      "chapter_title": "Cover",
      "chapter_title_original": "封面",
      "chapter_number": 1
    }
  ]
}
```

### 元数据文件结构

- **文档级元数据**：包含公司信息、下载统计等
- **章节级元数据**：包含每个章节的详细信息
- **双语支持**：同时保存英文文件名和原始中文名称

## 实际文件结构示例

```
downloads/
├── China_Mobile_Limited_20240101/
│   ├── Cover.pdf
│   ├── Table_of_Contents.pdf
│   ├── Summary.pdf
│   ├── Risk_Factors.pdf
│   └── Business.pdf
└── China_Mobile_Limited_20240101_metadata.json
```

对应的元数据文件内容：
```json
{
  "company_name": "China_Mobile_Limited",
  "company_name_original": "中国移动有限公司",
  "chapters": [
    {
      "chapter_title": "Cover",
      "chapter_title_original": "封面"
    },
    {
      "chapter_title": "Business", 
      "chapter_title_original": "业务"
    }
  ]
}
```

## 优势

1. **跨平台兼容性**：英文文件名避免编码问题
2. **信息完整性**：原始中文名称完整保存
3. **可读性**：英文文件名便于识别和管理
4. **可追溯性**：通过元数据可以还原原始信息
5. **自动化处理**：无需手动干预，自动生成合适的文件名

## 注意事项

- 元数据文件与PDF文件必须保持同步
- 删除PDF文件时建议同时删除对应的元数据
- 元数据文件采用UTF-8编码，确保中文正确显示
- 英文文件名映射表可根据需要扩展和更新