# Installing Bundles Forge for Codex

Enable skills in Codex via native skill discovery. Clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/odradekai/bundles-forge.git ~/.codex/bundles-forge
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/bundles-forge/skills ~/.agents/skills/bundles-forge
   ```

   **Windows (PowerShell):**
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills"
   cmd /c mklink /J "$env:USERPROFILE\.agents\skills\bundles-forge" "$env:USERPROFILE\.codex\bundles-forge\skills"
   ```

3. **Restart Codex** to discover the skills.

## Updating

```bash
cd ~/.codex/bundles-forge && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/bundles-forge
rm -rf ~/.codex/bundles-forge
```
