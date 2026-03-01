# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-03-01

### Added
- ✅ Complete Hashnode blog export functionality
- ✅ Export published posts and drafts (including unpublished)
- ✅ Export series/collection metadata
- ✅ Download and store images locally
- ✅ Output in Markdown and/or JSON formats
- ✅ Beautiful terminal UI with Rich
- ✅ Comprehensive error logging system
- ✅ 35 unit tests with full mock coverage

### Changed
- 🔄 Migrated from Click to Typer for modern CLI experience
- 🔄 Improved progress bars to show actual counts instead of estimates
- 🔄 Enhanced image URL extraction to handle markdown attributes

### Fixed
- 🐛 Fixed null slug handling in drafts (generates slugs from titles)
- 🐛 Fixed image URL extraction with markdown attributes (e.g., `align="left"`)
- 🐛 Fixed null content and coverImage handling
- 🐛 Fixed progress bar showing incorrect totals (80/105 → 80/80)
- 🐛 Fixed drafts not being exported due to GraphQL errors

### Technical Details

#### CLI Framework Migration (Click → Typer)
- Better type hints and IDE support
- Cleaner decorator syntax with `Annotated`
- Beautiful auto-generated help pages
- Modern Python 3.12+ features

#### Error Logging System
- Automatic error tracking for failed operations
- Human-readable log file (`export_errors.log`)
- Machine-readable JSON format (`export_errors.json`)
- Error count in export summary
- No crashes - export continues on errors

#### Progress Bar Improvements
- Indeterminate progress during downloads
- Accurate final counts based on successful operations
- No more misleading estimates

#### Image Handling
- Smart URL cleaning (removes markdown attributes)
- Proper handling of 403, 404, and timeout errors
- Duplicate image detection (downloads once, reuses)
- Comprehensive error logging

#### Drafts Support
- Client-side slug generation for drafts without slugs
- Handles null content and coverImage gracefully
- All 22 drafts exported successfully

### Dependencies
- `typer>=0.12.0` (replaced `click`)
- `requests>=2.31.0`
- `python-dotenv>=1.0.0`
- `rich>=13.7.0`
- `httpx>=0.27.0`
- `pillow>=10.2.0`

### Testing
- 35 unit tests passing
- Mock fixtures for all API calls
- Edge case coverage (null values, missing fields, etc.)
- Test coverage for error logging

### Documentation
- Comprehensive README
- Usage examples
- Error logging documentation
- Troubleshooting guide
- Testing guide

## Future Enhancements (Planned)

- [ ] Pydantic v2 dataclasses for type safety
- [ ] Async image downloads for better performance
- [ ] Resume capability for interrupted exports
- [ ] Export filtering by date range
- [ ] Export filtering by tags
- [ ] Custom markdown templates
- [ ] Progress persistence across runs
