# pytest-shell-script-test-harness

<https://github.com/MarximusMaximus/pytest-shell-script-test-harness>

by Marximus Maximus (<https://marximus.com>)

A pytest plugin for testing shell scripts. Provides a framework for writing tests
for shell scripts as well as tracks coverage.

**NOTE: Currently in Alpha phase.**

## Features

- Use pytest to run tests for shell scripts.
- Provides additional functions for use in shell script tests.
- Tracks coverage for shell script code and shell script tests.
- Works with most other pytest plugins*

## Usage

1. Install `pytest-shell-script-test-harness` via your favorite method, e.g.:
    - `pip install pytest-shell-script-test-harness`
    - `poetry add --group dev pytest-shell-script-test-harness`
2. Write the python and shell script portions of your tests.
3. Run pytest as you would normally.

### Additional Info

\* Tested against with the following as login shells and non-login shells, in every possible pairing:

- bash
- dash
- zsh

\* Tested with the following plugins so far:

- cov
- forked
- html
- metadata
- [prefer-nested-dup-tests](https://github.com/MarximusMaximus/pytest-prefer-nested-dup-tests)
- sugar
- typeguard
- xdist

## Bug Reports / Feature Requests

Please submit bug reports and feature requests to:
<https://github.com/MarximusMaximus/pytest-shell-script-test-harness/issues>

## Development & Contribution

Pull Requests will be reviewed at:
<https://github.com/MarximusMaximus/pytest-shell-script-test-harness/pulls>

## Like My Work & Want To Support It?

- Main Website: <https://marximus.com>
- Patreon (On Going Support): <https://www.patreon.com/marximus>
- Ko-fi (One Time Tip): <https://ko-fi.com/marximusmaximus>
