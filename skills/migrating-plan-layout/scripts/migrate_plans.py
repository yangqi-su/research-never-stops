#!/usr/bin/env python3
"""Audit, apply, and verify stable plan paths using only the standard library."""

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import time


LAYOUTS = ("copilot/plans/active", "copilot/plans/archive",
           "plans/active", "plans/archive")
LEGACY_LAYOUT = "plans/legacy-by-family"
LEGACY_OVERVIEWS = {"README.md", "family-index.tsv"}
SOURCE_LAYOUTS = (*LAYOUTS, LEGACY_LAYOUT)
LAYOUT_PATTERN = "(?:" + "|".join(re.escape(layout) for layout in SOURCE_LAYOUTS) + ")"
SKIP = {".git", ".plan-migration", "node_modules", "__pycache__"}
LIMIT = 16 * 1024 * 1024
OLD_PATH = re.compile(LAYOUT_PATTERN + r"(?:/|\b)")
RELATIVE_CODE = re.compile(r"\.\./|\.parents\[|chdir\(|dirname\(")


def walk(root, excluded=()):
    """Yield files and links without following links or ignoring research outputs."""
    def fail(error):
        raise error

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=fail):
        base = Path(directory)
        for name in sorted(dirs + files):
            path = base / name
            if name not in SKIP and (path.is_symlink() or name in files):
                yield path
        dirs[:] = sorted(name for name in dirs if name not in SKIP
                         and not (base / name).is_symlink()
                         and base / name not in excluded)


def discover(parent):
    projects = set()
    links = []
    def fail(error):
        raise error

    for directory, dirs, files in os.walk(parent, followlinks=False, onerror=fail):
        base = Path(directory)
        if (base.name in {"active", "archive", "legacy-by-family"}
                and base.parent.name == "plans"
                and (base.name != "legacy-by-family" or base.parent.parent.name != "copilot")):
            project = base.parent.parent
            if project.name == "copilot":
                project = project.parent
            projects.add(str(project))
        links.extend(str(base / name) for name in dirs + files
                     if (base / name).is_symlink())
        dirs[:] = sorted(name for name in dirs if name not in SKIP
                         and not (base / name).is_symlink())
    return {"projects": sorted(projects), "symlinks_not_followed": sorted(links)}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def replacement(root, aliases, moves):
    destinations = {Path(move["old"]).name: move["new"] for move in moves}
    # Former lifecycle/family locations refer to the same stable plan. Route
    # document and run references separately, using the discovered inventory.
    if not destinations:
        return lambda text: text
    # These observed variable spellings denote the current project's root.
    # Arbitrary variables, other projects' absolute paths and ../ stay untouched.
    prefixes = [str(root) + "/", *(alias + "/" for alias in aliases), "./", "",
                "${REPO_ROOT}/", "$REPO_ROOT/", "${PROJECT_ROOT}/", "$PROJECT_ROOT/",
                "{repo_root}/"]
    # Match the common prefix first. Plan names are considered only after an
    # old-layout prefix, rather than trying thousands of full paths everywhere.
    # Explicit names preserve support for spaces and punctuation in filenames.
    pattern = re.compile(
        r"(?<![\w/.-])(?P<prefix>" + "|".join(re.escape(p) for p in sorted(set(prefixes), key=len, reverse=True))
        + r")(?P<layout>" + LAYOUT_PATTERN + r")/(?P<entry>"
        + "|".join(re.escape(name) for name in sorted(destinations, key=len, reverse=True))
        + r")(?=/|$|[\s\"'`),;:\]}])")

    # A bare container is ambiguous. Only rewrite the observed expressions
    # whose role explicitly identifies a run directory (not a plan document).
    r_run_dir = re.compile(
        r"(?m)^(?P<start>[ \t]*run_dir[ \t]*(?:<-|=)[ \t]*file\.path\("
        r"[ \t]*repo_root[ \t]*,[ \t]*)(?P<quote>[\"'])"
        + LAYOUT_PATTERN + r"(?P=quote)(?=[ \t]*,[ \t]*plan_id[ \t]*\))")
    template_run = re.compile(
        r"(?<![\w/.$-])(?P<prefix>\{repo_root\}/)" + LAYOUT_PATTERN
        + r"/\{plan_id\}(?=/|$|[\s\"'`),;:\]}])")

    def transform(text):
        if not any(layout in text for layout in SOURCE_LAYOUTS):
            return text
        text = pattern.sub(lambda match: match[0] if (match["layout"] == LEGACY_LAYOUT
                                                    and match["entry"] in LEGACY_OVERVIEWS)
                           else match["prefix"] + destinations[match["entry"]], text)
        text = r_run_dir.sub(lambda match: match["start"] + match["quote"]
                            + "copilot/plans/runs" + match["quote"], text)
        return template_run.sub(lambda match: match["prefix"] + "copilot/plans/runs/{plan_id}", text)

    return transform


