# Event Sourcing in Python

This repository contains the source code inspired by the blog post series [Implementing Event Sourcing in Python](https://breadcrumbscollector.tech/categories/event-sourcing//) with updates for 2024.

## Parts

1. Branch for [part 1](https://breadcrumbscollector.tech/implementing-event-sourcing-in-python-part-1-aggregates/) is [here](https://github.com/dclimber/Implementing-Event-Sourcing-in-Python/tree/part-1)
2. Branch for [part 2](https://breadcrumbscollector.tech/implementing-event-sourcing-in-python-part-2-robust-event-store-atop-postgresql/) is [here](https://github.com/dclimber/Implementing-Event-Sourcing-in-Python/tree/part2)

## Getting Started

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/) for dependency management

### Setup

To set up the project, run:

```bash
make setup
```

This will install all dependencies in a virtual environment managed by Poetry.

### Running Tests

To run the tests with code coverage, execute:

```bash
make test
```

This will run all the unit, integration, and acceptance tests using `pytest` and generate a code coverage report.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
