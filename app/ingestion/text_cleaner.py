import re


class ScientificTextCleaner:
    """
    Performs light cleaning while preserving line boundaries
    needed for scientific section-heading detection.
    """

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return ""

        # Remove null characters occasionally produced by PDFs.
        text = text.replace("\x00", "")

        # Normalize Windows / old-Mac line endings.
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Join words broken across lines:
        #
        # predic-
        # tion
        #
        # becomes:
        #
        # prediction
        text = re.sub(
            r"(?<=\w)-\n(?=[a-z])",
            "",
            text,
        )

        cleaned_lines: list[str] = []

        for line in text.split("\n"):

            # Collapse repeated spaces/tabs.
            line = re.sub(
                r"[ \t]+",
                " ",
                line,
            )

            cleaned_lines.append(
                line.strip()
            )

        text = "\n".join(cleaned_lines)

        # Prevent too many blank lines.
        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()