def relocated(name, moves):
    for move in moves:
        if name == move["old"] or name.startswith(move["old"] + "/"):
            return move["new"] + name[len(move["old"]):]
    return name


def target_comparison(root, name, destination, target, moves):
    """Compare lexical targets; do not follow links or require outputs to exist."""
    before = os.path.normpath(root / name / target)
    after = os.path.normpath(root / destination / target)
    expected = before
    for move in moves:
        old = str(root / move["old"])
        if before == old or before.startswith(old + "/"):
            expected = str(root / move["new"]) + before[len(old):]
            break
    return {"before_target": before, "after_target": after,
            "expected_target": expected, "target_changed": after != expected}


def relative_path_review(root, name, text, moves):
    """Explain simple __file__ parent chains; leave cwd-dependent code for review."""
    destination = relocated(name, moves)
    if destination == name:
        return []
    items, explained_lines = [], set()
    if name.endswith(".md"):
        # Simple inline links and reference definitions. More complex Markdown
        # (escaped parentheses, HTML, or generated links) still needs review.
        links = re.compile(r"\]\(<?([^\s<>)]*)>?|^\s*\[[^\]]+\]:\s*<?([^\s<>]+)>?")
        for number, line in enumerate(text.splitlines(), 1):
            for match in links.finditer(line):
                target = (match.group(1) or match.group(2)).split("#", 1)[0].split("?", 1)[0]
                if not target or target.startswith("/") or re.match(r"[\w+.-]+:", target):
                    continue
                comparison = target_comparison(root, str(Path(name).parent),
                                               str(Path(destination).parent), target, moves)
                if comparison["target_changed"]:
                    items.append({"path": name, "line": number, "expression": target,
                                  "reason": "relative Markdown link changes target",
                                  "suggested_target": os.path.relpath(comparison["expected_target"],
                                                                      root / Path(destination).parent),
                                  **comparison})
    if name.endswith(".py"):
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return [{"path": name, "reason": "Python syntax could not be parsed; review relative paths manually"}]

        def parent_depth(node):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "Path" and len(node.args) == 1
                    and isinstance(node.args[0], ast.Name) and node.args[0].id == "__file__"
                    and not node.keywords):
                return 0
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in {"resolve", "absolute"}
                    and not node.args and not node.keywords):
                return parent_depth(node.func.value)
            if isinstance(node, ast.Attribute) and node.attr == "parent":
                depth = parent_depth(node.value)
                return None if depth is None else depth + 1
            if (isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute)
                    and node.value.attr == "parents" and isinstance(node.slice, ast.Constant)
                    and type(node.slice.value) is int and node.slice.value >= 0):
                depth = parent_depth(node.value.value)
                return None if depth is None else depth + node.slice.value + 1
            return None

        parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        for node in ast.walk(tree):
            depth = parent_depth(node)
            if not depth or parent_depth(parents.get(node)) is not None:
                continue
            comparison = target_comparison(root, name, destination, "/".join([".."] * depth), moves)
            explained_lines.update(range(node.lineno, node.end_lineno + 1))
            if comparison["target_changed"]:
                items.append({"path": name, "line": node.lineno,
                              "expression": ast.get_source_segment(text, node),
                              "reason": "file-relative parent calculation changes target",
                              **comparison})
    for number, line in enumerate(text.splitlines(), 1):
        # A parsed, unchanged __file__ chain needs no review. Other operations
        # on the same line (../, chdir, dirname) still need their working context.
        pattern = re.compile(r"\.\./|chdir\(|dirname\(") if number in explained_lines else RELATIVE_CODE
        if pattern.search(line):
            items.append({"path": name, "line": number, "expression": line.strip()[:500],
                          "reason": "relative paths/working-directory context needs review"})
    return items


