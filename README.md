# hashcommit

A tool to generate a Git commit with a specific hash part.

## Prerequisites

Ensure you have Git installed on your system.

## Installation

You can install the package using pip:

```sh
pip install hashcommit
```

## Demo

This repository's history was rewritten using the `rewrite_the_history.sh` script and each new commit is added by using the `hashcommit` command. You can check the result [here](https://github.com/wozniakpl/hashcommit/commits/main/).

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

By default, the author is preserved when overwriting. To overwrite the author, use the `--no-preserve-author` option:

```sh
hashcommit --hash <desired_hash_part> --overwrite --no-preserve-author
```

### Overwriting Commits in the Past

You can overwrite the existing commit that has other commits on top of it. To do this, use the `--commit` option:

```sh
hashcommit --hash <desired_hash_part> --overwrite --commit <commit_hash>
```

### Rewriting the History

You can rewrite the history of the current branch using the `rewrite_the_history.sh` script. This script will recreate the commit history, ensuring that each commit's hash conforms to a sequence specified by the `-d` argument, which sets the number of digits for the sequence number.

For example, to rewrite the history with a two-digit sequence number at the beginning:

```sh
./scripts/rewrite_the_history.sh -d 2
```

Note: The default value for `-d` is 3. As the number of commits increases, consider adjusting the digit value accordingly to balance performance and the required hash length.

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
tox -e format && tox -e checks && tox -e py312 --
```

To run tox tests under docker (not using your git):

```sh
docker compose up
```

To set up an environment with `hashcommit` installed and a git repository initialized in the `/repo` directory, use Docker Compose:

```sh
docker compose run --rm --workdir /repo test bash
```

## License

This project is licensed under the MIT License.
