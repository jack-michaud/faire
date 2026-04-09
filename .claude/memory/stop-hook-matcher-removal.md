Stop hooks should not include a matcher field — it prevents them from firing.
The Stop event (and SessionStart) fire without a tool context, so "matcher": "*"
has nothing to match against and silently prevents the hook from triggering.
Remove the matcher field from Stop hook definitions entirely. The working
ralph-loop plugin in claude-plugins-official confirms this pattern: its Stop
hook has no matcher and fires correctly.
<evidence: User reported Stop hook not firing in inline-experiential-learning plugin. Compared with working ralph-loop Stop hook — the only structural difference was the matcher field. Removing it fixed the issue.>
