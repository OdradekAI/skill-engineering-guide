# Installing Skill Engineering Guide for OpenCode

## Installation

Add to your `opencode.json` under the `plugins` key:

```json
{
  "plugins": [
    {
      "name": "skill-engineering-guide",
      "url": "https://github.com/odradekai/skill-engineering-guide.git"
    }
  ]
}
```

OpenCode will clone the repo and load the plugin on next start.

## Updating

OpenCode manages plugin updates. To force an update, remove and re-add the plugin entry.
