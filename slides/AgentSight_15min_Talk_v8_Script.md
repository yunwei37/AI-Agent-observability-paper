# AgentSight 15‑Minute Talk — Full Speaker Script (v8)

Authors: Yusheng Zheng (UC Santa Cruz), Yanpeng Hu (ShanghaiTech University), Tong Yu (eunomia-bpf Community), Andi Quinn (UC Santa Cruz)

## AgentSight: System‑Level Observability for AI Agents Using eBPF

Opening. Good morning/afternoon. This talk presents AgentSight, a system‑level observability framework for AI agents. Our focus is the semantic gap that separates what an agent intends to do (its prompts and tool calls) from what the operating system actually executes (processes, syscalls, file and network I/O). Traditional tooling delivers one side or the other, but rarely connects why to what.

What we propose. AgentSight observes at the system boundaries every agent must cross: the network boundary (where prompts and responses traverse TLS) and the kernel boundary (where processes, files, and sockets are touched). By correlating those two streams, we can attribute concrete effects back to a specific intent, then ask an observer LLM to explain risks and inefficiencies in natural language.

Roadmap. I'll start with two short motivation examples—one about security, one about performance—then lay out the problem precisely, discuss the limits of current approaches, present the key idea and the challenges it must overcome, and conclude with the architecture, pipeline, implementation, and evaluation results. We'll finish with a quick open‑source tour and the main takeaways.



## Motivation — Security: Trusted Artifact Exfiltration

Consider a security scenario that looks perfectly benign on paper. We ask the agent to *build and publish* a release; its plan is ordinary—`mvn package && mvn deploy`. The trouble hides in familiar tooling. A legacy or auto‑generated build step uses over‑broad globs and resource expansion, so a child process quietly reads sensitive local files—like `~/.aws/credentials` or `.env`—and stashes those bytes in a non‑obvious location inside the artifact; for Java this might be `META‑INF/.aws/credentials` inside the JAR. The next step is a normal deploy to the company's internal registry.

From the outside, everything appears normal: the prompt contains no adversarial instruction; the processes (`mvn`, `jar`, `tar`, `rsync`) are expected; the egress is a trusted first‑party service. What's missing is the causal link. We need to show that a benign intent ("publish a release") immediately preceded sensitive reads and artifact writes that contradict policy. This is the kind of case where looking only at prompts or only at syscalls fails—what matters is the connection between them.



## Motivation — Performance: Who Burned CPU/Memory?

Now a performance and cost example. In agentic workflows, bursts of CPU or memory usage often seem to come from nowhere. Was it a long‑running tool, a heavy prompt/response, a retrying loop, or a large retrieval/storage step? Without attribution, it’s easy to optimize the wrong thing.  

Two observations make this urgent. First, we can join prompts and commands with resource metrics to see *exactly* which LLM response or subprocess drove a spike. Second, recent evidence shows the environment around the model can dominate end‑to‑end cost: serverless execution overhead for agents can be ≥ 40% of total cost, and in some settings up to 70% of the cost of the LLM API calls. In other words, a large share of spend and latency sits outside the model invocation. With clear attribution, we can fix bad loops or arguments, cache expensive steps, and target hot spots in retrieval and storage that need engineering attention.



## Motivation: Agentic Systems in Production

Stepping back, today's agents modify files, spawn processes, and run commands autonomously. That power brings non‑determinism: the same high‑level goal can unfold as different low‑level sequences across runs. For production teams, this complicates both reliability (was the outcome correct and reproducible?) and security (did anything happen that wasn't intended?).

Traditional monitoring splits the world in two. Application‑side telemetry shows the plan—prompts, tool calls, and high‑level events—but not the OS‑level consequences. System‑side telemetry shows the effects—processes, files, sockets—but not the motivation behind them. When those views aren't reconciled, it's hard to judge whether a run was safe and efficient or why it wasn't. That gap motivates the rest of the talk.



## The Semantic Gap (Why vs. What)

