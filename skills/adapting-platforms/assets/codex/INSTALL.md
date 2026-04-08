# Installing <Project Name> for Codex

Enable skills in Codex via native skill discovery. Clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url> ~/.codex/<project-name>
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/<project-name>/skills ~/.agents/skills/<project-name>
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\<project-name>" "$env:USERPROFILE\.codex\<project-name>\skills"
   ```

3. **Restart Codex** to discover the skills.

## Updating

```bash
cd ~/.codex/<project-name> && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/<project-name>
rm -rf ~/.codex/<project-name>
```
