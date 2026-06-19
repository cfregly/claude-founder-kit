Subject: Keep your agent's sandbox state between turns

Hey {first_name},

Congrats on getting into YC! Quick tip if you are building a multi-step agent that runs code over your users' files.

A real agent runs across several turns: it ingests a file, cleans it, builds intermediate tables, fits a model, renders a chart. The annoying part is state. If the sandbox does not persist between turns, you re-upload the file and re-run setup on every call, and you write glue to checkpoint the work yourself.

[Claude code execution](https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool) keeps its container and its files across separate requests. Capture the container id from one response, pass it back on the next, and a file written in one turn is there in the next. Containers live 30 days, so the state is there even after the user steps away.

It is one field you carry between calls:

```python
r1 = client.beta.messages.create(model="claude-sonnet-4-6", betas=["code-execution-2025-08-25"],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}], messages=[...])
container_id = r1.container.id                       # keep this

r2 = client.beta.messages.create(model="claude-sonnet-4-6", betas=["code-execution-2025-08-25"],
    container=container_id,                           # reuse it: the file from r1 is still here
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}], messages=[...])
```

I measured the durability directly: I wrote a file in one request, then read it back from the same container after a 31-minute idle, and it was still there.

Want to watch it first, no clone needed? The brief opens with a gif of the run:
https://github.com/cfregly/claude-feature-briefs/blob/main/code_exec_state/README.md

See it run (about a minute):

```
git clone https://github.com/cfregly/claude-feature-briefs && cd claude-feature-briefs
export ANTHROPIC_API_KEY=your-key
make code_exec_state          # write a file and read it back from the reused container
```

Happy building! 🚀
{your_name}
Building with Claude