We call this the semantic gap between why and what. Intent arrives as natural‑language goals and LLM responses. Actions materialize as syscalls, process trees, file and network I/O. For example, a *refactor* task might pick up a hidden prompt from a web page, triggering `/etc/passwd` exfiltration. App‑level logs frame it as a successful tool action; OS‑level logs show a curl and some file reads. Neither alone tells you that the actions contradict the goal.

The core observability question becomes: *Can we causally link a particular LLM output to the concrete system behavior that followed?* Doing so requires more than pattern‑matching—it requires grounded attribution at the system boundary and a semantic interpretation that says whether the behavior is consistent with the intent.



## Limits of Existing Approaches

Why don't existing approaches solve this by default? Intent‑side solutions rely on inserting an SDK/instrumentation into the agent application. That's feasible for code you own, but impossible for closed‑source agents such as Claude Code. As soon as you rely on third‑party binaries, you lose the ability to instrument their internals.

On the other side, action‑side tools like Falco or Tracee produce comprehensive OS events—exactly what ran—but without any semantic link to intent, it's hard to tell routine automation from misuse. And while interpretability gives insight into model internals, it typically doesn't account for external OS effects. The missing piece is a technique that unifies intent and effects without assuming control over agent source code.



## Key Idea: Boundary Tracing

Our key idea is boundary tracing. Instead of instrumenting inside agent frameworks, we observe at stable system interfaces that all agents must traverse. At the network boundary, we attach uprobes to TLS functions such as `SSL_read` and `SSL_write` to recover plaintext LLM traffic—prompts and responses after decryption, before they leave or arrive. At the kernel boundary, we attach kprobes/tracepoints to capture process lineage and key syscalls that reflect real work—`execve`, `openat2`, `connect`, and so on.

Because we watch boundaries, the approach is framework‑agnostic and requires no code changes to the agent or its tools. Shell escapes and subprocesses are still visible. Boundary tracing lays the substrate for correlating why to what.



## Challenges (3.1)

Two challenges from the paper drive the design.

First, bridging the semantic gap between intent and action. An agent's intent is expressed in natural language and interpreted at runtime by an LLM—there is no fixed source code for static analysis. For example, the intent "find and fix the bug" is semantically rich but operationally ambiguous, potentially resulting in complex sequences of file reads, compilations, and test runs. This creates two sub-problems: we cannot predict which syscalls will occur a priori, making traditional static analysis impossible; and we must interpret a correlated trace to decide whether the syscall cascade legitimately fulfills the stated goal—a semantic judgment requiring an observer LLM.

Second, isolating the causal signal from system noise. Agents autonomously spawn arbitrary tools—shells, compilers, downloaders, test runners—leading to unpredictable, high-volume event streams. Static filters like "only watch `git`" are brittle and fail when agents use `curl` and `bash` to achieve similar outcomes. Our solution has two parts: dynamic in-kernel filtering that tracks fork/exec to build a complete lineage tree and applies rules in the kernel to pass only agent-descendant events to userspace; and efficient capture that keeps the entire causal chain while discarding background noise, dramatically reducing overhead.



## Architecture Overview

The architecture has two data streams. First, the intent stream: we use eBPF uprobes on SSL_read and SSL_write to capture plaintext prompts and responses at the network boundary. Second, the action stream: we use eBPF kprobes and tracepoints to capture process creation, file operations, and network I/O at the kernel boundary.

A userspace daemon performs real-time correlation of both streams. It also runs an observer LLM that interprets the correlated trace to explain what happened and whether it's consistent with the stated goal.



## From Signals → Causality → Semantics

Here is the pipeline in one slide. Capture intent at TLS and effects at the kernel boundary, aggressively filtering in‑kernel so only relevant events leave the kernel. Correlate using three signals: process lineage to attribute child actions to the initiating agent; a short Δt window (on the order of 100–500 ms) to link events that follow an LLM response; and argument matching to connect concrete strings—filenames, URLs, command arguments—between the LLM output and the later syscalls.  

