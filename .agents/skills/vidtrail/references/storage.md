# Materials, reuse, and destination

## Follow the user's organization

Read current project rules. Use the chosen destination, otherwise the project's established note/material location. With neither, deliver in the conversation and suggest a save location. Do not mandate a new knowledge base, directory tree, master source catalog, or rearrangement of existing files.

External destinations such as Notion are optional and require actual tools and authorization. Establish the destination before writing, then read back the result. If success is uncertain, inspect before retrying; do not create duplicates blindly.

## Reuse by stable identity

Use platform ID + part/cid, with title only as a hint. For local material without an ID, use SHA256 as supporting identity. Check the current project and user-designated locations for originals, receipts, notes and external task records. A new question means incremental analysis, not another original copy or overwritten conclusion.

## Originals

The helper requires `--data-root` or `VIDEO_RESEARCH_DATA_ROOT` outside the distribution repository. Receipts/materials live beneath that root under platform/video ID/part. This acquisition layout does not decide the note destination. Without the helper, use the project's existing material organization.

Record source URL, ID/part, creator/date (unknown when unavailable), retrieval date, material type, actual path, byte count, SHA256, and separate acquisition/text/visual status. Preserve originals; derivative notes cite original timestamps/lines. Use relative links inside the repository. A different machine cannot read an unsynchronized absolute path; label it unavailable instead of pretending access.

Keep transcripts as evidence and substantial media temporary where appropriate. Media, cookies, private notes and actual user-material receipts do not belong in this distribution. Cleanup suggestions must identify exact files and conditions; never automatically delete or suggest discarding the only evidence.

## Writes and Git

Write, stage, commit or push only within applicable user authorization. Check working state and remote changes first. Fast-forward pull only when safe; preserve both sides of changes without automatic reset/stash/force-push. Stage explicit task paths, never blanket-add private working material.