def plan_inventory(root, legacy_status=None):
    """Inspect only immediate plan entries, destinations, and lifecycle statuses."""
    moves, statuses, blockers = [], {}, []
    destinations = set()
    plan_sources = {}
    for layout in SOURCE_LAYOUTS:
        source = root / layout
        if not os.path.lexists(source):
            continue
        if any(part.is_symlink() for part in [source, source.parent, source.parent.parent]):
            blockers.append(f"Linked plan container: {layout}")
            continue
        for item in sorted(source.iterdir()):
            # Family overview/index files stay in place; their references are scanned.
            if layout == LEGACY_LAYOUT and item.name in LEGACY_OVERVIEWS and item.is_file() and not item.is_symlink():
                continue
            if item.is_symlink() or not (item.is_dir() or item.suffix == ".md"):
                blockers.append(f"Unsupported plan entry: {item.relative_to(root)}")
                continue
            plan_id = item.name if item.is_dir() else item.stem
            if plan_id in {"active", "archive", "legacy-by-family", "", ".", ".."}:
                blockers.append(f"Reserved plan name: {plan_id}")
            if plan_id in plan_sources and plan_sources[plan_id] != layout:
                blockers.append(f"Plan ID collision: {plan_id}")
            plan_sources[plan_id] = layout
            container = "runs" if item.is_dir() else "docs"
            target = f"copilot/plans/{container}/{item.name}"
            if target in destinations or os.path.lexists(root / target):
                blockers.append(f"Destination exists or collides: {target}")
            destinations.add(target)
            moves.append({"old": str(item.relative_to(root)), "new": target})
            status = "active" if source.name == "active" else "finished"
            if layout == LEGACY_LAYOUT:
                if legacy_status is None:
                    blockers.append("Choose --legacy-status active or finished for plans/legacy-by-family")
                    continue
                status = legacy_status
            statuses[f"copilot/plans/runs/{plan_id}/PLAN_STATUS.md"] = f"Status: {status}\n"
            existing_status = source / plan_id / "PLAN_STATUS.md"
            if existing_status.parent.is_symlink() or existing_status.is_symlink():
                blockers.append(f"Linked status: {existing_status.relative_to(root)}")
            elif existing_status.exists() and existing_status.stat().st_nlink > 1:
                blockers.append(f"Hardlinked status: {existing_status.relative_to(root)}")
            elif existing_status.exists() and existing_status.read_text() != f"Status: {status}\n":
                blockers.append(f"Conflicting status: {existing_status.relative_to(root)}")
    for status_path in statuses:
        parent = root / Path(status_path).parent
        if parent.exists() and str(parent.relative_to(root)) not in destinations:
            blockers.append(f"Status directory already exists: {parent.relative_to(root)}")
    for part in [root / "copilot", root / "copilot/plans",
                 root / "copilot/plans/docs", root / "copilot/plans/runs"]:
        if part.is_symlink():
            blockers.append(f"Linked destination container: {part}")

    return moves, statuses, sorted(set(blockers))


