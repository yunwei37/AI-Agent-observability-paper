# Makefile for LaTeX compilation

# Main document name (without .tex extension)
MAIN = main
SHORT = short/saa
SAA = saa

# LaTeX compiler
LATEX = xelatex
PDFLATEX = pdflatex
BIBTEX = bibtex
LATEXFLAGS = -interaction=nonstopmode

# Default target
all: $(MAIN).pdf

# Main compilation rule
$(MAIN).pdf: $(MAIN).tex $(MAIN).bbl
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex

# Bibliography compilation
$(MAIN).bbl: $(MAIN).aux ai.bib
	$(BIBTEX) $(MAIN)

# Initial compilation to generate .aux file
$(MAIN).aux: $(MAIN).tex
	$(LATEX) $(LATEXFLAGS) $(MAIN).tex

# Clean auxiliary files
clean:
	rm -f *.aux *.log *.out *.bbl *.blg *.toc *.lof *.lot *.cut *.gz

# Clean everything including PDF
cleanall: clean
	rm -f $(MAIN).pdf

# Force recompilation
force: clean all

# Short paper compilation
short: $(SHORT).pdf

$(SHORT).pdf: $(SHORT).tex $(SHORT).bbl
	cd short && $(LATEX) $(LATEXFLAGS) saa.tex
	cd short && $(LATEX) $(LATEXFLAGS) saa.tex

$(SHORT).bbl: $(SHORT).aux ai.bib
	cd short && $(BIBTEX) saa

$(SHORT).aux: $(SHORT).tex
	cd short && $(LATEX) $(LATEXFLAGS) saa.tex

# SAA paper compilation (root level, uses pdflatex)
saa: $(SAA).pdf

$(SAA).pdf: $(SAA).tex $(SAA).bbl
	$(PDFLATEX) $(LATEXFLAGS) $(SAA).tex
	$(PDFLATEX) $(LATEXFLAGS) $(SAA).tex

$(SAA).bbl: $(SAA).aux ai.bib
	$(BIBTEX) $(SAA)

$(SAA).aux: $(SAA).tex
	$(PDFLATEX) $(LATEXFLAGS) $(SAA).tex

.PHONY: all clean cleanall force short saa