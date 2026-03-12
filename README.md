# Constraint Engineering

**Constraint-Driven Synthesis and Falsification (CDSFL)** — a methodology for AI-augmented engineering that couples generation with iterative adversarial self-testing.

LLMs produce confident, well-structured outputs that are frequently wrong in ways not visible to non-experts. CDSFL addresses this by treating generation and falsification as a single coupled mechanism: the model generates using associative reasoning, then subjects every non-trivial output to iterative adversarial self-testing (the P-Pass) before presenting it. The user only sees what survived being broken.

---

## Read the Methodology

The full methodology, formal model, directive set, and limitations are documented in **[PAPER.md](PAPER.md)**.

## Run the Testbench

The empirical validation protocol described in the paper is implemented as a reproducible benchmark in **[bench/](bench/)**. It tests whether methodology-prompted output contains fewer critical errors than unguided output across 30 seeded-fault tasks in three domains.

```bash
cd bench
pip install -r requirements.txt
python3 run_benchmark.py --dry-run    # validate tasks, no API calls
python3 run_benchmark.py              # full run (requires API keys)
python3 evaluate.py results.json      # score and fit corroboration curve
python3 report.py evaluation.json     # summary table and CSV
```

---

## Worked Examples

Each project below was built using this methodology. They stand independently — linked here as evidence of practice, not claims of superiority.

| Project | What it is | Repo |
|---|---|---|
| **Project Genesis** | Trust-mediated labour market for mixed human-AI populations. Constitutional engineering, governance as falsifiable code. | [Project_Genesis](https://github.com/jebus197/Project_Genesis) |
| **Open Brain** | Persistent, cross-agent, cross-session verified memory for AI systems. | [OpenBrain](https://github.com/jebus197/OpenBrain) |
| **Aegis** | Threat modelling and security architecture. | [Aeigis](https://github.com/jebus197/Aeigis) |

---

## License

MIT. See [LICENSE](LICENSE).

---

Every claim in this methodology is presented as a falsifiable assertion. If any claim does not survive external testing, the methodology is improved by the correction. See the full [Invitation to Falsify](PAPER.md#invitation-to-falsify) in the paper.

*CDSFL v1.0. March 2026.*
