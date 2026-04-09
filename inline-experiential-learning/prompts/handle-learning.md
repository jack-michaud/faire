The learning agent detected something worth storing. Follow these steps:

1. Parse LEARNING_RECOMMENDATIONS from the stop hook reason. Split on `---` delimiters — there may be multiple.
2. For each learning, confirm with the user via AskUserQuestion. Prompt by type:
   - correction: "Store this as a memory? Is this reproducible or a one-off?\n\n<suggested_content>"
   - new_process: "Save this new process?\n\n<suggested_content>"
   - trigger_improvement: "Memory file <path> was relevant but wasn't consulted. Update its name/summary?\n\nCurrent: <current line 1>\nProposed: <new line 1>"
   - duplicate: "This overlaps with <existing file>. Merge, replace, or skip?"
   - conflict: "This contradicts <existing file>. Which is correct?"
3. On confirmation: Write/edit the leaf file. Use the memory file format:
   ```
   One sentence summary of the learning (~8-15 words).
   Full description with context, nuance, and reasoning. Include enough
   detail that the agent can act on this knowledge without further research.
   <evidence: what session/correction produced this learning>
   ```
   File name is the title (kebab-case slug). No redundant heading inside.
4. On rejection: Skip that learning, continue to next.
5. After all learnings are processed, rebuild the index once:
   bash "$CLAUDE_PLUGIN_ROOT/scripts/rebuild-memory-index.sh"

You have full session context — write richer memory files than the stop hook could.
