# Track: Live Config Validation with OpenCode

## Overview
Validate configuration against a running OpenCode instance to catch errors before they cause runtime failures.

## Problem Statement
Static schema validation catches structural errors but not semantic ones (e.g., invalid model names, unreachable providers). Live validation provides real-world feedback.

## Goals
1. Validate model names against available providers
2. Test provider connectivity and authentication
3. Verify MCP server availability
4. Check tool permissions against running instance

## Acceptance Criteria
- [ ] Model name validation against OpenCode's model list
- [ ] Provider connectivity test with timeout
- [ ] MCP server health check
- [ ] Real-time validation status indicators
- [ ] Batch validation for entire config

## Technical Notes
- Use OpenCode CLI for model listing (opencode-cli models)
- Implement async validation with progress indicators
- Cache validation results for 5 minutes
- Add validation tab to main navigation