import unicodedata
from typing import Literal

from inferencesh import BaseApp, BaseAppSetup
from pydantic import BaseModel, Field

# Gurmukhi (U+0A00) and Devanagari (U+0900) share a layout, so most letters
# map by a fixed offset. The special cases below cover where Punjabi spelling
# differs: addak (gemination), tippi/bindi (nasals), ੲ/ੳ vowel carriers,
# ੜ, and Devanagari conjuncts that Gurmukhi writes without a halant.
OFFSET = 0x100

GUR_ADDAK, GUR_TIPPI, GUR_BINDI, GUR_HALANT, GUR_NUKTA = "ੱ", "ੰ", "ਂ", "੍", "਼"
DEV_HALANT, DEV_NUKTA, DEV_ANUSVARA = "्", "़", "ं"

# Unaspirated partner used when a doubled consonant is aspirated (ਅੱਛਾ -> अच्छा).
ASPIRATE_BASE = {
    "ख": "क", "घ": "ग", "छ": "च", "झ": "ज", "ठ": "ट",
    "ढ": "ड", "थ": "त", "ध": "द", "फ": "प", "भ": "ब",
}

# Gurmukhi carriers ੳ/ੲ and ਅ combine with a vowel sign into one independent vowel.
GUR_CARRIER_VOWELS = {
    ("ੳ", "ੁ"): "उ", ("ੳ", "ੂ"): "ऊ", ("ੳ", "ੋ"): "ओ",
    ("ੲ", "ਿ"): "इ", ("ੲ", "ੀ"): "ई", ("ੲ", "ੇ"): "ए",
    ("ਅ", "ਾ"): "आ", ("ਅ", "ੈ"): "ऐ", ("ਅ", "ੌ"): "औ",
}
GUR_CARRIER_FALLBACK = {"ੳ": "उ", "ੲ": "इ"}
# NFC splits ਸ਼ and ਲ਼ into letter + nukta; Devanagari has single letters for both.
GUR_NUKTA_LETTERS = {"ਸ": "श", "ਲ": "ळ"}

# Devanagari letters with no direct Gurmukhi slot.
DEV_TO_GUR_SPECIAL = {
    "ष": "ਸ਼", "ऋ": "ਰਿ", "ृ": "ਿਰ", "ॐ": "ਓਮ",
    "ॅ": "ੈ", "ॉ": "ੌ", "ऍ": "ਐ", "ऑ": "ਔ", "ऽ": "",
}
# Gurmukhi keeps a subjoined form (pairin) only for these letters.
PAIRIN = {"र", "ह", "व"}
# Vowel signs after which a nasal is written with tippi rather than bindi.
TIPPI_AFTER = {"ਿ", "ੁ", "ੂ", "ਅ", "ਇ", "ਉ", "ਊ"}

ROMAN_CONSONANTS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ng",
    "च": "ch", "छ": "chh", "ज": "j", "झ": "jh", "ञ": "ny",
    "ट": "t", "ठ": "th", "ड": "d", "ढ": "dh", "ण": "n",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "ळ": "l", "व": "v",
    "श": "sh", "ष": "sh", "स": "s", "ह": "h",
}
ROMAN_NUKTA = {"क": "q", "ख": "kh", "ग": "gh", "ज": "z", "फ": "f", "ड": "r", "ढ": "rh"}
ROMAN_VOWELS = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo",
    "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au", "ऋ": "ri", "ऑ": "o", "ऍ": "e",
}
ROMAN_MATRAS = {
    "ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo", "ृ": "ri",
    "े": "e", "ै": "ai", "ो": "o", "ौ": "au", "ॉ": "o", "ॅ": "e",
}
ROMAN_MARKS = {"ं": "n", "ँ": "n", "ः": "h", "।": ".", "॥": "."}


def is_gurmukhi(ch: str) -> bool:
    return "਀" <= ch <= "੿"


def is_devanagari(ch: str) -> bool:
    return "ऀ" <= ch <= "ॿ"


