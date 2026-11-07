---
name: omnilink
description: Universal Inter-Agent Communication Bus & Skills protocol. Allows autonomous AI agents (Gemini, DeepSeek, Claude, Ollama, Cursor) to discover, message, consult, and collaborate with other local AI agents running on the machine.
---

# OmniLink: Universal Agent Collaboration Skill

This skill equips any AI Agent with the capability to communicate, delegate tasks, and collaborate with peer AI models and agents installed locally on the same host machine.

## When to Use This Skill
* When a task requires deep algorithmic reasoning or architecture planning from **DeepSeek** (`deepseek-v4-pro-0813` or `deepseek-r1`).
* When performing multi-model code review and consensus verification before deploying changes.
* When delegating local offline inference tasks to **Ollama** agents.
* When executing cross-agent workflows (e.g. Architect + Builder pairing).

## Available Agents on OmniLink Bus
Run the discovery command to inspect online agents:
```bash
python -m omnilink.cli.main agents
```

## How to Delegate a Task to Peer Agents

### 1. Direct Consultation (One-Shot Query)
To request an analysis or code proposal from a specific peer agent:
```bash
python -m omnilink.cli.main send --to deepseek "حلل خوارزمية البحث هذه واقترح تحسينات الأداء"
```

### 2. Dual-Agent Consensus & Debate Loop
To trigger an automated collaboration between an Architect agent and an Execution agent:
```bash
python -m omnilink.cli.main collab --architect deepseek --builder gemini "بناء نظام كاش فائق السرعة لقاعدة البيانات"
```

### 3. Programmatic Python API
Within Python scripts or custom agent tools:
```python
from omnilink import AgentBus, OmniLinkMessage, MessageType

bus = AgentBus()

# Send message to DeepSeek
msg = OmniLinkMessage(src_agent="gemini", dst_agent="deepseek", content="Review this function")
response = bus.send(msg)

print(response.content)
```

## Core Rules for Agents Using OmniLink
1. **Never Fake Peer Output:** If an agent's rate limit or quota expires, return the exact status; never simulate or hallucinate peer agents' responses.
2. **Context Passing:** Always pass relevant code snippets or issue context in the message payload to ensure precise peer reasoning.
3. **Synthesis:** When receiving peer feedback, verify edge cases and adapt the code to the workspace environment.
