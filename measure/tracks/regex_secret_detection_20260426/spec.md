# Regex-Based Secret Detection

## Problem
SecretsMasker uses simple substring match instead of regex, potentially missing secrets with varying formats.

## Solution
Upgrade SecretsMasker from substring to regex pattern matching for more robust secret detection.

## Acceptance Criteria
- [ ] Regex patterns for common secret formats (API keys, tokens, passwords)
- [ ] All existing substring matches still detected
- [ ] New regex patterns catch additional secret formats
- [ ] Performance impact negligible
