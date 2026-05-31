# Pull Request Review Context

## Summary

This pull request changes timeout handling in the authentication refresh path.

## Patch notes

- Adds a retry loop around token refresh.
- Changes timeout from 5 seconds to 30 seconds.
- Updates one integration test.

## Maintainer concerns

- Could mask provider outages.
- Might block CLI shutdown.
- Needs a clear changelog note if user-visible.

