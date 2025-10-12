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

Now let's talk about performance. When you run agent workflows in production, you'll often see sudden spikes in CPU or memory. But where did they come from? Without attribution, you're guessing. Was it a long-running tool? A huge prompt? A retry loop? A big retrieval step? You don't know.

Here's why this matters. Recent studies show that agent infrastructure can dominate costs. Serverless environment overhead can be 40 percent or more of total cost. In some deployments, CPU and memory can take up to 70 percent of what you pay for LLM API calls. That means the majority of your spend is actually outside the model itself. It's in the infrastructure around it.

To fix this, we need to optimize the heavy steps. Fix loops and wrong arguments when LLMs are using tools. Tune long-running tools. Optimize retrieval and storage operations. But you can only do this if you can attribute resource consumption. This requires joining prompts and commands with CPU and memory metrics to pinpoint exactly which LLM response or subprocess burned the resources. Only then can you identify the optimization opportunities.

## Slide 4 — The Semantic Gap (Why vs. What)

Let me frame the broader context and define this semantic gap more precisely. Agentic systems in production are powerful. Agents modify files, spawn processes, and execute code autonomously. But this brings non-deterministic behavior that fundamentally breaks traditional observability paradigms.

Here's a concrete example of the gap in action. Imagine an agent tasked with code refactoring. Due to a malicious prompt it reads from an external URL in search results when looking for API documentation, the agent gets an indirect prompt injection. Now, application-level monitoring sees a benign intent: "refactor code." It sees a successful tool execution. But it's completely blind to what happens at the system level. Meanwhile, system monitoring sees a bash process writing to a file and reading slash etc slash passwd. But without semantic context, these look like routine operations.

Neither side can bridge the gap to understand that a benign intention has been twisted into a malicious action. This is the core problem: we have two disconnected views. The intent side shows prompts and responses, the high-level why. The action side shows syscalls and processes, the low-level what. What we desperately need is causal linkage from LLM output to system behavior.

This gap creates a unique threat model for AI agents. We face risks like prompt injection attacks where malicious instructions get embedded in data. Goal drift, where the agent slowly deviates from its original purpose. And unintended capability escalation, where the agent discovers and uses system capabilities it wasn't supposed to have. That's the semantic gap we're addressing.



## Slide 5 — Limits of Existing Approaches

As we discussed before, existing tools cannot solve this problem and require heavy sdk instrumentation:

First, intent-side solutions with SDKs need SDK inside the agent app. That's infeasible for closed-source agents like Claude Code.

Second, action-side tools like Falco or Tracee produce many events but have no link to intent or semantics.

Third, interpretability research focuses on model internals, not external OS effects.

What's missing is a technique that unifies intent and effects without requiring access to agent source code.



## Slide 6 — Key Idea: Boundary Tracing

Our key idea is boundary tracing. The insight is simple but powerful: while agent internals and frameworks are volatile and constantly changing, the interfaces through which they interact with the world are stable and unavoidable. Every agent must cross two boundaries. The kernel boundary for system operations. And the network boundary for communication with LLM backends.

By monitoring at these boundaries rather than inside the application, we achieve comprehensive observation that's independent of implementation details. To get the data, we use eBPF. At the network boundary, we attach uprobes to TLS functions like SSL underscore read and SSL underscore write. This lets us capture plaintext LLM traffic after decryption but before it reaches the application. At the kernel boundary, we use kprobes and tracepoints to capture process lineage and key syscalls like execve, openat2, and connect.

This approach is framework-agnostic and requires zero code changes. Crucially, it shifts the trust model. We're no longer assuming a cooperative agent. We're enforcing observation at tamper-proof system boundaries.

But we face two significant challenges. The first challenge is bridging the semantic gap itself. An agent's intent is expressed in natural language and interpreted at runtime by an LLM. There's no fixed source code we can analyze statically. For example, "find and fix the bug" is semantically rich but operationally vague. It could trigger file reads, compilations, test runs, anything. We face two sub-problems. We can't predict which syscalls will occur ahead of time. And we need to interpret the correlated trace to decide if those syscalls legitimately fulfill the goal. That's a semantic judgment that requires an observer LLM.

The second challenge is isolating signal from noise. Agents spawn arbitrary tools: shells, compilers, test runners. This leads to high-volume, unpredictable event streams. Static filters break immediately. A rule to "only watch git" fails the moment an agent uses curl and bash instead. Our solution has two parts. First, dynamic in-kernel filtering. We track fork and exec to build a complete lineage tree, then apply rules in the kernel to pass only agent-descendant events to userspace. Second, we correlate and filter with an LLM. The observer LLM connects intent to effects and helps us understand what matters. This AI-to-watch-AI approach is what makes semantic analysis possible.



## Slide 7 — Architecture Overview

