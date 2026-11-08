# Discover and compare videos

Search is for selecting sources, not establishing what their full content says. If the user supplies a specific video, proceed to acquisition without forcing a broad search. During discovery, do not download media, transcribe, upload, or create a learning directory.

Infer the task, audience level, explanatory versus demonstrated content, language, recency, and desired number from the request. For explicitly recent research, start with the last 90 days while retaining older relevant sources with dates. For broad research without a requested count, recommend roughly 3–5 strong candidates; do not pad a weak result set.

## Search with a reason

Break a broad topic into distinct angles, such as a practical demonstration, underlying concepts, or cost and limitations. For a narrow question, search its actual gap. Use one main concept with a few qualifiers per query, beginning with functional terms and then specific project names.

Read and assess one query group before choosing the next. Deduplicate by platform ID and exclude advertisements or course cards without a valid video identity. Query, page, or sort changes are purposeful discovery, not permission to repeat a failed acquisition.

Judge relevance, prerequisites, demonstrated process, date, and duration rather than popularity alone. After two distinct query groups mostly miss the target, or a route reports an error, access challenge, or empty response, stop expanding that route. Use another actually available platform/browser route or return the checked range and gaps. Do not loop the same failed command.

## Available commands

Read actual help. The pinned bilibili-cli 0.6.2 supports `--type user|video` (default: user), `--page`, `-n/--max`, `--json`, and `--yaml`:

```sh
bili search "topic keywords" --type video --page 1 --max 20 --yaml
yt-dlp --flat-playlist --dump-single-json --skip-download "ytsearch10:topic keywords"
```

`--max` truncates the current page; it does not paginate. Stock bili 0.6.2 does not provide the maintainer's separate search-patch options for ordering, dates, duration, or page size. That patch is not bundled or installed here. Use normal browser filters or assess returned fields when supported; report unknown dates or durations instead of guessing. yt-dlp flat search can omit such fields.

Use browser search only if the host exposes a real browser tool. Follow its configured browser order and existing sessions; do not invent query parameters or bypass challenges. A browser login is not a CLI credential, and different browsers do not share sessions automatically.

## Deliver candidates and stop when requested

For each candidate give title, creator, platform ID and part, source URL, date, duration (or unknown), relevance, and uncertainty. State queries, routes, pages checked, and representative rejection reasons. Label the basis: metadata/page inspection, **full text not read**. If only one strong result exists, explain the comparison range rather than filling a quota.

Candidate-only requests end here. Do not acquire subtitles, download, transcribe, or write learning notes. After selection, follow [Workflow](workflow.md).

Do not automatically spawn agents. If delegation is explicitly requested or required by the current environment, give bounded search directions and complete candidate fields; the main task verifies identity and relevance. Shared acquisition/upload resources need one owner.
