# Changelog

## [1.3.0] - 2026-04-08

### Changed

- Renamed project from `skill-forge` to `bundles-forge`
- Replaced `skill-project` / `skill-projects` terminology with `bundles` throughout
- Renamed all 11 skill directories:
  - `auditing-skill-projects` → `auditing`
  - `designing-skill-projects` → `designing`
  - `optimizing-skill-projects` → `optimizing`
  - `releasing-skill-projects` → `releasing`
  - `scaffolding-skill-projects` → `scaffolding`
  - `adapting-skill-platforms` → `adapting-platforms`
  - `iterating-skill-feedback` → `iterating-feedback`
  - `managing-skill-versions` → `managing-versions`
  - `scanning-skill-security` → `scanning-security`
  - `writing-skill-content` → `writing-skill`
  - `using-skill-forge` → `using-bundles-forge`
- Renamed OpenCode plugin file to `bundles-forge.js`
- Renamed command `/use-skill-forge` → `/use-bundles-forge`
- Updated all repository URLs to `odradekai/bundles-forge`
- Replaced all `skill-forge:` cross-reference prefixes with `bundles-forge:`
- Updated all cross-reference skill names to match new directory names

## [1.2.0] - 2026-04-07

### Added

- New skill: `iterating-skill-feedback` for receiving user feedback about skills, validating suggestions against core goals, forking external skills with identifiers, and automatic post-change auditing
- Scope clarification between `optimizing-skill-projects` (project engineering) and `iterating-skill-feedback` (single-skill effectiveness)

### Changed

- Updated `auditing-skill-projects` integration: added Suggests relationship to `iterating-skill-feedback`
- Updated `optimizing-skill-projects` integration: added Cross-refers relationship to `iterating-skill-feedback`
- Updated `using-skill-forge` routing table, skill priority, and red flags to include the new skill
- Updated workflow diagrams in README to show audit branching into both optimizing and iterating paths

## [1.1.0] - 2026-04-07

### Changed

- Renamed project from `skill-engineering-guide` to `skill-forge`
- Renamed bootstrap skill directory `using-skill-engineering-guide` → `using-skill-forge`
- Renamed OpenCode plugin file to `skill-forge.js`
- Updated all repository URLs to `odradekai/skill-forge`
- Replaced all `seg:` cross-reference prefixes with `skill-forge:`
- Renamed command `/use-seg` → `/use-skill-forge`

### Removed

- Removed project abbreviation `seg` — all references now use the full name `skill-forge`

## [1.0.0] - 2026-04-06

### Added

- Initial release as a structured skill-project
- Refactored from single-skill folder to full plugin architecture following superpowers conventions
- Multi-platform support: Claude Code, Cursor, Codex, OpenCode, Copilot CLI, Gemini CLI
- Platform manifests for all 6 supported platforms
- Session bootstrap hooks with Windows polyglot support
- Version synchronization infrastructure (`.version-bump.json` + `bump-version.sh`)
- **skill-engineering-guide** skill: project scaffolding, auditing, optimization, and platform adaptation
