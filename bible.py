#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import base64
import json
import re
import sys
import typing as t
import urllib.parse
import urllib.request
from dataclasses import dataclass

BOOKS = {
    1: ("Genesis", 50),
    2: ("Exodus", 40),
    3: ("Leviticus", 27),
    4: ("Numbers", 36),
    5: ("Deuteronomy", 34),
    6: ("Joshua", 24),
    7: ("Judges", 21),
    8: ("Ruth", 4),
    9: ("1 Samuel", 31),
    10: ("2 Samuel", 24),
    11: ("1 Kings", 22),
    12: ("2 Kings", 25),
    13: ("1 Chronicles", 29),
    14: ("2 Chronicles", 36),
    15: ("Ezra", 10),
    16: ("Nehemiah", 13),
    17: ("Esther", 10),
    18: ("Job", 42),
    19: ("Psalms", 150),
    20: ("Proverbs", 31),
    21: ("Ecclesiastes", 12),
    22: ("Song of Solomon", 8),
    23: ("Isaiah", 66),
    24: ("Jeremiah", 52),
    25: ("Lamentations", 5),
    26: ("Ezekiel", 48),
    27: ("Daniel", 12),
    28: ("Hosea", 14),
    29: ("Joel", 3),
    30: ("Amos", 9),
    31: ("Obadiah", 1),
    32: ("Jonah", 4),
    33: ("Micah", 7),
    34: ("Nahum", 3),
    35: ("Habakkuk", 3),
    36: ("Zephaniah", 3),
    37: ("Haggai", 2),
    38: ("Zechariah", 14),
    39: ("Malachi", 4),
    40: ("Matthew", 28),
    41: ("Mark", 16),
    42: ("Luke", 24),
    43: ("John", 21),
    44: ("Acts", 28),
    45: ("Romans", 16),
    46: ("1 Corinthians", 16),
    47: ("2 Corinthians", 13),
    48: ("Galatians", 6),
    49: ("Ephesians", 6),
    50: ("Philippians", 4),
    51: ("Colossians", 4),
    52: ("1 Thessalonians", 5),
    53: ("2 Thessalonians", 3),
    54: ("1 Timothy", 6),
    55: ("2 Timothy", 4),
    56: ("Titus", 3),
    57: ("Philemon", 1),
    58: ("Hebrews", 13),
    59: ("James", 5),
    60: ("1 Peter", 5),
    61: ("2 Peter", 3),
    62: ("1 John", 5),
    63: ("2 John", 1),
    64: ("3 John", 1),
    65: ("Jude", 1),
    66: ("Revelation", 22),
}

REVERSE_LOOKUP = {v[0].lower().replace(" ", ""): k for k, v in BOOKS.items()}

SPECIAL_ABBREVATIONS = {
    "dn": "Daniel",
    "dt": "Deuteronomy",
    "gn": "Genesis",
    "hb": "Habakkuk",
    "hg": "Haggai",
    "jdg": "Judges",
    "jg": "Judges",
    "jm": "James",
    "jn": "John",
    "jr": "Jeremiah",
    "lv": "Leviticus",
    "mc": "Micah",
    "mk": "Mark",
    "ml": "Malachi",
    "mr": "Mark",
    "mt": "Matthew",
    "nb": "Numbers",
    "phm": "Philemon",
    "php": "Philippians",
    "pm": "Philemon",
    "pp": "Philippians",
    "zc": "Zechariah",
    "zp": "Zephaniah",
}
REVERSE_LOOKUP_NO_VOWELS = {
    re.sub(r"[a|e|i|o|u|A|E|I|O|O]", "", k): v for k, v in REVERSE_LOOKUP.items()
}
EMPTY_SPACE = " "  # U+2003


def fuzzy_match(phrase: str, base: str) -> t.Optional[int]:
    cur = 0
    score = 0
    for char in phrase:
        if char == " ":
            continue
        if char not in base[cur:]:
            return None
        cur += base[cur:].index(char)
        score += cur
    return score


class BookNotFound(Exception):
    pass


