# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LaTeX academic paper repository for "AgentSight: System-Level Observability for AI Agents Using eBPF". The paper is formatted using the ACM LaTeX template and is being prepared for submission to an ACM conference.

## Build Commands

The project uses a Makefile for LaTeX compilation with xelatex:

- `make` or `make all` - Compiles the main paper (main.tex → main.pdf)
- `make clean` - Removes auxiliary LaTeX files (*.aux, *.log, *.bbl, etc.)
- `make cleanall` - Removes all generated files including the PDF
- `make force` - Clean rebuild (equivalent to `make clean && make all`)

The compilation process follows the standard LaTeX workflow:
1. xelatex (generates .aux)
2. bibtex (processes bibliography)
3. xelatex (twice, to resolve references)

## Project Structure

- `main.tex` - Primary paper document (full version)
- `short/workshop.tex` - Condensed workshop version
- `ai.bib`, `ai2.bib` - Bibliography files
- `acmart.cls` - ACM LaTeX class file
- `ACM-Reference-Format.bst` - ACM bibliography style

## Key Technical Details

The paper uses:
- Unicode support for system diagrams (requires xelatex)
- Chinese font support (CJKutf8 package)
- ACM conference format with anonymous submission option
- Multiple bibliography files (ai.bib is the primary one)

## Research Context

AgentSight is a system-level observability framework for AI agents that:
- Uses eBPF for kernel-level monitoring without code instrumentation
- Intercepts TLS-encrypted LLM communications
- Correlates high-level agent intentions with low-level system operations
- Claims <3% performance overhead

The implementation is available at: https://github.com/eunomia-bpf/agentsight