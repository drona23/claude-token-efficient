# Known Patterns

## Anti-patterns to avoid
- Writing code before reading existing files
- Hardcoding absolute paths
- Not testing before declaring done
- Re-reading files unnecessarily
- Over-engineering simple solutions

## Good patterns
- Read first, then write
- Test after every significant change
- Use relative paths
- Keep solutions minimal
- Handle edge cases in data (nulls, empty strings, type mismatches)

## WebSocket patterns
- Track clients manually with a Set - do not rely on pub/sub channels for broadcast
- Send confirmation to sender first, then broadcast to others
- Use setTimeout(0) to give test listeners time to register before broadcast fires
