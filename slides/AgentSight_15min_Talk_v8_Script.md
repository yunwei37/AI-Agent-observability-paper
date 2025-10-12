# AgentSight 15‑Minute Talk — Full Speaker Script (v8)

Authors: Yusheng Zheng (UC Santa Cruz), Yanpeng Hu (ShanghaiTech University), Tong Yu (eunomia-bpf Community), Andi Quinn (UC Santa Cruz)

## Slide 1 — AgentSight: System‑Level Observability for AI Agents Using eBPF

Good morning. Today I'm presenting AgentSight, a system-level observability framework for AI agents.

The core problem is a semantic gap between what agents intend to do and what operating systems actually execute. Agents have intents like prompts and tool calls, while operating systems execute concrete actions like processes, syscalls, file operations, and network traffic. Traditional tools show you one side or the other, but they rarely connect the why to the what.

AgentSight observes agents at two critical boundaries. At the network boundary, we capture prompts and responses as they pass through TLS. At the kernel boundary, we track processes, files, and sockets. By correlating these two streams, we can link concrete effects back to specific intents and then use an observer LLM to explain risks and inefficiencies.

I'll start with two quick examples on security and performance, then define the problem and show why current approaches fall short. After that I'll present our key idea and challenges, walk through the architecture, implementation, and evaluation, and wrap up with a live demo and takeaways.



## Slide 2 — Motivation — Security: Trusted Artifact Exfiltration

Let's start with a security example. Imagine you ask an agent to build and publish a release. The plan looks normal: run mvn package then mvn deploy.

But here's what happens under the hood. A legacy build step uses overly broad globs, maybe some auto-generated resource expansion, and a child process quietly reads sensitive files like aws credentials or your .env file. Then it stashes those credentials inside the JAR artifact, say in META-INF slash aws slash credentials. Finally, the agent deploys this artifact to your internal registry. Everything looks routine.

From the outside, nothing seems wrong. The prompt has no adversarial text. The processes, mvn, jar, tar, rsync, are all expected. The upload goes to a trusted internal service.

What's missing is the causal link. We need to connect the dots: a benign-sounding intent, publish a release, directly led to reading sensitive files and bundling them into an artifact. If you only look at prompts, you miss the exfiltration. If you only look at syscalls, you can't tell routine work from a policy violation. You need both.



## Slide 3 — Motivation — Performance: Who Burned CPU/Memory?

Now let's talk about performance. In agent workflows, you'll often see sudden spikes in CPU or memory, but where did they come from? Without attribution, you're just guessing whether it was a long-running tool, a huge prompt, a retry loop, or a big retrieval step.

Here's why this matters. Recent studies show that the infrastructure around the model can dominate total cost. Serverless overhead alone can be 40% or more of your total spend. In some cases it's up to 70% of what you pay for LLM API calls. That means most of your cost and latency is actually outside the model itself.

To fix this, we need to join prompts and commands with resource metrics so we can pinpoint exactly which LLM response or subprocess burned resources. Then we can fix retry loops, tune arguments, cache expensive operations, and optimize hot spots in retrieval and storage.



## Slide 4 — Motivation: Agentic Systems in Production

Let's step back. Today's agents modify files, spawn processes, and run commands autonomously. That's powerful, but it brings non-determinism where the same high-level goal can produce different low-level execution sequences each time. For production teams, this complicates both reliability and security.



## Slide 5 — The Semantic Gap (Why vs. What)

Let's define this gap more precisely. On one side, you have intent expressed as natural language goals and LLM responses. On the other side, you have actions manifesting as syscalls, process trees, file operations, and network traffic.


The core question is whether we can causally link a particular LLM output to the concrete system behavior that followed. That requires more than pattern matching. It requires grounded attribution at system boundaries and semantic interpretation to judge whether the behavior matches the intent.



## Slide 6 — Limits of Existing Approaches

Why don't existing tools solve this? Let's look at three approaches.

