import json
import subprocess
import sys


def upgrade_all() -> None:
    # Get outdated packages in JSON format
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
        capture_output=True,
        text=True,
    )

    try:
        outdated = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse pip output.")
        print(result.stdout)
        return

    if not outdated:
        print("All packages are already up to date.")
        return

    print("Upgrading packages:")
    for pkg in outdated:
        name = pkg["name"]
        print(f"  → {name}")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", name])

    print("\nDone!")


if __name__ == "__main__":
    upgrade_all()
