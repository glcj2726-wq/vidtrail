"""Install an explicit skill link/copy without replacing existing skills."""
import argparse
from pathlib import Path
import shutil


def install(destination, copy=False):
    source = Path(__file__).resolve().parents[1] / ".agents/skills/coco-video-research-distill"
    target = Path(destination).expanduser().resolve() / source.name
    if target.exists() or target.is_symlink():
        if target.is_symlink() and target.resolve() == source:
            return target
        raise FileExistsError("Existing skill preserved; select a different skills directory.")
    target.parent.mkdir(parents=True, exist_ok=True)
    if copy:
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        target.symlink_to(source, target_is_directory=True)
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--project", type=Path)
    group.add_argument("--skills-dir", type=Path)
    parser.add_argument("--copy", action="store_true", help="Copy instead of symlink; updates require manual replacement.")
    args = parser.parse_args()
    try:
        print(install(args.skills_dir if args.skills_dir else args.project / ".agents/skills", args.copy))
    except (OSError, RuntimeError) as exc:
        parser.exit(1, f"Installation stopped: {exc}\n")
