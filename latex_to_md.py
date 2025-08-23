#!/usr/bin/env python3
import re
import sys

def latex_to_markdown(latex_file):
    with open(latex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove LaTeX preamble and document structure
    content = re.sub(r'\\documentclass.*?\n', '', content)
    content = re.sub(r'\\usepackage.*?\n', '', content)
    content = re.sub(r'\\begin\{document\}', '', content)
    content = re.sub(r'\\end\{document\}', '', content)
    content = re.sub(r'\\maketitle', '', content)
    
    # Convert title, author, abstract
    title_match = re.search(r'\\title\{([^}]+)\}', content)
    if title_match:
        title = title_match.group(1)
        content = re.sub(r'\\title\{[^}]+\}', f'# {title}\n', content)
    
    # Convert abstract
    abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
    if abstract_match:
        abstract = abstract_match.group(1).strip()
        # Escape backslashes in the replacement string
        abstract_escaped = abstract.replace('\\', '\\\\')
        content = re.sub(r'\\begin\{abstract\}.*?\\end\{abstract\}', f'## Abstract\n\n{abstract_escaped}\n', content, flags=re.DOTALL)
    
    # Convert sections
    content = re.sub(r'\\section\*?\{([^}]+)\}', r'## \1', content)
    content = re.sub(r'\\subsection\*?\{([^}]+)\}', r'### \1', content)
    content = re.sub(r'\\subsubsection\*?\{([^}]+)\}', r'#### \1', content)
    
    # Convert emphasis
    content = re.sub(r'\\textit\{([^}]+)\}', r'*\1*', content)
    content = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', content)
    content = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', content)
    content = re.sub(r'\\texttt\{([^}]+)\}', r'`\1`', content)
    
    # Convert lists
    content = re.sub(r'\\begin\{itemize\}', '', content)
    content = re.sub(r'\\end\{itemize\}', '', content)
    content = re.sub(r'\\begin\{enumerate\}', '', content)
    content = re.sub(r'\\end\{enumerate\}', '', content)
    content = re.sub(r'\\item\s+', '- ', content)
    
    # Convert citations
    content = re.sub(r'\\cite\{([^}]+)\}', r'[\1]', content)
    content = re.sub(r'\\citep\{([^}]+)\}', r'[\1]', content)
    
    # Convert figures and tables
    content = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '[Figure]', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{table\}.*?\\end\{table\}', '[Table]', content, flags=re.DOTALL)
    
    # Remove input commands
    content = re.sub(r'\\input\{[^}]+\}', '', content)
    
    # Remove other LaTeX commands
    content = re.sub(r'\\[a-zA-Z]+\*?\{([^}]*)\}', r'\1', content)
    content = re.sub(r'\\[a-zA-Z]+\*?\s*', '', content)
    content = re.sub(r'%.*\n', '', content)
    content = re.sub(r'\$([^$]+)\$', r'\1', content)  # Remove inline math delimiters
    
    # Clean up extra whitespace
    content = re.sub(r'\n\n+', '\n\n', content)
    content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)
    
    return content.strip()

def main():
    # Process main file
    main_content = latex_to_markdown('main.tex')
    
    # Process included files
    included_files = ['intro.tex', 'bg2.tex', 'design-impl.tex', 'eval-conclusion.tex']
    full_content = main_content + '\n\n'
    
    for file in included_files:
        try:
            file_content = latex_to_markdown(file)
            if file_content:
                full_content += f"---\n\n{file_content}\n\n"
        except Exception as e:
            print(f"Warning: Could not process {file}: {e}", file=sys.stderr)
    
    # Write to output file
    with open('agentsight_paper.md', 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    print("Conversion complete! Output saved to agentsight_paper.md")

if __name__ == "__main__":
    main()