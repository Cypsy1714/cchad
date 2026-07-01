"""Lookup tables that turn dependencies and files into stack signals.

Each mapping value is a ``(descriptor_field, signal)`` pair, where
``descriptor_field`` is one of the sets on :class:`~cchad.models.StackDescriptor`.
These are intentionally data, so broadening detection is a one-line edit.
"""

from __future__ import annotations

Signal = tuple[str, str]

# Exact npm dependency name -> signal.
JS_DEPENDENCY_SIGNALS: dict[str, Signal] = {
    "react": ("frameworks", "react"),
    "react-dom": ("frameworks", "react"),
    "next": ("frameworks", "next"),
    "vue": ("frameworks", "vue"),
    "svelte": ("frameworks", "svelte"),
    "vite": ("frameworks", "vite"),
    "nuxt": ("frameworks", "nuxt"),
    "remotion": ("frameworks", "remotion"),
    "express": ("frameworks", "express"),
    "fastify": ("frameworks", "fastify"),
    "tailwindcss": ("frameworks", "tailwind"),
    "typescript": ("languages", "typescript"),
    "mongodb": ("databases", "mongodb"),
    "mongoose": ("databases", "mongodb"),
    "pg": ("databases", "postgres"),
    "postgres": ("databases", "postgres"),
    "mysql": ("databases", "mysql"),
    "mysql2": ("databases", "mysql"),
    "redis": ("databases", "redis"),
    "ioredis": ("databases", "redis"),
    "prisma": ("infra", "prisma"),
    "@prisma/client": ("infra", "prisma"),
    "jest": ("test_runners", "jest"),
    "vitest": ("test_runners", "vitest"),
    "mocha": ("test_runners", "mocha"),
    "cypress": ("test_runners", "cypress"),
    "@playwright/test": ("test_runners", "playwright"),
}

# Scoped-package prefix -> signal (matched when no exact hit is found).
JS_PREFIX_SIGNALS: dict[str, Signal] = {
    "@remotion/": ("frameworks", "remotion"),
    "@angular/": ("frameworks", "angular"),
    "@nestjs/": ("frameworks", "nestjs"),
    "@sveltejs/": ("frameworks", "svelte"),
}

# Normalized (lowercase, dash) Python distribution name -> signal.
PY_DEPENDENCY_SIGNALS: dict[str, Signal] = {
    "fastapi": ("frameworks", "fastapi"),
    "flask": ("frameworks", "flask"),
    "django": ("frameworks", "django"),
    "starlette": ("frameworks", "starlette"),
    "uvicorn": ("infra", "uvicorn"),
    "pymongo": ("databases", "mongodb"),
    "motor": ("databases", "mongodb"),
    "psycopg": ("databases", "postgres"),
    "psycopg2": ("databases", "postgres"),
    "psycopg2-binary": ("databases", "postgres"),
    "asyncpg": ("databases", "postgres"),
    "pymysql": ("databases", "mysql"),
    "redis": ("databases", "redis"),
    "sqlalchemy": ("infra", "sqlalchemy"),
    "pydantic": ("infra", "pydantic"),
    "celery": ("infra", "celery"),
    "pytest": ("test_runners", "pytest"),
}

# Go module path prefix -> signal.
GO_MODULE_SIGNALS: dict[str, Signal] = {
    "github.com/gin-gonic/gin": ("frameworks", "gin"),
    "github.com/labstack/echo": ("frameworks", "echo"),
    "github.com/gofiber/fiber": ("frameworks", "fiber"),
    "go.mongodb.org/mongo-driver": ("databases", "mongodb"),
    "github.com/lib/pq": ("databases", "postgres"),
    "github.com/jackc/pgx": ("databases", "postgres"),
}

# Presence of a config file -> signal.
CONFIG_FILE_SIGNALS: dict[str, Signal] = {
    "vite.config.js": ("frameworks", "vite"),
    "vite.config.ts": ("frameworks", "vite"),
    "next.config.js": ("frameworks", "next"),
    "next.config.mjs": ("frameworks", "next"),
    "next.config.ts": ("frameworks", "next"),
    "nuxt.config.ts": ("frameworks", "nuxt"),
    "svelte.config.js": ("frameworks", "svelte"),
    "tailwind.config.js": ("frameworks", "tailwind"),
    "tailwind.config.ts": ("frameworks", "tailwind"),
    "remotion.config.ts": ("frameworks", "remotion"),
    "tsconfig.json": ("languages", "typescript"),
    "Dockerfile": ("infra", "docker"),
    "docker-compose.yml": ("infra", "docker"),
    "docker-compose.yaml": ("infra", "docker"),
    "pytest.ini": ("test_runners", "pytest"),
}

# File extension -> language signal.
EXTENSION_LANGUAGES: dict[str, Signal] = {
    ".ts": ("languages", "typescript"),
    ".tsx": ("languages", "typescript"),
    ".js": ("languages", "javascript"),
    ".jsx": ("languages", "javascript"),
    ".mjs": ("languages", "javascript"),
    ".py": ("languages", "python"),
    ".go": ("languages", "go"),
    ".rs": ("languages", "rust"),
    ".rb": ("languages", "ruby"),
    ".java": ("languages", "java"),
}

# Directories never worth walking for the extension histogram.
IGNORE_DIRS: frozenset[str] = frozenset(
    {
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        "__pycache__",
        ".next",
        ".nuxt",
        ".turbo",
        ".svelte-kit",
        "coverage",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "target",
        "vendor",
        ".idea",
        ".vscode",
    }
)
