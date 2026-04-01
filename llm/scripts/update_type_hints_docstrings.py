from llm.src.agent import CopilotAutoRefactor
from llm.conf import GITHUB_TOKEN, REPO_NAME
from pathlib import Path

def main():
    # file_regex = "rectilinear.py"  # all Python files
    # source_dir = "src/petres/grids/"
    source_dir = "src/petres/"
    file_regex = "**/*.py"  # all Python files in the repo
    prompt_path = ".github/prompts/Enhanced Type Hints and NumPy Docstrings.prompt.md"
    agent = CopilotAutoRefactor(
        github_token=GITHUB_TOKEN,
        repo_name=REPO_NAME,
        instruction_path=prompt_path,
        target_branch_name = "dev",
        working_branch_name = "copilot/type-hints-docstrings",
        auto_review = True,
        auto_merge = True,
    )
    agent.run(
        file_regex=file_regex,
        source_dir=source_dir,
    )

if __name__ == "__main__":
    main()