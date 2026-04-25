# Implementation Plan: Live Config Validation with OpenCode

## Phase 1: Validation Service
- [ ] 1.1 Create ValidationService interface
- [ ] 1.2 Implement ModelValidator using opencode-cli
- [ ] 1.3 Add ProviderValidator with connectivity checks
- [ ] 1.4 Write unit tests for validation logic

## Phase 2: MCP Server Validation
- [ ] 2.1 Create McpValidator for server health checks
- [ ] 2.2 Implement timeout handling for slow servers
- [ ] 2.3 Add server capability verification
- [ ] 2.4 Write tests for MCP validation scenarios

## Phase 3: Validation UI
- [ ] 3.1 Create ValidationTab with status indicators
- [ ] 3.2 Add per-field validation badges (green/yellow/red)
- [ ] 3.3 Implement batch "Validate All" button
- [ ] 3.4 Write component tests for validation display

## Phase 4: Real-Time Validation
- [ ] 4.1 Add debounced validation on config changes
- [ ] 4.2 Implement validation result caching
- [ ] 4.3 Create validation status bar integration
- [ ] 4.4 Write integration tests for real-time flow

## Phase 5: Advanced Validation
- [ ] 5.1 Add custom validation rules engine
- [ ] 5.2 Implement validation presets for different environments
- [ ] 5.3 Create validation report export
- [ ] 5.4 Write end-to-end tests for full validation workflow