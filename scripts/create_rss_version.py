#!/usr/bin/env python3

import sys
import os
import yaml
from datetime import datetime

def read_yaml_frontmatter(file_path):
    """Read YAML frontmatter from a Quarto markdown file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split on first and second '---' to get frontmatter
    parts = content.split('---', 2)
    if len(parts) >= 2:
        try:
            return yaml.safe_load(parts[1])
        except yaml.YAMLError as e:
            print(f"Error parsing YAML frontmatter: {e}")
            sys.exit(1)
    return None

def create_rss_version(date_str):
    """Create RSS version of a seminar file given its date."""
    # Convert date to expected format
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format")
        sys.exit(1)
    
    # Construct file paths
    source_file = f"seminars/{date.strftime('%Y-%m-%d')}.qmd"
    target_dir = "seminars-rss"
    target_file = f"{target_dir}/{date.strftime('%Y-%m-%d')}.qmd"
    
    # Check if source file exists
    if not os.path.exists(source_file):
        print(f"Error: Source file {source_file} not found")
        sys.exit(1)
    
    # Create target directory if it doesn't exist
    os.makedirs(target_dir, exist_ok=True)
    
    # Read frontmatter from source file
    frontmatter = read_yaml_frontmatter(source_file)
    if not frontmatter:
        print("Error: Could not read frontmatter from source file")
        sys.exit(1)
    
    # Create simplified frontmatter for RSS version
    rss_frontmatter = {
        'title': frontmatter.get('title', ''),
        'speaker': frontmatter.get('speaker', ''),
        'affiliation': frontmatter.get('affiliation', ''),
        'date': frontmatter.get('date', ''),
        'published': frontmatter.get('published', ''),
        'date-format': frontmatter.get('date-format', ''),
        'abstract': frontmatter.get('abstract', '')
    }
    
    # Write RSS version
    with open(target_file, 'w') as f:
        f.write('---\n')
        yaml.dump(rss_frontmatter, f, allow_unicode=True, sort_keys=False)
        f.write('---\n\n')
        f.write('{{< meta abstract >}}\n')
    
    print(f"Created RSS version at {target_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_rss_version.py YYYY-MM-DD")
        sys.exit(1)
    
    create_rss_version(sys.argv[1])