@dataclass
class Book:
    number: int
    name: str
    chapter_count: int

    @classmethod
    def get_book(cls, string: str) -> "Book":
        value = string.lower().replace(" ", "")
        try:
            return cls.from_number(int(value))
        except ValueError:
            pass

        if value in REVERSE_LOOKUP:
            return cls.from_number(REVERSE_LOOKUP[value])

        if value in SPECIAL_ABBREVATIONS:
            return cls.from_number(
                REVERSE_LOOKUP[SPECIAL_ABBREVATIONS[value].lower().replace(" ", "")]
            )

        if value in REVERSE_LOOKUP_NO_VOWELS:
            return cls.from_number(REVERSE_LOOKUP_NO_VOWELS[value])

        for key in REVERSE_LOOKUP:
            if key.startswith(value):
                return cls.from_number(REVERSE_LOOKUP[key])

        for key in REVERSE_LOOKUP:
            if value in key:
                return cls.from_number(REVERSE_LOOKUP[key])

        matched = list(
            sorted(
                filter(
                    lambda s: s[0] is not None,
                    [(fuzzy_match(value, key), key) for key in REVERSE_LOOKUP],
                )
            )
        )
        if matched:
            return cls.from_number(REVERSE_LOOKUP[matched[0][1]])
        raise BookNotFound(f"Cannot find book {string}")

    @classmethod
    def from_number(cls, number: int) -> "Book":
        return Book(
            number=number, name=BOOKS[number][0], chapter_count=BOOKS[number][1]
        )

    def next(self) -> "Book":
        number = self.number + 1
        if number > len(BOOKS):
            number %= len(BOOKS)
        return self.from_number(number)

    def prev(self) -> "Book":
        number = self.number - 1
        if number == 0:
            number = len(BOOKS)
        return self.from_number(number)


def verse_to_markdown(
    text: str, number: t.Optional[int] = None, strict: bool = False
) -> str:
    if not strict:
        indent_break = "\n    "
    else:
        indent_break = f"<br>{EMPTY_SPACE}"

    # open quote
    text = re.sub(r'(?<=\S) "', f'{indent_break}"', text)
    # open quote
    text = re.sub(r" '", f"{indent_break}'", text)
    # full stop followed by space with optional quote or ref to footnote
    text = re.sub(r"\.('|\"|)(\(\d+\)|) +", rf".\1\2{indent_break}", text)
    # closing marks
    for mark in [
        "!",
        ";",
        '"',
        "?",
        ":",
    ]:
        text = re.sub(rf"\{mark} ", f"{mark}{indent_break}", text)
    # single quote but not possessives
    text = re.sub(r"(?<!s)' ", f"'{indent_break}", text)
    for link_word in [
        "so",
        # "so that",
        "but",
        "because",
        "not because",
        "therefore",
        "for",
        "in order that",
        "unless",
        "not only",
        "which",
        "where",
        "when",
        "who",
        "whose",
        "whom",
        "of whom",
        "of which",
        "even though",
        "since",
    ]:
        text = re.sub(
            rf"(,|;)(?P<ref>\(\d+\)|) {link_word} ",
            rf"\1\2{indent_break}{link_word} ",
            text,
        )
    for conjunction in ["When", "But when", "So when"]:
        text = re.sub(rf"({conjunction}( \w+)+,) ", rf"\1{indent_break}", text)
    text = re.sub(
        r"(,|;)(?P<ref>\(\d+\)|) as (?!\w+ as)",  # not as many|well|far|... as
        rf"\1\2{indent_break}as ",
        text,
    )
    text = re.sub(
        r"(,|;)(?P<ref>\(\d+\)|) and (?!(\w+ |)(\w+)(\.|;))",  # and but not oxford comma
        rf"\1\2{indent_break}and ",
        text,
    )
    if number:
        return f"{number}. {text}"
    else:
        return text


