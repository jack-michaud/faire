# faire

> A Claude Code plugin for software engineering skills

**faire** is a collection of development skills that help you follow best practices for test-driven development, code review, debugging, systematic problem-solving, and more.

## Installation

### From Marketplace (Recommended)

Add the faire marketplace to your Claude Code configuration:

```bash
/plugin marketplace add jack-michaud/faire
```

Then install the faire plugin:

```bash
/plugin install faire@faire
```

Or browse and install interactively:

```bash
/plugin
```

### Manual Installation

Clone the repository directly:

```bash
# Clone the repository
git clone https://github.com/jack-michaud/faire.git ~/.claude/plugins/faire
```

### For Teams

Configure your `.claude/settings.json` to automatically add the marketplace:

```json
{
  "extraKnownMarketplaces": {
    "faire": {
      "source": {
        "source": "github",
        "repo": "jack-michaud/faire"
      }
    }
  }
}
```

## What's Included

### Testing Skills
- **Test-Driven Development**: RED-GREEN-REFACTOR cycle for implementing features
- More testing skills coming soon...

### Collaboration Skills
- **SOLID Principles Review**: Code review focusing on SOLID principles
- **PR File Review**: Review pull request files for artifacts and quality
- More collaboration skills coming soon...

### Debugging Skills
- Skills for systematic debugging and problem-solving

### Workflow Skills
- Skills for common development workflows

### Meta Skills
- **Writing Skills**: How to create new skills effectively

## Usage

Skills are automatically discovered by Claude when this plugin is installed. Claude will use relevant skills based on your requests.

For example:
- When implementing a feature, Claude will use the Test-Driven Development skill
- When reviewing code, Claude will use code review skills
- When debugging, Claude will use systematic debugging approaches

## Contributing

Contributions are welcome! Please feel free to submit pull requests with:
- New skills
- Improvements to existing skills
- Bug fixes
- Documentation enhancements

## License

MIT License - see LICENSE file for details
