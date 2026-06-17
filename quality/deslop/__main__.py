"""CLI: de-slop a file or stdin.

    python -m deslop README.md
    python -m deslop index.html
    python -m deslop README.md --no-judge
    echo "Our leverage is seamless" | python -m deslop -

Exit code is the count of error+warn findings, capped at 255 (0 means clean), so
it drops into a pre-commit hook or CI step. The cap keeps a doc with 256+ findings
from wrapping back to a false 0.

The Claude judge reads for semantic slop the rules cannot catch (vague claims,
hedges, empty sentences). claude-opus-4-8 reviews every interactive run (a key is
set and stdout is a TTY) and prints advisory notes below the score. The gate
(check_docs, CI, `--min-score`) stays deterministic and never calls the API: when
stdout is piped to a subprocess the judge does not fire by default. The judge
never changes the deterministic score or the exit code, so the gate stays
reproducible. `--judge` forces the attempt regardless of TTY (it prints why it
skipped when no key is set). `--no-judge` turns it off even when a key is set.
"""
from __future__ import annotations

import os
import sys

from .rules import lint, load_config


def main(argv: list[str]) -> int:
    flags = [a for a in argv if a.startswith("-") and a != "-"]
    positional = [a for a in argv if not a.startswith("-") or a == "-"]
    known = {"--judge", "--no-judge"}
    if len(positional) != 1 or any(f not in known for f in flags):
        print(__doc__.strip())
        return 0
    # The judge reviews every interactive run (a key is set and stdout is a TTY).
    # --judge forces the attempt regardless of TTY (so a no-key run prints why it
    # skipped), --no-judge turns it off even when a key is set. The score below is
    # decided before any of this and never depends on it.
    force_judge = "--judge" in flags
    no_judge = "--no-judge" in flags
    src = positional[0]
    text = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
    # A .desloprc next to the file (or up at the repo root) blesses intentional
    # choices so the linter does not nag.
    config = load_config(os.path.dirname(os.path.abspath(src)) if src != "-" else None)
    report = lint(text, config)

    name = "stdin" if src == "-" else src
    head = f"{name}: prose {report['prose_grade']} ({report['prose_score']}/100)"
    if "visual_grade" in report:
        head += f", visual {report['visual_grade']} ({report['visual_score']}/100)"
    if config.get("_path"):
        head += f"  [.desloprc applied]"
    print(head)

    blocking = 0
    for f in report["findings"]:
        loc = f":{f['line']}" if f.get("line") else ""
        print(f"  [{f['severity'].upper()}] {f['rule']}{loc} {f['message']}")
        print(f"          fix: {f['fix']}")
        if f["severity"] in ("error", "warn"):
            blocking += 1
    if not report["findings"]:
        print("  clean")

    # The Claude judge is advisory only: it prints below the score and never
    # changes it or the exit code, so the deterministic gate stays reproducible.
    # The rules already decided the grade. By default it runs only on a direct
    # interactive run, detected by stdout.isatty(). When stdout is a pipe or a
    # subprocess (check_docs, CI, `make check`), it does not fire, so the gate
    # never calls the API. --judge forces it on regardless, --no-judge forces
    # it off. With no key the run is a no-op (--judge prints why).
    from .judge import available, judge_text
    run_judge = (not no_judge) and (force_judge or (available() and sys.stdout.isatty()))
    if run_judge:
        jr = judge_text(text)
        if not jr["live"]:
            why = jr.get("error", "no ANTHROPIC_API_KEY or anthropic not installed")
            print(f"  [judge] skipped ({why})")
        elif not jr["findings"]:
            print(f"  [judge] {jr['model']}: no semantic slop found")
        else:
            print(f"  [judge] {len(jr['findings'])} advisory note(s) from "
                  f"{jr['model']} (not scored):")
            for f in jr["findings"]:
                print(f"    - \"{f['quote']}\"")
                print(f"      why: {f['why']}")
                print(f"      try: {f['suggestion']}")

    # Cap at 255: the process exit code is a byte, so a doc with 256+ blocking
    # findings would otherwise wrap to 0 and read as falsely clean.
    return min(blocking, 255)


def cli() -> int:
    """Console-script entry point (`deslop <file>`), wired in pyproject.toml."""
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
