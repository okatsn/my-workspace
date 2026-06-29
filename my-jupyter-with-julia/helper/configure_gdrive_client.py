#!/usr/bin/env python3
# # TO USE:
# python configure_gdrive_client.py $GDRIVE_CLIENT_ID $GDRIVE_CLIENT_SECRET ./
# python configure_gdrive_client.py -r $GDRIVE_CLIENT_ID $GDRIVE_CLIENT_SECRET ./projects
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    # 1. Set up the CLI interface
    parser = argparse.ArgumentParser(
        description="Configure DVC Google Drive remotes with custom OAuth credentials.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively scan for all .dvc repositories inside the target directory.",
    )
    parser.add_argument("client_id", help="Google OAuth Client ID string")
    parser.add_argument("client_secret", help="Google OAuth Client Secret string")
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target workspace or root directory to scan.",
    )

    args = parser.parse_args()

    # 2. Fail-Fast: Environment & Input Validation
    if not shutil.which("dvc"):
        print(
            "❌ Error: DVC CLI is not installed or not found in PATH.", file=sys.stderr
        )
        sys.exit(1)

    if not args.client_id.strip() or not args.client_secret.strip():
        print("❌ Error: Client ID and Client Secret cannot be empty.", file=sys.stderr)
        sys.exit(1)

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(f"❌ Error: Target path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # 3. Discover DVC Workspaces based on chosen mode
    if args.recursive:
        print(f"🔍 Recursively scanning for DVC workspaces under: {target_path}")
        dvc_dirs = list(target_path.rglob(".dvc"))
        if not dvc_dirs:
            print("⚠️ No DVC repositories found under the specified path.")
            sys.exit(0)
    else:
        print(f"🔍 Checking single target workspace at: {target_path}")
        single_dvc = target_path / ".dvc"
        if not single_dvc.is_dir():
            print(
                f"❌ Error: '{target_path}' is not a valid DVC workspace (missing .dvc directory).",
                file=sys.stderr,
            )
            sys.exit(1)
        dvc_dirs = [single_dvc]

    summary = []

    # 4. Iterate through discovered projects
    for dvc_dir in dvc_dirs:
        project_root = dvc_dir.parent
        # Make the display path relative to execution path for a cleaner summary
        try:
            display_name = str(project_root.relative_to(Path.cwd()))
            if display_name == ".":
                display_name = project_root.name
        except ValueError:
            display_name = project_root.name

        try:
            # Query DVC remotes for this specific project
            res = subprocess.run(
                ["dvc", "--cd", str(project_root), "remote", "list"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Filter for Google Drive remotes
            gdrive_remotes = []
            for line in res.stdout.splitlines():
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].startswith("gdrive://"):
                        gdrive_remotes.append(parts[0])

            if not gdrive_remotes:
                summary.append((display_name, "⚪ Skipped (No gdrive remotes)"))
                continue

            # Update credentials for each discovered gdrive remote
            for remote in gdrive_remotes:
                subprocess.run(
                    [
                        "dvc",
                        "--cd",
                        str(project_root),
                        "remote",
                        "modify",
                        "--local",
                        remote,
                        "gdrive_client_id",
                        args.client_id,
                    ],
                    check=True,
                    capture_output=True,
                )

                subprocess.run(
                    [
                        "dvc",
                        "--cd",
                        str(project_root),
                        "remote",
                        "modify",
                        "--local",
                        remote,
                        "gdrive_client_secret",
                        args.client_secret,
                    ],
                    check=True,
                    capture_output=True,
                )

            summary.append(
                (display_name, f"✅ Configured ({', '.join(gdrive_remotes)})")
            )

        except subprocess.CalledProcessError:
            summary.append((display_name, "❌ Failed (DVC CLI Error)"))
        except Exception as e:
            summary.append((display_name, f"❌ Failed ({type(e).__name__})"))

    # 5. Print Execution Summary
    print("\n📊 Configuration Execution Summary:")
    print("-" * 65)
    for project, status in summary:
        print(f"{project:<35} -> {status}")
    print("-" * 65)


if __name__ == "__main__":
    main()
