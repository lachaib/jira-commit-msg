from contextlib import contextmanager
from pathlib import Path
from subprocess import check_output
from tempfile import NamedTemporaryFile

import pytest
from typer import Exit

from jira_commit_msg import branch_name, prepare_commit_msg


@contextmanager
def commit_msg_file(source: Path):
    with NamedTemporaryFile(mode="w+") as tmp:
        tmp.write(source.read_text())
        tmp.seek(0)
        yield Path(tmp.name)


@pytest.mark.parametrize(
    ("force_issue_id", "skip_merge_commit"),
    [
        pytest.param(False, False, id="no force no skip"),
        pytest.param(True, False, id="force no skip"),
        pytest.param(False, True, id="no force skip"),
        pytest.param(True, True, id="force skip"),
    ],
)
def test_prepare_commit_msg_without_issue_no_cc(force_issue_id: bool, skip_merge_commit: bool):
    """Test that the hook adds the issue id to the commit message

    force_issue_id and skip_merge_commit should not have any effect on the result
    """
    with commit_msg_file(Path("test/commit-files/commit-msg-without-issue.txt")) as tmp:
        prepare_commit_msg(tmp, "AA-123", False, force_issue_id, skip_merge_commit, "message")

        assert tmp.read_text() == Path("test/commit-files/commit-msg-with-issue.txt").read_text()


@pytest.mark.parametrize(
    ("force_issue_id", "skip_merge_commit"),
    [
        pytest.param(False, False, id="no force no skip"),
        pytest.param(True, False, id="force no skip"),
        pytest.param(False, True, id="no force skip"),
        pytest.param(True, True, id="force skip"),
    ],
)
def test_prepare_commit_msg_with_issue_no_cc(force_issue_id: bool, skip_merge_commit: bool):
    """Test idempotency of the hook in case the issue is already written in commit

    force_issue_id and skip_merge_commit should not have any effect on the result
    """
    with commit_msg_file(Path("test/commit-files/commit-msg-with-issue.txt")) as tmp:
        prepare_commit_msg(tmp, "AA-123", False, force_issue_id, skip_merge_commit, "message")

        assert tmp.read_text() == Path("test/commit-files/commit-msg-with-issue.txt").read_text()


@pytest.mark.parametrize(
    ("force_issue_id", "skip_merge_commit"),
    [
        pytest.param(False, False, id="no force no skip"),
        pytest.param(True, False, id="force no skip"),
        pytest.param(False, True, id="no force skip"),
        pytest.param(True, True, id="force skip"),
    ],
)
def test_prepare_commit_msg_without_issue_cc(force_issue_id: bool, skip_merge_commit: bool):
    """Test that the hook adds the issue id to the commit message"""
    with commit_msg_file(Path("test/commit-files/commit-msg-without-issue-cc.txt")) as tmp:
        prepare_commit_msg(tmp, "AA-123", True, force_issue_id, skip_merge_commit, "message")

        assert tmp.read_text() == Path("test/commit-files/commit-msg-with-issue-cc.txt").read_text()


@pytest.mark.parametrize(
    ("force_issue_id", "skip_merge_commit"),
    [
        pytest.param(False, False, id="no force no skip"),
        pytest.param(True, False, id="force no skip"),
        pytest.param(False, True, id="no force skip"),
        pytest.param(True, True, id="force skip"),
    ],
)
def test_prepare_commit_msg_with_issue_cc(force_issue_id: bool, skip_merge_commit: bool):
    """Test idempotency of the hook in case the issue is already written in commit"""
    with commit_msg_file(Path("test/commit-files/commit-msg-with-issue-cc.txt")) as tmp:
        prepare_commit_msg(tmp, "AA-123", True, force_issue_id, skip_merge_commit, "message")

        assert tmp.read_text() == Path("test/commit-files/commit-msg-with-issue-cc.txt").read_text()


@pytest.mark.parametrize(
    ("conventional_commit", "filename"),
    [
        pytest.param(True, "test/commit-files/commit-msg-with-issue-cc.txt", id="cc"),
        pytest.param(False, "test/commit-files/commit-msg-with-issue.txt", id="no cc"),
    ],
)
def test_prepare_commit_msg_with_issue_force_issue_id(conventional_commit: bool, filename: str):
    """Test that an issue id in the pattern will pass the issue id enforcement
    Commit msg file will be left unchanged
    """
    with commit_msg_file(Path(filename)) as tmp:
        prepare_commit_msg(tmp, "AA-123", conventional_commit, True, True, "message")

        assert tmp.read_text() == Path(filename).read_text()


@pytest.mark.parametrize(
    ("conventional_commit", "filename"),
    [
        pytest.param(True, "test/commit-files/commit-msg-without-issue-cc.txt", id="cc"),
        pytest.param(False, "test/commit-files/commit-msg-without-issue.txt", id="no cc"),
    ],
)
def test_prepare_commit_msg_without_issue_force_issue_id_no_issue(
    conventional_commit: bool, filename: str
):
    """Test that the hook adds the issue id to the commit message"""
    with commit_msg_file(Path(filename)) as tmp:
        with pytest.raises(Exit) as exit_exc:
            prepare_commit_msg(tmp, "master", conventional_commit, True, True, "message")

        assert exit_exc.value.exit_code == 1
        # file should be left unchanged
        assert tmp.read_text() == Path(filename).read_text()


@pytest.mark.parametrize(
    ("conventional_commit", "filename"),
    [
        pytest.param(True, "test/commit-files/commit-msg-without-issue-cc.txt", id="cc"),
        pytest.param(False, "test/commit-files/commit-msg-without-issue.txt", id="no cc"),
    ],
)
def test_prepare_commit_msg_skip_merge_commits(conventional_commit: bool, filename: str):
    """Test that merge commits are bypassed, even when trying to force an issue id."""
    with commit_msg_file(Path(filename)) as tmp:
        prepare_commit_msg(tmp, "AA-123", conventional_commit, True, True, "merge")

        assert tmp.read_text() == Path(filename).read_text()


def test_get_branch_name():
    """Test that the branch name is correctly extracted from the repo."""
    from_git = check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()  # noqa: S607
    from_repo = branch_name()
    assert from_repo == from_git
