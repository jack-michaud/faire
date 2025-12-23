# faire

**[faire](https://www.wordreference.com/fren/faire)** is a [Claude Plugin Marketplace](https://code.claude.com/docs/en/plugin-marketplaces) of tested and evaluated software development plugins that help Claude create high quality software.

> Anything post 1.0 is tested and evaluated. Anything 0.X is in active development.

See [this section](#evaluating-claude-code-plugins) for more details on the testing and evaluation strategy.

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

## Evaluating Claude Code plugins

> [!NOTE]
> "this is a gamechanger, trust me bro"
> Creating evaluations to systematically measure the performance of AI systems is
> how we stay objective to the real impact of AI tools.
> I'm inspired by people and teams like:
> - Cognition (which created Devin) ([their eval for devin](https://cognition.ai/blog/evaluating-coding-agents))
> - ARC Prize Foundation
> - spences10 (who created [svelte-claude-skills](https://github.com/spences10/svelte-claude-skills) with an eval for hooks)
>
> These people and teams are data driven and transparent about the quality of AI systems.

I will fill this out as I become more opinionated about this. 

I'm currently working on a python [service](http://gorodinski.com/blog/2012/04/14/services-in-domain-driven-design-ddd/) writing skill
with an eval [here](./jack-software/evals/).


## License

MIT License - see LICENSE file for details
