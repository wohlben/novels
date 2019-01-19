from os import environ as _environ

if _environ.get("CI") == "true":
    print("processins is unavailable in CI")
    __all__ = []
else:
    from .TextRanker import TextRanker

    __all__ = ["TextRanker"]
