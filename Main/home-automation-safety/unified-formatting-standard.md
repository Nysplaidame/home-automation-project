# Unified Documentation Formatting Standard
*For Home Automation Project - Obsidian Vault Efficiency Optimized*

## YAML Frontmatter Standard
```yaml
---
title: [Descriptive Title]
description: [Brief single-line description]
tags: [tag1, tag2, tag3]
aliases: [Essential Alias 1, Essential Alias 2]
created: YYYY-MM-DD
modified: YYYY-MM-DD
type: [document-type]
status: [active/archived/placeholder]
---
```

### YAML Rules:
- **Tags**: Inline format `[tag1, tag2, tag3]` (max 5 tags)
- **Aliases**: Essential only (max 3 aliases)
- **Dates**: Simple format `YYYY-MM-DD`
- **Single YAML block**: No duplicates
- **Required fields**: title, description, tags, type, status
- **Optional fields**: aliases, created, modified, project_context, phase, progress

## Link Format Standard
```markdown
[[filename]]                    # Preferred - relative path
[[filename|Custom Text]]        # With alias when needed
[[folder/filename]]             # Only when disambiguation needed
```

### Link Rules:
- **Relative paths only**: No full project structure paths
- **File extensions**: Omit .md extensions
- **Bidirectional**: Ensure backlinks exist
- **Broken links**: Remove and note "session file deep-archived" for missing session states

## Header Formatting
```markdown
# Main Title (H1 - once per document)
## Major Section (H2)
### Subsection (H3)
#### Detail Level (H4 - sparingly)
```

### Header Rules:
- **Emoji usage**: Minimal, only for status (🚨, ✅, 📋)
- **Consistent hierarchy**: Logical progression
- **Dividers**: Use `---` sparingly between major sections

## Content Structure Standards

### Kanban Boards:
```markdown
## Backlog
- [ ] **Task Name** - Brief description #priority

## Ready
- [ ] **Task Name** - Brief description #priority

## In Progress  
- [ ] **Task Name** - Brief description #priority

## Done
- [x] **Task Name** - Brief description #priority
```

### Progress References:
- **Status consistency**: Use same progress % across related files
- **Date stamps**: Update modified date when progress changes
- **Cross-references**: Ensure related files reference each other

## File Organisation
- **Consistent naming**: kebab-case for files
- **Template adherence**: Use established patterns per document type
- **Navigation links**: Include essential navigation in each file

## Session State Documentation Guidelines

### Essential Drafting Practices
- **Context Window Optimization:** Include only critical information, avoid duplication
- **Strategic Summary:** Focus on key decisions and next steps over detailed explanations
- **Specific Technical Terms:** Include IP ranges, model numbers, version numbers where relevant
- **Prioritize Actionable Content:** Emphasize next steps and critical context
- **Maintain Efficiency:** Keep sessions under typical context window limits

### Session-Specific YAML Requirements
```yaml
tags: [session-state, concise, descriptive-tag]
type: session-state
status: complete
progress_percent: [number]
session_duration: [minutes]
session_success_rating: [1-5]
prev_session: "[[link-to-previous]]"
next_session: "[[link-to-next]]" # if known
```

### Backlink Management for Sessions
- **Session Chain:** Maintain clear navigation between related sessions
- **Strategic Links:** Focus on most important connections, not exhaustive linking
- **Archive Awareness:** Use proper paths for archived sessions

## Implementation Priority:
1. Fix duplicate/broken YAML frontmatter
2. Standardise link formats and fix broken references  
3. Ensure bidirectional linking
4. Consolidate formatting inconsistencies
5. Update cross-references and navigation