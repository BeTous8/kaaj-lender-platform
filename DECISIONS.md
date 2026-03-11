# Architecture Decisions

## Why rules are stored as database rows

Lender credit policies change frequently — minimum FICO thresholds get adjusted, states get added to exclusion lists, hard stops get added or removed. If rules were hardcoded in Python, every change would require a code deployment. By storing each rule as a row (`field_name`, `operator`, `value`, `is_hard_stop`), the underwriting engine is fully data-driven: the evaluation logic never changes, only the data does. It also means the Policies page can let users edit rules live without touching code.

## Why `selectinload` instead of lazy loading

When evaluating an application against all lenders, the code must traverse three levels: lenders → programs → policy rules. SQLAlchemy's default lazy loading would fire a separate database query every time it accessed a relationship — one per lender to get programs, one per program to get rules. With five lenders and sixteen programs, that's over twenty queries for a single underwrite request (the N+1 problem). `selectinload` collapses this into three queries total regardless of how many lenders or programs exist, which keeps the underwrite response fast and the database load predictable.

## Why matching logic lives in a service, not the router

The router's job is HTTP: parse the request, call the right function, return a response. If the matching logic lived inside the router, it would be impossible to test without standing up an HTTP server, and it would be harder to reuse — for example, if a background job later needed to trigger underwriting without an HTTP call. Putting `run_matching()` in `services/matching.py` means it's a plain async function that takes an app ID and a database session and returns results. The router just calls it and shapes the output into JSON. Each layer does one thing.
