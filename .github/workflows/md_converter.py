#!/usr/bin/env python3

import os
import re
import sys
import glob
import shutil
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

# Output directory for HTML files
OUTPUT_DIR = "html_output"


def find_markdown_files():
    """Find all markdown files in the repository."""
    print("Finding markdown files...")
    md_files = []
    for path in glob.glob("**/*.md", recursive=True):
        # Skip files in node_modules and .git directories
        if "node_modules" in path or ".git" in path:
            continue
        md_files.append(path)

    print(f"Found {len(md_files)} markdown files")
    for file in md_files:
        print(f"  - {file}")
    return md_files


def find_images_in_markdown(md_file):
    """Extract image references from a markdown file."""
    images = []
    md_dir = os.path.dirname(md_file)

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find Markdown image syntax ![alt](path)
    for match in re.finditer(r"!\[.*?\]\((.*?)\)", content):
        img_path = match.group(1)
        # Skip external images
        if img_path.startswith(("http://", "https://", "data:")):
            continue

        # Normalize path
        if img_path.startswith("./"):
            img_path = img_path[2:]

        # Check if referenced from images dir or same dir
        if img_path.startswith("images/"):
            # Image referenced from images directory
            full_path = os.path.join(md_dir, img_path)
            if os.path.exists(full_path):
                print(f"  Found image: {img_path} at {full_path}")
                images.append((full_path, img_path))
        else:
            # Check if image is in the same directory
            direct_path = os.path.join(md_dir, img_path)
            if os.path.exists(direct_path):
                print(f"  Found image (same dir): {img_path} at {direct_path}")
                images.append((direct_path, f"images/{os.path.basename(img_path)}"))

    # Find HTML img tags <img src="path">
    for match in re.finditer(r'<img[^>]*src="([^"]*)"[^>]*>', content):
        img_path = match.group(1)
        # Skip external images
        if img_path.startswith(("http://", "https://", "data:")):
            continue

        # Normalize path
        if img_path.startswith("./"):
            img_path = img_path[2:]

        # Check if referenced from images dir or same dir
        if img_path.startswith("images/"):
            # Image referenced from images directory
            full_path = os.path.join(md_dir, img_path)
            if os.path.exists(full_path):
                print(f"  Found image (HTML): {img_path} at {full_path}")
                images.append((full_path, img_path))
        else:
            # Check if image is in the same directory
            direct_path = os.path.join(md_dir, img_path)
            if os.path.exists(direct_path):
                print(f"  Found image (HTML, same dir): {img_path} at {direct_path}")
                images.append((direct_path, f"images/{os.path.basename(img_path)}"))

    return images


def get_document_title(md_file, content):
    """Extract title from markdown content or filename."""
    # Try to get title from first heading
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if title_match:
        return title_match.group(1)

    # Fall back to filename
    return os.path.basename(md_file).replace(".md", "")


