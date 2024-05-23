# hashcommit

A tool to generate a Git commit with a specific hash prefix.

## Installation

You can install the package using pip:

```sh
pip install hashcommit
```

## Usage

By default, `hashcommit` will use the files that are staged (added using `git add`) to create a commit with a specific hash prefix. If no files are staged, it will create an empty commit.

To create a new commit with a specific hash prefix:

```sh
hashcommit --hash <desired_hash_part> --message "<commit_message>"
```

To overwrite the current commit with a specific hash prefix:

```sh
hashcommit --hash <desired_hash_part> --message "<commit_message>" --overwrite
```

You can also specify if the hash must begin with, contain, or end with the desired string using the `--match-type` option. The default is to match the beginning of the hash:

```sh
hashcommit --hash <desired_hash_part> --message "<commit_message>" --match-type <begin|contain|end>
```

## Development

To develop or contribute to this project, clone the repository and install the dependencies:

```sh
git clone https://github.com/wozniakpl/hashcommit.git
cd hashcommit
pip install -e .
```

## License

This project is licensed under the MIT License.