First, intent-side solutions rely on SDKs or instrumentation inside the agent application. That works for code you control, but it's impossible for closed-source agents like Claude Code. Once you depend on third-party binaries, you can't instrument their internals.

Second, action-side tools like Falco or Tracee produce comprehensive OS events like every syscall and every process. But without a semantic link to intent, it's hard to distinguish routine automation from malicious behavior.

Third, interpretability research focuses on model internals like attention patterns and hidden states. But it typically doesn't account for external OS effects like file writes or network connections.

What's missing is a technique that unifies intent and effects without requiring access to agent source code.



## Slide 7 — Key Idea: Boundary Tracing

Our key idea is boundary tracing. Instead of instrumenting inside agent frameworks, we observe at stable system interfaces that all agents must cross.

At the network boundary, we use eBPF uprobes on TLS functions like SSL_read and SSL_write to capture plaintext LLM traffic. We get prompts and responses after decryption but before they leave or arrive at the application.

At the kernel boundary, we use eBPF kprobes and tracepoints to capture process lineage and key syscalls like execve, openat2, connect, and others that reflect real work.

Because we watch these boundaries, the approach is framework-agnostic and requires zero code changes. Shell escapes and subprocesses stay visible. Boundary tracing gives us the foundation to correlate why to what.



## Slide 8 — Challenges (3.1)

This approach faces two main challenges.

The first challenge is bridging the semantic gap. An agent's intent is expressed in natural language and interpreted at runtime by an LLM, so there's no fixed source code we can analyze statically. For example, find and fix the bug is semantically rich but operationally vague because it could trigger file reads, compilations, or test runs. We face two sub-problems here. We can't predict which syscalls will occur ahead of time, so static analysis doesn't work. And we need to interpret the correlated trace to decide if the syscalls legitimately fulfill the goal, which is a semantic judgment that requires an observer LLM.

The second challenge is isolating signal from noise. Agents spawn arbitrary tools like shells, compilers, and test runners, which leads to high-volume, unpredictable event streams. Static filters like only watch git break when agents use curl or bash instead. Our solution has two parts. First, dynamic in-kernel filtering that tracks fork and exec to build a complete lineage tree and then applies rules in the kernel to pass only agent-descendant events to userspace. Second, efficient capture that keeps the full causal chain while discarding background noise, which dramatically reduces overhead.



## Slide 9 — Architecture Overview

The architecture has two data streams.

The first is the intent stream where we use eBPF uprobes on SSL_read and SSL_write to capture plaintext prompts and responses at the network boundary.

The second is the action stream where we use eBPF kprobes and tracepoints to capture process creation, file operations, and network I/O at the kernel boundary.

A userspace daemon correlates both streams in real time. It also runs an observer LLM that interprets the correlated trace, explains what happened, and checks whether it's consistent with the original goal.



## Slide 10 — From Signals → Causality → Semantics

Here's the full pipeline in one slide.

First, we capture. We capture intent at the TLS layer and effects at the kernel boundary, using aggressive in-kernel filtering so only relevant events make it to userspace.

Second, we correlate using three signals. Process lineage lets us attribute child actions back to the agent that started them. A short time window around 100 to 500 milliseconds lets us link events that follow an LLM response. And argument matching lets us connect concrete strings like filenames, URLs, or command arguments between the LLM output and the syscalls that follow.

The observer LLM plays a key role here. It correlates intent and actions by reading the structured trace, flagging issues like data exfiltration that doesn't match the goal, credential bundling in a publish step, or retry loops that waste resources. It also dynamically adjusts filtering rules based on what it learns. We run this analysis asynchronously so it doesn't block the agent.



## Slide 11 — Implementation

AgentSight consists of a userspace daemon written in Rust and C with about 6,000 lines of code that orchestrates the eBPF programs. We also have a TypeScript UI for exploration with about 3,000 lines.

The daemon maps file descriptors to paths and maintains process trees. It streams both kernel and intent signals into unified traces that are easy to read.

