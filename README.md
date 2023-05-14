# Retry Failed Workflow Jobs

This Github action allows you to retry failed jobs within a Github workflow. With this action, you can automatically retry failed jobs, up to a certain number of times, without having to manually re-run the entire workflow.

## Table of contents

- [Inputs](#inputs)
- [Usage](#Usage)

## Inputs

Add a step like this to your workflow:
```yaml
- uses: EndBug/add-and-commit@v9 # You can change this to use a specific version.
  with:
    # A Github personal access token (PAT) with `repo` scope or the default `GITHUB_TOKEN`
    # This is required to access the Github API.
    token: ${{ secrets.GITHUB_TOKEN }}

    # The ID of the workflow run that you want to retry failed jobs for.
    # Default: depends on the default_author input
    workflow_run_id: ${{ github_run_id }}

    # The maximum number of times to retry a failed job..
    # The default value is 3.
    max_retries: 3
```

## Usage

To use this action, add it as a step within a separate job in your workflow so that the failed ones won't affect the action. Here's an example of how you can use this action in your workflow:


Here's an example of how you can use this action in your workflow:

```yaml
name: My Workflow

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2
      - name: Build and Test
        run: |
          make build
          make test

  retry:
    runs-on: ubuntu-latest
    steps:
      - name: Retry failed jobs
        uses: hourki-actions/retry-workflow-action@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          workflow_run_id: ${{ github.run_id }}
          max_retries: 5

```

## License

This action is distributed under the MIT license, check the [license](LICENSE) for more info.