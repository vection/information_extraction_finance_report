import re
from fuzzywuzzy import fuzz


def is_number(text: str) -> bool:
    """
    Checks if the given text is a number.
    The number can contain optional currency symbols ($, €, etc.),
    digits, periods (.), commas (,), or a percentage sign (%),
    but it must not contain any alphabetic characters.

    Args:
        text (str): The text to check.

    Returns:
        bool: True if the text represents a number, False otherwise.
    """
    # Regex to match numbers with optional currency symbols, commas, decimals, and an optional ending %
    pattern = r'^\s*[\$\€\£\¥]?\s*[\d,]*(\.\d+)?%?\s*$'
    return bool(re.fullmatch(pattern, text))


def find_correlative_row(block, words, threshold=6):
    """
        Identifies and returns a list of words that are correlative to the given text block on y-axis sorted by x-axis (left to right)

        Args:
            block (tuple): A tuple representing the coordinates, text, and other properties of the block.
                           Format: (x0, y0, x1, y1, text, ...)
            words (list of tuples): A list of tuples where each tuple represents a word's coordinates, text, and other properties.
                                    Format: (word_x0, word_y0, word_x1, word_y1, word_text, ...)
            threshold (int, optional): The maximum allowable distance (in pixels) between the y-coordinates of the block and words to be considered "correlative".
                                       Default is 6.

        Returns:
            list of tuples: A list of words (in tuple format) that are aligned with the given block, sorted by y0 and x0 position.
    """
    x0, y0, x1, y1, text, _, _ = block

    list_of_words_row = []

    for word in words:
        word_x0, word_y0, word_x1, word_y1, word_text, _, _, _ = word
        if (word_y0 < ((y0 + y1) / 2) < word_y1) and (
                abs(word_y0 - y0) <= threshold and abs(word_y1 - y1) <= threshold) and is_number(word_text) and (
                not x0 < word_x0 < x1):
            list_of_words_row.append(word)

    list_of_words_row.sort(key=lambda b: (b[1], b[0]))  # y0, x0
    return list_of_words_row


def find_tables_pdf(page,
                metrics=['Total revenues, net of interest expense', "Citigroup's net income", 'Book value per share',
                         'Tangible book value per share', 'Common Equity Tier 1 (CET1) Capital ratio'],
                known_columns=["3Q'24", "2Q'24", "3Q'23", "QoQ%", "YoY%"]):
    """
    Extracts table data from a specified page in a PDF document and returns it as a structured dictionary.
    Each metric name consider sentence in a row located in the table.

    Args:
        pdf_path (str): The path to the PDF file from which the table will be extracted.
        page_number (int, optional): The page number to extract the table from (1-indexed). Default is 2.
        metrics (list of str, optional): A list of key metric names to locate in the table. Default includes several key financial metrics.
        known_columns (list of str, optional): A list of known column headers used to structure the extracted data.

    Returns:
        dict: A dictionary where keys are the metric names from the `metrics` list,
              and values are sub-dictionaries mapping column names from `known_columns` to the corresponding extracted values.
    """
    # Extract text blocks from the page
    blocks = page.get_text("blocks", sort=True, delimiters='\n')
    words = page.get_text("words", sort=True)

    # Sort the blocks by vertical position (y0) and then by horizontal position (x0)
    blocks.sort(key=lambda b: (b[1], b[0]))  # y0, x0
    words.sort(key=lambda b: (b[1], b[0]))  # y0, x0

    metrics_dict = {}
    for metric in metrics:
        for block in blocks:
            x0, y0, x1, y1, text, _, _ = block
            if fuzz.ratio(metric, text) >= 80:
                block_correlative = find_correlative_row(block, words)
                metrics_dict[metric] = block_correlative

    # transform to labeles
    for key, vals in metrics_dict.items():
        metrics_dict[key] = {metric_name: val[4] for metric_name, val in zip(known_columns, vals)}

    return metrics_dict


def find_tables_excel(excel_content, metrics=['Total revenues, net of interest expense', "Citigroup's net income",
                                          'Book value per share', 'Tangible book value per share',
                                          'Common Equity Tier 1 (CET1) Capital ratio'],
                      wanted_order={4: "2Q'24", 5: "3Q'24"}):
    """
        Extracts specific metrics from an Excel file and returns the data as a structured dictionary.
        Each metric name consider sentence in a row located in the table.
        The goal is to find the row that contains the metric I want to extract and pull the correlated values by order of known columns.

        Args:
            excel_content (str): The excel file content
            metrics (list of str, optional): A list of metric names to locate in the Excel file.
                                             Default includes several key financial metrics.
            wanted_order (dict, optional): A mapping of column indices to the corresponding desired column names.
                                           Used to rename the extracted data columns. Default is {4: "2Q'24", 5: "3Q'24"}.

        Returns:
            dict: A dictionary where keys are the metric names from the `metrics` list,
                  and values are sub-dictionaries mapping the column names (based on `wanted_order`) to the corresponding extracted values.
    """
    def filter_none_values(rows):
        filtered_rows = []
        for row in rows:
            filtered_row = tuple(value for value in row if value is not None)
            filtered_rows.append(filtered_row)
        return filtered_rows

    excel_content = filter_none_values(excel_content)
    final_metrics = {}
    for row in excel_content:
        for metric_name in metrics:
            if metric_name not in final_metrics:
                final_metrics[metric_name] = {}

            if row and len(row) > 0 and isinstance(row[0], str) and fuzz.ratio(row[0], metric_name) >= 80:
                for index, quarter in wanted_order.items():
                    if quarter not in final_metrics[metric_name]:
                        final_metrics[metric_name][quarter] = row[index]

    return final_metrics



def clean_and_compare(val1, val2):
    # Define a function to clean and normalize the numeric values
    def clean_value(value):
        value = str(value).strip()  # Ensure value is a string and remove leading/trailing spaces

        # Remove common symbols such as $, €, etc.
        value = value.translate(str.maketrans('', '', "$€"))  # Remove specific currency symbols
        value = value.replace(",", "")  # Remove commas

        # Remove any other non-numeric characters (punctuation)
        value = ''.join(c for c in value if c.isdigit() or c == '.')

        # Check if there's a decimal point, convert to float if present
        if '.' in value:
            try:
                return float(value)  # Convert to float if it's a decimal number
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to a valid number.")
        else:
            try:
                return int(value)  # Convert to integer if no decimal point
            except ValueError:
                raise ValueError(f"Cannot convert '{value}' to a valid number.")

    # Clean both values
    cleaned_val1 = clean_value(val1)
    cleaned_val2 = clean_value(val2)

    # Compare the cleaned values
    return cleaned_val1 == cleaned_val2