def audit(root, aliases, progress=False, legacy_status=None):
    started = time.monotonic()
    if progress:
        print("Audit: inspecting plan inventory and discovering nested projects", file=sys.stderr, flush=True)
    moves, statuses, blockers = plan_inventory(root, legacy_status)
    review = []

    nested = [Path(p) for p in discover(root)["projects"] if Path(p) != root]
    review.extend({"path": str(p.relative_to(root)), "reason": "nested project excluded"}
                  for p in nested)
    transform = replacement(root, aliases, moves)
    edits, snapshot, socket_deletions = [], {}, []
    scanned_bytes = 0
    last_progress = time.monotonic()
    if progress:
        print(f"Audit: discovery finished in {last_progress - started:.1f}s; "
              f"{len(moves)} moves, {len(nested)} nested projects; scanning files",
              file=sys.stderr, flush=True)
    for count, path in enumerate(walk(root, nested), 1):
        now = time.monotonic()
        if progress and now - last_progress >= 60:
            print(f"Audit: {count} entries, {scanned_bytes / 2**30:.2f} GiB read, "
                  f"{now - started:.0f}s elapsed; current file: {path.relative_to(root)}",
                  file=sys.stderr, flush=True)
            last_progress = now
        name = str(path.relative_to(root))
        info = path.lstat()
        snapshot[name] = [info.st_size, info.st_mtime_ns, info.st_mode]
        if stat.S_ISLNK(info.st_mode):
            snapshot[name].append(os.readlink(path))
            target = os.readlink(path)
            comparison = target_comparison(root, str(Path(name).parent),
                                           str(Path(relocated(name, moves)).parent), target, moves)
            review.append({"path": name, "reason": "symlink", "target": target, **comparison})
            continue
        if stat.S_ISSOCK(info.st_mode) and relocated(name, moves) != name:
            socket_deletions.append({"path": name, "device": info.st_dev, "inode": info.st_ino})
            continue
        if not stat.S_ISREG(info.st_mode):
            blockers.append(f"Special file: {name}")
            continue
        if info.st_size > LIMIT:
            review.append({"path": name, "reason": "over 16 MiB; not scanned"})
            continue
        data = path.read_bytes()
        scanned_bytes += len(data)
        snapshot[name].append(digest(data))
        try:
            text = data.decode("utf-8") if b"\0" not in data else None
        except UnicodeDecodeError:
            text = None
        if text is None:
            review.append({"path": name, "reason": "binary/non-UTF-8; not scanned"})
            continue
        updated = transform(text)
        if updated != text:
            if info.st_nlink > 1:
                blockers.append(f"Rewriting would affect hardlinks: {name}")
            edits.append({"path": name, "destination": relocated(name, moves),
                           "before": snapshot[name][3], "after": digest(updated.encode("utf-8"))})
        reasons = []
        if OLD_PATH.search(updated):
            reasons.append("old-layout text remains after mapped replacements")
        review.extend(relative_path_review(root, name, updated, moves))
        if reasons:
            review.append({"path": name, "reason": "; ".join(reasons)})
    if progress:
        print(f"Audit: scan finished; {len(snapshot)} entries, {scanned_bytes / 2**30:.2f} GiB read, "
              f"{time.monotonic() - started:.1f}s elapsed; {len(edits)} edits, {len(blockers)} blockers, "
              f"{len(socket_deletions)} socket deletion candidates",
              file=sys.stderr, flush=True)
    return {"project": str(root), "aliases": aliases, "legacy_status": legacy_status, "moves": moves,
            "statuses": statuses, "edits": edits, "blockers": sorted(set(blockers)),
            "review": review, "snapshot": snapshot, "socket_deletions": socket_deletions}


def checked_rewrite(root, name, edit, transform):
    """Check the exact input and output approved by the saved audit before writing."""
    path = root / name
    if any(part.is_symlink() for part in [path, *path.parents] if part != root and root in part.parents):
        raise SystemExit(f"Linked rewrite path: {name}")
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise SystemExit(f"Rewrite requires a regular, unshared file: {name}")
    data = path.read_bytes()
    if digest(data) != edit["before"]:
        raise SystemExit(f"File changed since audit: {name}")
    updated = transform(data.decode("utf-8")).encode("utf-8")
    if digest(updated) != edit["after"]:
        raise SystemExit(f"Replacement differs from saved audit: {name}")
    return updated


def prepare_saved_audit(root, report, removed_empty, exclude_rewrites=()):
    """Reuse an audit with a narrow, explicit exception for deleted empty entries."""
    report = {**report, "blockers": list(report["blockers"]),
              "snapshot": dict(report["snapshot"]), "removed_empty_entries": {}}
    excluded = set(exclude_rewrites)
    unknown = excluded - {edit["path"] for edit in report["edits"]}
    if unknown:
        raise SystemExit("Excluded rewrite not in audit: " + ", ".join(sorted(unknown)))
    report["excluded_rewrites"] = [edit for edit in report["edits"] if edit["path"] in excluded]
    report["edits"] = [edit for edit in report["edits"] if edit["path"] not in excluded]
    report["review"] = report["review"] + [
        {"path": name, "reason": "rewrite explicitly excluded; content preserved without hash validation"}
        for name in sorted(excluded)]
    for name in removed_empty:
        original = report["snapshot"].get(name)
        blocker = f"Unsupported plan entry: {name}"
        if (blocker not in report["blockers"] or original is None
                or original[0] != 0 or not stat.S_ISREG(original[2])
                or len(original) != 4 or original[3] != digest(b"")
                or os.path.lexists(root / name)):
            raise SystemExit(f"Not an audited, now-removed empty blocked entry: {name}")
        report["blockers"].remove(blocker)
        report["removed_empty_entries"][name] = report["snapshot"].pop(name)
    if report["blockers"]:
        raise SystemExit("Unresolved audit blockers: " + "; ".join(report["blockers"]))
    moves, statuses, blockers = plan_inventory(root, report["legacy_status"])
    if blockers or moves != report["moves"] or statuses != report["statuses"]:
        raise SystemExit("Plan inventory changed since audit: " + "; ".join(blockers))
    transform = replacement(root, report["aliases"], report["moves"])
    last_progress = time.monotonic()
    print(f"Saved audit: checking {len(report['edits'])} rewrite files; no full-project scan",
          file=sys.stderr, flush=True)
    for index, edit in enumerate(report["edits"], 1):
        checked_rewrite(root, edit["path"], edit, transform)
        if time.monotonic() - last_progress >= 60:
            print(f"Saved audit: checked {index}/{len(report['edits'])} rewrite files",
                  file=sys.stderr, flush=True)
            last_progress = time.monotonic()
    report["validation_scope"] = "saved-audit-targeted"
    return report


