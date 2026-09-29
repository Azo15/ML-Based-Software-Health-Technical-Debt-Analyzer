"""
Module for mining Git repositories and extracting commit data.
Uses PyDriller to traverse commits, identify bug-fixing commits,
and extract file modifications.
"""
import re
from typing import List, Dict, Any
from pydriller import Repository
from utils.logger import logger

class GitMiner:
    """
    Mines a Git repository to extract source code changes and label them
    based on commit messages (e.g., bug-fix vs feature).
    """

    # Keywords commonly used in bug-fixing commit messages
    BUG_FIX_KEYWORDS = [
        "fix", "bug", "patch", "resolve", "issue", "hotfix",
        "error", "crash", "exception", "defect"
    ]

    def __init__(self, repo_path: str):
        """
        Initializes the GitMiner.

        Args:
            repo_path (str): Path to the local repository or URL to a remote repository.
        """
        self.repo_path = repo_path
        # Precompile regex for faster matching
        self.bug_fix_regex = re.compile(
            r'\b(?:' + '|'.join(self.BUG_FIX_KEYWORDS) + r')\b', 
            re.IGNORECASE
        )

    def is_bug_fix_commit(self, commit_msg: str) -> bool:
        """
        Determines if a commit message indicates a bug fix.

        Args:
            commit_msg (str): The commit message.

        Returns:
            bool: True if it's a bug fix, False otherwise.
        """
        return bool(self.bug_fix_regex.search(commit_msg))

    def mine_commits(self, max_commits: int = 100) -> List[Dict[str, Any]]:
        """
        Mines the repository for commits and extracts modified Python files.

        Args:
            max_commits (int): Maximum number of commits to analyze to prevent long runs.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing file data and bug-fix labels.
        """
        if max_commits < 1:
            raise ValueError("max_commits must be at least 1")

        logger.info(f"Starting to mine repository: {self.repo_path}")
        dataset = []
        commit_count = 0

        try:
            # PyDriller visits the oldest commit first by default. A bounded
            # analysis must start from the current history, not the root commit.
            for commit in Repository(self.repo_path, order="reverse").traverse_commits():
                if commit_count >= max_commits:
                    logger.info(f"Reached max commits limit ({max_commits}). Stopping miner.")
                    break

                is_bug_fix = self.is_bug_fix_commit(commit.msg)

                for modified_file in commit.modified_files:
                    # We are only interested in Python files that exist and have source code
                    path = modified_file.new_path or modified_file.old_path
                    if path and path.endswith('.py') and modified_file.source_code:
                        dataset.append({
                            'commit_hash': commit.hash,
                            'commit_date': commit.committer_date.isoformat(),
                            'filename': modified_file.filename,
                            'path': path.replace('\\', '/'),
                            'old_path': modified_file.old_path,
                            'source_code': modified_file.source_code,
                            'source_code_before': modified_file.source_code_before,
                            'is_bug_fix_candidate': int(is_bug_fix),
                            'is_bug_fix': int(is_bug_fix)
                        })
                
                commit_count += 1
                if commit_count % 20 == 0:
                    logger.debug(f"Processed {commit_count} commits...")

            logger.info(f"Mining completed. Extracted {len(dataset)} Python file modifications from {commit_count} commits.")
            return dataset

        except Exception as e:
            logger.error(f"Error while mining repository: {e}")
            raise
