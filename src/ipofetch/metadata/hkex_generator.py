"""HKEXnews metadata generator for prospectus documents."""

import json
from datetime import datetime
from pathlib import Path
from typing import List
from typing import Optional

from ipofetch import __version__
from ipofetch.types import BatchResult
from ipofetch.types import ChapterMetadata
from ipofetch.types import DocumentMetadata
from ipofetch.types import HKEXChapter


class HKEXMetadataGenerator:
    """港交所招股说明书元数据生成器."""

    def generate_document_metadata(
        self,
        document_id: str,
        company_name: str,
        original_url: str,
        chapters: List[HKEXChapter],
        batch_result: BatchResult,
        output_dir: str,
    ) -> DocumentMetadata:
        """Generate document-level metadata.

        Args:
            document_id: Document ID
            company_name: Company name
            original_url: Original prospectus page URL
            chapters: List of chapters
            batch_result: Download batch result
            output_dir: Output directory path

        Returns:
            DocumentMetadata object
        """
        # Generate chapter metadata for successful downloads
        chapter_metadata_list = []
        
        for i, chapter in enumerate(chapters):
            if i < len(batch_result.download_results):
                download_result = batch_result.download_results[i]
                if download_result.success:
                    chapter_metadata = self.generate_chapter_metadata(
                        document_id=document_id,
                        company_name=company_name,
                        chapter=chapter,
                        local_path=download_result.pdf_path,
                        file_size=download_result.file_size,
                        download_time=download_result.download_time,
                    )
                    chapter_metadata_list.append(chapter_metadata)

        return DocumentMetadata(
            document_id=document_id,
            company_name=company_name,
            original_url=original_url,
            total_chapters=len(chapters),
            download_date=datetime.now().isoformat(),
            chapters=chapter_metadata_list,
            language="zh-CN",
            exchange_type="hkexnews",
        )

    def generate_chapter_metadata(
        self,
        document_id: str,
        company_name: str,
        chapter: HKEXChapter,
        local_path: str,
        file_size: int,
        download_time: float,
    ) -> ChapterMetadata:
        """Generate chapter-level metadata.

        Args:
            document_id: Document ID
            company_name: Company name
            chapter: Chapter information
            local_path: Local file path
            file_size: File size in bytes
            download_time: Download time in seconds

        Returns:
            ChapterMetadata object
        """
        return ChapterMetadata(
            document_id=document_id,
            company_name=company_name,
            chapter_number=chapter.chapter_number,
            chapter_title=chapter.chapter_title,
            pdf_url=chapter.pdf_url,
            local_path=local_path,
            file_size=file_size,
            download_time=datetime.now().isoformat(),
            language="zh-CN",
        )

    def save_metadata_to_file(
        self,
        metadata: DocumentMetadata,
        output_dir: str,
        filename: Optional[str] = None,
    ) -> str:
        """Save metadata to JSON file.

        Args:
            metadata: Document metadata to save
            output_dir: Output directory path
            filename: Optional custom filename

        Returns:
            Path to the saved metadata file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if filename is None:
            safe_company_name = self._sanitize_filename(metadata.company_name)
            filename = f"{safe_company_name}_{metadata.document_id}_metadata.json"

        metadata_file = output_path / filename

        # Convert metadata to dictionary for JSON serialization
        metadata_dict = {
            "document_id": metadata.document_id,
            "company_name": metadata.company_name,
            "original_url": metadata.original_url,
            "total_chapters": metadata.total_chapters,
            "download_date": metadata.download_date,
            "language": metadata.language,
            "exchange_type": metadata.exchange_type,
            "tool_version": __version__,
            "chapters": [
                {
                    "document_id": chapter.document_id,
                    "company_name": chapter.company_name,
                    "chapter_number": chapter.chapter_number,
                    "chapter_title": chapter.chapter_title,
                    "pdf_url": chapter.pdf_url,
                    "local_path": chapter.local_path,
                    "file_size": chapter.file_size,
                    "download_time": chapter.download_time,
                    "language": chapter.language,
                }
                for chapter in metadata.chapters
            ],
        }

        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata_dict, f, ensure_ascii=False, indent=2)

        return str(metadata_file)

    def generate_summary_report(
        self,
        metadata: DocumentMetadata,
        batch_result: BatchResult,
    ) -> str:
        """Generate a human-readable summary report.

        Args:
            metadata: Document metadata
            batch_result: Download batch result

        Returns:
            Formatted summary report string
        """
        report_lines = [
            "=" * 60,
            "港交所招股说明书下载报告",
            "=" * 60,
            "",
            f"公司名称: {metadata.company_name}",
            f"文档编号: {metadata.document_id}",
            f"下载日期: {metadata.download_date}",
            f"原始链接: {metadata.original_url}",
            "",
            "下载统计:",
            f"  总章节数: {batch_result.total_chapters}",
            f"  成功下载: {batch_result.successful_downloads}",
            f"  下载失败: {batch_result.failed_downloads}",
            f"  成功率: {batch_result.successful_downloads / batch_result.total_chapters * 100:.1f}%",
            f"  总文件大小: {self._format_file_size(batch_result.total_size)}",
            f"  总下载时间: {batch_result.total_time:.2f} 秒",
            "",
        ]

        if metadata.chapters:
            report_lines.extend([
                "成功下载的章节:",
                "-" * 40,
            ])
            
            for chapter in metadata.chapters:
                size_str = self._format_file_size(chapter.file_size)
                report_lines.append(
                    f"  {chapter.chapter_number:2d}. {chapter.chapter_title} ({size_str})"
                )
            
            report_lines.append("")

        if batch_result.errors:
            report_lines.extend([
                "下载错误:",
                "-" * 40,
            ])
            
            for error in batch_result.errors:
                report_lines.append(f"  • {error}")
            
            report_lines.append("")

        report_lines.extend([
            f"工具版本: IPOFetch {__version__}",
            "=" * 60,
        ])

        return "\n".join(report_lines)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem compatibility.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename safe for filesystem use
        """
        # Replace problematic characters
        replacements = {
            '/': '_',
            '\\': '_',
            ':': '_',
            '*': '_',
            '?': '_',
            '"': '_',
            '<': '_',
            '>': '_',
            '|': '_',
            '\n': '_',
            '\r': '_',
            '\t': '_',
        }
        
        sanitized = filename
        for old, new in replacements.items():
            sanitized = sanitized.replace(old, new)
        
        # Remove extra spaces and limit length
        sanitized = ' '.join(sanitized.split())
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized.strip()

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format.

        Args:
            size_bytes: File size in bytes

        Returns:
            Formatted file size string
        """
        if size_bytes == 0:
            return "0 B"
        
        units = ["B", "KB", "MB", "GB"]
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        else:
            return f"{size:.1f} {units[unit_index]}"