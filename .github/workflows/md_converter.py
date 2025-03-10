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
        # Skip files in node_modules, .git directories and the docs branch
        if "node_modules" in path or ".git" in path or path.startswith("docs/"):
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
                print(f"  Warning: Referenced image not found: {full_path}")
                # Try to find the image in the current directory
                base_name = os.path.basename(img_path)
                alt_path = os.path.join(md_dir, base_name)
                if os.path.exists(alt_path):
                    print(f"  Found image in current directory instead: {alt_path}")
                    images.append((alt_path, f"images/{base_name}"))
        else:
            # Check if image is in the same directory
            direct_path = os.path.join(md_dir, img_path)
            if os.path.exists(direct_path):
                print(f"  Found image (same dir): {img_path} at {direct_path}")
                images.append((direct_path, f"images/{os.path.basename(img_path)}"))
            else:
                print(f"  Warning: Image not found: {direct_path}")

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
                print(f"  Warning: Referenced HTML image not found: {full_path}")
                # Try to find the image in the current directory
                base_name = os.path.basename(img_path)
                alt_path = os.path.join(md_dir, base_name)
                if os.path.exists(alt_path):
                    print(
                        f"  Found HTML image in current directory instead: {alt_path}"
                    )
                    images.append((alt_path, f"images/{base_name}"))
        else:
            # Check if image is in the same directory
            direct_path = os.path.join(md_dir, img_path)
            if os.path.exists(direct_path):
                print(f"  Found image (HTML, same dir): {img_path} at {direct_path}")
                images.append((direct_path, f"images/{os.path.basename(img_path)}"))
            else:
                print(f"  Warning: HTML image not found: {direct_path}")

    # Also check for any images in the markdown directory that might not be referenced
    print(f"  Looking for any images in {md_dir}")
    for img_ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]:
        for img_file in glob.glob(os.path.join(md_dir, f"*{img_ext}")):
            if os.path.isfile(img_file):
                img_name = os.path.basename(img_file)
                img_rel_path = f"images/{img_name}"
                if not any(src == img_file for src, _ in images):
                    print(f"  Found additional image in directory: {img_file}")
                    images.append((img_file, img_rel_path))

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

    # Read markdown content
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
    except Exception as e:
        print(f"  Error reading markdown file: {e}")
        return None

    # Extract images before conversion
    images = find_images_in_markdown(md_file)
    print(f"  Found {len(images)} images in {md_file}")

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

        # Escape backticks and other special chars in content to prevent JS injection
        md_content_escaped = md_content.replace("`", "\\`").replace("$", "\\$")

        # Write content to temporary file to avoid command line length limitations
        temp_md_file = os.path.join(os.path.dirname(html_path), "_temp_md_content.md")
        with open(temp_md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        # Use file-based approach to avoid command line issues
        temp_js_file = os.path.join(os.path.dirname(html_path), "_temp_convert.js")
        js_content = (
            '''
            const fs = require('fs');
            const converter = require("'''
            + converter_path.replace("\\", "\\\\")
            + '''");
            
            // Read markdown content
            const mdContent = fs.readFileSync("'''
            + temp_md_file.replace("\\", "\\\\")
            + '''", "utf8");
            
            // Convert to HTML
            converter.convert(mdContent, "'''
            + title.replace('"', '\\"')
            + """")
                .then(html => {
                    process.stdout.write(html);
                })
                .catch(err => {
                    console.error("Error:", err);
                    process.exit(1);
                });
            """
        )
        with open(temp_js_file, "w", encoding="utf-8") as f:
            f.write(js_content)

        # Run the conversion script
        html_content = subprocess.check_output(["node", temp_js_file], text=True)

        # Clean up temporary files
        try:
            os.remove(temp_md_file)
            os.remove(temp_js_file)
        except:
            pass

        # Fix image paths in HTML
        soup = BeautifulSoup(html_content, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if not src.startswith(("http://", "https://", "data:", "images/")):
                # If image is not in images/ directory or external, update path
                img["src"] = f"images/{os.path.basename(src)}"
                print(
                    f"  Updated image path in HTML: {src} -> images/{os.path.basename(src)}"
                )

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
                    try:
                        shutil.copy2(src_path, target_path)
                        print(f"  Copied image: {src_path} to {target_path}")
                    except Exception as e:
                        print(f"  Error copying image: {e}")
                else:
                    print(f"  Image not found at the time of copying: {src_path}")
        else:
            # Create empty images directory anyway
            images_dir = os.path.join(os.path.dirname(html_path), "images")
            os.makedirs(images_dir, exist_ok=True)
            print(f"  Created empty images directory: {images_dir}")
            # Create a placeholder file to ensure the directory is preserved
            with open(os.path.join(images_dir, ".placeholder"), "w") as f:
                f.write("# This file ensures the images directory is preserved")

        return html_path
    except subprocess.CalledProcessError as e:
        print(f"  Error converting markdown: {e}")
        if e.output:
            print(f"  Node output: {e.output}")
        return None
    except Exception as e:
        print(f"  Unexpected error: {e}")
        return None


def copy_to_docs_branch():
    """Copy HTML files and images to the docs branch."""
    print("\nPreparing to switch to docs branch...")

    # Print current working directory and git status for debugging
    print(f"Current working directory: {os.getcwd()}")

    # First, verify output directory exists and has content
    if not os.path.exists(OUTPUT_DIR):
        print(f"ERROR: Output directory {OUTPUT_DIR} does not exist!")
        return False

    # Check content of output directory
    print("Content of output directory:")
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            print(f"  {os.path.join(root, file)}")

    # Save current branch name
    current_branch = subprocess.check_output(
        ["git", "branch", "--show-current"], text=True
    ).strip()
    print(f"Current branch: {current_branch}")

    # Check if docs branch exists
    result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", "docs"],
        capture_output=True,
        text=True,
    )

    docs_exists = "docs" in result.stdout

    # Before switching branches, save the output directory to a temporary location outside the git repo
    temp_output = "/tmp/md_converter_output"
    if os.path.exists(temp_output):
        shutil.rmtree(temp_output)
    shutil.copytree(OUTPUT_DIR, temp_output)
    print(f"Copied output to {temp_output}")

    # Switch to or create docs branch
    if docs_exists:
        print("docs branch exists, checking out")
        subprocess.run(["git", "fetch", "origin", "docs"], check=True)
        subprocess.run(["git", "checkout", "docs"], check=True)
    else:
        print("docs branch doesn't exist, creating it")
        subprocess.run(["git", "checkout", "--orphan", "docs"], check=True)
        # Clean the working directory
        subprocess.run(["git", "rm", "-rf", "."], check=True)
        # Create initial README
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

    # Copy files from temporary location
    print("Copying generated files to docs branch...")
    for root, dirs, files in os.walk(temp_output):
        # Create relative path
        rel_path = os.path.relpath(root, temp_output)
        if rel_path == ".":
            rel_path = ""

        # Create target directory
        target_dir = os.path.join(".", rel_path)
        os.makedirs(target_dir, exist_ok=True)

        # Copy files
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, file)
            shutil.copy2(src_file, dst_file)
            print(f"Copied: {dst_file}")

    # Force create empty directories by adding .gitkeep
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "images":
                gitkeep_path = os.path.join(root, dir_name, ".gitkeep")
                with open(gitkeep_path, "w") as f:
                    f.write("")
                print(f"Created .gitkeep in {os.path.join(root, dir_name)}")

    # Display final structure
    print("\nFinal structure in docs branch:")
    for root, dirs, files in os.walk("."):
        if ".git" in root:
            continue
        level = root.count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root) or '.'}/")
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

    return True


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

    # Add all files including directories
    subprocess.run(["git", "add", "-A"], check=True)

    # Check if there are changes to commit
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    if result.stdout.strip():
        print("Changes detected, committing...")
        print(f"Git status: {result.stdout}")

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
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Files in current directory: {os.listdir('.')}")

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

    # Check output directory
    if success_count == 0:
        print("No HTML files were generated, aborting.")
        return 1

    print(f"Content of {OUTPUT_DIR} directory:")
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            print(f"  {os.path.join(root, file)}")

    # Switch to docs branch and copy files
    try:
        if copy_to_docs_branch():
            success = commit_and_push_docs()
            if success:
                print("\nWorkflow completed successfully!")
                return 0
            else:
                print("\nFailed to commit or push changes!")
                return 1
        else:
            print("\nFailed to copy files to docs branch!")
            return 1
    except Exception as e:
        print(f"Error in docs branch operations: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

