# HKEX Prospectus PDF Mapping Generation

## 1. Background

The PDF documents for prospectuses downloaded from the Hong Kong Stock Exchange (HKEX) are typically split into multiple files, with each file representing a chapter or section of the full document. To treat these separate files as a single, continuous document for analysis and data extraction, a mapping file is required.

This feature will introduce a process to generate a `_mapping.json` file. This file will contain metadata for each individual PDF file, including its page count and its starting page number within the context of the combined document.

## 2. Functional Requirements

### 2.1. Triggering Condition

The mapping generation process shall be triggered immediately after the successful download of all PDF files for a given IPO prospectus. This process involves parsing each PDF to extract metadata and create the mapping file.

### 2.2. Input

- A directory containing a set of PDF files (`.pdf`) and a metadata file (e.g., `meta.json`) for a single prospectus.
- The PDF files are assumed to be named in a way that allows for correct alphabetical sorting to reflect the chapter order.
- A metadata file (e.g., `康灃生物科技（上海）股份有限公司_2022120700981.json`) from which the base name for the output file can be derived.

### 2.3. Processing Steps

1.  **Identify Input Files**: Scan the input directory to find all `.pdf` files and the core metadata JSON file.
2.  **Determine Basename**: Extract the base name from the metadata file. For example, from `康灃生物科技（上海）股份有限公司_2022120700981.json`, the base name is `康灃生物科技（上海）股份有限公司_2022120700981`.
3.  **Sort PDF Files**: Sort the list of identified PDF files alphanumerically by their filenames. This is crucial to ensure the correct chapter order.
4.  **Parse PDFs and Count Pages**: For each PDF file in the sorted list:
    - Open and parse the PDF to determine the total number of pages it contains.
    - Handle potential errors, such as corrupted or unreadable PDF files.
5.  **Calculate Starting Page Numbers**:
    - The first PDF file in the list has a starting page number of 1.
    - For each subsequent file, the starting page number is calculated by summing the page counts of all preceding files and adding 1.
    - `start_page_n = (sum of pages for file_1 to file_n-1) + 1`
6.  **Generate Mapping Data**: Create a data structure (e.g., a list of objects) that holds the information for each file.

### 2.4. Output

- A single JSON file will be created and saved in the same directory as the input PDF files.
- The mapping file's name will be derived from the metadata file's name, with `_mapping.json` as the suffix. For example: `康灃生物科技（上海）股份有限公司_2022120700981_mapping.json`.
- This file will contain a JSON array of objects.
- Each object in the array will represent one PDF file and have the following key-value pairs:
  - `filename`: The name of the PDF file (e.g., `"chapter1.pdf"`).
  - `page_count`: The number of pages in that specific PDF file (an integer).
  - `start_page`: The calculated starting page number for this file within the consolidated document (an integer).

## 3. JSON Output Structure Example

Given a directory with a metadata file `康灃生物科技（上海）股份有限公司_2022120700981.json` and the following PDF files:
- `01_cover.pdf` (2 pages)
- `02_summary.pdf` (10 pages)
- `03_risk_factors.pdf` (25 pages)

The generated file will be named `康灃生物科技（上海）股份有限公司_2022120700981_mapping.json` and its content would look like this:

```json
[
  {
    "filename": "01_cover.pdf",
    "page_count": 2,
    "start_page": 1
  },
  {
    "filename": "02_summary.pdf",
    "page_count": 10,
    "start_page": 3
  },
  {
    "filename": "03_risk_factors.pdf",
    "page_count": 25,
    "start_page": 13
  }
]
```

## 4. Non-Functional Requirements

### 4.1. Error Handling

- If a PDF file cannot be opened or parsed, the process should log a detailed error message, including the filename.
- The process should decide on a failure strategy: either halt the entire mapping generation for that IPO or skip the problematic file and continue with a warning. The preferred approach is to halt and report an error, as an incomplete mapping could be misleading.

### 4.2. Performance

- The PDF parsing should be efficient. The choice of library (e.g., `PyMuPDF/fitz` is generally faster than `pypdf`) should consider performance.

### 4.3. Idempotency

- If a mapping file (e.g., `..._mapping.json`) already exists, it should be overwritten with the newly generated data to ensure the mapping is always up-to-date with the downloaded files.

## 5. Testing URL
The following URLs can be used for testing the mapping generation process:
- `https://www1.hkexnews.hk/listedco/listconews/sehk/2010/0913/ltn20100913006_c.htm`
- `https://www1.hkexnews.hk/listedco/listconews/sehk/2022/1230/2022120700981_c.htm`
- `https://www1.hkexnews.hk/listedco/listconews/sehk/2013/1129/ltn20131129074_c.htm`
- `https://www1.hkexnews.hk/listedco/listconews/sehk/2022/0905/2022072601437_c.htm`
- `https://www1.hkexnews.hk/listedco/listconews/sehk/2004/0308/ltn20040308000_c.htm`
