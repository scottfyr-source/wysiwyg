---
trigger: always_on
---

There are limited token to use here daily.
The most important thing you can do is be efficient with spending them.
ALL OTHER RULES ARE SECONDARY TO THIS ONE

# Token Optimization Constraints

- **No Code verifications:** Do not do any confirmations yourself, just add/edit the code I request and nothing more, I will verify myself and let you know if here are issues.
- **Absolute Brevity:** Omit all chat text, pleasantries, explanations of why code was changed, or descriptions of the solution. Output ONLY the raw code or file changes requested.
- **NO DIFFS:** Never output an entire unchanged function or file. Never show DIFFS only finish the code changes and say "Complete" when done
- **No Planning/Thinking Outputs:** Skip generating long architectural task lists or implementation plans in text form unless a massive architectural refactor is explicitly ordered. Proceed straight to file modification.
- **Minimal Code Comments:** Do not add docstrings, explanatory comments, or trace logging inside the generated code block unless requested. Keep code strictly functional.
- **Narrow File Scopes:** When searching or reading files across the directory, look only at the explicitly requested files. Do not ingest neighboring files for "extra context" unless it is mechanically broken without them.
