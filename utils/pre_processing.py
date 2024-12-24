import re


def clean_text(text):
    """
    Cleans text data while preserving sentence structure and grammar.

    Args:
        text: The input text string.

    Returns:
        The cleaned text string.
    """

    # 1. Normalize whitespace:
    text = " ".join(text.split())  # Replaces multiple spaces with single spaces
    # text = text.lower()

    # 2. Remove unwanted characters (while preserving punctuation):
    text = re.sub(r"[^a-zA-Z0-9.,!?;:'\"\s]", "", text)

    # 3. Handle special characters or line breaks (if needed):
    text = text.replace("\n", " ")  # Replace newlines with spaces
    text = text.replace("\t", " ")  # Replace tabs with spaces
    text = text.replace("•", " ")  # Remove bullet points

    return text


# def clean_text_md(text: str) -> str:
#     """
#     Cleans markdown text while preserving headers, bullet points, and formatting.

#     Args:
#         text: Input markdown text string

#     Returns:
#         Cleaned markdown text string
#     """
#     # Split into lines for processing
#     lines = text.splitlines()
#     cleaned_lines = []

#     for line in lines:
#         line = line.strip()

#         # Skip lines with only underscores
#         if re.match(r'^[_\-]+$', line):
#             continue

#         # Clean bullet points
#         if line.startswith('- ●') or line.startswith('- ·') or line.startswith('- '):
#             line = '● ' + line[3:].strip()

#         # Preserve headers and content
#         if line.startswith('#') or line.strip():
#             # Remove multiple spaces
#             line = re.sub(r'\s+', ' ', line)
#             # Remove multiple hyphens
#             line = re.sub(r'-+', '-', line)
#             # Remove special characters but preserve basic punctuation
#             line = re.sub(r'[^a-zA-Z0-9.,!?;:\'"\s#\-]', '', line)
#             cleaned_lines.append(line)
#         else:
#             cleaned_lines.append('')  # Preserve single blank lines

#     # Join lines and clean up multiple newlines
#     text = '\n'.join(cleaned_lines)
#     text = re.sub(r'\n{3,}', '\n\n', text)

#     return text.strip()


# def clean_text_md(text: str) -> str:
#     """
#     Cleans both markdown and plain text while preserving structure and readability.

#     Args:
#         text: Input text string (markdown or plain)

#     Returns:
#         Cleaned text string
#     """
#     # Split into lines for processing
#     lines = text.splitlines()
#     cleaned_lines = []

#     for line in lines:
#         line = line.strip()

#         # Skip horizontal rules and separator lines
#         if re.match(r'^[_\-=]+$', line):
#             continue

#         # Clean bullet points (handles various bullet formats)
#         if re.match(r'^[-•·●\*]\s+', line):
#             line = '• ' + re.sub(r'^[-•·●\*]\s+', '', line).strip()

#         # Handle headers and content
#         if line:
#             # Clean multiple spaces
#             line = re.sub(r'\s+', ' ', line)
#             # Clean multiple hyphens except in headers
#             if not line.startswith('#'):
#                 line = re.sub(r'-+', '-', line)
#             # Remove unwanted special characters
#             line = re.sub(r'[^\w\s.,!?;:\'"\-#@()/]', '', line)
#             cleaned_lines.append(line)
#         else:
#             cleaned_lines.append('')  # Keep single blank lines

#     # Join and clean up multiple newlines
#     text = '\n'.join(cleaned_lines)
#     text = re.sub(r'\n{3,}', '\n\n', text)

#     return text.strip()


def clean_text_md(text: str) -> str:
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip separator lines
        if re.match(r"^[\s_\-=]+$", line):
            continue

        # Standardize bullet points to •
        # if re.match(r'^[-●·\*]\s+|^-\s+[●·]\s+', line):
        #     line = '• ' + re.sub(r'^[-●·\*]\s+|^-\s+[●·]\s+', '', line).strip()

        # Handle headers and content
        if line:
            # Clean multiple spaces
            line = re.sub(r"\s+", " ", line)
            # Remove underscore lines even if mixed with other characters
            if not re.match(r"^.*[_]+.*$", line):
                # Clean multiple hyphens except in headers
                if not line.startswith("#"):
                    line = re.sub(r"-+", "-", line)
                # Remove unwanted special characters
                line = re.sub(r'[^\w\s.,!?;:\'"\-#@()/]', "", line)
                cleaned_lines.append(line)
        else:
            cleaned_lines.append("")  # Keep single blank lines

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
