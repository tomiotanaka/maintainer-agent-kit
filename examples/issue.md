# Issue: Crash when importing large JSON file

## Summary

The app crashes when importing a JSON file larger than 50 MB.

## Environment

- Version: 1.4.2
- OS: macOS 15
- Reproducible: yes

## Steps

1. Open the app.
2. Import a 75 MB JSON export.
3. Wait for parsing to finish.

## Expected

The import either completes or shows a clear validation error.

## Actual

The process exits without writing an error log.

