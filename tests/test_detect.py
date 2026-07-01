from __future__ import annotations

from cchad.detect import detect_stack


def test_detects_js_frameworks(make_repo):
    repo = make_repo(**{"package.json": {"dependencies": {"react": "^18", "vite": "^5"}}})
    stack = detect_stack(repo)
    assert {"javascript", "react", "vite"} <= stack.signals


def test_detects_typescript_from_dev_and_tsconfig(make_repo):
    repo = make_repo(
        **{
            "package.json": {"devDependencies": {"typescript": "^5"}},
            "tsconfig.json": "{}",
        }
    )
    assert "typescript" in detect_stack(repo).languages


def test_detects_scoped_remotion(make_repo):
    repo = make_repo(**{"package.json": {"dependencies": {"@remotion/cli": "^4"}}})
    assert "remotion" in detect_stack(repo).frameworks


def test_detects_python_from_pyproject(make_repo):
    repo = make_repo(
        **{"pyproject.toml": '[project]\nname="x"\ndependencies=["fastapi","motor","asyncpg"]\n'}
    )
    stack = detect_stack(repo)
    assert {"python", "fastapi", "mongodb", "postgres"} <= stack.signals


def test_detects_python_from_requirements(make_repo):
    repo = make_repo(**{"requirements.txt": "Flask==3.0\npsycopg2-binary>=2.9\n# comment\n"})
    stack = detect_stack(repo)
    assert {"python", "flask", "postgres"} <= stack.signals


def test_detects_go_modules(make_repo):
    repo = make_repo(
        **{"go.mod": "module x\n\ngo 1.22\n\nrequire github.com/gin-gonic/gin v1.9.1\n"}
    )
    stack = detect_stack(repo)
    assert {"go", "gin"} <= stack.signals


def test_malformed_package_json_does_not_crash(make_repo):
    repo = make_repo(**{"package.json": "{ this is not json"})
    # Still recognizes it as a JS project without raising.
    assert "javascript" in detect_stack(repo).languages


def test_ignores_vendor_directories(make_repo):
    repo = make_repo(**{"node_modules/pkg/index.rs": "fn main() {}"})
    # A .rs file buried in node_modules must not register rust.
    assert "rust" not in detect_stack(repo).languages


def test_empty_directory_is_empty(make_repo):
    repo = make_repo()
    assert detect_stack(repo).signals == set()


def test_missing_directory_is_empty(tmp_path):
    assert detect_stack(tmp_path / "does-not-exist").signals == set()