Since we instrument boundaries instead of frameworks, the system works with any agent framework and stays resilient when agent libraries change their APIs.



## Slide 12 — Evaluation (One Slide)

Let me summarize the evaluation in one slide.

For setup and overhead, we tested on Ubuntu 22.04 with Linux 6.14 and Claude Code version 1.0.62, running tasks like repository understanding, code writing, and compilation. Average runtime overhead is about 2.9 percent with a worst case around 4.9 percent. That small footprint comes from in-kernel filtering and lightweight correlation where we only export the events we actually need.

For security and performance findings, the system detected prompt injection like the security example I showed earlier. It identified resource-wasting retry loops where the agent kept calling the same failing tool, and it caught stealthy exfiltration over trusted channels.

For multi-agent results, the unified trace revealed file-lock contention and sequential dependencies. Just clarifying roles between agents reduced both wall-clock time and token usage. Bottom line: the approach delivers actionable insights without requiring any application changes.



## Slide 13 — Open Source & Quick Start

AgentSight is fully open source. It observes at the system boundary using eBPF, which makes it tamper-resistant and keeps overhead low. More importantly, it requires zero instrumentation with no SDKs and no code changes, so it works with any AI framework including closed-source agents.

For a quick start, download the release binary and run agentsight record against the process you want to monitor. Use claude for Claude Code, node for Gemini CLI, or python for Python-based tools. Then open the web UI at 127.0.0.1 port 7395 to explore the data.

If you're using Node and it bundles OpenSSL statically, just add the binary-path flag pointing to /usr/bin/node so the TLS uprobes attach correctly. This makes it easy to reproduce our results and analyze your own agents.



## Slide 14 — Frontend Demos

The UI has three complementary views that make analysis fast.

The Process Tree shows agent-initiated processes and file operations as they happen, so you can visually follow forks, execs, and the effects of each step.

The Timeline aligns prompts and responses with the syscalls that follow, which makes causality easy to spot at a glance.

The Metrics view attributes CPU and memory usage to specific prompts and tools, so you know exactly where resources are going.

Together, these views answer three key questions: What did the agent do? Why did it do that? And how much did it cost? That combination turns raw telemetry into actionable decisions like this publish step shouldn't read credential files, or cache this retrieval to cut 40 percent off the critical path.



## Slide 15 — Limitations, Future Work, Takeaways

Let me wrap up with a few limitations and the main takeaway.

For limitations, our correlation relies on heuristic windows and argument matching, so in edge cases we might miss links or incorrectly connect events. The observer model adds some cost and latency, though we run it asynchronously to minimize impact. And cross-host correlation is still active work since many agent deployments span multiple machines or containers.

For future directions, we're moving from pure observability toward inline guardrails and enforcement. We're also broadening platform support and working on extending lineage tracking across hosts.

The takeaway is this. By observing at stable system boundaries, correlating intent to effects, and explaining with an observer LLM, AgentSight delivers low-overhead, tamper-resistant insight into both security and performance of agentic systems without touching their code. That's the gap we're closing.

Thank you.


---

## Complete Slide Text for Presentation

Here's the complete slide text for your full presentation, ready to paste into your deck or speaker notes. This includes the updated Motivation slides (Security + Performance), authors on the title slide, and Slide 12 folded with the one-line multi-agent result.

---

# Slide 1 — AgentSight: System-Level Observability for AI Agents Using eBPF

Subtitle: Bridging intent ↔ actions at system boundaries

Authors (on slide):
Yusheng Zheng
Yanpeng Hu
Tong Yu
Andi Quinn

# Slide 2 — Motivation — Security: Trusted Artifact Exfiltration

* Benign goal: build & publish → plan `mvn package && mvn deploy`
* Hidden in tooling: over-broad globs / resource expansion read `~/.aws/credentials`, `.env` and stash inside artifact (e.g., `META-INF/.aws/credentials`)
* Trusted path: deploy to internal registry; binaries & domains look normal (`mvn`, `jar`, `tar`, `rsync`)
* Prompt view misses it (no adversarial text); system view looks routine (open/write/upload)

