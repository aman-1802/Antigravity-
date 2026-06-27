# E2E Test Suite Execution Instructions (TEST_READY.md)

This document provides details on how to run the E2E verification test suite for the India Engineering Export Feasibility Study PDF Report.

## Prerequisites

The E2E test suite requires Python 3 and the `pypdf` library, with a fallback to `fitz` (PyMuPDF).
To install these dependencies:
```bash
pip install pypdf pymupdf reportlab
```

*Note: All dependencies are already pre-installed on this system.*

## Running the E2E Verification Script

The verification script `verify_engineering_pdf.py` is located at the root of the repository. It accepts a target PDF file path as an optional command-line argument. If not specified, it defaults to validating `market research/india_engineering_export_feasibility.pdf`.

### Commands

1.  **Validate the Generated Engineering Export Feasibility PDF (Default)**:
    ```bash
    python verify_engineering_pdf.py
    ```
    Or explicitly:
    ```bash
    python verify_engineering_pdf.py "market research/india_engineering_export_feasibility.pdf"
    ```

2.  **Validate a Custom or Generated PDF Report**:
    ```bash
    python verify_engineering_pdf.py "path/to/custom_report.pdf"
    ```

### Expected Exit Codes

*   **Exit Code `0`**: All verification rules passed successfully. The PDF matches the target specification.
*   **Exit Code `1`**: One or more verification rules failed. The validation logs will output a detailed report showing which check failed and why.

---

## Running the E2E Test Suite

The E2E test harness `test_validator.py` executes 60 distinct programmatically verified test cases across 4 validation tiers.

### Run Command

```bash
python test_validator.py
```

### Feature Coverage & Assertions Matrix

| Tier | Group / Feature | Test Cases Run | Key Parsed & Verified Elements |
|---|---|---|---|
| **Tier 1** | F1: File Existence & Size | 5 (F1.1 - F1.5) | Valid PDF check, missing file path check, empty 0-byte file check, non-PDF file format check, corrupted file check. |
| | F2: Scoring Matrix Check | 5 (F2.6 - F2.10) | Matrix presence, exactly 10 products, >10 products, missing matrix, too few products (<10), incomplete matrix. |
| | F3: Selected Product Profiles | 5 (F3.11 - F3.15) | Profiles presence, exactly 3 profiles, >3 profiles, missing profiles section, too few profiles (<3), unmatched profiles. |
| | F4: Selected Product Details | 5 (F4.16 - F4.20) | All details present, missing demand stats, missing target sectors, <3 Indian companies, no companies. |
| | F5: Rejected Products List | 5 (F5.21 - F5.25) | Rejected section presence, exactly 7 rejected, >7 rejected, missing rejected section, <7 rejected, missing reasons. |
| **Tier 2** | F1 BVA: File Properties | 5 (F1.26 - F1.30) | Exactly 1-byte file check, massive 50MB PDF check, special characters/spaces in filename check, directory path check, locked file permission check. |
| | F2 BVA: Matrix Boundaries | 5 (F2.31 - F2.35) | Matrix exactly 10 products, matrix exactly 9 products, duplicate product names, empty scores, no headers. |
| | F3 BVA: Profiles Boundaries | 5 (F3.36 - F3.40) | Exactly 3 profiles, exactly 2 profiles, no names in profile headings, duplicate profiles, empty profiles. |
| | F4 BVA: Company Details | 5 (F4.41 - F4.45) | Exactly 3 companies per profile, exactly 2 companies, demand stats with zero values, non-Indian company keywords check, mixed completeness check. |
| | F5 BVA: Rejection Boundaries | 5 (F5.46 - F5.50) | Exactly 7 rejected, exactly 6 rejected, rejection reason too short (<3 words), duplicate rejected products, overlap between selected and rejected products. |
| **Tier 3** | Combinatorial Testing | 5 (T3_C1 - T3_C5) | Valid matrix & selected but invalid rejected, valid matrix & rejected but invalid selected, invalid matrix but valid selected & rejected, valid matrix & rejected but company shortage in profiles, non-PDF format with correct text content. |
| **Tier 4** | Real-World Application | 5 (T4_S1 - T4_S5) | Full happy path execution, sourcing matrix omitted entirely, profile company shortage, rejected products list shortage, corrupted PDF compilation output. |