Then explain. An observer LLM reads the structured trace and flags risks (e.g., data exfiltration inconsistent with the goal), inconsistencies (e.g., a publish step bundling credentials), and waste (e.g., a retry loop with no learning), returning a confidence score. We run this analysis asynchronously to avoid blocking the agent.



## Implementation

Implementation‑wise, AgentSight is a userspace daemon (~6 K LOC in Rust/C) that orchestrates the eBPF programs, along with a TypeScript UI (~3 K LOC) for exploration. The daemon maps file descriptors to paths, maintains process trees, and streams kernel and intent signals into unified, human‑readable traces. Because we instrument boundaries, not frameworks, the system is framework‑agnostic and remains resilient to API churn in agent libraries and tools.



## Evaluation (One Slide)

Let me summarize evaluation in one slide. We tested on Ubuntu 22.04 (Linux 6.14) with Claude Code 1.0.62 across repository understanding, code writing, and compilation. The average runtime overhead is ~2.9%, with a worst case of ~4.9%. That small footprint reflects in‑kernel filtering and lightweight correlation: we only export events we truly need.  

In terms of findings, the system detected prompt injection (as in our earlier story), identified resource‑wasting loops that retried the same failing tool call, and surfaced stealthy exfiltration via trusted channels. In multi‑agent runs, the unified trace revealed file‑lock contention and sequential dependencies, and simply clarifying roles reduced both wall‑clock time and token usage. In short: the approach provides actionable signal without demanding application changes.



## Open Source & Quick Start

AgentSight is open source. It observes at the system boundary using eBPF, which makes it tamper‑resistant and keeps overhead low. Just as important, it requires zero instrumentation—no SDKs and no code changes—so it works with any AI framework or closed‑source agent.

Quick start. Download the release binary, run `agentsight record` against the process you care about—`claude` for Claude Code, `node` for Gemini‑CLI, or `python` for Python tools—and open http://127.0.0.1:7395 to explore the data. For cases where Node bundles OpenSSL statically, the `--binary-path` option lets you point at `/usr/bin/node` so the TLS uprobes attach correctly. This lowers the barrier to entry so you can reproduce our results and analyze your own agents quickly.



## Frontend Demos

The UI offers three complementary views that make analysis fast. The Process Tree shows agent‑initiated processes and file operations as they happen, so you can visually follow forks, execs, and the effects of specific steps. The Timeline aligns prompts and responses with the system calls that follow, making causality easier to spot at a glance. The Metrics view attributes CPU and memory usage to concrete prompts and tools, so performance work starts with facts, not guesswork.

Together these views answer three practical questions: *What did the agent do? Why did it do that?* and *How much did it cost in resources?* That combination is what turns raw telemetry into operational decisions—for example, "this publish step should not read credential files," or "cache this retrieval to cut 40% off the critical path."



## Limitations, Future Work, Takeaways

To close, a few limitations and the takeaway. Our correlation uses heuristic windows and argument matching; in edge cases this can miss links or over‑link events. The observer model adds some cost and latency, though we run it asynchronously. Finally, cross‑host correlation is active future work; many agent deployments span multiple machines or containers.

Those are also directions: move from observability to inline guardrails and enforcement, broaden platform support, and extend lineage across hosts. The takeaway is simple: observing at stable system boundaries, then correlating intent to effects and explaining with an observer LLM, gives you low‑overhead, tamper‑resistant insight into both security and performance of agentic systems—without touching their code. That's the gap AgentSight is designed to close.


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
- The need of optimize heavy steps: fix loops/args, long run tools, tune retrieval/storage
- Requires join prompts/commands with CPU & memory to attribute spikes


---

# Slide 4 — Motivation: Agentic Systems in Production

* Agents modify files, spawn processes, execute code
* Non-deterministic behavior complicates reliability & security
---

# Slide 5 — The Semantic Gap (Why vs. What)

* Intent: prompts/responses; Actions: syscalls/processes
* Example: refactor → hidden prompt → `/etc/passwd` exfiltration
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
* Correlate: lineage + short Δt (≈ 100–500 ms) + argument matching, observer LLM correlate the intend and actions, dynamically adjust filtering rules

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
