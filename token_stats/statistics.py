"""Conteos sobre tokens ya reconocidos, independientes del lexer y de HTTP."""

from collections import Counter


def summarize_tokens(tokens):
    """Cuenta por type sin modificar los tokens; incluye los tokens estructurales."""
    counts = Counter(token["type"] for token in tokens)
    total = sum(counts.values())
    return {
        "total_tokens": total,
        "distinct_types": len(counts),
        "by_type": [
            {
                "type": token_type,
                "count": count,
                "percentage": round(count * 100 / total, 2),
            }
            for token_type, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ],
    }
