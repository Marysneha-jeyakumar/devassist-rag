from dataclasses import dataclass
import re


@dataclass(frozen=True)
class DetectedSection:
    title: str
    section_type: str


@dataclass
class SectionSegment:
    heading: DetectedSection | None
    text: str


class SectionDetector:
    """
    Detects common scientific-paper headings.

    This is a heuristic detector. It does not require an LLM.
    """

    NUMBER_PREFIX_PATTERN = re.compile(
        r"""
        ^\s*
        (?:
            \d+(?:\.\d+)*       # 1, 2, 2.1, 3.2.1
            |
            [IVXLC]+            # I, II, III, IV...
        )
        [.)]?
        \s+
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    SECTION_PATTERNS = [
        (
            "abstract",
            re.compile(
                r"abstract",
                re.IGNORECASE,
            ),
        ),
        (
            "introduction",
            re.compile(
                r"introduction",
                re.IGNORECASE,
            ),
        ),
        (
            "literature_review",
            re.compile(
                r"(literature review|related work|related studies)",
                re.IGNORECASE,
            ),
        ),
        (
            "background",
            re.compile(
                r"background",
                re.IGNORECASE,
            ),
        ),
        (
            "study_area",
            re.compile(
                r"(study area|study site|study region)",
                re.IGNORECASE,
            ),
        ),
        (
            "dataset",
            re.compile(
                r"(data|dataset|datasets|data set|data sets|"
                r"data source|data sources|data collection)",
                re.IGNORECASE,
            ),
        ),
        (
            "methodology",
            re.compile(
                r"(methodology|methods|materials and methods|"
                r"materials & methods|data and methods|"
                r"research methodology)",
                re.IGNORECASE,
            ),
        ),
        (
            "model",
            re.compile(
                r"(model development|model architecture|"
                r"proposed model|proposed method)",
                re.IGNORECASE,
            ),
        ),
        (
            "results_discussion",
            re.compile(
                r"(results and discussion|results & discussion)",
                re.IGNORECASE,
            ),
        ),
        (
            "results",
            re.compile(
                r"(results|findings|experimental results)",
                re.IGNORECASE,
            ),
        ),
        (
            "discussion",
            re.compile(
                r"discussion",
                re.IGNORECASE,
            ),
        ),
        (
            "limitations",
            re.compile(
                r"(limitations|study limitations)",
                re.IGNORECASE,
            ),
        ),
        (
            "future_work",
            re.compile(
                r"(future work|future research|future directions)",
                re.IGNORECASE,
            ),
        ),
        (
            "conclusion",
            re.compile(
                r"(conclusion|conclusions|conclusion and future work)",
                re.IGNORECASE,
            ),
        ),
        (
            "references",
            re.compile(
                r"(references|bibliography)",
                re.IGNORECASE,
            ),
        ),
        (
            "acknowledgements",
            re.compile(
                r"(acknowledgement|acknowledgements|"
                r"acknowledgment|acknowledgments)",
                re.IGNORECASE,
            ),
        ),
    ]

    def detect(
        self,
        line: str,
    ) -> DetectedSection | None:

        line = line.strip()

        if not line:
            return None

        # Headings should normally be short.
        if len(line) > 120:
            return None

        if len(line.split()) > 15:
            return None

        # Remove section numbering.
        #
        # "2.1 Study Area"
        # becomes
        # "Study Area"
        candidate = self.NUMBER_PREFIX_PATTERN.sub(
            "",
            line,
        )

        candidate = candidate.strip(
            " :-–—."
        )

        if not candidate:
            return None

        for section_type, pattern in self.SECTION_PATTERNS:

            if pattern.fullmatch(candidate):

                return DetectedSection(
                    title=candidate,
                    section_type=section_type,
                )

        return None

    def split_page(
        self,
        text: str,
    ) -> list[SectionSegment]:

        segments: list[SectionSegment] = []

        current_heading: DetectedSection | None = None
        buffer: list[str] = []

        for line in text.split("\n"):

            detected = self.detect(line)

            if detected is not None:

                if buffer:

                    segment_text = "\n".join(
                        buffer
                    ).strip()

                    if segment_text:
                        segments.append(
                            SectionSegment(
                                heading=current_heading,
                                text=segment_text,
                            )
                        )

                current_heading = detected
                buffer = []

            else:

                buffer.append(line)

        segment_text = "\n".join(
            buffer
        ).strip()

        if segment_text or current_heading is not None:

            segments.append(
                SectionSegment(
                    heading=current_heading,
                    text=segment_text,
                )
            )

        return segments