def apply(root, report, delete_sockets=False, use_saved_audit=False, removed_empty=(), exclude_rewrites=()):
    if report["project"] != str(root):
        raise SystemExit("Audit belongs to another project.")
    if (removed_empty or exclude_rewrites) and not use_saved_audit:
        raise SystemExit("--acknowledge-removed-empty and --exclude-rewrite require --use-saved-audit.")
    if use_saved_audit:
        report = prepare_saved_audit(root, report, removed_empty, exclude_rewrites)
    else:
        if report["blockers"]:
            raise SystemExit("Resolve audit blockers and audit again before applying.")
        if audit(root, report["aliases"], legacy_status=report["legacy_status"]) != report:
            raise SystemExit("Project changed since audit. Review a fresh audit before applying.")
    if report["socket_deletions"] and not delete_sockets:
        raise SystemExit("Audited sockets require --delete-sockets after confirming their jobs are stopped.")
    if not report["moves"] and not report["edits"]:
        return {"result": "no changes"}
    backup = root / ".plan-migration/backup"
    backup.mkdir()  # Exclusive creation protects the previous recovery copy.
    (backup / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
    # Moves are recovered by reversing the audit's path map. Only rewritten
    # content needs a second copy; large unchanged run artifacts stay in place.
    sources = {edit["path"] for edit in report["edits"]}
    for destination, content in report["statuses"].items():
        name = destination
        for move in report["moves"]:
            if destination.startswith(move["new"] + "/"):
                name = move["old"] + destination[len(move["new"]):]
                break
        if name in report["snapshot"] and report["snapshot"][name][3] != digest(content.encode()):
            sources.add(name)
    for name in sorted(sources):
        source, target = root / name, backup / "originals" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    # Recheck the exact audited inode before destructive cleanup, rather than
    # trusting a filename such as manager.sock. Never follow linked ancestors.
    for entry in report["socket_deletions"]:
        path = root / entry["path"]
        info = path.lstat()
        if (not stat.S_ISSOCK(info.st_mode)
                or (info.st_dev, info.st_ino) != (entry["device"], entry["inode"])
                or any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents)):
            raise SystemExit(f"Audited socket changed; stop and inspect: {entry['path']}")
        path.unlink()
    transform = replacement(root, report["aliases"], report["moves"])
    for move in report["moves"]:
        target = root / move["new"]
        target.parent.mkdir(parents=True, exist_ok=True)
        (root / move["old"]).rename(target)
    for edit in report["edits"]:
        path = root / edit["destination"]
        path.write_bytes(checked_rewrite(root, edit["destination"], edit, transform))
    for name, content in report["statuses"].items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for layout in SOURCE_LAYOUTS:
        path = root / layout
        if path.exists():
            if layout == LEGACY_LAYOUT and any((path / name).is_file() for name in LEGACY_OVERVIEWS):
                continue
            path.rmdir()
    return verify(root, report)


