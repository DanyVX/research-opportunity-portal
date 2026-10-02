# Build verification

Verified on October 2, 2026 using Python 3.12 and a temporary local MySQL 8.0.46 database.

- Full Python suite: 21 passed (19 validation/API checks and 2 real MySQL integration scenarios).
- After adding the very-long-ID guard, the 19 validation checks passed again.
- Real MySQL scenarios: three creates, complete list, single retrieval, update, unchanged update, close, persisted retrieval, delete, deleted-record GET/PUT/DELETE 404s, missing data 400, more than ten records and literal SQL-like input.
- JavaScript syntax check passed.
- Chromium browser checks passed: create via form, complete details, edit, close/reopen, delete, deleted-record 404, 12 records displayed, search and desktop/mobile layouts.
- Desktop and mobile screenshots were visually inspected; no page overflow was detected at a 390-pixel viewport.

The browser verification used temporary database records, not frontend hard-coded data. No test credentials or database contents are included.

Not completed here: installing/running on your personal Windows device, importing/running in the Postman desktop app, publishing a GitHub repository, and recording your demonstration video. The Postman collection is supplied; use it yourself for the required demonstration.
