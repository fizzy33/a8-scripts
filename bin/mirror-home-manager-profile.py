#!/usr/bin/env python3


from pathlib import Path
import sys
from typing import Optional
import os

docs = f"""
This script will mirror the home manager profile on the dev user into the root user.  The need for this script
is because you cannot use home manager on the root user (it changes the default profile and creates chaos),
"""


nix_path = Path("/nix")

class PathService:
    def makeDirectoriesIfNeeded(self, p: Path) -> None:
        if not p.exists():
            p.mkdir(parents = True)
    def unlinkIfExists(self, p: Path) -> None:
        if p.is_symlink():
            p.unlink()
    def symlink(self, target: Path, link: Path) -> None:
        print(f"creating symlink target={target}  link={link}")
        if not target.is_relative_to(nix_path):
            raise Exception(f"{target} is not relative to /nix/ will not do this since it is a security risk")
        link.symlink_to(target)

class DryRunPathService:
    def makeDirectoriesIfNeeded(self, p: Path) -> None:
        if not p.exists():
            print(f"mkdirs {p}")
    def unlinkIfExists(self, p: Path) -> None:
        if p.is_symlink():
            print(f"unlink {p}")
    def symlink(self, target: Path, link: Path) -> None:
        print(f"create symlink target={target}  link={link}")

def logWarning(msg: str) -> None:
    print("WARNING !! " + msg)

def homeManagerProfileInNixStore(sourceHome: Path) -> Path:
    source = Path(sourceHome, ".profile") 
    p = source.readlink().parent
    if p.name.endswith("home-manager-files"):
        return p
    raise Exception(f"{source} is not managed by home manager")


def entries(d: Path) -> [Path]:
    return map(lambda p: Path(d, p), os.listdir(d))

def run(args) -> None:

    overwrite = args.force
    dry_run = args.dry_run
    homeManagerRoot = homeManagerProfileInNixStore(args.source)
    sourceHome = args.source
    targetHome = args.target

    pathService = PathService()
    if dry_run:
        pathService = DryRunPathService()

    def createSymlink(target: Path, link: Path) -> None:
        link_exists = link.exists()
        pathService.makeDirectoriesIfNeeded(link.parent)
        link_is_already_correct = False
        if link_exists:
            link_contents = link.readlink()
            if link_contents == target:
                print(f"no action needed link is correct {link}")
                link_is_already_correct = True

        if overwrite or not link_exists:
            pathService.unlinkIfExists(link)
            if not target.exists():
                logWarning(f"target path does not exist @ {target}")
            else:
                if not link_is_already_correct:
                    pathService.symlink(target, link)
        else:
            if not link_is_already_correct:
                print(f"leaving {link} in place")

    def walkHomeManagerProfile(d: Path) -> None:
        # print(f"walking {d}")
        for ch in entries(d):
            if ch.is_symlink():
                target = ch
                link = Path(targetHome, ch.relative_to(homeManagerRoot))
                createSymlink(target, link)
            elif ch.is_dir:
                walkHomeManagerProfile(ch)
            else:
                logWarning(f"there should only be symlink's and directories in the home manager profile -- {ch}")

    walkHomeManagerProfile(homeManagerRoot)

    pathService.symlink(Path(sourceHome, ".nix-profile").resolve(), Path(targetHome, ".nix-profile"))




def main() -> None:

    import argparse
    parser = argparse.ArgumentParser(
        prog = 'mirror-home-manager-profile',
        description = docs,
    )
    parser.add_argument("--force", "-f", action='store_true', help='force the link creation i.e. overwrite existing links', default=False)
    parser.add_argument("--source", "-s", help='home directory to source', required=True)
    parser.add_argument("--target", "-t", help='home directory to target', required=True)

    subparsers = parser.add_subparsers(dest="command", help='sub-commands')

    runParser = subparsers.add_parser("run", help='do the actual work and change the system')

    dryRunParser = subparsers.add_parser("dryrun", help='show the actual work that would be done (default)')

    subparsers.add_parser("help", help='print this help')

    args = parser.parse_args()

    if args.command == "run":
        args.dry_run = False
        run(args)
    elif args.command == "dryrun" or args.command is None:
        args.dry_run = True
        run(args)
    elif args.command == "help":
        parser.print_help()
    else:
        badargs = " ".join(sys.argv[1:])
        print(f"don't know how to handle command of {args.command} in {badargs}")
        parser.print_help()


if __name__ == '__main__':
    main()