@dataclass
class Verse:
    """
    {
        "book": {"id": 43, "name": "John", "testament": "NT"},
        "chapterId": 5,
        "id": 43005001,
        "verse": "After this there was a feast of the Jews, and Jesus went up to Jerusalem.",
        "verseId": 1,
    }
    """

    book: Book
    chapter_number: int
    number: int
    text: str = ""


@dataclass
class Chapter:
    number: int
    book: Book
    verses: t.List[Verse]


def argument_parser():
    parser = argparse.ArgumentParser(description="make md file for bible verses")
    parser.add_argument(
        "query",
        help="query of bible books and verses",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="strict",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="debug",
    )
    return parser


def get_esv_passages(start_verse: Verse, end_verse: t.Optional[Verse]) -> str:
    book = start_verse.book
    if book.chapter_count == 1:
        qs = f"{book.name}"
        if start_verse.number > 0:
            qs = f"{qs}{start_verse.number}"
        if end_verse and end_verse.chapter_number:
            qs = f"{qs}-{end_verse.chapter_number}"
    else:
        qs = f"{book.name}+{start_verse.chapter_number}"
        if start_verse.number > 0:
            qs = f"{qs}:{start_verse.number}"
        if end_verse:
            qs = f"{qs}-{end_verse.chapter_number}"
            if end_verse.number > 0:
                qs = f"{qs}:{end_verse.number}"
    qs = urllib.parse.urlencode({"q": qs})
    token = base64.b85decode(b"F<~)fGGa1gV_`WmF=I40Gc!0aGch(}F=8}gH92B8HaKN6G%;Z_")
    response = urllib.request.urlopen(
        urllib.request.Request(
            url=f"https://api.esv.org/v3/passage/text/?{qs}",
            headers={"Authorization": f"Token {token.decode()}"},
        )
    )
    return json.loads(response.read())["passages"][0]


def process_1(text: str) -> str:
    for old, new in [
        ("“", '"'),
        ("”", '"'),
        ("‘", "'"),
        ("’", "'"),
    ]:
        text = text.replace(old, new)
    return text


