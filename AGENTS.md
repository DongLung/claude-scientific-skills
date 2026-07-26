# Repository Guidance

Every skill in `skills/` must conform to the open [Agent Skills specification](https://agentskills.io/specification).
CI enforces this in `.github/workflows/skill-spec-validation.yml`. Validate locally before
opening a PR:

```bash
uv sync
for d in skills/*/; do uv run skills-ref validate "$d"; done
```

## Frontmatter

`SKILL.md` starts with YAML frontmatter. **Only these six fields are allowed** — the spec
defines a closed set, and any other top-level key is a validation error:

| Field | Required | Constraints |
| --- | --- | --- |
| `name` | Yes | 1–64 chars, lowercase letters/digits/hyphens only, no leading, trailing, or consecutive hyphens, and **must equal the directory name**. |
| `description` | Yes | 1–1024 chars. Say what the skill does *and* when to use it, with the keywords that should trigger it. |
| `license` | No | License name, or a reference to a bundled license file. |
| `compatibility` | No | Max 500 chars. Environment requirements only — omit it if the skill has none. |
| `allowed-tools` | No | A **space-separated string**, e.g. `Read Write Edit Bash`. Not a YAML list. |
| `metadata` | No | Mapping of string keys to **string** values, except the host manifest blocks below. Required here: `metadata.version`. |

Put anything else — authorship, upstream versions, review dates, client-specific config — inside
`metadata`, never at the top level.

### Write block-style YAML, not JSON flow style

The reference validator parses frontmatter with `strictyaml`, which **rejects JSON-style flow
mappings and sequences**. A flow mapping does not merely fail one check: the whole frontmatter
fails to parse, so `name` and `description` become unreadable and the skill will not register.

```yaml
# Wrong -- breaks the validator
metadata: {"version": "1.1", "skill-author": "K-Dense Inc."}

# Right
metadata:
  version: "1.1"
  skill-author: K-Dense Inc.
```

### Quote `metadata` scalars

Quote values that would otherwise be parsed as a number, boolean, or date — `version: "1.0"`,
`last-reviewed: "2026-07-23"` — so they stay strings as the spec requires.

### Host manifest blocks stay nested mappings

`metadata.openclaw` and `metadata.hermes` are the documented exception: keep them as **nested
mappings**, not JSON strings. OpenClaw's `resolveOpenClawManifestBlock()` requires
`typeof candidate === "object"`, so a JSON string silently disables its dependency gating and
credential injection. Nested mappings still pass `skills-ref validate`.

```yaml
metadata:
  version: "1.1"
  skill-author: Exa
  openclaw:
    primaryEnv: EXA_API_KEY
    envVars:
      - name: EXA_API_KEY
        required: true
        description: Exa search API key.
```

## Versioning

- Every `SKILL.md` must carry a version under the `metadata` mapping:
  ```yaml
  metadata:
    version: "1.0"
  ```
- When updating an existing skill, increment its `metadata.version` in the same change. Use quoted
  numeric strings and advance the visible version sequence (for example, `1.0` to `1.1`). Use a new
  major version only for a breaking or substantial redesign.

## Body and layout

- Keep `SKILL.md` under 500 lines. CI warns above that. Move long reference material into
  `references/` so agents load it only when needed.
- Optional directories: `references/` (documentation), `scripts/` (executable helpers),
  `assets/` (templates and static resources). Only `SKILL.md` is required.
- Reference other files with relative paths from the skill root, kept one level deep.
