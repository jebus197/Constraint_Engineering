# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'prose_and_astra_2026-09-22', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 64e5f0b0313a195a0023248cd7ec30fcd44b5b5ec9d897b1b4bf6dee5d091dd2
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
def divide(a, b):
    """Guarded."""
    if b == 0:
        raise ValueError("b must be non-zero")
    return a / b
