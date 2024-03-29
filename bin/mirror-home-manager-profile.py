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
            print(f"removing symlink {p}")
            p.unlink()
        elif p.is_file():
            print(f"removing file {p}")
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
        link_file_exists = link.exists()
        pathService.makeDirectoriesIfNeeded(link.parent)
        link_is_already_correct = False
        if link_file_exists:
            if link.is_symlink():
                link_contents = link.readlink()
                if link_contents == target:
                    link_is_already_correct = True

        if link_is_already_correct:
            print(f"no action needed link is correct {link}")
        elif overwrite or not link_file_exists:
            pathService.unlinkIfExists(link)
            if not target.exists():
                logWarning(f"target path does not exist @ {target}")
            else:
                if not link_is_already_correct:
                    pathService.symlink(target, link)
        else:
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

    createSymlink(Path(sourceHome, ".nix-profile").resolve(), Path(targetHome, ".nix-profile"))




def main() -> None:

    import argparse
    parser = argparse.ArgumentParser(
        prog = 'mirror-home-manager-profile',
        description = docs,
    )
    subparsers = parser.add_subparsers(dest="command", help='sub-commands')
    def subparser(name: str, help: str):
        subParser = subparsers.add_parser(name, help=help)
        subParser.add_argument("--force", "-f", action='store_true', help='force the link creation i.e. overwrite existing links', default=False)
        subParser.add_argument("--source", "-s", help='home directory to source', required=True)
        subParser.add_argument("--target", "-t", help='home directory to target', required=True)
        return subParser

    runParser = subparser("run", "do the actual work")
    dryRunParser = subparser("dryrun", 'show the actual work that would be done')

    subparsers.add_parser("help", help='print this help')

    args = parser.parse_args()

    if args.command == "run":
        args.dry_run = False
        run(args)
    elif args.command == "dryrun":
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

