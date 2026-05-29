"""Shared constants for Voynich corpus analysis."""

# The 8 exact forms: ok/ot prefix + ar/al/or/ol suffix
FORMS: list[str] = [
    "okal", "okar", "okol", "okor",
    "otal", "otar", "otol", "otor",
]

# Standalone border values (matrix elements)
BORDER: frozenset[str] = frozenset({"ar", "al", "or", "ol"})

# Operator prefixes (mode/locus/class operators)
OPERATORS: frozenset[str] = frozenset({"ok", "ot", "qo", "yk", "yt"})

# Closure/terminal borders
CLOSURES: frozenset[str] = frozenset({"-dy", "-y", "-aiin"})

# Valid locus kinds (IVTFF)
LOCUS_KINDS: frozenset[str] = frozenset({"P", "L", "C", "R"})

# Valid manual annotation statuses for visual review
ANNOTATION_STATUSES: frozenset[str] = frozenset({"annotated", "not_visible", "uncertain"})

# Axis decomposition: a/o axis (stronger, Cramer's V≈0.26 for prefix)
A_SUFFIXES: frozenset[str] = frozenset({"al", "ar"})   # a-axis
O_SUFFIXES: frozenset[str] = frozenset({"ol", "or"})   # o-axis

# r/l axis (weaker, possibly visual/diagrammatic)
R_SUFFIXES: frozenset[str] = frozenset({"ar", "or"})   # r-axis
L_SUFFIXES: frozenset[str] = frozenset({"al", "ol"})   # l-axis

# Key statistical findings (for documentation/reference)
ROTA_43_CHI2 = 10.54        # chi²(1df) for ar-group vs al/ol-group standalone rate
ROTA_43_AR_RATE = 0.154     # 15.4% — forms ending in -ar followed by standalone border
ROTA_43_AL_RATE = 0.068     # 6.8%  — forms ending in -al/-ol followed by standalone border
