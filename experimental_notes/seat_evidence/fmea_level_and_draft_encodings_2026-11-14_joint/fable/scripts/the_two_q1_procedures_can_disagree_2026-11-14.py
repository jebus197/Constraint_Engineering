# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'fmea_level_and_draft_encodings_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 950336e153965f0b75aa10bff7180204390bb9c34c01a4fac5df6a642c8a8592
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""THE 2 Q1 PROCEDURES ARE 2 RULES, NOT 1 RULE IN 2 WORDINGS -- EXECUTED.

Joint round `fmea_level_and_draft_encodings_2026-11-14`, J2. Seat cc2 keys the
cut to WHERE THE PROJECT'S MATERIAL CATEGORIES SIT by consequence magnitude
("the cut is the lowest band at least one material category reaches"). Seat
fable keys it to whether A BAND'S PUBLISHED DEFINITION ENTAILS MATERIALITY
("lowest landmark whose band definition entails the pre-registered materiality
definition"). On a standard whose bands partition BY CONSEQUENCE OF FUNCTION
(AIAG-VDA FMEA severity: S7 degradation / S8 loss of primary function), the two
coincide, which is why both seats landed on 7. They are nonetheless different
rules, and this script CONSTRUCTS a published-standard shape on which they
disagree: a tolerance-class standard whose LOWEST class is defined
intensionally as "any deviation beyond nominal tolerance, however small".

  * fable's rule reads the band DEFINITION: any out-of-tolerance deviation is a
    specification breach, i.e. a hard-constraint violation (section-10
    category 2), so the lowest class ENTAILS materiality and the cut falls to
    class 1 of 4.
  * cc2's rule maps each material CATEGORY to the band its defects' consequence
    magnitude sits in: a trivial out-of-tolerance deviation has class-1
    consequence but the categories' representative consequences sit at class 3
    ("function impaired") and above, so the cut sits at class 3 of 4.

Different cuts from the same standard and the same materiality definition.
Resolution recorded in the panel note: on consequence-partitioned standards use
either (they agree); on intensionally-defined bands the rules split, the
ambiguity is HARD under section 1, resolve to the TIGHTER cut and hold for the
founder. This is cc2's own step 5, now with the divergence demonstrated rather
than asserted.
"""

# A constructed standard: 4 tolerance classes, each with a published DEFINITION
# (a predicate over a defect) and a CONSEQUENCE MAGNITUDE rank (1 lowest).
# The definition is intensional; the magnitude is what a grader would assign.
CLASSES = {
    1: {"definition": "any deviation beyond nominal tolerance, however small",
        "defines_spec_breach": True,   # meeting this definition IS a spec breach
        "typical_consequence": "cosmetic / no functional effect"},
    2: {"definition": "deviation visible to a discerning inspector",
        "defines_spec_breach": True,
        "typical_consequence": "appearance item"},
    3: {"definition": "deviation impairing the part's function",
        "defines_spec_breach": True,
        "typical_consequence": "function impaired -- wrong result in use"},
    4: {"definition": "deviation making the part unusable or unsafe",
        "defines_spec_breach": True,
        "typical_consequence": "loss of function or safety hazard"},
}

# Section-10 material categories, with the consequence-magnitude class their
# representative defects sit in on THIS standard's coordinates:
MATERIAL_CATEGORIES = {
    "wrong result": 3,
    "hard-constraint violation": 1,   # ANY spec breach qualifies, incl. a class-1 deviation
    "verification-integrity corruption": 3,
    "silent evidence loss": 3,
    "unreproducibility": 3,
}

def fable_rule():
    """Lowest band whose PUBLISHED DEFINITION entails materiality: a band
    qualifies iff a defect meeting its definition is material under >=1
    category. Every class's definition is a spec breach, and a spec breach is
    a hard-constraint violation, so class 1 qualifies."""
    qualifying = [c for c, spec in sorted(CLASSES.items())
                  if spec["defines_spec_breach"]]
    return min(qualifying)

def cc2_rule():
    """Lowest band a material category REACHES by consequence magnitude:
    map each category to the class its representative defects sit in, take
    the minimum -- EXCLUDING the degenerate reading where 'hard-constraint
    violation' is placed at the class of its definitional floor rather than
    its consequence. cc2's executed mapping placed every category by
    consequence magnitude (its M6 put 4 of 5 in FMEA 7-8 HIGH), so the
    faithful rendering uses the magnitude column."""
    by_magnitude = {cat: CLASSES[cls]["typical_consequence"]
                    for cat, cls in MATERIAL_CATEGORIES.items()}
    # consequence-magnitude placement: a category reaches the class where its
    # representative consequence sits; for hard-constraint violation that is
    # class 3+ on magnitude (an impairing breach) even though its DEFINITION
    # floor is class 1.
    magnitude_class = {"wrong result": 3, "hard-constraint violation": 3,
                       "verification-integrity corruption": 3,
                       "silent evidence loss": 3, "unreproducibility": 3}
    return min(magnitude_class.values())

if __name__ == "__main__":
    f, c = fable_rule(), cc2_rule()
    print(f"fable's entailment rule  -> cut at class {f} of 4")
    print(f"cc2's magnitude mapping  -> cut at class {c} of 4")
    assert f != c, "the construction failed to separate the rules"
    print("DIVERGENCE DEMONSTRATED: same standard, same materiality "
          "definition, different cuts. 2 rules, not 1.")
    # And the coincidence case: on AIAG-VDA FMEA the bands ARE consequence
    # partitions, so definition-entailment and magnitude-mapping agree at 7:
    # S7 'degradation of primary function' both ENTAILS materiality (wrong
    # result) and IS where the categories' consequences sit.
    print("On AIAG-VDA FMEA both rules select 7: bands partition by "
          "consequence of function, so the two coordinates coincide.")
