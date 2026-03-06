# Deploy Watch

## Context
After the human merges the PR, monitor the deployment pipeline. This phase detects deployment workflows and watches for completion.

## Agents

### Agent: deploy-watcher
- **Type**: general-purpose
- **Instructions**: |
    Monitor deployment for the merged PR on branch {{branch_name}}.

    1. **Detect deployment workflow**:
       - Check GitHub Actions: `gh run list --branch main --limit 5`
       - Look for workflows triggered by the merge commit
       - Common deploy workflow names: "deploy", "release", "cd", "production"

    2. **Watch deployment**:
       ```
       gh run watch <run-id>
       ```
       Or poll status:
       ```
       gh run view <run-id> --json status,conclusion
       ```

    3. **Report result**:
       - SUCCESS: Deployment completed successfully
       - FAILURE: Deployment failed with error details
       - NOT_FOUND: No deployment workflow detected

    4. If deployment takes longer than 15 minutes, report the current status and suggest the human check manually.

- **Output**: Deploy status (success/failure/not_found/timeout) with details

## Coordination
Single agent. No coordination needed.

## Output Contract
Store in `phases.deploy_watch.data`:
- deploy_status (string: "success" | "failure" | "not_found" | "timeout")
- deploy_url (string, if available)
- deploy_duration (string)
- details (string)

## Failure Handling
- No deployment workflow found: Report and proceed to production validation (user may deploy manually)
- Deployment fails: Report error details, save state, end session for human intervention
- Timeout: Report current status, suggest manual check, save state, end session
