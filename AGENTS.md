# AGENTS.md
Chatty is a peer-to-peer chat application with a PySide6 (Qt) GUI.

This project uses `uv` for dependency management and virtual environments. The venv lives at `.venv`.

- Install dependencies: `uv sync`
- Run the app: `uv run chatty`
- Add a dependency: `uv add <package>`
- Python version is pinned to `>=3.14,<3.15` (PySide6 constraint)

## Project structure
The package uses a `src/` layout with hatchling as the build backend.

## Documentation
Place future documentation in the docs/ directory.
Update the index here, by telling the name of the file and brief description.

## Git commits
Follow conventional commits.
