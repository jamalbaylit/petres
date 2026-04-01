from llm.src.agent import CopilotAutoRefactor
from llm.conf import GITHUB_TOKEN, REPO_NAME
from pathlib import Path

def main():
    file_regex = "rectilinear.py"  # all Python files
    source_dir = "src/petres/grids/"
    # source_dir = "src/petres"
    prompt_path = ".github/prompts/Enhanced Type Hints and NumPy Docstrings.prompt.md"
    agent = CopilotAutoRefactor(
        github_token=GITHUB_TOKEN,
        repo_name=REPO_NAME,
        instruction_path=prompt_path,
        auto_merge = False,
    )
    agent.run(
        file_regex=file_regex,
        source_dir=source_dir,
        max_rounds=1
    )

if __name__ == "__main__":
    main()