from github.PullRequest import PullRequest
from github.Repository import Repository
from github.Issue import Issue
from github import Github
from github.GithubObject import (
    NotSet,
)

from typing import List
import requests


class GithubToolkit:
    def __init__(self, token: str, repo_name: str):
        self.repo_name = repo_name
        self.token = token
        self.github = Github(token)
        self.repo: Repository = self.github.get_repo(repo_name)

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    
    def review_pr(self, pr: PullRequest, event: str = "APPROVE", body: str = "[AUTO] Review") -> PullRequest:
        pr.create_review(event=event, body=body)
        return pr
    

    def convert_draft_to_ready(self, pr: PullRequest) -> PullRequest:
        """
        Convert a draft PR to ready for review via GraphQL
        (PyGitHub does not support this via REST).
        """
        query = """
        mutation($pullRequestId: ID!) {
            markPullRequestReadyForReview(input: { pullRequestId: $pullRequestId }) {
                pullRequest {
                    isDraft
                    number
                }
            }
        }
        """
        _, data = self.repo._requester.requestJsonAndCheck(
            "POST",
            "https://api.github.com/graphql",
            input={"query": query, "variables": {"pullRequestId": pr.node_id}},
        )
        is_draft = (
            data.get("data", {})
            .get("markPullRequestReadyForReview", {})
            .get("pullRequest", {})
            .get("isDraft", True)
        )
        print(f"  PR #{pr.number} draft={is_draft}")
        return pr


    def get_issue_prs_open(self, issue: Issue, owner: str) -> List[PullRequest]:
        return [pr for pr in self.get_linked_pr_graphql(issue, owner)]
    
    
    # def get_issue_prs_closed(self, issue: Issue) -> List[PullRequest]:
    #     return [pr for pr in self.get_issue_prs(issue) if pr.state == "closed"]

    # def get_issue_prs(self, issue: Issue) -> List[PullRequest]:
    #     for event in issue.get_timeline():
    #         if event.event == "cross-referenced" and event.source:
    #             if hasattr(event.source.issue, "pull_request") and event.source.issue.pull_request:
    #                 pr = event.source.issue.as_pull_request()
    #                 yield pr    
    
    def get_linked_pr_graphql(self, issue:Issue, owner: str):
        repo = issue.repository.full_name.split('/')[1]
        issue_number = issue.number if isinstance(issue, Issue) else int(issue) 
        token = self.token
        """
        Query the issue's timelineItems for a ConnectedEvent linking a PR.
        """
        import requests
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
            issue(number: $number) {
            timelineItems(first: 20, itemTypes: [CONNECTED_EVENT, CROSS_REFERENCED_EVENT]) {
                nodes {
                ... on CrossReferencedEvent {
                    source {
                    ... on PullRequest {
                        url
                        number
                        state
                    }
                    }
                }
                ... on ConnectedEvent {
                    subject {
                    ... on PullRequest {
                        url
                        number
                        state
                    }
                    }
                }
                }
            }
            }
        }
        }
        """
        resp = requests.post(
            "https://api.github.com/graphql",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": query, "variables": {"owner": owner, "repo": repo, "number": issue_number}},
        )
        resp.raise_for_status()
        nodes = (
            ((resp.json().get("data") or {})
            .get("repository") or {})
            .get("issue") or {}
        ).get("timelineItems", {}).get("nodes", [])
        for node in nodes:
            pr = node.get("source") or node.get("subject")
            if pr and pr.get("url"):
                yield pr


    def filter_prs(
        self,
        owner: str = NotSet,
        from_branch_pattern: str = NotSet,
        to_branch: str = NotSet,
        state: str = "all",
    ) -> List[PullRequest]:
        """
        Return all PRs where:
        - author login matches `owner`
        - head branch matches `from_branch_pattern`
        - base branch matches `to_branch`

        Patterns support wildcards via fnmatch (e.g. "copilot/*").
        """
        from fnmatch import fnmatch
        prs = self.repo.get_pulls(
            state=state,
            base=to_branch,
        )
        # for pr in prs:
            # print(f"PR #{pr.number}: head={pr.head.ref}, base={pr.base.ref}, author={pr.user.login}")
        prs = [
            pr
            for pr in prs
            if pr.user.login == owner
            and fnmatch(pr.head.ref, from_branch_pattern)
            # and fnmatch(pr.base.ref, to_branch)
        ]
        return prs



    def create_branch(self, new_branch_name: str, base_branch_name: str):
        base_branch = self.repo.get_branch(base_branch_name)
        self.repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_branch.commit.sha)
    
    def get_pr(self, pr_number: int) -> PullRequest:
        return self.repo.get_pull(pr_number)
    
    def get_branch(self, branch_name: str):
        return self.repo.get_branch(branch_name)
    
    def get_issues(self, *, state=NotSet, assignee=NotSet):
        return self.repo.get_issues(state=state, assignee=assignee)

    def get_issue(self, issue_number: int) -> Issue:
        return self.repo.get_issue(number=issue_number)

    def create_issue_with_copilot_agent(
        self,
        title: str,
        body: str,
        *,
        base_branch: str = "dev",
        assignees: list[str] | None = None,
        custom_instructions: str = "",
    ) -> dict:
        """
        Create an issue assigned to copilot-swe-agent with agent_assignment.
        This will trigger Copilot to create a PR targeting `base_branch`.
        """

        url = f"https://api.github.com/repos/{self.repo_name}/issues"


        if assignees is None:
            assignees = ["copilot-swe-agent[bot]"]

        payload = {
            "title": title,
            "body": body,
            "assignees": assignees,
            "agent_assignment": {
                "target_repo": self.repo_name,
                "base_branch": base_branch,
                "custom_instructions": custom_instructions,
                "custom_agent": "",
            },
        }

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code >= 300:
            raise Exception(f"GitHub API error: {response.status_code} {response.text}")

        return response.json()
    

    def create_issue(self, title: str, body: str, assignees: list[str] = NotSet) -> Issue:
        issue = self.repo.create_issue(title=title, body=body, assignees=assignees)
        return issue
    
    def get_open_issues(self):
        return list(self.repo.get_issues(state="open"))
    
    def get_closed_issues(self):
        return list(self.repo.get_issues(state="closed"))

    def merge_pr(
        self, 
        pr: PullRequest,
        commit_message: str = NotSet,
        commit_title: str = NotSet,
        merge_method: str = NotSet,
        sha: str = NotSet,
        delete_branch: bool = False,
    ) -> PullRequest:
        pr.merge(
            commit_message=commit_message,
            commit_title=commit_title,
            merge_method=merge_method,
            sha=sha,
            delete_branch=delete_branch,
        )
        return pr
    

    

    def change_pr_base(self, pr: PullRequest, new_base: str) -> PullRequest:
        pr.edit(base=new_base)
        return pr

    def get_pr_by_issue_number(self, issue_number: int) -> PullRequest | None:
        issue = self.repo.get_issue(number=issue_number)
        if issue.pull_request is None:
            return None
        pr = self.repo.get_pull(issue.number)
        return pr
    
    def get_issue_assignees(self, issue: int | Issue) -> List[str]:
        if isinstance(issue, int):
            issue = self.repo.get_issue(number=issue)
        elif hasattr(issue, "assignees"):  # already an issue object
            issue = issue
        else:
            raise ValueError("Invalid issue input. Must be an issue number or an Issue object.")
        return [assignee.login for assignee in issue.assignees]  # list of usernames
