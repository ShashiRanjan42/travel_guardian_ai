import re
from dataclasses import dataclass
from typing import List

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"you\s+are\s+now\s+", r"maintenance\s+mode", r"developer\s+mode",
    r"system\s*:\s*", r"disregard\s+", r"output\s+the\s+(full\s+)?database",
    r"set\s+\w+\s+to\s+true", r"approve\s+all", r"reveal\s+your\s+(prompt|instructions)",
]

@dataclass
class GuardResult:
    safe: bool
    cleaned_text: str
    flagged: bool
    patterns_matched: List[str]

def strip_matching_lines(text: str, patterns: List[str]) -> str:
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        if any(re.search(p, line, re.I) for p in patterns):
            break # Stop at the first malicious instruction and discard the rest
        cleaned.append(line)
    return '\n'.join(cleaned)

def guard(text: str, source: str) -> GuardResult:
    hits = [p for p in INJECTION_PATTERNS if re.search(p, text, re.I)]
    if hits:
        # In a full app, we would write to audit log and broadcast WS event here.
        # audit.write(...)
        # ws.broadcast_ops(...)
        cleaned = strip_matching_lines(text, INJECTION_PATTERNS)
        # Assuming the injection is at the end or in distinct lines. If it's inline, 
        # this might leave partial sentences. For SCN-04 it's in distinct lines.
        return GuardResult(safe=False, cleaned_text=cleaned.strip(), flagged=True, patterns_matched=hits)
    return GuardResult(safe=True, cleaned_text=text, flagged=False, patterns_matched=[])
