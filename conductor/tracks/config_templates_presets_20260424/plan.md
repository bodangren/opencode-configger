# Implementation Plan: Config Templates & Presets

## Phase 1: Template Infrastructure
- [x] 1.1 Create Template dataclass with metadata (name, description, tags, config)
- [x] 1.2 Implement TemplateRepository for loading/saving templates
- [x] 1.3 Create built-in template JSONC files (python_dev, fullstack, datascience, devops, minimal)
- [x] 1.4 Write unit tests for template loading and validation

## Phase 2: Template Browser UI
- [x] 2.1 Create TemplatesTab with search and filter
- [x] 2.2 Build TemplateCard component with preview
- [x] 2.3 Add template detail view with config diff
- [x] 2.4 Write component tests for template browser

## Phase 3: Template Application
- [x] 3.1 Implement template merge with existing config
- [x] 3.2 Add merge strategy selector (replace/overlay/selective)
- [x] 3.3 Create confirmation dialog before applying
- [x] 3.4 Write integration tests for template application

## Phase 4: Custom Templates
- [x] 4.1 Add "Save as Template" functionality
- [x] 4.2 Implement template export (JSONC file)
- [x] 4.3 Add template import from file
- [x] 4.4 Write tests for custom template operations

## Phase 5: Polish & Documentation
- [x] 5.1 Add template descriptions and usage tips
- [x] 5.2 Create template preview with syntax highlighting
- [x] 5.3 Add template versioning support
- [x] 5.4 Write end-to-end tests for full template workflow