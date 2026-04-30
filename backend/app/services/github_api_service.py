import asyncio
import logging
from typing import Optional, List, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)


class GitHubAPIService:
    """GitHub API client for fetching repo metadata, PRs, commits, users."""

    def __init__(self, token: Optional[str] = None, org: Optional[str] = None):
        self.token = token
        self.org = org
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AegisTwin/1.0",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

    async def get_repo_metadata(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """Fetch repository metadata."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch repo metadata: {e}")
        return None

    async def get_pr_metadata(self, owner: str, repo: str, pr_number: int) -> Optional[Dict[str, Any]]:
        """Fetch PR metadata including title, description, labels, author."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch PR metadata: {e}")
        return None

    async def get_pr_files(self, owner: str, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Fetch list of files changed in a PR."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        files = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        files = await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch PR files: {e}")
        return files

    async def get_commits(self, owner: str, repo: str, branch: str = "main", limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent commits from a branch."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"sha": branch, "per_page": min(limit, 100)}
        commits = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        commits = await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch commits: {e}")
        return commits

    async def get_contributors(self, owner: str, repo: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch list of contributors."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {"per_page": min(limit, 100), "anon": "false"}
        contributors = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        contributors = await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch contributors: {e}")
        return contributors

    async def get_issues(self, owner: str, repo: str, state: str = "open", limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch issues (and PRs, which are issues in GitHub API)."""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state, "per_page": min(limit, 100)}
        issues = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        issues = await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch issues: {e}")
        return issues

    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch user profile."""
        url = f"{self.base_url}/users/{username}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        return await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch user {username}: {e}")
        return None

    async def get_org_repos(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch all repos for the configured organization."""
        if not self.org:
            return []
        url = f"{self.base_url}/orgs/{self.org}/repos"
        params = {"per_page": min(limit, 100), "type": "all"}
        repos = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        repos = await resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch org repos: {e}")
        return repos
