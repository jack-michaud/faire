
# Writing services eval

Writing a service is a [Claude Code Skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) that I am testing. In my skill prompt, I have a variety of requirements that need to be followed to create a service in the way that I like, and my evaluation ensures that the skill actually adheres to my requirements.

- Uses the [Claude Code Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) to simulate a Claude Code session
- Experiment tracking is done through a logger service to measure the effect of prompt changes

# Insights

## Haiku 4.5 is not as good as Sonnet 4.5 at instruction following for simple skills

![](./assets/benchmark_comparison.png)
