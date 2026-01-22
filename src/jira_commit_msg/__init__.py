from pathlib import Path
from re import compile as regex
from typing import Annotated

from git import Repo
from typer import Argument, Exit, Option, Typer, echo

app = Typer()

JIRA_ISSUE_REGEX = regex(r"(?P<issue_id>[A-Z]+-\d+)")


def branch_name(repo: Repo | None = None) -> str:
    """Get branch name from git repo"""
    if repo is None:
        repo = Repo(Path.cwd())
    try:
        return repo.active_branch.name
    except TypeError:  # pragma: no cover (CI pull request)
        return repo.head.name  # (HEAD)


@app.command()
def prepare_commit_msg(  # noqa: PLR0913
    commit_msg_file: Annotated[
        Path,
        Argument(
            help="Commit Message File",
            envvar="COMMIT_MSG_FILE",
        ),
    ],
    branch_name: Annotated[
        str, Option(hidden=True, default_factory=branch_name)
    ],  # enable dependency injection for testing
    use_conventional_commit: Annotated[
        bool, Option(help="Use Conventional Commit", envvar="USE_CONVENTIONAL_COMMIT")
    ] = False,
    force_issue_id: Annotated[
        bool,
        Option(help="Force an issue id to be present in branch name or commit message"),
    ] = False,
    skip_merge_commit: Annotated[bool, Option(help="Skip Merge Commit")] = True,
    msg_source: Annotated[
        str | None,
        Option(
            "--commit-msg-source",
            help="Message Source (second argument passed to prepare-commit-msg)",
            envvar="PRE_COMMIT_COMMIT_MSG_SOURCE",
        ),
    ] = None,
) -> None:
    """Prepare commit message for Jira"""

    if skip_merge_commit and msg_source == "merge":
        echo("Skipping merge commit")
        return

    commit_msg = commit_msg_file.read_text()

    if issue_id_match := JIRA_ISSUE_REGEX.match(branch_name):
        issue_id = issue_id_match.group("issue_id")

        if issue_id in commit_msg:
            echo("Issue already in commit message")
            return

        if use_conventional_commit:
            # add issue id as footer of commit message
            commit_msg_file.write_text(f"{commit_msg}\n\nCloses: #{issue_id}")

        else:
            commit_msg_file.write_text(f"[{issue_id}] - {commit_msg}")

    elif force_issue_id and not JIRA_ISSUE_REGEX.search(commit_msg):
        echo("An issue id is mandatory to commit, please add it to the commit message")
        raise Exit(1)
