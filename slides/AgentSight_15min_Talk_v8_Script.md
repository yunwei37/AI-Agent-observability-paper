# AgentSight 15‑Minute Talk — Full Speaker Script (v8)

Authors: Yusheng Zheng (UC Santa Cruz), Yanpeng Hu (ShanghaiTech University), Tong Yu (eunomia-bpf Community), Andi Quinn (UC Santa Cruz)

## Slide 1 — AgentSight: System‑Level Observability for AI Agents Using eBPF

Good morning. Today I'm presenting AgentSight, a system-level observability framework for AI agents.

The core problem is a semantic gap between what agents intend to do and what operating systems actually execute. Agents have intents like prompts and tool calls, while operating systems execute concrete actions like processes, syscalls, file operations, and network traffic. Traditional tools show you one side or the other, but they rarely connect the why to the what.

AgentSight observes agents at two critical boundaries. At the network boundary, we capture prompts and responses as they pass through TLS. At the kernel boundary, we track processes, files, and sockets. By correlating these two streams, we can link concrete effects back to specific intents and then use an observer LLM to explain risks and inefficiencies.

I'll start with two quick examples on security and performance, then define the problem and show why current approaches fall short. After that I'll present our key idea and challenges, walk through the architecture, implementation, and evaluation, and wrap up with a live demo and takeaways.



## Slide 2 — Motivation — Security: Trusted Artifact Exfiltration

Let's start with a detailed security example. Imagine you ask the agent to "package and publish the release." The LLM replies with a benign plan: mvn package then mvn deploy. Everything looks normal in the conversation.

But here's what happens under the hood. Downstream, there's a legacy or auto-generated build recipe that was written earlier by a human or maybe another LLM. This recipe uses over-broad globs and resource expansion. So the child processes quietly read sensitive files like tilde slash dot aws slash credentials and dot env. Then they tuck those bytes into non-obvious places inside the JAR. For example, META-INF slash dot aws slash credentials, ZIP extra fields, or tar PAX headers. After that, the agent runs the standard deploy to your own internal registry.

Now here's why this is invisible to existing defenses. Prompt-side defenses see nothing. The conversation and plan contain no adversarial text whatsoever. Traditional rule-based and signature-based tools also see nothing unusual. Why? Because egress is to a whitelisted first-party endpoint over TLS. The processes are all familiar: mvn, jar, tar, rsync. And the syscalls look exactly like routine packaging: normal open and write on dotfiles, writes to the artifact, upload to the registry. There are no odd domains, no suspicious helper processes, no malware binaries.

In typical setups that don't do deep content-aware scanning of every internal artifact, and most don't because unpacking nested ZIPs and JARs and inspecting manifest and service files is expensive, this leak is effectively invisible. Prompt scanning misses it because there's no malicious text. Traditional host and network monitors miss it because all the operations look routine.


## Slide 3 — Motivation — Performance: Who Burned CPU/Memory?

Now let's talk about performance. Agent infrastructure can dominate costs. Serverless environment costs can be 40% or more of total cost, CPU and memory can take up to 70% of LLM API cost. That means a lot of of your spend is actually outside the model itself.

We need to optimize heavy steps: fix loops and arguments, tune long-running tools, and optimize retrieval and storage. This requires joining prompts and commands with CPU and memory metrics to attribute spikes to specific actions.

## Slide 4 — The Semantic Gap (Why vs. What)

Let me frame the broader context. Agentic systems in production are powerful. Agents modify files, spawn processes, and execute code. But this brings non-deterministic behavior that complicates both reliability and security.

What they have is two disconnected views. Intent side shows prompts and responses. Actions side shows syscalls and processes. What we need is causal linkage from LLM output to system behavior. That's the semantic gap we're addressing.



## Slide 5 — Limits of Existing Approaches

Why don't existing tools solve this? Let's look at three approaches.

First, intent-side solutions with SDKs need SDK inside the agent app. That's infeasible for closed-source agents like Claude Code.

Second, action-side tools like Falco or Tracee produce many events but have no link to intent or semantics.

Third, interpretability research focuses on model internals, not external OS effects.

What's missing is a technique that unifies intent and effects without requiring access to agent source code.



## Slide 6 — Key Idea: Boundary Tracing

Our key idea is boundary tracing. To get data, we observe intent at the network boundary using TLS function uprobes, and observe effects at the kernel using process lineage and syscalls. This approach is framework-agnostic and requires zero code changes.

But we face two key challenges. First, bridging the semantic gap between intent and action. Second, isolating the causal signal from system noise.

Our solution is to correlate and filter with an LLM. The observer LLM helps us connect intent to effects and dynamically filter what matters.



## Slide 7 — Architecture Overview

The architecture has two data streams.

The intent stream uses eBPF uprobes on SSL_read and SSL_write to capture prompts and responses.

The action stream uses eBPF kprobes and tracepoints to capture process and I/O events.

A userspace daemon performs correlation with an observer LLM that interprets the trace and checks consistency with goals.



## Slide 8 — From Signals → Causality → Semantics

Here's the full pipeline.

First, we capture. We capture intent via TLS and effects via exec, fork, openat2, connect, and execve, with in-kernel filters to reduce noise.

Second, we correlate. We use a time window plus argument matching to link events. The observer LLM correlates intent and actions, and dynamically adjusts filtering rules based on what it learns.



## Slide 9 — Implementation

AgentSight consists of a userspace daemon, about 6K lines of code in Rust and C, plus a TypeScript UI with about 3K lines.

The daemon handles file path mapping, process trees, network trace, metrics, and LLM prompts. Everything is streamed into unified traces.

Since we instrument boundaries instead of frameworks, the system is instrumentation-free and framework-agnostic.



## Slide 10 — Evaluation

Let me summarize the evaluation.

Setup: Ubuntu 22.04 with Linux 6.14, Claude Code version 1.0.62. Average overhead is about 2.9 percent with a max around 4.9 percent across repo understanding, code writing, and compilation tasks.

For use cases, we can detect prompt injection, detect tool use loops with wrong arguments, and detect multi-agent collaboration issues. The approach delivers actionable insights without requiring any application changes.



## Slide 11 — Open Source & Quick Start

AgentSight is fully open source at github.com/eunomia-bpf/agentsight.

For a quick start, the slide shows the commands to download and run agentsight. You can monitor claude, node, python, or any other agent process. Then visit the web UI at 127.0.0.1 port 7395 to explore the data.

## Slide 12 — Frontend Demos: Process Tree

The UI has three complementary views. Let me show you the first one.

The Process Tree shows real-time agent interactions and operations. You can visually follow process creation, file operations, and see exactly what the agent is doing at the system level.

## Slide 13 — Frontend Demos: Timeline

The Timeline view aligns prompts and responses with system calls. This makes causality easy to spot at a glance. You can see exactly which LLM response triggered which system actions.

## Slide 14 — Frontend Demos: Metrics

The Metrics view shows CPU and memory attribution. You can see exactly which prompts and tools consumed resources, making it easy to identify optimization opportunities.

## Slide 15 — Limitations, Future Work, Takeaways

Let me wrap up.

For limitations, our correlation relies on heuristic windows and argument matching. The observer model adds some cost and latency. And cross-host correlation is still active work.

For future directions, we're moving toward inline guardrails and enforcement, and broadening platform support.

The takeaway is this: boundary tracing plus hybrid correlation bridges intent and actions with low overhead. That's how we close the semantic gap.

Thank you.
