# Citi Assignment
### Objective
The objective of this assignment was to extract key financial metrics for Q3 2024 and Q2 2024 from the provided PDF and Excel files using both Non-LLM and LLM-based methodologies.

---

### Introduction
This project focused on developing two distinct approaches for extracting critical financial metrics from a Citi financial report provided in PDF and Excel formats. The extracted metrics are for Q3 2024 and Q2 2024. The two approaches used are:

1. **Non-LLM Methodology**: Extracting metrics using traditional file processing techniques.
2. **LLM-Based Methodology**: Leveraging a large language model (LLM) to extract and structure the required metrics.

Both approaches aim to extract the same set of metrics but differ in implementation, accuracy, and scalability.

---

### Non-LLM Methodology
The Non-LLM approach relies on classic file parsing and text extraction techniques. This method was implemented for both PDF and Excel file formats, with slight variations in approach due to file structure differences.

#### **PDF File Processing**
1. **File Reading**: PyMuPDF was used to read the PDF file, focusing on page 1 where the relevant metrics are located.
2. **Text Extraction**: The PDF content is extracted as text blocks and individual words.
3. **Metric Identification**: Using the FuzzyWuzzy library, fuzzy matching is performed to identify the relevant metric names within the text blocks.
4. **Value Extraction**: Once the metric name is located, the corresponding values are extracted from the same row (i.e., the same y-axis) but different x-axis positions.
5. **Value Ordering**: Extracted values are ordered based on their x-axis positions (left-to-right) to correctly assign them to Q2 and Q3 labels.
6. **Labeling**: The values are labeled as Q2 or Q3, ensuring they are assigned to the correct quarter.

#### **Excel File Processing**
1. **File Reading**: The Excel file is read, and cells containing "None" or empty values are filtered out.
2. **Text Parsing**: Similar to the PDF approach, the metric name is identified, and the corresponding values are extracted.
3. **Value Alignment**: The values are ordered using x-axis positions and labeled for Q2 and Q3.

The key insight for both PDF and Excel files is that the relevant metrics and their corresponding values lie on the same row (same y-axis) but at different positions on the x-axis. This insight is crucial for consistent extraction across different file formats.

---

### LLM-Based Methodology
The LLM-based approach leverages a large language model (LLM) to extract and format the financial metrics. This method allows for a more flexible and adaptable solution, especially for files with varying structures.

#### **Implementation Steps**
1. **Prompt Design**: A structured prompt was created to instruct the LLM on which metrics to extract. The prompt includes clear instructions and an example of the desired output format.
2. **Output Format**: To ensure the extracted output follows a valid JSON structure, the Pydantic library is used to define a schema. This schema guarantees that the LLM output is well-formed and correctly structured.
3. **File Processing**: Similar to the Non-LLM approach, text from the PDF and Excel files is extracted. However, in the case of the Excel file, "None" values are removed to avoid irrelevant information.
4. **LLM Execution**: The extracted text is passed to the LLM (GPT-4o-mini by OpenAI) via Langchain, along with the prompt. The LLM returns a structured JSON output containing the desired Q2 and Q3 metrics.

This method provides more flexibility and can handle more dynamic documents, especially if the document’s structure changes over time.

---

### Setup Instructions
1. Install the required dependencies using:
   ```bash
   pip install -r requirements.txt
   ```
2. Place the PDF and Excel files in the project’s root folder.
3. Set the `OPENAI_API_KEY` as an environment variable to access the LLM.
4. Run the extraction script with:
   ```bash
   python extract_metrics.py
   ```

---

### Match Function
To evaluate the correctness of the extracted values, I implemented custom match function. This function goes beyond simple string comparison to account for variations in formatting and notation.

#### **Key Matching Considerations**
- **Numerical Formatting**: The function accounts for differences in number representations, such as `20139.0000` vs. `20,139`, which are considered equivalent.
- **Percentage Conversion**: There is a distinction between decimal and percentage formats, e.g., `0.1359` vs. `13.6%`, which are not considered a match.
- **Rounding Differences**: Values like `0.137` and `13.7%` may seem equivalent, but they are treated as distinct due to context-specific differences.

This function ensures that even if the extracted values have slight formatting differences, the match logic can correctly classify them as "matched" or "unmatched."

---

### Challenges and Solutions
1. **Defining the Match Function**: One of the primary challenges was deciding what constitutes a "match" between extracted values and ground truth. For instance, `20139.0000` and `20,139` clearly refer to the same value, while `0.1359` and `13.6%` do not. The solution involved implementing logic to handle formatting and rounding differences.
2. **Document Structure Variations**: The current approach assumes the structure of the PDF and Excel files is known, which may not always be the case. This challenge is addressed by leveraging the LLM’s ability to understand unstructured text.
3. **File Format Differences**: PDF and Excel files have different structures and quirks (e.g., None values in Excel). Custom logic was implemented to handle each format appropriately.
4. **Scanned Documents**: If the files were scanned documents, OCR tools like Tesseract would be required, adding complexity to the project.

---

### Summary
This project demonstrates the use of both traditional and modern AI-driven methods for extracting key financial metrics from structured files. The Non-LLM approach utilizes file parsing and position-based logic, while the LLM-based approach offers greater flexibility and adaptability.

**Key Highlights:**
- **Non-LLM Approach**: Accurate and efficient for structured files but requires document-specific logic.
- **LLM-Based Approach**: More adaptable to dynamic file structures but dependent on LLM performance and prompt design.