def is_dev_consonant(ch: str) -> bool:
    return "क" <= ch <= "ह" or ch == "ळ"


def shift(ch: str, delta: int) -> str:
    """Move a letter between the Gurmukhi and Devanagari blocks, if the target exists."""
    target = chr(ord(ch) + delta)
    return target if unicodedata.name(target, None) else ch


def gurmukhi_to_devanagari(text: str) -> str:
    out = []
    chars = list(unicodedata.normalize("NFC", text))
    i = 0
    while i < len(chars):
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        if not is_gurmukhi(ch):
            out.append(ch)
        elif (ch, nxt) in GUR_CARRIER_VOWELS:
            out.append(GUR_CARRIER_VOWELS[(ch, nxt)])
            i += 1
        elif ch in GUR_CARRIER_FALLBACK:
            out.append(GUR_CARRIER_FALLBACK[ch])
        elif ch == GUR_ADDAK:
            doubled = shift(nxt, -OFFSET) if is_gurmukhi(nxt) else ""
            if is_dev_consonant(doubled):
                out.append(ASPIRATE_BASE.get(doubled, doubled) + DEV_HALANT)
        elif ch in GUR_NUKTA_LETTERS and nxt == GUR_NUKTA:
            out.append(GUR_NUKTA_LETTERS[ch])
            i += 1
        elif ch in (GUR_TIPPI, GUR_BINDI):
            out.append(DEV_ANUSVARA)
        elif ch == "ੜ" and nxt == GUR_HALANT and i + 2 < len(chars) and chars[i + 2] == "ਹ":
            out.append("ढ" + DEV_NUKTA)
            i += 2
        elif ch == "ੜ":
            out.append("ड" + DEV_NUKTA)
        elif ch in ("ੴ",):
            out.append(ch)
        elif ch in ("ੑ", "ੵ", "ੵ"):
            pass
        else:
            out.append(shift(ch, -OFFSET))
        i += 1
    return "".join(out)


def devanagari_to_gurmukhi(text: str) -> str:
    out = []
    chars = list(unicodedata.normalize("NFC", text))
    i = 0
    while i < len(chars):
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        if not is_devanagari(ch) or ch in ("।", "॥"):
            out.append(ch)
        elif ch == DEV_HALANT:
            prev = chars[i - 1] if i > 0 else ""
            if nxt == "य" and i + 2 < len(chars) and chars[i + 2] == "ा":
                # Punjabi spells -्या as ਿਆ (प्यार -> ਪਿਆਰ).
                out.append("ਿਆ")
                i += 3
                continue
            if is_dev_consonant(nxt) and nxt != prev and ASPIRATE_BASE.get(nxt) != prev:
                if nxt in PAIRIN:
                    out.append(GUR_HALANT)
            elif is_dev_consonant(nxt):
                # Doubled consonant: Gurmukhi writes addak before a single letter.
                out[-1] = GUR_ADDAK
        elif ch in (DEV_ANUSVARA, "ँ"):
            prev = out[-1] if out else ""
            consonant_before = "ਕ" <= prev <= "ਹ" or prev in ("ੜ", GUR_NUKTA)
            out.append(GUR_TIPPI if consonant_before or prev in TIPPI_AFTER else GUR_BINDI)
        elif ch in ("ड", "ढ") and nxt == DEV_NUKTA:
            out.append("ੜ" if ch == "ड" else "ੜ੍ਹ")
            i += 1
        elif ch in DEV_TO_GUR_SPECIAL:
            out.append(DEV_TO_GUR_SPECIAL[ch])
        else:
            out.append(shift(ch, OFFSET))
        i += 1
    return "".join(out)