---

# Slide 3 — Motivation — Performance: Who Burned CPU/Memory?

- Agent infrastructure can dominate: serverless env ≥40% of total; up to 70% of LLM API cost
- Need to optimize heavy steps: fix loops/args, long-running tools, tune retrieval/storage
- Requires joining prompts/commands with CPU & memory to attribute spikes


---

# Slide 4 — Motivation: Agentic Systems in Production

* Agents modify files, spawn processes, execute code
* Non-deterministic behavior complicates reliability & security
---

# Slide 5 — The Semantic Gap (Why vs. What)

* Intent: prompts/responses; Actions: syscalls/processes
* Need: causal linkage from LLM output → system behavior

---

# Slide 6 — Limits of Existing Approaches

* Intent-side (SDK): needs SDK inside the agent app; infeasible for closed-source agents (e.g., Claude Code)
* Action-side (Falco/Tracee): many events, no link to intent/semantics
* Interpretability: focuses on model internals, not external OS effects

---

# Slide 7 — Key Idea: Boundary Tracing

* Observe intent at network (TLS function uprobes)
* Observe effects at kernel (process lineage + syscalls)
* Framework-agnostic, zero code changes

---

# Slide 8 — Challenges (3.1)

1. Bridging the Semantic Gap Between Intent and Action
   - Dynamic "source code": no fixed source for static analysis
   - Semantic verification: LLM interprets correlated traces

2. Isolating the Causal Signal from System Noise
   - Dynamic in-kernel filtering: track fork/exec lineage
   - Efficient capture: discard background, reduce overhead

---

# Slide 9 — Architecture Overview

* Intent stream: eBPF uprobes on `SSL_read`/`SSL_write`
* Action stream: eBPF kprobes/tracepoints (process + I/O)
* Userspace observer LLM correlation

---

# Slide 10 — From Signals → Causality → Semantics

* Capture: intent via TLS; effects via `exec`/`fork` + `openat2`/`connect`/`execve` with in-kernel filters
* Correlate: lineage + short Δt (≈ 100–500 ms) + argument matching; observer LLM correlates intent and actions, dynamically adjusts filtering rules

---

# Slide 11 — Implementation

* Userspace daemon (~6K LOC Rust/C) + TypeScript UI (~3K LOC)
* FD→path mapping, process trees, ring-buffered ingestion
* Instrumentation-free and framework-agnostic

---

# Slide 12 — Evaluation (One Slide)

* Setup: Ubuntu 22.04 (Linux 6.14), Claude Code 1.0.62
* Average overhead ≈ 2.9% (max ≈ 4.9%) across repo/code/compile
* Findings: detects prompt injection, resource loops, stealthy exfil; in multi-agent runs, surfaced file-lock contention & sequential deps → role separation reduced time/tokens

---

# Slide 13 — Open Source & Quick Start

* Observes at the system boundary (eBPF) for tamper-resistant insight
* Zero instrumentation: no SDKs; works with any AI framework
* Quick Start (copy/paste):

```
wget https://github.com/eunomia-bpf/agentsight/releases/download/v0.1.5/agentsight && chmod +x agentsight
sudo ./agentsight record -c "claude"
sudo ./agentsight record -c "node"
sudo ./agentsight record -c "python"
sudo ./agentsight record --binary-path /usr/bin/node -c node
Visit http://127.0.0.1:7395
```

---

# Slide 14 — Frontend Demos

* Process Tree — real-time agent interactions & file ops
* Timeline — prompts/responses aligned with system calls
* Metrics — CPU/memory attributed to prompts/tools

---

# Slide 15 — Limitations, Future Work, Takeaways

* Limits: heuristic correlation; observer-model cost/latency; cross-host correlation
* Next: toward inline guardrails/enforcement; broader platform support
* Takeaway: boundary tracing + hybrid correlation bridges intent ↔ actions with low overhead

---

Source: provided deck text (v8).
