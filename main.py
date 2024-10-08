import unicodedata
from collections import Counter
import re
from pathlib import Path
import itertools as it
from dataclasses import dataclass
import json

VOWEL_LETTERS = tuple(range(0x0904, 0x0914 + 1))
CONSONANT_LETTERS = tuple(range(0x0915, 0x0939 + 1)) + tuple(range(0x0958, 0x095F + 1))
VOWEL_SIGNS = tuple(range(0x093D, 0x094F + 1))

# fmt: off
VOWEL_LETTER_START     = "\u0904"
VOWEL_LETTER_END       = "\u0914"

CONSONANT_LETTER_START = "\u0915"
CONSONANT_LETTER_END   = "\u0939"

VOWEL_SIGN_START       = "\u093D"
VOWEL_SIGN_END         = "\u094F"
# fmt: on

VOWEL_LETTERS_RE = r"[\u0904-\u0914]"
CONSONANT_LETTERS_RE = r"[\u0915-\u0939\u0958-\u095F]"
VOWEL_SIGNS_RE = r"[\u093D-\u094F]"
DIACRITICAL_MARK_RE = r"[\u0900-\u0903]"
NUKTA_SIGN_RE = r"\u093C"
DIGIT_RE = r"[\u0966-\u096F]"

SYLLABLE_RE = rf"(?:({VOWEL_LETTERS_RE})|({CONSONANT_LETTERS_RE})({NUKTA_SIGN_RE}?)({VOWEL_SIGNS_RE}?))({DIACRITICAL_MARK_RE}?)|({DIGIT_RE})"
SYLLABLE_REC = re.compile(SYLLABLE_RE)

file_paths = list((Path(__file__).parent / "./data/corpus").glob("*"))


@dataclass(unsafe_hash=True)
class Syllable:
    vowel: str | None

    consonant: str | None
    nukta: str | None
    vowel_sign: str | None

    diacritical_mark: str | None

    digit: str | None

    def __str__(self):
        return "".join(
            filter(
                None,
                [
                    self.vowel,
                    self.consonant,
                    None,
                    self.vowel_sign,
                    self.diacritical_mark,
                    self.digit,
                ],
            )
        )

    def __dict__(self):
        return {
            "vowel": self.vowel,
            "consonant": self.consonant,
            "nukta": self.nukta,
            "vowel_sign": self.vowel_sign,
            "diacritical_mark": self.diacritical_mark,
            "digit": self.digit,
        }

    def remove_nukta(self):
        return Syllable(
            self.vowel,
            self.consonant,
            None,
            self.vowel_sign,
            self.diacritical_mark,
            self.digit,
        )


def is_devanagari_character(c: int) -> bool:
    return 0x0900 <= c <= 0x097F


def unicode_name(c: int | str) -> str:
    prefix = "DEVANAGARI "

    if isinstance(c, int):
        assert 0x0900 <= c <= 0x097F
        c = chr(c)

    assert isinstance(c, str)
    assert 0x0900 <= ord(c) <= 0x097F

    name = unicodedata.name(c)
    return name[len(prefix) :]


def unicode_by_name():
    pass


def unicode_name_tiny(c: int | str) -> str:
    name = unicode_name(c)
    return name.split()[-1]


def analyze_character_frequency(text: str):
    counter = Counter(filter(is_devanagari_character, map(ord, text)))

    frequency_array = [0] * (16 * 8)
    for c, f in counter.items():
        frequency_array[c - 0x0900] = f
    print(counter)

    for i in range(0, len(frequency_array), 16):
        print(
            *[
                f"{chr(0x0900 + i + j):3} {f:7}"
                for j, f in enumerate(frequency_array[i : i + 16])
            ],
            sep=" | ",
        )


def load_text(start: int = 0, count: int = 10) -> str:
    return "\n\n".join(
        file_path.read_text() for file_path in file_paths[start : start + count]
    )


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)  # Change consecutive whitespaces into a SPACE.
    text = re.sub(
        r"[^ \u0900-\u097F]", "", text
    )  # Remove all non-Devanagari characters.
    return text


def show_devanagari_unicode_block():
    for c in range(0x0900, 0x097F + 1):
        print(f"U+{c:04X}", unicodedata.category(chr(c)), unicodedata.name(chr(c)))


def show_consonant_vowel():
    for c in CONSONANT_LETTERS:
        for v in VOWEL_SIGNS:
            print(f"{chr(c)}{chr(v)}")


def syllables_from_words(words: list[str]) -> list[Syllable]:
    faulty_words = 0
    syllables = []

    for word in words:
        collect = [
            *it.chain.from_iterable(
                map(
                    lambda syllable_match: filter(None, syllable_match),
                    SYLLABLE_REC.findall(word),
                )
            )
        ]

        gotten = len(collect)
        if gotten != len(word):
            faulty_words += 1
            # print(word, list(map(unicode_name, word)), collect, gotten, len(word))
            continue

        word_syllables = SYLLABLE_REC.findall(word)

        for syllable_raw in word_syllables:
            syllable = Syllable(*map(lambda c: c if c else None, syllable_raw))
            syllables.append(syllable.remove_nukta())

    return syllables


count = 10
counter = Counter()

for start in range(0, len(file_paths), count):
    counter.update(
        syllables_from_words(normalize_text(load_text(start, count)).split())
    )

common_ones = sorted(counter.most_common(300), key=lambda kv: str(kv[0]))

json_raw = [
    {"syllable": syllable.__dict__(), "frequency": frequency}
    for syllable, frequency in common_ones
]

with open("data/frequency.json", "w") as f:
    json.dump(json_raw, f)

count = 20

with open("data/syllables.txt", "w") as f:
    for i in range(0, len(common_ones), count):
        reprs = [str(kv[0]) for kv in common_ones[i : i + count]]
        f.write("\n".join(reprs) + "\n\n\n")
