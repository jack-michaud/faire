
# Writing services eval

Writing a service is a [Claude Code Skill](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) that I am testing. In my skill prompt, I have a variety of requirements that need to be followed to create a service in the way that I like, and my evaluation ensures that the skill actually adheres to my requirements.

- Uses the [Claude Code Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview) to simulate a Claude Code session
- Experiment tracking is done through a logger service to measure the effect of prompt changes

# Insights

## Haiku 4.5 is not as good as Sonnet 4.5 at instruction following for simple skills

![](./assets/benchmark_comparison.png)

## GLM-4.7 is better than Haiku but not as good as Sonnet

Using [OpenRouter's Claude Code Integration](https://openrouter.ai/docs/guides/guides/claude-code-integration) I tested GLM-4.7 with the same Claude Code harness.

NOTE: I haven't changed the prompt for this; given that this is a different model family, it may require different prompting.

Cost to run GLM-4.7 on eval: `$2.75`

![](./assets/benchmark_comparison_glm_4_7.png)

# Tips

Running the eval

```
for i in {1..20}; do echo "=== Run $i/20 ===" && make run-services-eval && jj abandon -r @; done
```

If using an openrouter model, source `.env.openrouterclaude`.

Generating a graph

```
uv run python jack-software/evals/create_benchmark_graph.py -o jack-software/evals/assets/benchmark_comparison_glm_4_7.png -r 24dd1ad:Haiku -r 11de541:GLM-4.7 -r 6cf39c8:Sonnet --db evals.db
```
