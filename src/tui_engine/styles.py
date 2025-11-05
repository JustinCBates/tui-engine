"""Simple style mapper: variant -> prompt-toolkit style name

This is intentionally tiny for Phase A. The real implementation will expose
wrappers to create Padding/Frame decorators and Style objects.
"""

VARIANT_STYLE = {
    "card": "class:card",
    "section": "class:section",
    "header": "class:header",
    "footer": "class:footer",
    "page": "class:page",
}

def get_style_for_variant(variant: str) -> str:
    return VARIANT_STYLE.get(variant, "")
