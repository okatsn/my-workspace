#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def main():
    # 0. Validate credentials
    client_id = os.environ.get("GDRIVE_CLIENT_ID")
    client_secret = os.environ.get("GDRIVE_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ Error: GDRIVE_CLIENT_ID or GDRIVE_CLIENT_SECRET environment variables are missing.")
        sys.exit(1)

    print("🔍 Scanning for DVC workspaces...")
    # Find all .dvc directories starting from the current working directory
    dvc_dirs = list(Path(".").rglob(".dvc"))

    if not dvc_dirs:
        print("⚠️ No DVC repositories found.")
        sys.exit(0)

    summary = []

    # Iterate through each discovered project
    for dvc_dir in dvc_dirs:
        project_root = dvc_dir.parent
        project_name = project_root.name if project_root.name else str(project_root)

        try:
            # Get list of remotes for this specific project
            res = subprocess.run(
                ["dvc", "-C", str(project_root), "remote", "list"],
                capture_output=True, text=True, check=True
            )

            # Filter out gdrive remotes
            gdrive_remotes = []
            for line in res.stdout.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].startswith("gdrive://"):
                        gdrive_remotes.append(parts[0])

            if not gdrive_remotes:
                summary.append((project_name, "⚪ Skipped (No gdrive remotes)"))
                continue

            # Configure each found gdrive remote
            for remote in gdrive_remotes:
                subprocess.run([
                    "dvc", "-C", str(project_root), "remote", "modify", "--local",
                    remote, "gdrive_client_id", client_id
                ], check=True, capture_output=True)

                subprocess.run([
                    "dvc", "-C", str(project_root), "remote", "modify", "--local",
                    remote, "gdrive_client_secret", client_secret
                ], check=True, capture_output=True)

            summary.append((project_name, f"✅ Configured ({', '.join(gdrive_remotes)})"))

        except subprocess.CalledProcessError as e:
            summary.append((project_name, f"❌ Failed (DVC CLI Error)"))
        except Exception as e:
            summary.append((project_name, f"❌ Failed ({type(e).__name__})"))

    # 4. Print Summary Output
    print("\n📊 Configuration Execution Summary:")
    print("-" * 50)
    for project, status in summary:
        print(f"{project:<25} -> {status}")
    print("-" * 50)

if __name__ == "__main__":
    main()