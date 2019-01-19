from os import environ as _environ

if _environ.get("CI") == "true":
    print("processins is unavailable in CI")
    __all__ = []
else:
    from .TextRanker import TextRanker
    from .utilites import set_custom_boundaries

    __all__ = ["TextRanker", "set_custom_boundaries"]
