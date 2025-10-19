# Browser Testing Plugin

Browser testing and automation plugin for Claude Code with Playwright MCP integration.

## Features

- **Playwright MCP Server**: Full integration with the Playwright Model Control Protocol server for browser automation
- **Browser Control**: Launch and control browsers (Chromium, Firefox, WebKit)
- **Page Automation**: Navigate pages, interact with elements, and capture screenshots
- **Testing**: Run end-to-end tests and validation scenarios
- **Debugging**: Inspect DOM, debug test failures, and analyze browser behavior

## Installation

Install from the faire plugin marketplace:

```shell
/plugin install browser-testing@faire
```

After installation, restart Claude Code to enable the Playwright MCP server.

## Usage

Once installed, you can use Claude to:

- **Create and run browser automation scripts** - Claude can write and execute Playwright code
- **Test web applications** - Set up end-to-end testing scenarios
- **Debug browser issues** - Use the MCP tools to inspect and interact with pages
- **Automate workflows** - Capture screenshots, test interactions, and validate functionality

Example interaction:

> "Can you open https://example.com and take a screenshot?"

Claude will use the Playwright MCP tools to:
1. Launch a browser instance
2. Navigate to the URL
3. Capture and save the screenshot

## Requirements

- Node.js 16+ (for `npx` to work)
- Playwright MCP server (`@playwright/mcp` package)

The plugin automatically installs and manages the Playwright MCP server through Claude Code's MCP system.

## Configuration

The plugin uses the following MCP server configuration:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

This configuration:
- Uses `npx` to run the latest Playwright MCP server
- Automatically manages dependencies
- Runs the server on startup when the plugin is enabled

## Troubleshooting

### Playwright MCP server fails to start
- Ensure Node.js and `npx` are in your PATH
- Try running `npx @playwright/mcp@latest` manually to verify it works
- Check that `@playwright/mcp` is available on npm

### Browser operations are slow
- Playwright MCP may need to download browser binaries on first use
- Subsequent operations will be faster as browsers are cached

### Permission errors
- Ensure you have write permissions to the directory where browsers will be cached
- On macOS, you may need to allow Playwright tools in System Preferences

## Documentation

For more information:
- [Playwright Documentation](https://playwright.dev/)
- [Claude Code MCP Integration](https://docs.claude.com/en/docs/claude-code/mcp)
- [Plugin System](https://docs.claude.com/en/docs/claude-code/plugins)

## Version

- **Current Version**: 1.0.0
- **Author**: Jack Michaud
- **Last Updated**: 2025-10-19