The architecture has two data streams.

The intent stream uses eBPF uprobes on SSL_read and SSL_write to capture prompts and responses.

The action stream uses eBPF kprobes and tracepoints to capture process and I/O events.

A userspace daemon performs correlation with an observer LLM that interprets the trace and checks consistency with goals.



## Slide 8 — From Signals → Causality → Semantics

Here's the full pipeline, from raw signals to causal understanding to semantic analysis.

First, we capture the two streams. We capture intent via TLS by intercepting SSL functions. We capture effects via the kernel by monitoring exec, fork, openat2, connect, and execve. Crucially, we apply aggressive in-kernel filters right at the source. By building the process lineage tree in eBPF, we only send events from the agent and its descendants to userspace. This dramatically reduces overhead while keeping the full causal chain intact.

Second, we correlate using three complementary signals. Signal one is process lineage. We track every fork and exec to build a complete tree. This lets us attribute child actions back to the agent that spawned them, even across multiple levels of subprocesses. Signal two is temporal proximity. We use a short time window, typically 100 to 500 milliseconds, to link actions that occur immediately after an LLM response. Signal three is argument matching. We directly match content from LLM responses—filenames, URLs, command strings—with the arguments of subsequent system calls. Together, these three signals give us high-confidence causal links.

Third, we perform semantic analysis. Once we have a correlated trace, we pass it to an observer LLM. We format the trace as a structured chronological log and prompt a powerful model like GPT-4 or Claude to act as a security analyst. The prompt asks: Do these actions align with the stated goal? Are there deviations, inefficiencies, or security risks? The LLM reads the trace, understands the semantic nuance, and returns a natural language explanation plus a confidence score. This AI-to-watch-AI approach lets us detect threats that don't match predefined patterns. The observer also dynamically adjusts filtering rules based on what it learns, creating a feedback loop that improves detection over time. We run this analysis asynchronously, so it doesn't block the agent.



## Slide 9 — Implementation

AgentSight is implemented as a userspace daemon, about 6,000 lines of code in Rust and C, plus a TypeScript UI with about 3,000 lines for visualization and analysis. The system is designed for high performance, processing raw event streams from the kernel into correlated, human-readable data.

The daemon orchestrates a suite of eBPF programs. For capturing semantic intent, we attach uprobes to SSL underscore read and SSL underscore write functions in crypto libraries like OpenSSL. A significant implementation challenge here is handling streaming protocols like Server-Sent Events, which fragment a single JSON response across numerous SSL read calls. We solve this with a stateful reassembly mechanism that buffers data chunks per connection and parses them for event boundaries.

For capturing system actions, we use stable tracepoints like sched underscore process underscore exec to build the process tree, and kprobes for detailed monitoring of syscalls like openat2, connect, and execve. The daemon maintains file descriptor to path mappings, network traces, metrics, and LLM prompts. Everything is streamed through eBPF ring buffers into unified traces that preserve causality.

Since we instrument boundaries instead of frameworks, the system is completely instrumentation-free and framework-agnostic. It works with any agent framework and stays resilient when agent libraries change their APIs.



## Slide 10 — Evaluation

Now let's look at the evaluation results. We want to answer two questions: what's the performance overhead, and how well does this actually work in practice?

We tested on Ubuntu 22.04 with Linux 6.14 and Claude Code version 1.0.62. We ran three real developer workflows: understanding a repository, writing code, and compiling projects. The overhead was minimal. Average is 2.9 percent, maximum is 4.9 percent. That small footprint comes from our in-kernel filtering approach.

Now let me show you three use cases that demonstrate effectiveness. First is prompt injection detection. An agent cloning a C project reads a README file with a hidden malicious prompt that tries to exfiltrate slash etc slash passwd. AgentSight captured the complete attack chain. It took 521 raw events and merged them into just 37 meaningful events. The observer LLM analyzed this trace and returned a high-confidence attack score. It noted that the actions were completely inconsistent with the stated goal of clone and build.

Second use case is reasoning loop detection. We had a research agent that repeatedly called a web search tool with the wrong arguments. It got an error, but then failed to correct its mistake. It just kept retrying the exact same failing command in a try-fail-re-reason loop. AgentSight flagged this anomalous resource consumption. The observer LLM identified the root cause and prevented further waste.

Third is multi-agent coordination. We monitored six collaborating software development agents and captured 3,153 events after correlation. The analysis revealed file-lock contention and sequential dependencies that were blocking the frontend and test agents. This showed that clarifying roles more explicitly could reduce both runtime and token cost. This demonstrates how boundary tracing captures multi-agent dynamics that application-level monitoring simply cannot see across process boundaries.

Bottom line: the approach delivers actionable insights for security, performance, and coordination, all with no application changes required.



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
