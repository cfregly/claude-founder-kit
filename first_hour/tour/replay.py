"""make demo - replay the recorded tour. No key, no beta, runs in seconds."""
import pathlib

transcript = pathlib.Path(__file__).resolve().parent.parent / "transcript.md"
print(transcript.read_text())
