from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from datetime import datetime, timezone
from pathlib import Path
import time
import glob

from github.PullRequest import PullRequest
from github.Repository import Repository
from github import Github


class CopilotAutoRefactor:
    open_issues = None
    agent_name = "copilot-swe-agent[bot]"
    target_branch_name = "dev"
    
    def __init__(
        self,
        github_token: str,
        repo_name: str,
        instruction_path: str,
        auto_merge: bool = False,
        max_wait_seconds: int = 600,
        poll_interval: int = 7,
    ):
        self.github = Github(github_token)
        self.repo: Repository = self.github.get_repo(repo_name)
        self.instruction_path = Path(instruction_path)
        self.instruction_name = self.instruction_path.stem
        self.auto_merge = auto_merge
        self.max_wait_seconds = max_wait_seconds
        self.poll_interval = poll_interval

    @staticmethod
    def _create_branch(self, new_branch_name: str, base_branch_name: str):
        base_branch = self.repo.get_branch(base_branch_name)
        self.repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_branch.commit.sha)
        print(f"Created new branch: {new_branch_name}")

    # ---------------------------
    # PUBLIC ENTRYPOINT
    # ---------------------------
    def run(
        self, 
        file_regex: str, 
        source_dir: str, 
        max_rounds: int = 1
    ):
        target_files = self._find_target_files(file_regex, source_dir)
        self.workflow(target_files, max_rounds)

    def _find_target_files(self, file_regex: str, source_dir: str) -> List[str]:
        """
        Search for files matching the regex in the source directory.
        Returns a list of file paths.
        """
        if not Path(source_dir).is_dir():
            raise ValueError("`source_dir` must be a directory.")

        return glob.glob(f"{source_dir}/**/{file_regex}", recursive=True)

    def workflow(self, target_files: List[str], max_rounds: int = 1):
        for i in range(max_rounds):
            print(f"\n🚀 ROUND {i+1}")

            issue_numbers = self.create_issues_concurrently(target_files)

            pr = self._wait_for_pr(issue_numbers)

            if not pr:
                print("❌ No PR created.")
                return

            if not self._validate_pr(pr):
                print("❌ Validation failed.")
                return

            if self.auto_merge:
                self._merge_pr(pr)

    # ---------------------------
    # ISSUE CREATION
    # ---------------------------
    def _get_open_issues(self):
        if self.open_issues is None:
            self.open_issues = list(self.repo.get_issues(state="open"))
        return self.open_issues

    def create_issues_concurrently(self, files_to_fix: List[str], purpose="Refactor") -> List[int]:
        """
        Create multiple issues concurrently for a list of files.
        Skips files that already have an open issue.
        Returns a list of newly created issue numbers.
        """
        issue_numbers = []

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._create_issue, f, purpose) for f in files_to_fix]
            for future in as_completed(futures):
                result = future.result()
                if result is not None:  # Skip if _create_issue returned None
                    issue_numbers.append(result)

        return issue_numbers
    
    def get_assignees(self, issue_number: int) -> List[str]:
        if isinstance(issue_number, int):
            issue = self.repo.get_issue(number=issue_number)
        elif hasattr(issue_number, "assignees"):  # already an issue object
            issue = issue_number
        return [assignee.login for assignee in issue.assignees]  # list of usernames

    def _is_open_issue_exist(self, target_file, purpose) -> Optional[int]:
        """
        Check if an open issue already exists for the target file and purpose.
        Returns the issue number if found, otherwise None.
        """
        issues = self._get_open_issues()
        for issue in issues:
            if target_file in issue.title and purpose in issue.title:
                return issue
        return None
    

    def _create_issue(self, target_file, purpose="Refactor"):
        """
        Creates a single GitHub issue and returns its number.
        """
        issue = self._is_open_issue_exist(target_file, purpose)

        if issue is not None:
            # check assignees
            assignees = self.get_assignees(issue)
            if 'Copilot' in assignees:
                print(f"⚠️ Issue already exists for {target_file} with issue number: {issue.number}")
                return issue.number
            else:
                issue.edit(state="closed")
                print(f"🚨 Closed existing issue #{issue.number} for {target_file} since it's not assigned to the agent.")

        title = self._generate_issue_title(target_file, purpose)
        body = self._generate_issue_body(target_file)
        issue = self.repo.create_issue(
            title=title, 
            body=body, 
            assignees=["copilot-swe-agent[bot]"],
        )
        return issue.number
    
    def _generate_issue_title(self, target_file, purpose="Refactor"):
        """
        Generate a descriptive issue title.
        """
        # readable time 
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        return f"[AUTO] {purpose} {target_file} ({timestamp})"
    
    def _generate_issue_body(self, target_file):
        body = f"""
## 🎯 Task
Apply instructions from `{self.instruction_path}` to `{target_file}`.

## 📁 Target
{target_file}

## 📘 Instructions
{self.instruction_path.read_text()}

"""
        if self.target_branch_name is not None:
            body += f"- **IMPORTANT**: Open the pull request targeting the `{self.target_branch_name}` branch, NOT `main` or `master`.\n"
        return body
   
    

    # ---------------------------
    # WAIT FOR PR
    # ---------------------------
    def _wait_for_pr(self, issue_numbers: List[int]) -> Optional[PullRequest]:
        print("⏳ Waiting for Copilot PR...")
        start = time.time()

        issue_refs = set([f"#{n}" for n in issue_numbers])


        while time.time() - start < self.max_wait_seconds:
            pulls = self.repo.get_pulls(state="open")

            for pr in pulls:
                body = pr.body or ""
                print(pr)
                print("body:", body)

                # ✅ Primary: explicit reference
                if any(ref in body for ref in issue_refs):
                    print(f"✅ PR found (by issue ref): {pr.html_url}")
                    return pr   
            time.sleep(self.poll_interval)         

    # ---------------------------
    # VALIDATION HOOK
    # ---------------------------
    def _validate_pr(self, pr: PullRequest) -> bool:
        print("🧪 Validating PR...")

        # 🔧 Customize this:
        # - run tests
        # - run mypy
        # - run flake8
        # - check diff size, etc.

        commits = pr.get_commits()
        for c in commits:
            print(f"• {c.commit.message}")

        return True  # <-- plug real validation here

    # ---------------------------
    # MERGE
    # ---------------------------
    def _merge_pr(self, pr: PullRequest):
        print("🔀 Merging PR...")
        pr.merge()
        print(f"✅ Merged: {pr.html_url}")