# Installing Skill Forge for Codex

Enable skills in Codex via native skill discovery. Clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/odradekai/skill-forge.git ~/.codex/skill-forge
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/skill-forge/skills ~/.agents/skills/skill-forge
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\skill-forge" "$env:USERPROFILE\.codex\skill-forge\skills"
   ```

3. **Restart Codex** to discover the skills.

## Updating

```bash
cd ~/.codex/skill-forge && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/skill-forge
rm -rf ~/.codex/skill-forge
```