def convert_markdown_to_html(md_file):
    """Convert a markdown file to HTML using Node.js."""
    print(f"\nProcessing {md_file}...")

    # Extract images before conversion
    images = find_images_in_markdown(md_file)
    print(f"  Found {len(images)} images in {md_file}")

    # Read markdown content
    with open(md_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Get document title
    title = get_document_title(md_file, md_content)
    print(f"  Document title: {title}")

    # Determine output path
    rel_path = os.path.relpath(md_file, ".")
    html_path = os.path.join(OUTPUT_DIR, rel_path.replace(".md", ".html"))
    print(f"  Output path: {html_path}")

    # Create output directory
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    # Convert markdown to HTML using Node.js
    try:
        # Use the Node.js converter
        script_dir = os.path.dirname(os.path.abspath(__file__))
        converter_path = os.path.join(script_dir, "converter.js")

        # Escape backticks in content to prevent JS injection
        md_content_escaped = md_content.replace("`", "\\`")

        cmd = [
            "node",
            "-e",
            f'const converter = require("{converter_path}"); '
            f'converter.convert(`{md_content_escaped}`, "{title}").then(html => console.log(html));',
        ]
        html_content = subprocess.check_output(cmd, text=True)

        # Fix image paths in HTML
        soup = BeautifulSoup(html_content, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if not src.startswith(("http://", "https://", "data:", "images/")):
                # If image is not in images/ directory or external, update path
                img["src"] = f"images/{os.path.basename(src)}"

        html_content = str(soup)

        # Write HTML file
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  HTML file created: {html_path}")

        # Process images
        if images:
            # Create images directory
            images_dir = os.path.join(os.path.dirname(html_path), "images")
            os.makedirs(images_dir, exist_ok=True)
            print(f"  Created images directory: {images_dir}")

            # Copy images
            for src_path, target_rel_path in images:
                if os.path.exists(src_path):
                    target_path = os.path.join(
                        os.path.dirname(html_path), target_rel_path
                    )
                    # Ensure target directory exists
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    # Copy the image
                    shutil.copy2(src_path, target_path)
                    print(f"  Copied image: {src_path} to {target_path}")
                else:
                    print(f"  Image not found: {src_path}")

        return html_path
    except subprocess.CalledProcessError as e:
        print(f"Error converting markdown: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def copy_to_docs_branch():
    """Copy HTML files and images to the docs branch."""
    print("\nSwitching to docs branch...")

    # Check if docs branch exists
    result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", "docs"],
        capture_output=True,
        text=True,
    )

    if "docs" in result.stdout:
        print("docs branch exists, checking out")
        subprocess.run(["git", "fetch", "origin", "docs"], check=True)
        subprocess.run(["git", "checkout", "docs"], check=True)
    else:
        print("docs branch doesn't exist, creating it")
        subprocess.run(["git", "checkout", "--orphan", "docs"], check=True)
        subprocess.run(["git", "rm", "-rf", "."], check=True)
        with open("README.md", "w") as f:
            f.write("# Documentation\n")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial docs branch commit"], check=True
        )

    # Clean everything except .git
    for item in os.listdir("."):
        if item != ".git":
            path = os.path.join(".", item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    # Copy files from output directory
    print("Copying generated files to docs branch...")
    for root, dirs, files in os.walk(OUTPUT_DIR):
        # Create relative path
        rel_path = os.path.relpath(root, OUTPUT_DIR)
        if rel_path == ".":
            rel_path = ""

        # Create target directory
        target_dir = os.path.join(".", rel_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # Copy files
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            shutil.copy2(src_file, dst_file)

    # Display final structure
    print("\nFinal structure in docs branch:")
    for root, dirs, files in os.walk("."):
        if ".git" in root:
            continue
        level = root.count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        for file in files:
            print(f"{indent}  {file}")

    # Check for images
    print("\nChecking for images directories:")
    found = False
    for root, dirs, files in os.walk("."):
        if "images" in dirs:
            found = True
            images_dir = os.path.join(root, "images")
            print(f"Found images directory: {images_dir}")
            print("Contents:")
            for file in os.listdir(images_dir):
                print(f"  {file}")

    if not found:
        print("No images directories found!")


def commit_and_push_docs():
    """Commit changes and push to docs branch."""
    print("\nCommitting changes...")

    # Configure git
    subprocess.run(
        ["git", "config", "--global", "user.name", "GitHub Action"], check=True
    )
    subprocess.run(
        ["git", "config", "--global", "user.email", "action@github.com"], check=True
    )

    # Add all files
    subprocess.run(["git", "add", "."], check=True)

    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    if result.stdout.strip():
        print("Changes detected, committing...")
        # Get current branch name for commit message
        branch_name = os.environ.get("GITHUB_REF_NAME", "unknown")
        commit_msg = f"Convert Markdown to HTML from branch {branch_name}"

        # Commit changes
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)

        # Push to docs branch
        print("Pushing to docs branch...")
        token = os.environ.get("PERSONAL_ACCESS_TOKEN")
        if not token:
            print("ERROR: PERSONAL_ACCESS_TOKEN not found!")
            return False

        repo = os.environ.get("GITHUB_REPOSITORY")
        remote_url = f"https://x-access-token:{token}@github.com/{repo}"
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
        subprocess.run(["git", "push", "origin", "docs"], check=True)
        print("Successfully pushed to docs branch")
        return True
    else:
        print("No changes to commit")
        return True


def main():
    """Main function to convert markdown files to HTML and publish to docs branch."""
    print("Starting markdown to HTML conversion...")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Created output directory: {OUTPUT_DIR}")

    # Find markdown files
    md_files = find_markdown_files()
    if not md_files:
        print("No markdown files found.")
        return 1

    # Convert each markdown file
    success_count = 0
    for md_file in md_files:
        result = convert_markdown_to_html(md_file)
        if result:
            success_count += 1

    # Print summary
    print(f"\nConverted {success_count} of {len(md_files)} markdown files to HTML")

    # Switch to docs branch and copy files
    try:
        copy_to_docs_branch()
        success = commit_and_push_docs()
        if success:
            print("\nWorkflow completed successfully!")
            return 0
        else:
            print("\nFailed to commit or push changes!")
            return 1
    except Exception as e:
        print(f"Error in docs branch operations: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
