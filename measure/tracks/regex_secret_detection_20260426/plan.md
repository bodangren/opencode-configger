# Regex-Based Secret Detection — Implementation Plan

## Phase 1: Pattern Design [ ]
- [ ] Research common secret formats (API keys, JWTs, passwords)
- [ ] Design regex patterns for each format
- [ ] Test patterns against sample configs

## Phase 2: Implementation [ ]
- [ ] Replace substring matching with regex in SecretsMasker
- [ ] Add configuration for custom secret patterns
- [ ] Update tests for new detection logic

## Phase 3: Validation [ ]
- [ ] Test with real config files containing secrets
- [ ] Verify no false positives on non-secret values
- [ ] Benchmark performance impact
