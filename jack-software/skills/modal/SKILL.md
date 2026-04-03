---
name: modal
description: "Modal.com platform knowledge for serverless GPU workloads. Use when a project uses Modal for deployment, GPU compute, or serverless functions — covers environment configuration, app structure, and Modal CLI patterns."
---

# Modal

Reference knowledge for building and deploying applications on [Modal.com](https://modal.com).

## When to Use

Activate this skill when:
- The project imports `modal` or uses Modal decorators (`@app.function`, `@app.cls`)
- The user asks about serverless GPU deployment, Modal environments, or Modal CLI commands
- Code references Modal concepts like `Stub`, `Image`, `Volume`, `Secret`, or `NetworkFileSystem`

## Core Patterns

- **App structure**: Define apps with `modal.App()`, attach functions with decorators
- **Container images**: Build custom images with `modal.Image.debian_slim().pip_install(...)`
- **GPU selection**: Use `gpu="T4"`, `gpu="A10G"`, or `gpu="A100"` in function decorators
- **Secrets**: Access secrets via `modal.Secret.from_name("secret-name")`
- **Volumes**: Persist data with `modal.Volume` and mount at specified paths

## CLI Reference

```bash
modal run app.py          # Run a Modal app locally
modal deploy app.py       # Deploy to Modal cloud
modal environment list    # List available environments
modal token set           # Configure authentication
```

## Additional Documentation

If not covered by the resources below, search the official docs at `https://modal.com/docs/reference` or examples at `https://modal.com/docs/examples/agent`.

# Resources

Custom docs written on Modal topics:

- `resources/environments.md` — Environment configuration and management
