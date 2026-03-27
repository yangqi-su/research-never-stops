---
name: analysis-project-bootstrap
description: Bootstrap a minimal agent-assisted analysis scaffold in a new or existing repository, preserving existing files and adding only the smallest useful planning and status structure.
compatibility: opencode
metadata:
  domain: general-analysis
  workflow: bootstrap
---

# Analysis Project Bootstrap

Use this skill when a repository needs a lightweight agent-assisted analysis scaffold.

## When to use

- a project has no `AGENTS.md`, `STATUS.md`, or planning template yet
- you want a small, generic scaffold before adding domain-specific skills
- you need to preserve an existing repository while making it easier for agents to reason about it

## Guidance

- inspect the repository first
- avoid replacing existing files wholesale
- add only the minimal planning and status structure
- defer domain-specific workflow modules until the project has been summarized

## Example prompts

- Bootstrap a minimal OCAF-style analysis scaffold in this repository.
- Add status tracking and a reusable plan template without changing the project's workflow scripts.
