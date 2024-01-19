# JIRA Issue in Commit Messages

Wherever I worked, JIRA is the key ticketing system to track issues, and a common convention to link commits to JIRA tickets is to put the ticket inside the commit message.

In completion to that, Atlassian VS Code plugin (and probably in other IDEs) creates branches using the issue id and slug.

And they recommend using a custom `prepare-commit-msg` hook to pass it to commits. Brilliant idea!

What's missing in the ecosystem _(or I didn't find it)_ is a `prepare-commit-msg`` hook compliant with `prepare-commit` tool.


Enters this tool.

## Usage

Add the following section in your `.pre-commit-config.yaml`

```yaml
    repo: https://github.com/lachaib/jira-commit-msg
    rev: v0.1
    hooks:
      - id: jira-commit-msg
        args: []
        stages: [prepare-commit-msg]
```

> [!NOTE]
> In order for this hook to be used, you need to install pre-commit also on the `prepare-commit-msg` hook, either by installing manually `pre-commit install -t prepare-commit-msg` or better, by specifying the install stage so that all users will share the setup:
> ```yaml
> default_install_hook_types:
>  - pre-commit
>  - prepare-commit-msg
> ```
>
> And as it means other hook would be run for both stages, _which you may want to avoid for performance reasons_, it is recommended to as well update the `default_stage` for which hooks not specifying it are run:
> ```yaml
> default_stages:
>  - pre-commit
> ``` 

### Available arguments

* `--use-conventional-commit/--no-use-conventional-commit` (default: `False`): Following this convention, the issue id will be added as footer of the commit message. Otherwise, the issue id will be added as an anchor at the beginning of commit message (`[ISSUE_ID] -  MESSAGE`)
* `--skip-merge-commit/--no-skip-merge-commit` (default: `True`): Skip merge commits to be edited.
* `--force-issue-id/--no-force-issue-id` (default: `False`): Force an issue id to be present in a commit message.

