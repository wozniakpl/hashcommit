import subprocess
import hashlib
import time
import argparse

def get_commit_hash(commit_content):
    """Compute the Git commit hash from the commit content."""
    commit_data = f"commit {len(commit_content)}\0{commit_content}".encode('utf-8')
    return hashlib.sha1(commit_data).hexdigest()

def create_commit_content(message, timestamp, tree_hash, parent_hash, author, committer):
    """Create the commit content with the specified message and timestamp."""
    commit_content = f"tree {tree_hash}\n"
    if parent_hash:
        commit_content += f"parent {parent_hash}\n"
    commit_content += f"{author}\n"
    commit_content += f"{committer}\n\n"
    commit_content += f"{message}\n"
    commit_content += f"{timestamp}\n"
    return commit_content

def get_tree_hash():
    """Get the current tree hash."""
    return subprocess.check_output(["git", "write-tree"]).decode().strip()

def get_parent_hash():
    """Get the current HEAD hash."""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_author_info(timestamp):
    """Get author and committer information from Git config."""
    try:
        name = subprocess.check_output(["git", "config", "user.name"]).decode().strip()
    except subprocess.CalledProcessError:
        name = "hashcommit"  # A default name if not found
    email = subprocess.check_output(["git", "config", "user.email"]).decode().strip()
    return f"author {name} <{email}> {timestamp} +0000", f"committer {name} <{email}> {timestamp} +0000"

def write_commit(commit_content):
    """Write the commit content to the Git repository and update HEAD."""
    commit_hash = subprocess.check_output(["git", "hash-object", "-t", "commit", "--stdin", "-w"], input=commit_content.encode('utf-8')).decode().strip()
    subprocess.check_call(["git", "update-ref", "HEAD", commit_hash])
    return commit_hash

def hash_matches(commit_hash, desired_hash, match_type):
    """Check if the commit hash matches the desired hash according to the match type."""
    if match_type == "begin":
        return commit_hash.startswith(desired_hash)
    elif match_type == "contain":
        return desired_hash in commit_hash
    elif match_type == "end":
        return commit_hash.endswith(desired_hash)
    else:
        raise ValueError("Invalid match type. Choose from 'begin', 'contain', 'end'.")

def initial_commit_if_needed(overwrite):
    """Create an initial commit if needed."""
    if not overwrite and get_parent_hash() is None:
        subprocess.check_call(["git", "commit", "--allow-empty", "-m", "Initial commit"])

def find_matching_commit(desired_hash, commit_message, match_type, overwrite):
    """Find a commit hash matching the desired criteria."""
    timestamp = int(time.time())
    author_info, committer_info = get_author_info(timestamp)

    while True:
        tree_hash = get_tree_hash()
        parent_hash = get_parent_hash() if not overwrite else None
        commit_content = create_commit_content(commit_message, timestamp, tree_hash, parent_hash, author_info, committer_info)
        commit_hash = get_commit_hash(commit_content)
        
        if hash_matches(commit_hash, desired_hash, match_type):
            actual_commit_hash = write_commit(commit_content)
            print(f"Found matching commit hash: {actual_commit_hash}")
            break
        
        timestamp += 1

def main():
    parser = argparse.ArgumentParser(description="Generate a Git commit with a specific hash prefix.")
    parser.add_argument("--hash", required=True, help="Desired hash string.")
    parser.add_argument("--message", required=True, help="Commit message.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the current commit (default is to not overwrite the current commit).")
    parser.add_argument("--match-type", choices=["begin", "contain", "end"], default="begin", help="Match type: 'begin' (default), 'contain', 'end'.")
    args = parser.parse_args()

    try:
        initial_commit_if_needed(args.overwrite)
        find_matching_commit(args.hash, args.message, args.match_type, args.overwrite)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")

if __name__ == "__main__":
    main()