def verify(root, report):
    errors = []
    targeted = report.get("validation_scope") == "saved-audit-targeted"
    edited = {edit["path"] for edit in report["edits"]}
    deleted = {entry["path"] for entry in report["socket_deletions"]}
    for name, original in report["snapshot"].items():
        if targeted and name not in deleted:
            continue
        target = relocated(name, report["moves"])
        if name in deleted:
            if os.path.lexists(root / name) or os.path.lexists(root / target):
                errors.append(f"Audited socket remains: {name}")
            continue
        if name in edited or target in report["statuses"]:
            continue
        path = root / target
        if not os.path.lexists(path):
            errors.append(f"Missing original file: {target}")
        elif path.is_symlink():
            if os.readlink(path) != original[3]:
                errors.append(f"Changed symlink: {target}")
        elif len(original) > 3:
            if digest(path.read_bytes()) != original[3]:
                errors.append(f"Changed original file: {target}")
        elif path.stat().st_size != original[0] or path.stat().st_mtime_ns != original[1]:
            errors.append(f"Changed unscanned file metadata: {target}")
    for move in report["moves"]:
        if os.path.lexists(root / move["old"]) or not (root / move["new"]).exists():
            errors.append(f"Move not complete: {move['old']}")
    for name, content in report["statuses"].items():
        path = root / name
        if not path.is_file() or path.read_text() != content:
            errors.append(f"Unexpected status: {name}")
    for edit in report["edits"]:
        path = root / edit["destination"]
        if not path.is_file() or digest(path.read_bytes()) != edit["after"]:
            errors.append(f"Unexpected rewritten content: {edit['destination']}")
    for name in report.get("removed_empty_entries", {}):
        if os.path.lexists(root / name):
            errors.append(f"Acknowledged removed entry reappeared: {name}")
    if targeted:
        moves, _, blockers = plan_inventory(root, report["legacy_status"])
        current = {"moves": moves, "blockers": blockers, "review": report["review"]}
    else:
        current = audit(root, report["aliases"], legacy_status=report["legacy_status"])
    errors.extend(current["blockers"])
    if current["moves"]:
        errors.append("Old-layout plans remain in this project.")
    return {"mechanical_checks_passed": not errors, "errors": errors,
            "validation_scope": "saved-audit-targeted" if targeted else "full-project",
            "remaining_moves": current["moves"], "review": current["review"],
            "original_review": report["review"],
            "backup": str(root / ".plan-migration/backup")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("discover").add_argument("--parent", type=Path, required=True)
    for name in ["audit", "apply", "verify"]:
        command = commands.add_parser(name)
        command.add_argument("--project", type=Path, required=True)
        if name == "audit":
            command.add_argument("--alias", action="append", default=[])
            command.add_argument("--legacy-status", choices=["active", "finished"],
                                 help="Initial status for families in plans/legacy-by-family (required when present)")
        if name == "apply":
            command.add_argument("--use-saved-audit", action="store_true",
                                 help="Check inventory and rewrite hashes without a full-project rescan")
            command.add_argument("--acknowledge-removed-empty", action="append", default=[], metavar="PATH",
                                 help="Project-relative empty blocked entry removed since audit (repeatable)")
            command.add_argument("--exclude-rewrite", action="append", default=[], metavar="PATH",
                                 help="Preserve an exact audited file without rewriting or hash validation (repeatable; saved-audit mode)")
            command.add_argument("--delete-sockets", action="store_true",
                                 help="Delete only audited plan sockets; confirm their jobs are stopped first")
    args = parser.parse_args()
    if args.command == "discover":
        result = discover(args.parent.resolve(strict=True))
    else:
        root = args.project.resolve(strict=True)
        work = root / ".plan-migration"
        if work.is_symlink():
            raise SystemExit("Migration workspace must not be a symlink.")
        if args.command == "audit":
            result = audit(root, [alias.rstrip("/") for alias in args.alias], progress=True,
                           legacy_status=args.legacy_status)
            work.mkdir(exist_ok=True)
            report_path = work / "audit.json"
            if report_path.is_symlink():
                raise SystemExit("Audit must not be a symlink.")
            report_path.write_text(json.dumps(result, indent=2) + "\n")
            print(f"Audit: report saved to {report_path}", file=sys.stderr, flush=True)
            result = {key: value for key, value in result.items() if key != "snapshot"}
            result["audit_file"] = str(report_path)
        elif args.command == "apply":
            result = apply(root, json.loads((work / "audit.json").read_text()),
                           delete_sockets=args.delete_sockets, use_saved_audit=args.use_saved_audit,
                           removed_empty=args.acknowledge_removed_empty, exclude_rewrites=args.exclude_rewrite)
        else:
            result = verify(root, json.loads((work / "backup/audit.json").read_text()))
    print(json.dumps(result, indent=2))
    if result.get("blockers") or result.get("errors"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
