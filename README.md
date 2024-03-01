# govtech-csg-xcg-modelpermissions

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/8499/badge)](https://www.bestpractices.dev/projects/8499)

This package belongs to the **eXtended Code Guardrails (XCG)** project, which consists of a series of packages that harden the Django web framework to prevent common web application vulnerabilities.

Specifically, this package provides functionality to enforce permissions checks on users when they attempt to perform actions on a Django `Model` object (e.g. if a request accesses a view that tries to read a set of objects from the database).

By default, `modelpermissions` checks for permissions at the object level - i.e. the user must have the appropriate permissions for every single model object that they are trying to access/modify. This allows access control to be enforced at the level of single database records.

However, `modelpermissions` can also be configured to check for permissions at the model level, which means the user must have the appropriate permissions over the entire class of objects This approach is more coarse-grained, but having both options provides developers with the flexibility to determine the granularity of their applications's access control model.

*Do note that the README in this repository is intentionally limited in scope and is catered towards developers. For detailed instructions on installation, usage, and community guidelines, please refer to the published documentation at https://xcg.tech.gov.sg.*

## Security-related matters

For instructions on how to **report a vulnerability**, refer to the [official documentation website](https://xcg.tech.gov.sg/community/vulnerabilities).

Additionally, **enable email alerts for security issues by "watching" this repository**. The "watch" button can be found near the top right corner of this repo's home page, and there are various options for configuring notification volume. To receive security alerts, either enable notifications for **"All Activity"** or **"Custom -> Security alerts"**.

## Installing development dependencies

Before building or testing the package, or committing changes, install the development dependencies into a virtual environment:

```sh
# In the project root directory
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Building

The package can be built using [`build`](https://pypa-build.readthedocs.io/en/latest/) as the build frontend and [`setuptools`](https://setuptools.pypa.io/en/latest/) as the build backend.

Run the build command below:

```sh
# In the project root directory
python -m build .
```

This creates a directory named `dist/`, which should contain 2 files:

1. A `.whl` (wheel) file, which is a [binary distribution format](https://packaging.python.org/en/latest/specifications/binary-distribution-format/) for Python packages
2. A `.tar.gz` file, which is a [source distribution format](https://packaging.python.org/en/latest/specifications/source-distribution-format/) for Python packages

To view the source files included in the source distribution, use the `tar` utility as follows:

```sh
tar --list -f dist/<filename>.tar.gz
```

To install the package directly from either distribution files:

```sh
pip install <name_of_distribution_file>
```

## Testing

As the tests for this package use multiple variants of the Django settings module, a [convenience script](./tests/run_all_tests.sh) has been provided for ease of running all test methods. Execute the tests using the commands below:

```sh
pip install -e . # Performs an "editable install" of the govtech-csg-xcg-modelpermissions package
cd tests
/bin/bash run_all_tests.sh
```

## Running pre-commit hooks

*Note: This section is only relevant if you intend to contribute code*

This project uses the [`pre-commit` tool](https://pre-commit.com) to run Git pre-commit hooks for linting and code quality checks. The `pre-commit` tool itself should have been installed along with the [development dependencies](#installing-development-dependencies). After cloning the repository **for the first time**, run the command below to "install" the Git hooks:

```sh
pre-commit install
```

The command above creates a file `.git/hooks/pre-commit`, which defines the shell commands to run before any Git commit is created.

Subsequently, any invocation of `git commit` will trigger the commands, rejecting the commit if there are linting errors. Issues should be automatically fixed, but you will need to re-stage the changes before attempting the commit again.

For a list of hooks run by `pre-commit`, see its [configuration file](.pre-commit-config.yaml).
