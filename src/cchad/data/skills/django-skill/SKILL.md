---
name: django-conventions
description: Django patterns. Use when building or reviewing Django apps.
---

# Django conventions

## Structure
- Split the project into focused apps; keep each app's models, views, and urls together.
- Keep views thin. Put business logic in model methods, managers, or a services module.
- Read settings from the environment (django-environ or `os.environ`); never commit
  secrets. Keep `DEBUG = False` outside local dev.

## ORM
- Avoid N+1 queries: use `select_related` (FK) and `prefetch_related` (M2M/reverse).
- Push filtering into the database with querysets; don't loop in Python over full tables.
- Add custom `Manager`/`QuerySet` methods for reusable queries.
- Always create and review migrations; never edit the database by hand.

## APIs & safety
- Use Django REST Framework serializers for API input/output and validation.
- Rely on the ORM and the template auto-escaping to avoid SQL injection and XSS.
- Enforce permissions in one place, not scattered per view.
