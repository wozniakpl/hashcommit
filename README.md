# hashcommit

A tool to generate a Git commit with a specific hash part.

## Installation

You can install the package using pip:

```sh
pip install hashcommit
```

## Usage

### Creating a New Commit

To create a new commit with a specific hash part:

```sh
hashcommit --hash <desired_hash_part> --message "<commit_message>"
```

### Overwriting the Last Commit

To overwrite the last commit with a specific hash part:

```sh
hashcommit --hash <desired_hash_part> --message "<commit_message>" --overwrite
```

### Match Type

You can also specify if the hash must begin with, contain, or end with the desired string using the `--match-type` option. The default is to match the beginning of the hash:

```sh
hashcommit --hash <desired_hash_part> --message "<commit_message>" --match-type <begin|contain|end>
```

### Example Usage

To find and use a specific commit hash:

```sh
hashcommit --hash fff --match-type contain --message "foobar" ; git log -1 | cat
```

Example output:

```
Found matching commit hash: 93fffe4756192c250a7234c7c5fd81752c747091
commit 93fffe4756192c250a7234c7c5fd81752c747091
Author: Your Name <your-email@domain.com>
Date:   Thu May 23 17:06:24 2024 +0000

    foobar
```

### Author Preservation

By default, the author is not preserved and gets overwritten when overwriting a commit. This feature will be implemented in the future.

### Overwriting Commits in the Past

Overwriting a particular commit in the past will be implemented in the future.

## Development

To develop or contribute to this project, clone the repository and install the dependencies:

```sh
git clone https://github.com/wozniakpl/hashcommit.git
cd hashcommit
pip install -e .
```

### Running Locally

You can run tests locally using tox or act:

```sh
# Using tox
tox

# Using act
act
```

You can use the following command for simplicity of development. It formats the code, runs the checks, and the tests on one Python version:

```sh
tox -e format && tox -e checks && tox -e py311 --
```

To set up an environment with `hashcommit` installed and a git repository initialized in the `/repo` directory, use Docker Compose:

```sh
docker compose run --rm tests bash
```

## License

This project is licensed under the MIT License.
