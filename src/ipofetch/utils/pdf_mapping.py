"""PDF mapping generation for HKEX prospectus chapters."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import fitz  # PyMuPDF
except ImportError:
    # Fallback to pypdf if PyMuPDF is not available
    try:
        import pypdf
    except ImportError:
        msg = "Neither PyMuPDF nor pypdf is available. Install PyMuPDF for better performance."
        raise ImportError(msg) from None


class PDFMappingGenerator:
    """Generator for PDF mapping files that track page numbers across multiple PDF files."""

    def __init__(self) -> None:
        """Initialize the PDF mapping generator."""
        self._use_pymupdf = "fitz" in globals()

    def generate_mapping(
        self,
        directory: str | Path,
        metadata_filename: str | None = None,
    ) -> dict[str, Any]:
        """Generate PDF mapping for all PDF files in a directory.

        Args:
            directory: Directory containing PDF files and metadata
            metadata_filename: Optional specific metadata filename to use as basename

        Returns:
            Dictionary containing mapping data

        Raises:
            ValueError: If no PDF files are found or directory doesn't exist
            RuntimeError: If PDF parsing fails
        """
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            msg = f"Directory does not exist: {directory}"
            raise ValueError(msg)

        # Find all PDF files in the directory
        pdf_files = sorted(dir_path.glob("*.pdf"))
        if not pdf_files:
            msg = f"No PDF files found in directory: {directory}"
            raise ValueError(msg)

        # Find metadata file to extract basename
        basename = self._extract_basename(dir_path, metadata_filename)
        if not basename:
            msg = "Could not determine basename for mapping file"
            raise ValueError(msg)

        # Parse each PDF and count pages
        mapping_data = []
        current_start_page = 1

        for pdf_file in pdf_files:
            try:
                page_count = self._count_pdf_pages(pdf_file)

                mapping_entry = {
                    "filename": pdf_file.name,
                    "page_count": page_count,
                    "start_page": current_start_page,
                }
                mapping_data.append(mapping_entry)

                current_start_page += page_count

            except Exception as e:
                # According to requirements, we should halt on PDF parsing errors
                msg = f"Failed to parse PDF file '{pdf_file.name}': {e}"
                raise RuntimeError(msg) from e

        result = {
            "basename": basename,
            "total_files": len(mapping_data),
            "total_pages": current_start_page - 1,
            "files": mapping_data,
        }

        return result

    def save_mapping_to_file(
        self,
        mapping_data: dict[str, Any],
        output_path: str | Path,
    ) -> Path:
        """Save mapping data to a JSON file.

        Args:
            mapping_data: Mapping data dictionary
            output_path: Path where to save the mapping file

        Returns:
            Path to the saved mapping file
        """
        output_file = Path(output_path)

        # Ensure parent directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Save mapping data as JSON
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(mapping_data, f, ensure_ascii=False, indent=2)

        return output_file

    def generate_and_save_mapping(
        self,
        directory: str | Path,
        metadata_filename: str | None = None,
        output_filename: str | None = None,
    ) -> Path:
        """Generate mapping and save to file in one operation.

        Args:
            directory: Directory containing PDF files and metadata
            metadata_filename: Optional specific metadata filename to use as basename
            output_filename: Optional custom output filename

        Returns:
            Path to the generated mapping file
        """
        mapping_data = self.generate_mapping(directory, metadata_filename)

        if output_filename:
            output_path = Path(directory) / output_filename
        else:
            # Generate filename based on basename from metadata
            basename = mapping_data["basename"]
            output_path = Path(directory) / f"{basename}_mapping.json"

        return self.save_mapping_to_file(mapping_data, output_path)

    def _count_pdf_pages(self, pdf_path: Path) -> int:
        """Count pages in a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Number of pages in the PDF

        Raises:
            RuntimeError: If PDF cannot be parsed
        """
        if not pdf_path.exists():
            msg = f"PDF file does not exist: {pdf_path}"
            raise RuntimeError(msg)

        try:
            if self._use_pymupdf:
                # Use PyMuPDF for better performance
                with fitz.open(str(pdf_path)) as doc:
                    return doc.page_count
            else:
                # Fallback to pypdf
                with pdf_path.open("rb") as f:
                    pdf_reader = pypdf.PdfReader(f)
                    return len(pdf_reader.pages)

        except Exception as e:
            msg = f"Failed to parse PDF '{pdf_path.name}': {e}"
            raise RuntimeError(msg) from e

    def _extract_basename(
        self,
        directory: Path,
        metadata_filename: str | None = None,
    ) -> str | None:
        """Extract basename from metadata file in directory.

        Args:
            directory: Directory to search for metadata files
            metadata_filename: Specific metadata filename to use

        Returns:
            Basename string or None if not found
        """
        if metadata_filename:
            # Use the specified metadata file
            metadata_file = directory / metadata_filename
            if metadata_file.exists():
                # Remove .json extension to get basename
                return metadata_file.stem

        # Look for JSON files that might be metadata
        json_files = list(directory.glob("*.json"))

        # Prefer files that look like HKEX metadata (company_name_document_id.json)
        for json_file in json_files:
            # Skip mapping files
            if json_file.name.endswith("_mapping.json"):
                continue

            # This looks like a metadata file
            return json_file.stem

        # Fallback: try to derive basename from PDF files
        pdf_files = list(directory.glob("*.pdf"))
        if pdf_files:
            # Extract common prefix from PDF files
            # For files like: Company_DocID_01_Title.pdf, Company_DocID_02_Title.pdf
            # The common prefix would be: Company_DocID
            first_pdf = pdf_files[0].stem

            # Split by underscores and remove the chapter number and title parts
            parts = first_pdf.split("_")
            if len(parts) >= 3:
                # Return company_document_id part
                return "_".join(parts[:-2])
            else:
                # Return first part as fallback
                return parts[0]

        return None