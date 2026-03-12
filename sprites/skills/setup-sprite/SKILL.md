---
name: setup-sprite
description: >-
  Set up a reproducible remote dev environment using sprites with credential-free
  git sync. Use when user asks to "set up a sprite", "create a remote dev environment",
  "use sprites", or mentions wanting a reproducible remote environment for a project.
---

# Setup Sprite

Set up and manage a remote dev environment using sprites. All git auth stays local — no credentials on the sprite.

## Initial Setup

Run these steps in order:

1. **Create the sprite**
   ```
   sprite create <project-name>
   ```

2. **Create a bare repo on the sprite**
   ```
   sprite exec -s <name> git init --bare /home/sprite/repos/<name>.git
   ```

3. **Start git daemon on the sprite**
   ```
   sprite exec -s <name> git daemon --reuseaddr --base-path=/home/sprite/repos --export-all --enable=receive-pack --port=9418 /home/sprite/repos
   ```

4. **Start the proxy (run in background locally)**
   ```
   sprite proxy -s <name> 9418
   ```

5. **Push code from local**
   ```
   git push git://localhost:9418/<name>.git <branch>
   ```

6. **Clone working copy on the sprite**
   ```
   sprite exec -s <name> git clone /home/sprite/repos/<name>.git /home/sprite/<name>
   ```

7. **Install dependencies**
   ```
   sprite exec -s <name> -dir /home/sprite/<name> npm install
   ```

8. **Create initial checkpoint**
   ```
   sprite checkpoint create -s <name> --comment "initial setup"
   ```

## Ongoing Workflow

- **Push updates:** `git push git://localhost:9418/<name>.git <branch>`
- **Pull changes back:** `git pull git://localhost:9418/<name>.git <branch>`
- **Run commands:** `sprite exec -s <name> -dir /home/sprite/<name> <command>`
- **Interactive shell:** `sprite console -s <name>`
- **Checkpoint:** `sprite checkpoint create -s <name> --comment "<description>"`
- **Restore:** `sprite restore <checkpoint-id> -s <name>`

## Key Design Decisions

- **Sprite targets do NOT go in Makefiles** — keep Makefiles for local dev only
- **No GitHub credentials on the sprite** — all git auth stays local
- **PRs are created from the local machine** after pulling changes from the sprite
- **Git daemon + sprite proxy** is the standard way to sync code

## Gotchas

- `sprite exec` treats the entire argument as one command — no semicolons or pipes. Run separate exec calls instead.
- The git daemon persists on the sprite after the exec that started it.
- If `sprite proxy` fails with "address already in use", kill old proxy processes locally: `pkill -f "sprite proxy"`
- The sprite is Ubuntu 25.04 with Node 22, npm, bun, and git pre-installed.
