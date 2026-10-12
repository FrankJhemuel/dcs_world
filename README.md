# dcs_world

A Python library for modeling and managing robots, their environments, and related systems.

> **Note:** This project is currently under active development. Its structure and APIs may change.

## Setup

### Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)

### Installation

Clone the repository:

```bash
git clone https://github.com/FrankJhemuel/dcs_world
cd dcs_world
```

Create the virtual environment and install the project dependencies:

```bash
uv sync
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Alternatively, run Python commands directly through `uv` without activating the environment:

```bash
uv run python
```

### Development

To add a dependency:

```bash
uv add <package>
```

To run tests:

```bash
uv run pytest
```

To build the package:

```bash
uv build
```

## Project Structure

The library is organized into modules, each responsible for a different part of the system.

- **Geometry:** Geometric data structures, such as positions and poses.
- **Robot:** Robot representations, configurations, statuses, and related utilities.
- **Infrastructure:** Infrastructure components and supporting elements of the environment.
- **System:** System-level components and abstractions.
- **World:** Representations and management of the environment in which robots operate.

The architecture is still evolving as the library develops.

## Project Configuration

- `pyproject.toml` — Package metadata, dependencies, and build configuration.
- `uv.lock` — Records resolved dependency versions for reproducible environments.
- `.python-version` — Specifies the Python version used by the project.
- `py.typed` — Marks the package as providing type information for static type checkers.