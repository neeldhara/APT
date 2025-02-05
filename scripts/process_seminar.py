#!/usr/bin/env python3

import sys
import os
from datetime import datetime
import pytz
import yaml
import re

def ensure_url_format(url):
    """Ensure URL has proper http:// or https:// prefix"""
    if not url:
        return url
    
    # Remove any leading/trailing whitespace
    url = url.strip()
    
    # If URL already has a protocol, return as is
    if re.match(r'^https?://', url):
        return url
    
    # Add http:// if no protocol is present
    return f'http://{url}'

def process_seminar_file(date_str):
    # Parse the input date
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    
    # Get the current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    
    # Convert date_obj to datetime with IST timezone for comparison
    date_with_tz = ist.localize(date_obj)
    
    # Construct the file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    file_path = os.path.join(project_root, 'seminars', f'{date_str}.qmd')
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    
    # Read the file content
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Split into frontmatter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        print("Error: Invalid file format - missing YAML frontmatter")
        sys.exit(1)
    
    # Parse YAML frontmatter
    try:
        metadata = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        sys.exit(1)
    
    # Check if automation is needed (process if automation is not 'clean')
    if metadata.get('automation') == 'clean':
        print(f"File {file_path} is marked as clean, skipping replacements")
        return
    
    # Fix speaker website URL format if present
    speaker_website = metadata.get('speaker-website', '')
    if speaker_website:
        fixed_url = ensure_url_format(speaker_website)
        if fixed_url != speaker_website:
            # Update the URL in metadata
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('speaker-website:'):
                    lines[i] = f'speaker-website: "{fixed_url}"'
                    break
            content = '\n'.join(lines)
            print(f"Updated speaker website URL format: {speaker_website} -> {fixed_url}")
            speaker_website = fixed_url
    
    # Process bio
    bio = metadata.get('bio', '')
    bio_replacement = '{{< meta bio >}}' if bio else 'Will be added soon.'
    content = content.replace('REPLACE-META-BIO', bio_replacement)
    
    # Process recording URL
    recording_url = metadata.get('recording-url', '')
    if recording_url and not recording_url.strip().startswith('{{< video'):
        # Update the recording URL in the metadata
        lines = parts[1].split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('recording-url:'):
                clean_url = recording_url.strip().strip('"')
                lines[i] = 'recording-url: "{{< video ' + clean_url + ' >}}"'
                break
        parts[1] = '\n'.join(lines)
        content = '---\n'.join(parts)
    
    # Process recording placeholder
    recording_url = metadata.get('recording-url', '')
    recording_replacement = '{{< meta recording-url >}}' if recording_url else 'A recording will be shared here shortly.'
    content = content.replace('REPLACE-META-RECORDING', recording_replacement)
    
    # Process slides URL
    slides_url = metadata.get('slides-url', '')
    slides_replacement = '[{{< fa file-pdf >}} Slides]({{< meta slides-url >}}){.btn .btn-outline-primary .rounded-pill}' if slides_url else ''
    content = content.replace('REPLACE-META-SLIDES', slides_replacement)
    
    # Process speaker website with fixed URL
    website_replacement = '[{{< fa globe >}} Website]({{< meta speaker-website >}}){.btn .btn-outline-primary .rounded-pill}' if speaker_website else ''
    content = content.replace('REPLACE-SPEAKER-WEBSITE', website_replacement)
    
    # Update status based on date
    current_status = 'past' if date_with_tz.date() < current_time.date() else 'upcoming'
    if metadata.get('status') != current_status:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('status:'):
                lines[i] = f'status: "{current_status}"'
                break
        content = '\n'.join(lines)
    
    # Set automation back to clean
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('automation:'):
            lines[i] = 'automation: clean'
            break
    content = '\n'.join(lines)
    
    # Write back to file
    with open(file_path, 'w') as file:
        file.write(content)
    
    print(f"Successfully processed {file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_seminar.py YYYY-MM-DD")
        sys.exit(1)
    
    process_seminar_file(sys.argv[1])
