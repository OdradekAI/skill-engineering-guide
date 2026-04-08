# Installing Bundles Forge for OpenCode

## Installation

Add to your `opencode.json` under the `plugins` key:

```json
{
  "plugins": [
    {
      "name": "bundles-forge",
      "url": "https://github.com/odradekai/bundles-forge.git"
    }
  ]
}
```

OpenCode will clone the repo and load the plugin on next start.

## Updating

OpenCode manages plugin updates. To force an update, remove and re-add the plugin entry.
