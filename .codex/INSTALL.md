# Installing Skill Engineering Guide for Codex

Enable skills in Codex via native skill discovery. Clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/odradekai/skill-engineering-guide.git ~/.codex/skill-engineering-guide
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/skill-engineering-guide/skills ~/.agents/skills/skill-engineering-guide
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\skill-engineering-guide" "$env:USERPROFILE\.codex\skill-engineering-guide\skills"
   ```

3. **Restart Codex** to discover the skills.

## Updating

```bash
cd ~/.codex/skill-engineering-guide && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/skill-engineering-guide
rm -rf ~/.codex/skill-engineering-guide
```
