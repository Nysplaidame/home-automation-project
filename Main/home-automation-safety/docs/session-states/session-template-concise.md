---
title: "Session Template - Concise Format"
description: "Concise template for efficient Claude session documentation"
tags:
  - template
  - session-state
  - concise
  - documentation
aliases:
  - "Concise Template"
  - "Short Session Template"
created: 2025-09-16
modified: 2025-09-17
type: template
project_context: "[[Main/home-automation-safety/README|Home Automation Project]]"
usage_instructions: "Copy and modify for concise session documentation"
---

# Session: [Title] - YYYY-MM-DD

## Current State
- **Phase:** [Project Phase] ([%] complete)
- **System Focus:** [Current system/area being worked on]
- **Repository:** [Git URL if applicable]
- **Branch:** [Current branch]
- **Status:** [Brief current status and readiness level]

## Key Decisions & Rationale
- **[Decision Name]:** [Problem] → [Solution] → [Why this approach]
- **[Decision Name]:** [Problem] → [Solution] → [Why this approach]
- **[Decision Name]:** [Problem] → [Solution] → [Why this approach]

## Session Accomplishments
- [x] [Completed goal with brief context of why it mattered]
- [x] [Completed goal with brief context of why it mattered]
- [ ] [Any incomplete goals and why they weren't finished]

## Technical State
- **Working Systems:** [What's operational and reliable]
- **Active Issues:** [Current blockers with severity level]
- **Immediate Dependencies:** [What must happen next and in what order]
- **Risk Factors:** [Potential failure points or concerns]

## Context for Next Session
- **Priority 1:** [Most critical next step]
- **Priority 2:** [Secondary next step]
- **Priority 3:** [Third priority]
- **Files to load:** [Essential files for context loading]
- **Context needed:** [Specific technical details or decisions to remember]

## Essential Resources
- **Architecture:** [Link to key architecture decisions]
- **Configuration:** [Links to critical config files or procedures]
- **External Resources:** [Important external links or references]
- **Previous session:** [Link to previous session state]

## Critical Context (Cannot Lose)
**System Architecture:**
[Essential technical details that would be catastrophic to lose]

**Safety/Security Considerations:**
[Critical safety or security information]

**Implementation Details:**
[Key technical specifications, IP ranges, configurations, etc.]

**Business Logic:**
[Project-specific rules, constraints, or requirements]

## Implementation Progress Tracking
- **Completed Phases:** [What major milestones are done]
- **Current Phase:** [Where we are now]
- **Next Phase:** [What comes after current work]
- **Blocked/Waiting:** [What's waiting on external factors]

## Cross-Reference Network
**Sub-Projects:** [Links to related prompts/projects with priority indicators]
**Related Decisions:** [Links to architecture decisions that impact current work]
**Session Chain:** [Links to related previous sessions]

## Quality Metrics
- **Documentation Status:** [How well documented is the current state]
- **Test Coverage:** [What has been validated/tested]
- **Technical Debt:** [Known shortcuts or temporary solutions]

---
**Duration:** [X]min | **Success:** [X]/5 | **Confidence:** [X]/5 | **Ready for:** [Next phase/milestone]
**Session Navigation:** [[previous]] ← → [[next]]

## ⚠️ **ESSENTIAL DRAFTING GUIDELINES**
**CRITICAL:** Follow these practices for every concise session:

### Context Window Optimization
- **Minimize Impact:** Always strive to minimize impact on context window
- **Essential Only:** Include only the most critical information for future sessions
- **Avoid Duplication:** Check previous sessions to prevent redundant content
- **Concise Format:** Use bullet points and brief descriptions for efficiency
- **Strategic Summary:** Focus on key decisions and next steps rather than detailed explanations

### Backlink Management
- **Identify Opportunities:** Actively identify potential backlink opportunities
- **Create Missing Links:** Create new backlinks where they add navigation value
- **Update Existing:** Update and maintain existing backlinks for accuracy
- **Strategic Links:** Focus on the most important connections, not exhaustive linking
- **Session Chain:** Maintain clear navigation between related sessions

### Obsidian Best Practices
- **Valid YAML:** Ensure all notes have properly formatted YAML frontmatter
- **Consistent Tags:** Use established tagging system consistently
- **Proper Aliases:** Add meaningful aliases for different reference styles
- **Wiki-Links:** Use `[[wiki-style]]` linking with descriptive display names
- **Metadata Standards:** Include all required metadata fields (created, modified, type, etc.)
- **Concise Structure:** Maintain the established concise template format for consistency

## Template Usage Notes
- Use specific technical terms over generic descriptions
- Include exact IP ranges, model numbers, version numbers where relevant
- Prioritize information that would take significant time to rediscover
- Link extensively to maintain context relationships
- Update progress percentages realistically
- Note any assumptions made during the session
- **Focus on uniqueness:** Avoid repeating information from previous sessions
- **Prioritize actionable content:** Emphasize next steps and critical context
- **Maintain efficiency:** Keep total session length under typical context window limits