def process_2(
    text: str,
    start_verse: t.Optional[Verse] = None,
    end_verse: t.Optional[Verse] = None,
    strict: bool = False,
) -> str:
    LINE_BREAK = "\n"
    PARAGRAPH_BREAK = "---\n"
    HEADER = "#"
    SECTION_HEADER = "##"
    footnote_mark = re.compile(r"^\((\d+)\)")
    verse_mark = re.compile(r"\[(\d+)\] *")
    paragraph_start = re.compile(r"  \S")
    input_lines = text.split("\n")
    if start_verse is not None:
        if start_verse.number <= 1:  # 0 when verse not specified
            start_chapter = start_verse.chapter_number
        else:
            start_chapter = min(
                start_verse.chapter_number + 1, start_verse.book.chapter_count
            )
    else:
        start_chapter = None
    if start_verse is not None and end_verse is not None:
        multi_chapter = start_verse.chapter_number < end_verse.chapter_number
    else:
        multi_chapter = False
    lines = []
    for i, line in enumerate(input_lines):
        if i == 0:  # heading 1
            lines.append(f"{HEADER} {line}{LINE_BREAK}")
        elif line == "Footnotes":
            lines.append(PARAGRAPH_BREAK)
            lines.append(f"{SECTION_HEADER} Footnotes")
        elif line.strip() == "":
            if (
                not lines[-1].startswith(HEADER)
                and not lines[-1].startswith(SECTION_HEADER)
                and not lines[-1].startswith(PARAGRAPH_BREAK)
                and lines[-1] != ""
            ):
                lines.append("")
        elif line.startswith(" "):  # verse
            if paragraph_start.match(line):
                if lines[-1].startswith(SECTION_HEADER):
                    lines.append("")
                else:
                    lines.append(PARAGRAPH_BREAK)
            # verses
            start = 0
            result = []
            verse_num = 0
            for i, item in enumerate(verse_mark.finditer(line)):
                end = item.span()[0]
                verse = line[start : end - 1]
                if verse_num == 0:
                    if verse.strip() != "":
                        result.append(
                            verse_to_markdown(
                                verse_mark.sub("", verse),
                                strict=strict,
                            )
                            + LINE_BREAK
                        )
                else:
                    if verse_num == 1:
                        if (
                            multi_chapter
                            and start_chapter is not None
                            and end_verse is not None
                            and start_chapter <= end_verse.chapter_number
                        ):
                            # add chapter number for multi chapter query
                            # TODO john7-8 doesn't really work well
                            if lines[-1] == "" and lines[-2].startswith(SECTION_HEADER):
                                lines[-2] = f"*{start_chapter}*\n" + lines[-2]
                                start_chapter += 1
                            if lines[-1] == PARAGRAPH_BREAK:
                                lines[-1] += f"\n*{start_chapter}*"
                                start_chapter += 1
                            if result != []:  # something before verse 1 e.g. John8
                                result.append(PARAGRAPH_BREAK)
                    result.append("")
                    result.append(
                        verse_to_markdown(
                            verse_mark.sub("", verse),
                            number=verse_num,
                            strict=strict,
                        )
                        + LINE_BREAK
                    )
                if i == 0:
                    verse_num = int(item.groups()[0])
                else:
                    while verse_num + 1 < int(item.groups()[0]):  # missing verse
                        verse_num += 1
                        result.append("")
                        result.append(f"{verse_num}. {EMPTY_SPACE}" + LINE_BREAK)
                    else:
                        verse_num = int(item.groups()[0])
                start = end
            if verse_num > 0:
                if verse_num == 1:
                    if (
                        multi_chapter
                        and start_chapter is not None
                        and end_verse is not None
                        and start_chapter <= end_verse.chapter_number
                    ):
                        if lines[-1] == "" and lines[-2].startswith(SECTION_HEADER):
                            lines[-2] = f"*{start_chapter}*\n" + lines[-2]
                            start_chapter += 1
                        if lines[-1] == PARAGRAPH_BREAK:
                            lines[-1] += f"\n*{start_chapter}*"
                            start_chapter += 1
                        if result != []:  # something before verse 1 e.g. John8
                            result.append(PARAGRAPH_BREAK)
                result.append("")
                result.append(
                    verse_to_markdown(
                        verse_mark.sub("", line[start : len(line)]),
                        number=verse_num,
                        strict=strict,
                    )
                    + LINE_BREAK
                )
            else:
                # prev line didn't actually finish
                assert start == 0
                lines[-1] = lines[-1].rstrip(LINE_BREAK)
                if lines[-1].startswith(SECTION_HEADER):
                    lines.append(LINE_BREAK)
                    lines.append(
                        verse_to_markdown(
                            line.strip(),
                            strict=strict,
                        )
                    )
                else:
                    if strict:
                        lines[-1] += f"<br>{EMPTY_SPACE}"
                        lines[-1] += verse_to_markdown(
                            line.strip(),
                            strict=True,
                        )
                    else:
                        lines[-1] += LINE_BREAK
                        lines[-1] += verse_to_markdown(
                            line,
                            strict=False,
                        )
            lines += result
        elif footnote_mark.match(line):
            footnote = footnote_mark.sub(r"- (\1)", line)
            lines.append(footnote)
        elif line.strip():  # headers
            lines.append(PARAGRAPH_BREAK)
            lines.append(f"{SECTION_HEADER} {line}")
    return "\n".join(lines).strip()


def process(
    text: str,
    start_verse: t.Optional[Verse] = None,
    end_verse: t.Optional[Verse] = None,
    strict: bool = False,
) -> str:
    return process_2(
        process_1(text),
        start_verse,
        end_verse,
        strict,
    )


def get_from_esv(
    query: str = "",
    start_verse: t.Optional[Verse] = None,
    end_verse: t.Optional[Verse] = None,
    strict: bool = False,
    debug: bool = False,
) -> str:
    if query == "" and start_verse is None:
        raise ValueError("specify either the query or the start verse")
    if start_verse is None:
        start_verse, end_verse = parse_query(query)
    text = get_esv_passages(start_verse, end_verse)
    if debug:
        with open(f"/tmp/{query}.txt", "w") as f:
            f.write(text)
    # text = open(f"/tmp/{query}.txt").read()
    return process(text, start_verse, end_verse, strict)


