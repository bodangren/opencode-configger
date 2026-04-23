# Implementation Plan: Config Templates & Presets

## Phase 1: Template Infrastructure
- [ ] 1.1 Create Template dataclass with metadata (name, description, tags, config)
- [ ] 1.2 Implement TemplateRepository for loading/saving templates
- [ ] 1.3 Create built-in template JSONC files (python_dev, fullstack, datascience, devops, minimal)
- [ ] 1.4 Write unit tests for template loading and validation

## Phase 2: Template Browser UI
- [ ] 2.1 Create TemplatesTab with search and filter
- [ ] 2.2 Build TemplateCard component with preview
- [ ] 2.3 Add template detail view with config diff
- [ ] 2.4 Write component tests for template browser

## Phase 3: Template Application
- [ ] 3.1 Implement template merge with existing config
- [ ] 3.2 Add merge strategy selector (replace/overlay/selective)
- [ ] 3.3 Create confirmation dialog before applying
- [ ] 3.4 Write integration tests for template application

## Phase 4: Custom Templates
- [ ] 4.1 Add "Save as Template" functionality
- [ ] 4.2 Implement template export (JSONC file)
- [ ] 4.3 Add template import from file
- [ ] 4.4 Write tests for custom template operations

## Phase 5: Polish & Documentation
- [ ] 5.1 Add template descriptions and usage tips
- [ ] 5.2 Create template preview with syntax highlighting
- [ ] 5.3 Add template versioning support
- [ ] 5.4 Write end-to-end tests for full template workflow