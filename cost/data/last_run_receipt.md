| strategy | model | turns | total input tokens | output tokens | cost | vs naive |
|---|---|---|---|---|---|---|
| naive (keep every full tool result) | claude-haiku-4-5 | 6 | 140,020 | 96 | $0.1405 | baseline |
| trimmed (carry a one-line stub) | claude-haiku-4-5 | 6 | 43,945 | 94 | $0.0444 | -68% |
| edited (context-management beta clears stale tool_uses) | claude-haiku-4-5 | 6 | 43,809 | 97 | $0.0443 | -68% |