def parse_single_chapter_no_verse(query: str) -> t.Tuple[str, int]:
    try:
        int(query[-1])  # TODO maybe this should return the whole book?
    except (IndexError, ValueError):
        query = query + "1"  # no chapter then 1
    match = re.match(r"(?P<book>^.+?)(?P<chapter>\d+)", query)
    if not match:
        return "1", 1
    return match.groupdict()["book"], int(match.groupdict()["chapter"])


def parse_single_chapter_with_start_verse(
    query: str,
) -> t.Optional[t.Tuple[str, int, int]]:
    match = re.match(r"^(?P<book>^.+?)(?P<chapter>\d+)(:|v)(?P<verse>\d+)$", query)
    if not match:
        return None
    return (
        match.groupdict()["book"],
        int(match.groupdict()["chapter"]),
        int(match.groupdict()["verse"] or "1"),
    )


def parse_single_chapter_with_verses(
    query: str,
) -> t.Optional[t.Tuple[str, int, int, int]]:
    match = re.match(
        r"^(?P<book>^.+?)(?P<chapter>\d+)(:|v)(?P<start_verse>\d+)(-|–)(?P<end_verse>\d+)$",
        query,
    )
    if not match:
        return None
    return (
        match.groupdict()["book"],
        int(match.groupdict()["chapter"]),
        int(match.groupdict()["start_verse"]),
        int(match.groupdict()["end_verse"]),
    )


def parse_chapters_with_verses(
    query: str,
) -> t.Optional[t.Tuple[str, int, int, int, int]]:
    match = re.match(
        r"^(?P<book>^.+?)(?P<start_chapter>\d+)((v|:)(?P<start_verse>\d+)|)(-|–)(?P<end_chapter>\d+)((:|v)(?P<end_verse>\d+)|)$",
        query,
    )
    if not match:
        return None
    start_verse = int(match.groupdict()["start_verse"] or "0")
    end_verse = int(match.groupdict()["end_verse"] or "0")
    if start_verse != 0 and end_verse == 0:  # 1cor2:11-13
        return None
    return (
        match.groupdict()["book"],
        int(match.groupdict()["start_chapter"]),
        start_verse,
        int(match.groupdict()["end_chapter"]),
        end_verse,
    )


def parse_query(query: str) -> t.Tuple[Verse, t.Optional[Verse]]:
    parsed_0 = parse_chapters_with_verses(query)
    if parsed_0:
        book, start_chapter, start_verse, end_chapter, end_verse = parsed_0
        return Verse(
            book=Book.get_book(book),
            chapter_number=int(start_chapter),
            number=start_verse,
        ), Verse(
            book=Book.get_book(book),
            chapter_number=int(end_chapter),
            number=end_verse,
        )

    parsed_1 = parse_single_chapter_with_verses(query)
    if parsed_1:
        book, chapter, start_verse, end_verse = parsed_1
        return Verse(
            book=Book.get_book(book),
            chapter_number=int(chapter),
            number=start_verse,
        ), Verse(
            book=Book.get_book(book),
            chapter_number=int(chapter),
            number=end_verse,
        )

    parsed_2 = parse_single_chapter_with_start_verse(query)
    if parsed_2:
        book, chapter, verse = parsed_2
        return (
            Verse(
                book=Book.get_book(book),
                chapter_number=int(chapter),
                number=verse,
            ),
            None,
        )

    book, chapter = parse_single_chapter_no_verse(query)
    return (
        Verse(
            book=Book.get_book(book),
            chapter_number=int(chapter),
            number=0,  # entire chapter
        ),
        None,
    )


def main(argv=None):
    args = argument_parser().parse_args(argv)
    print(get_from_esv(query=args.query, strict=args.strict, debug=args.debug))


if __name__ == "__main__":
    main(sys.argv[1:] or ["Ps8"])
