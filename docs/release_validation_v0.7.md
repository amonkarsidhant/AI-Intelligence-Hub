# DailyDex v0.7.0-rc1 Release Validation

Manual checklist for validating the DailyDex release candidate.

## Pre-Check

- [ ] Verify VERSION file contains `0.7.0-rc1`
- [ ] Verify README badge shows `v0.7.0-rc1`
- [ ] Verify no active user-facing references to AI Intelligence Hub

## Manual UI Validation

### Basic Load
- [ ] 1. Open http://localhost:8888
- [ ] 2. Confirm browser title says DailyDex
- [ ] 3. Confirm sidebar logo says DailyDex
- [ ] 4. Confirm Overview loads first

### Navigation
- [ ] 5. Confirm sidebar navigation works
- [ ] 6. Confirm top search is visible

### Theme
- [ ] 7. Toggle light/dark theme

### Data Operations
- [ ] 8. Click Refresh Now
- [ ] 9. Confirm source health updates
- [ ] 10. Save one item
- [ ] 11. Confirm toast appears

### Saved Board
- [ ] 12. Open Saved board
- [ ] 13. Change saved item status
- [ ] 14. Add notes/tags
- [ ] 15. Remove saved item

### Digest
- [ ] 16. Open Daily Digest
- [ ] 17. Generate/copy digest

### View Modes
- [ ] 18. Switch card/table views in GitHub
- [ ] 19. Switch card/table views in Models
- [ ] 20. Switch card/table views in Research

### Trends
- [ ] 21. Open Trends page
- [ ] 22. Confirm charts render or degrade gracefully

### Responsive
- [ ] 23. Resize browser to tablet width
- [ ] 24. Resize browser to mobile width
- [ ] 25. Confirm no horizontal overflow

### Documentation
- [ ] 26. Confirm README screenshots still match the actual UI
- [ ] 27. Confirm Docker image name and container name use dailydex

## Release Fields

| Field | Value |
|-------|-------|
| Date | |
| Browser | |
| Tester | |
| Result | |
| Notes | |

## Validation Notes

- All items should pass for a clean release
- Any failures should be documented in Notes with severity
- Charts may degrade gracefully on mobile (no crash)
- Toast notifications confirm save/ignore operations
