from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from datetime import datetime, timezone
from pathlib import Path
import time
import glob

from github.GithubException import GithubException
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository
from github import Github

from .toolkit import GithubToolkit

class CopilotAutoRefactor:
    open_issues = None
    agent_name = "copilot-swe-agent[bot]"

    
    def __init__(
        self,
        github_token: str,
        repo_name: str,
        instruction_path: str,
        target_branch_name: str = "dev",
        working_branch_name: str = "copilot/auto-refactor",
        auto_merge: bool = False,
        auto_review: bool = False, 
        max_wait_seconds: int = 600,
        poll_interval: int = 7,
    ):
        self.github = GithubToolkit(github_token, repo_name)




        # self.github = Github(github_token)
        # self.repo: Repository = self.github.get_repo(repo_name)
        self.instruction_path = Path(instruction_path)
        self.instruction_name = self.instruction_path.stem
        self.auto_merge = auto_merge
        self.auto_review = auto_review
        self.max_wait_seconds = max_wait_seconds
        self.poll_interval = poll_interval
        self.target_branch_name = target_branch_name
        self.working_branch_name = working_branch_name

        try:
            self.github.get_branch(self.working_branch_name)
            print(f"⚠️ Branch '{self.working_branch_name}' already exists.")
        except GithubException:
            self.github.create_branch(
                self.working_branch_name, 
                self.target_branch_name
            )



    # ---------------------------
    # PUBLIC ENTRYPOINT
    # ---------------------------
    def run(
        self, 
        file_regex: str, 
        source_dir: str, 
    ):
        target_files = self._find_target_files(file_regex, source_dir)
        if not target_files:
            print("No target files found. Exiting.")
            return
        self.workflow(target_files)


    def workflow(self, target_files: List[str]):
        print(f"🚀 Starting workflow for {len(target_files)} target files...")
        # issues = self.create_issues_concurrently(target_files)
        # print('=' * 50)
        # print(f"✅ Created {len(issues)} issues. Issue numbers: {issues}")
        # prs = self._wait_for_pr(issues)
        # if prs is None:
        #     print("❌ Workflow failed due to missing PRs.")
        #     return

        for file in target_files:


            completed = 0
                    
            # if self.auto_review or self.auto_merge:



            start = time.time()    
            completed = 0
            while time.time() - start < self.max_wait_seconds:
                issues = [self._create_issue(file, purpose=self.instruction_name)]
                prs = self.github.filter_prs(
                    owner='Copilot',
                    from_branch_pattern="copilot/*",
                    to_branch=self.working_branch_name,
                    state="open",
                )
                print(f"⏳ Waiting for all Copilot PRs... Found {completed}/{len(issues)} PRs so far.")
                completed += len(prs)
                for pr in prs:
                    if self.auto_review:
                        pr = self.github.convert_draft_to_ready(pr)
                        print(f"✅ Reviewed PR #{pr.number} with APPROVE.")
                    if self.auto_merge:
                        pr.merge(
                            commit_title=f"Auto-merged by {self.agent_name}.",
                            merge_method="squash",
                            delete_branch=True,
                        )
                        print(f"✅ Merged PR #{pr.number}.")

                if completed >= len(issues):
                    print(f"✅ All PRs have been processed (reviewed/merged).")
                    break
                time.sleep(self.poll_interval)


            print(
                f"❌ Timed out after {self.max_wait_seconds}s. "
                f"Expected {len(issues)} PRs but completed {completed}."
            )


            # delete issues after PR is merged
            print('=' * 50)
            for issue in issues:
                issue = self.github.get_issue(issue)
                issue.edit(state="closed")
                print(f"✅ Closed issue #{issue.number} after merging PR #{pr.number}.")
    # ---------------------------
    # ISSUE CREATION
    # ---------------------------


    def create_issues_concurrently(self, files_to_fix: List[str], purpose="Refactor") -> List[int]:
        """
        Create multiple issues concurrently for a list of files.
        Skips files that already have an open issue.
        Returns a list of newly created issue numbers.
        """
        issues = set()  # Use a set to avoid duplicates

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._create_issue, f, purpose) for f in files_to_fix]
            for future in as_completed(futures):
                result = future.result()
                if result is not None:  # Skip if _create_issue returned None
                    issues.add(result)
        return issues
    

    def _is_open_issue_exist(self, target_file, purpose) -> Issue | None:
        """
        Check if an open issue already exists for the target file and purpose.
        Returns the issue number if found, otherwise None.
        """
        issues = self.github.get_open_issues()
        for issue in issues:
            if target_file in issue.title and purpose in issue.title:
                return issue
        return None
    

    def _create_issue(self, target_file, purpose="Refactor") -> int:
        """
        Creates a single GitHub issue and returns it.
        """
        issue = self._is_open_issue_exist(target_file, purpose)

        if issue is not None:
            # Check assignees
            assignees = self.github.get_issue_assignees(issue)
            if 'Copilot' in assignees:
                print(f"⚠️ Issue already exists for {target_file} with issue number: {issue.number}")
                return issue.number
            else:
                issue.edit(state="closed")
                print(f"🚨 Closed existing issue #{issue.number} for {target_file} since it's not assigned to the agent.")

        # Need to create a new issue
        title = self._generate_issue_title(target_file, purpose)
        body = self._generate_issue_body(target_file)
        # issue = self.github.create_issue(
        #     title=title, 
        #     body=body, 
        #     assignees=["copilot-swe-agent[bot]"],
        # )

        issue = self.github.create_issue_with_copilot_agent(
            title=title,
            body=body,
            base_branch=self.working_branch_name,
        )
        print(f"✅ Created issue #{issue['number']} for {target_file}")
        issue_number = issue["number"] if isinstance(issue, dict) else issue.number
        return issue_number
    
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
        return body
   
    

    # ---------------------------
    # WAIT FOR PR
    # ---------------------------
    def _wait_for_pr(self, issue_numbers: List[int]) -> Optional[List[PullRequest]]:
        start = time.time()

        while time.time() - start < self.max_wait_seconds:

            prs = self.github.filter_prs(
                owner='Copilot',
                from_branch_pattern="copilot/*",
                to_branch=self.working_branch_name,
                state="open",
            )
            print(f"⏳ Waiting for all Copilot PRs... Found {len(prs)}/{len(issue_numbers)} PRs so far.")

            if len(prs) == len(issue_numbers):
                print(f"✅ Found all {len(prs)} PRs.")
                return prs

            time.sleep(self.poll_interval)

        print(
            f"❌ Timed out after {self.max_wait_seconds}s. "
            f"Expected {len(issue_numbers)} PRs but found {len(prs)}."
        )

        return None




    def _find_target_files(self, file_regex: str, source_dir: str) -> List[str]:
        """
        Search for files matching the regex in the source directory.
        Returns a list of file paths.
        """
        if not Path(source_dir).is_dir():
            raise ValueError("`source_dir` must be a directory.")

        return set(glob.glob(f"{source_dir}/**/{file_regex}", recursive=True))


    