def devanagari_to_roman(text: str) -> str:
    """Readable lyric-style romanization (aa/ee/oo), not academic IAST."""
    # Tokens are [kind, letters, vowel]; kind is "cons", "vowel", "mark" or "other".
    tokens = []
    chars = list(unicodedata.normalize("NFC", text))
    i = 0
    while i < len(chars):
        ch = chars[i]
        nxt = chars[i + 1] if i + 1 < len(chars) else ""
        if is_dev_consonant(ch):
            letters = ROMAN_CONSONANTS[ch]
            if nxt == DEV_NUKTA:
                letters = ROMAN_NUKTA.get(ch, letters)
                i += 1
                nxt = chars[i + 1] if i + 1 < len(chars) else ""
            vowel = "a"
            if nxt in ROMAN_MATRAS:
                vowel = ROMAN_MATRAS[nxt]
                i += 1
            elif nxt == DEV_HALANT:
                vowel = ""
                i += 1
            tokens.append(["cons", letters, vowel])
        elif ch in ROMAN_VOWELS:
            tokens.append(["vowel", ROMAN_VOWELS[ch], ""])
        elif ch in ("ं", "ँ", "ः"):
            tokens.append(["mark", ROMAN_MARKS[ch], ""])
        elif ch in (DEV_HALANT, DEV_NUKTA, "ऽ") or ch in ROMAN_MATRAS:
            pass
        elif "०" <= ch <= "९":
            tokens.append(["other", str(ord(ch) - ord("०")), ""])
        elif ch == "ॐ":
            tokens.append(["other", "om", ""])
        elif ch == "ੴ":
            tokens.append(["other", "Ik Onkar", ""])
        else:
            tokens.append(["other", ROMAN_MARKS.get(ch, ch), ""])
        i += 1

    # Schwa deletion per word: drop a word-final inherent "a", then right to left
    # drop an inherent "a" between a voiced syllable and a consonant that has a vowel
    # (करता -> kartaa, लड़का -> larkaa, but सति stays sati).
    start = 0
    while start < len(tokens):
        if tokens[start][0] == "other":
            start += 1
            continue
        end = start
        while end < len(tokens) and tokens[end][0] != "other":
            end += 1
        word = tokens[start:end]
        if len(word) > 1 and word[-1][0] == "cons" and word[-1][2] == "a":
            word[-1][2] = ""
        for j in range(len(word) - 2, 0, -1):
            tok, prev, nxt = word[j], word[j - 1], word[j + 1]
            prev_voiced = prev[0] in ("vowel", "mark") or (prev[0] == "cons" and prev[2])
            if tok[0] == "cons" and tok[2] == "a" and prev_voiced and nxt[0] == "cons" and nxt[2]:
                tok[2] = ""
        start = end
    return "".join(letters + vowel for _, letters, vowel in tokens)


def detect_scripts(text: str) -> list[str]:
    found = []
    if any(is_gurmukhi(c) for c in text):
        found.append("gurmukhi")
    if any(is_devanagari(c) and c not in ("।", "॥") for c in text):
        found.append("devanagari")
    return found


def convert(text: str, target: str) -> str:
    if target == "devanagari":
        return gurmukhi_to_devanagari(text)
    if target == "gurmukhi":
        return devanagari_to_gurmukhi(text)
    return devanagari_to_roman(gurmukhi_to_devanagari(text))


class AppSetup(BaseAppSetup):
    pass


class RunInput(BaseModel):
    text: str = Field(
        description="Lyrics or any text in Gurmukhi (Punjabi), Devanagari (Hindi), or a mix of both. Line breaks are kept.",
        examples=["ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ\nਪੰਜਾਬ ਦੀ ਧਰਤੀ"],
    )
    target_script: Literal["devanagari", "gurmukhi", "roman"] = Field(
        default="devanagari",
        description="Script to convert to: devanagari (Hindi letters), gurmukhi (Punjabi letters), or roman (readable English letters for lyrics and captions).",
    )


class RunOutput(BaseModel):
    text: str = Field(description="The converted text")
    detected_scripts: list[str] = Field(description="Indic scripts found in the input (gurmukhi, devanagari)")


class App(BaseApp):
    async def setup(self, config: AppSetup):
        pass

    async def run(self, input_data: RunInput) -> RunOutput:
        return RunOutput(
            text=convert(input_data.text, input_data.target_script),
            detected_scripts=detect_scripts(input_data.text),
        )
