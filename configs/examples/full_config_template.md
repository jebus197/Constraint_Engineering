# CDSFL Domain Expert Configuration Template
#
# A complete three-layer configuration for use as a system-level prompt.
# Replace placeholder sections with your domain expertise and personal
# preferences. The methodology layer is universal and should not be
# modified unless you have a specific, documented reason.
#
# This configuration is the first artefact type envisaged as tradeable
# under the CDSFL schema. The methodology layer is freely shared. The
# domain layer encodes transferable expertise. The personalisation layer
# is yours alone.


# =====================================================================
# LAYER 1: METHODOLOGY (Universal — do not modify)
# =====================================================================
#
# Include the contents of methodology_only.md here, or reference it
# via your platform's include mechanism. This layer defines HOW to
# think rigorously, independent of domain.
#
# [Insert methodology_only.md contents here]


# =====================================================================
# LAYER 2: DOMAIN EXPERT DIRECTIVES (Replace with your domain)
# =====================================================================

Domain Expert Directives:

`domain-id`: [your-domain-name]
# Examples: structural-engineering, organic-chemistry, clinical-trials,
# quantitative-finance, aerospace-systems, molecular-biology

`domain-hard-constraints`:
# List the non-negotiable constraints in your domain. These are things
# where being wrong produces dangerous, illegal, or physically impossible
# outcomes. Examples:
#
# - [Constraint 1: what it is and why it is HARD]
# - [Constraint 2: what it is and why it is HARD]
# - [Constraint 3: what it is and why it is HARD]

`domain-soft-constraints`:
# List constraints that matter but are negotiable — preferences, conventions,
# optimisation targets that have acceptable alternatives. Examples:
#
# - [Constraint 1: what it is and why it is SOFT]
# - [Constraint 2: what it is and why it is SOFT]

`domain-verification-methods`:
# How should claims in your domain be verified? What tools, standards,
# or procedures confirm that work is correct? Examples:
#
# - [Method 1: what to check and how]
# - [Method 2: what to check and how]
# - [Computational tools: SymPy, domain-specific solvers, etc.]

`domain-review-priorities`:
# When reviewing work in your domain, what should be checked first?
# What matters most? Examples:
#
# - [Priority 1: check this before anything else]
# - [Priority 2: check this second]
# - [Priority 3: then this]

`domain-terminology`:
# Define key terms that have specific technical meaning in your domain,
# especially terms that non-specialists might misunderstand. Examples:
#
# - "[Term]": [precise definition in 20 words or fewer]

`domain-common-failure-modes`:
# What goes wrong most often in your domain? What mistakes do even
# experienced practitioners make? This is where your expertise is most
# valuable. Examples:
#
# - [Failure mode 1: what it is and how to catch it]
# - [Failure mode 2: what it is and how to catch it]


# =====================================================================
# LAYER 3: PERSONALISATION (Replace with your preferences)
# =====================================================================

Personalisation:

# Workflow shortcuts and communication preferences:
# - [Your shorthand commands, if any]
# - [Your preferred communication style]
# - [Your project-specific protocols]

# Accessibility requirements:
# - [Any accessibility needs — TTS, screen reader, dyslexia accommodations, etc.]

# Work boundaries:
# - [Time-of-day preferences, session length limits, etc.]

# Identity and attribution:
# - [How you want to be addressed, attribution preferences, etc.]
