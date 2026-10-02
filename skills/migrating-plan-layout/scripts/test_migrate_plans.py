"""Small filesystem fixtures; temporary projects stay beneath the working directory."""

import importlib.util
import contextlib
import io
import json
import os
import re
import socket
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("migration", Path(__file__).with_name("migrate_plans.py"))
migration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".migration-test-", dir=Path.cwd())
        self.root = Path(self.temp.name).resolve()

    def tearDown(self):
        self.temp.cleanup()

    def put(self, name, content="example\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def run_apply(self, report):
        (self.root / ".plan-migration").mkdir(exist_ok=True)
        return migration.apply(self.root, report)

    def test_all_layouts_cross_references_and_backup(self):
        for index, layout in enumerate(migration.LAYOUTS):
            self.put(f"{layout}/p{index}.md")
            self.put(f"{layout}/p{index}/config.json", json.dumps({
                "absolute": f"{self.root}/{layout}/p{index}/out",
                "relative": f"{layout}/p{index}/out",
                "alias": f"/alias/project/{layout}/p{index}/out"}))
        original = "copilot/plans/active/p0/out plans/archive/p3/out\r\n"
        self.put("ignored.log", original)
        self.put(".gitignore", "*.log\n")
        report = migration.audit(self.root, ["/alias/project"])
        self.assertEqual(report["blockers"], [])
        result = self.run_apply(report)
        self.assertTrue(result["mechanical_checks_passed"], result)
        for index in range(4):
            directory = self.root / f"copilot/plans/runs/p{index}"
            self.assertTrue((self.root / f"copilot/plans/docs/p{index}.md").exists())
            expected = "active" if index % 2 == 0 else "finished"
            self.assertEqual((directory / "PLAN_STATUS.md").read_text(), f"Status: {expected}\n")
            config = json.loads((directory / "config.json").read_text())
            self.assertEqual(config["alias"], f"/alias/project/copilot/plans/runs/p{index}/out")
        self.assertEqual((self.root / "ignored.log").read_bytes(),
                         b"copilot/plans/runs/p0/out copilot/plans/runs/p3/out\r\n")
        backup = self.root / ".plan-migration/backup/originals"
        self.assertEqual((backup / "ignored.log").read_bytes(), original.encode())
        self.assertTrue((backup / "plans/archive/p3/config.json").exists())
        second = migration.audit(self.root, [])
        self.assertEqual(second["moves"], [])
        self.assertEqual(second["edits"], [])
        self.assertEqual(self.run_apply(second), {"result": "no changes"})

    def test_collision_prevents_all_changes(self):
        self.put("plans/active/p.md")
        self.put("copilot/plans/archive/p.md")
        report = migration.audit(self.root, [])
        self.assertTrue(report["blockers"])
        with self.assertRaises(SystemExit):
            self.run_apply(report)
        self.assertTrue((self.root / "plans/active/p.md").exists())

    def test_changed_input_refuses_apply(self):
        self.put("plans/active/p.md")
        report = migration.audit(self.root, [])
        self.put("new.log")
        with self.assertRaises(SystemExit):
            self.run_apply(report)
        self.assertFalse((self.root / ".plan-migration/backup").exists())

    def test_saved_audit_removed_placeholder_without_rescan(self):
        self.put("plans/archive/p.md", "plans/archive/p/output\n")
        self.put("plans/archive/p/output", "results\n")
        placeholder = self.put("plans/archive/.gitkeep", "")
        report = migration.audit(self.root, [])
        original = json.dumps(report, sort_keys=True)
        placeholder.unlink()
        # New references are deliberately outside the saved audit's coverage.
        self.put("new.log", "plans/archive/p/output\n")
        (self.root / ".plan-migration").mkdir()
        with patch.object(migration, "audit", side_effect=AssertionError("full scan")), \
                patch.object(migration, "discover", side_effect=AssertionError("discovery")), \
                patch.object(migration, "walk", side_effect=AssertionError("tree scan")):
            result = migration.apply(self.root, report, use_saved_audit=True,
                                     removed_empty=["plans/archive/.gitkeep"])
            self.assertTrue(result["mechanical_checks_passed"], result)
            saved = json.loads((self.root / ".plan-migration/backup/audit.json").read_text())
            self.assertTrue(migration.verify(self.root, saved)["mechanical_checks_passed"])
        self.assertEqual(result["validation_scope"], "saved-audit-targeted")
        self.assertEqual(json.dumps(report, sort_keys=True), original)
        self.assertIn("plans/archive/.gitkeep", saved["removed_empty_entries"])
        self.assertNotIn("plans/archive/.gitkeep", saved["snapshot"])
        self.assertEqual((self.root / "copilot/plans/docs/p.md").read_text(),
                         "copilot/plans/runs/p/output\n")
        self.assertEqual((self.root / "new.log").read_text(), "plans/archive/p/output\n")
        self.assertEqual((self.root / ".plan-migration/backup/originals/plans/archive/p.md").read_text(),
                         "plans/archive/p/output\n")

    def test_saved_audit_rejects_changed_rewrite_before_any_moves(self):
        path = self.put("plans/active/p.md", "plans/active/p.md\n")
        report = migration.audit(self.root, [])
        path.write_text("changed\n")
        with self.assertRaisesRegex(SystemExit, "File changed since audit"):
            migration.apply(self.root, report, use_saved_audit=True)
        self.assertTrue(path.exists())
        self.assertFalse((self.root / ".plan-migration/backup").exists())

    def test_saved_audit_rejects_changed_replacement_rules(self):
        self.put("plans/active/p.md", "plans/active/p.md\n")
        report = migration.audit(self.root, [])
        with patch.object(migration, "replacement", return_value=lambda text: text), \
                self.assertRaisesRegex(SystemExit, "Replacement differs"):
            migration.apply(self.root, report, use_saved_audit=True)
        self.assertFalse((self.root / ".plan-migration/backup").exists())

    def test_saved_audit_rechecks_inventory_and_collisions(self):
        self.put("plans/active/p.md")
        report = migration.audit(self.root, [])
        added = self.put("plans/active/new.md")
        with self.assertRaisesRegex(SystemExit, "Plan inventory changed"):
            migration.apply(self.root, report, use_saved_audit=True)
        added.unlink()
        self.put("copilot/plans/docs/p.md")
        with self.assertRaisesRegex(SystemExit, "Destination exists"):
            migration.apply(self.root, report, use_saved_audit=True)

    def test_saved_audit_cannot_waive_nonempty_or_existing_blocker(self):
        self.put("plans/archive/p.md")
        placeholder = self.put("plans/archive/.gitkeep", "not empty")
        report = migration.audit(self.root, [])
        placeholder.unlink()
        with self.assertRaisesRegex(SystemExit, "Not an audited"):
            migration.apply(self.root, report, use_saved_audit=True,
                            removed_empty=["plans/archive/.gitkeep"])
        placeholder = self.put("plans/archive/.gitkeep", "")
        report = migration.audit(self.root, [])
        with self.assertRaisesRegex(SystemExit, "Not an audited"):
            migration.apply(self.root, report, use_saved_audit=True,
                            removed_empty=["plans/archive/.gitkeep"])
        placeholder.unlink()
        with self.assertRaisesRegex(SystemExit, "Unresolved audit blockers"):
            migration.apply(self.root, report, use_saved_audit=True)

    def test_saved_audit_rejects_new_linked_rewrite_ancestor(self):
        self.put("plans/active/p.md")
        parent = self.root / "references"
        self.put("references/paths.md", "plans/active/p.md\n")
        report = migration.audit(self.root, [])
        parent.rename(self.root / "elsewhere")
        parent.symlink_to(self.root / "elsewhere", target_is_directory=True)
        with self.assertRaisesRegex(SystemExit, "Linked rewrite path"):
            migration.apply(self.root, report, use_saved_audit=True)

    def test_saved_audit_cli(self):
        self.put("plans/archive/p.md", "plans/archive/p.md\n")
        placeholder = self.put("plans/archive/.gitkeep", "")
        report = migration.audit(self.root, [])
        work = self.root / ".plan-migration"
        work.mkdir()
        (work / "audit.json").write_text(json.dumps(report))
        placeholder.unlink()
        command = [sys.executable, migration.__file__, "apply", "--project", str(self.root),
                   "--use-saved-audit", "--acknowledge-removed-empty", "plans/archive/.gitkeep"]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertTrue(json.loads(result.stdout)["mechanical_checks_passed"])

    def test_saved_audit_preserves_explicitly_excluded_growing_log(self):
        self.put("plans/archive/p.md", "plans/archive/p.md\n")
        log = self.put("logs/audit.err", "scanning plans/archive/p.md\n")
        report = migration.audit(self.root, [])
        original = json.dumps(report, sort_keys=True)
        log.write_text(log.read_text() + "audit finished\n")
        expected = log.read_bytes()
        work = self.root / ".plan-migration"
        work.mkdir()
        (work / "audit.json").write_text(json.dumps(report))
        command = [sys.executable, migration.__file__, "apply", "--project", str(self.root),
                   "--use-saved-audit", "--exclude-rewrite", "logs/audit.err"]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        self.assertTrue(json.loads(result.stdout)["mechanical_checks_passed"])
        self.assertEqual(log.read_bytes(), expected)
        saved = json.loads((work / "backup/audit.json").read_text())
        self.assertEqual([e["path"] for e in saved["excluded_rewrites"]], ["logs/audit.err"])
        self.assertTrue(any("explicitly excluded" in x["reason"] for x in saved["review"]))
        self.assertEqual(json.dumps(report, sort_keys=True), original)
        self.assertFalse((work / "backup/originals/logs/audit.err").exists())
        self.assertEqual((self.root / "copilot/plans/docs/p.md").read_text(),
                         "copilot/plans/docs/p.md\n")

    def test_saved_audit_exclusion_is_exact_and_does_not_waive_other_edits(self):
        self.put("plans/archive/p.md", "plans/archive/p.md\n")
        self.put("logs/audit.err", "plans/archive/p.md\n")
        report = migration.audit(self.root, [])
        with self.assertRaisesRegex(SystemExit, "Excluded rewrite not in audit"):
            migration.apply(self.root, report, use_saved_audit=True, exclude_rewrites=["logs/*.err"])
        self.put("plans/archive/p.md", "changed plan\n")
        with self.assertRaisesRegex(SystemExit, "File changed since audit"):
            migration.apply(self.root, report, use_saved_audit=True, exclude_rewrites=["logs/audit.err"])
        self.assertFalse((self.root / ".plan-migration/backup").exists())

    def test_saved_audit_rejects_new_hardlink_and_status_conflict(self):
        path = self.put("plans/archive/p/config.md", "plans/archive/p/output\n")
        report = migration.audit(self.root, [])
        link = self.root / "extra-link"
        os.link(path, link)
        with self.assertRaisesRegex(SystemExit, "unshared file"):
            migration.apply(self.root, report, use_saved_audit=True)
        link.unlink()
        self.put("plans/archive/p/PLAN_STATUS.md", "Status: active\n")
        with self.assertRaisesRegex(SystemExit, "Conflicting status"):
            migration.apply(self.root, report, use_saved_audit=True)

    def test_saved_audit_socket_opt_in_and_targeted_verification(self):
        self.put("plans/archive/p/config.md", "plans/archive/p/output\n")
        self.make_socket("plans/archive/p/manager.sock")
        report = migration.audit(self.root, [])
        (self.root / ".plan-migration").mkdir()
        with self.assertRaisesRegex(SystemExit, "require --delete-sockets"):
            migration.apply(self.root, report, use_saved_audit=True)
        self.assertFalse((self.root / ".plan-migration/backup").exists())
        result = migration.apply(self.root, report, use_saved_audit=True, delete_sockets=True)
        self.assertTrue(result["mechanical_checks_passed"], result)
        saved = json.loads((self.root / ".plan-migration/backup/audit.json").read_text())
        self.put("copilot/plans/runs/p/config.md", "damaged\n")
        self.put("copilot/plans/runs/p/PLAN_STATUS.md", "Status: active\n")
        result = migration.verify(self.root, saved)
        self.assertFalse(result["mechanical_checks_passed"])
        self.assertTrue(any("Unexpected rewritten content" in x for x in result["errors"]))
        self.assertTrue(any("Unexpected status" in x for x in result["errors"]))

    def test_boundaries_and_relative_path_review(self):
        self.put("plans/active/p.md")
        self.put("plans/active/p/run.py", 'root = Path("../results")\n')
        text = ('plans/active/p/data ./plans/active/p/data '
                '/other/project/plans/active/p/data plans/active/p-long/data '
                '../plans/active/p/data')
        self.put("paths.txt", text)
        report = migration.audit(self.root, [])
        self.assertTrue(any("relative paths" in item["reason"] for item in report["review"]))
        self.run_apply(report)
        self.assertEqual((self.root / "paths.txt").read_text(),
                         text.replace("plans/active/p/data ./plans/active/p/data",
                                       "copilot/plans/runs/p/data ./copilot/plans/runs/p/data", 1))

    def test_prefix_replacement_includes_former_locations_and_containers(self):
        self.put("copilot/plans/archive/p.md")
        self.put("copilot/plans/archive/p/out", "result")
        text = "\n".join(f"{prefix}{layout}/p/out" for layout in migration.LAYOUTS
                         for prefix in ("", "./", f"{self.root}/", "/alias/project/"))
        text += "\ncopilot/plans/active/ plans/archive\n"
        text += "plans/active/p.md copilot/plans/archive/p.md\n"
        text += "/other/copilot/plans/active/p ../plans/archive/p plans/active-extra/p"
        self.put("references.txt", text)
        report = migration.audit(self.root, ["/alias/project"])
        self.run_apply(report)
        actual = (self.root / "references.txt").read_text()
        self.assertEqual(actual.count("copilot/plans/runs/p/out"), 16)
        self.assertIn("copilot/plans/active/ plans/archive\n", actual)
        self.assertEqual(actual.count("copilot/plans/docs/p.md"), 2)
        self.assertTrue(actual.endswith(
            "/other/copilot/plans/active/p ../plans/archive/p plans/active-extra/p"))

    def test_relative_target_review_preserves_internal_paths(self):
        self.put("copilot/plans/active/p/scripts/run.py", (
            "internal = Path(__file__).resolve().parents[1] / 'artifacts'\n"
            "root = Path(__file__).resolve().parents[5]\n"
            "target.parent.mkdir(parents=True)\n"
            "cwd_path = '../results'\n"))
        report = migration.audit(self.root, [])
        items = [x for x in report["review"] if x["path"].endswith("run.py")]
        self.assertEqual([x["line"] for x in items], [4])
        self.assertFalse(report["edits"])

    def test_relative_symlink_target_comparison(self):
        script = self.put("copilot/plans/active/p/scripts/run.py", "pass\n")
        (script.parent / "internal").symlink_to("../artifacts")
        (script.parent / "external").symlink_to("../../../../../data")
        report = migration.audit(self.root, [])
        links = {Path(x["path"]).name: x for x in report["review"] if x["reason"] == "symlink"}
        self.assertFalse(links["internal"]["target_changed"])
        self.assertFalse(links["external"]["target_changed"])

    def test_legacy_root_depth_change_is_reported(self):
        self.put("plans/active/p/scripts/run.py",
                 "root = Path(__file__).resolve().parents[4]\n")
        report = migration.audit(self.root, [])
        self.assertEqual(report["review"][0]["before_target"], str(self.root))
        self.assertEqual(report["review"][0]["after_target"], str(self.root / "copilot"))
        self.assertEqual(report["statuses"]["copilot/plans/runs/p/PLAN_STATUS.md"],
                         "Status: active\n")

    def test_document_links_and_independent_directory_only_plan(self):
        self.put("copilot/plans/active/p.md", "[Results](p/output.txt)\n[Other](q.md)\n")
        self.put("copilot/plans/active/q.md")
        self.put("copilot/plans/active/p/output.txt")
        self.put("copilot/plans/archive/legacy-run/results.txt")
        report = migration.audit(self.root, [])
        links = [x for x in report["review"] if x["reason"] == "relative Markdown link changes target"]
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["suggested_target"], "../runs/p/output.txt")
        self.assertEqual(report["statuses"]["copilot/plans/runs/legacy-run/PLAN_STATUS.md"],
                         "Status: finished\n")

    def test_linked_destination_container_blocks_apply(self):
        self.put("copilot/plans/active/p.md")
        (self.root / "copilot/plans/docs").symlink_to(self.root)
        self.assertTrue(any("Linked destination container" in x
                            for x in migration.audit(self.root, [])["blockers"]))

    def test_discovery_nested_projects_and_links(self):
        self.put("plans/archive/parent.md")
        self.put("child/copilot/plans/active/child.md")
        self.put("child/reference.txt", "plans/archive/parent.md")
        (self.root / "linked").symlink_to(self.root / "child", target_is_directory=True)
        found = migration.discover(self.root)
        self.assertEqual(len(found["projects"]), 2)
        self.assertEqual(len(found["symlinks_not_followed"]), 1)
        report = migration.audit(self.root, [])
        self.assertFalse(any(edit["path"].startswith("child/") for edit in report["edits"]))

    def test_binary_symlink_and_status_conflict(self):
        self.put("plans/archive/p.md")
        binary = self.root / "data.bin"
        binary.write_bytes(b"\x00plans/archive/p")
        (self.root / "linked").symlink_to(binary)
        report = migration.audit(self.root, [])
        self.assertTrue(any("binary" in item["reason"] for item in report["review"]))
        self.assertTrue(any(item["reason"] == "symlink" for item in report["review"]))
        self.put("plans/archive/p/PLAN_STATUS.md", "Status: active\n")
        self.assertTrue(migration.audit(self.root, [])["blockers"])

    def test_verification_detects_lost_or_changed_unedited_files(self):
        self.put("plans/active/p.md")
        self.put("plans/active/p/results.txt", "valuable result\n")
        report = migration.audit(self.root, [])
        self.run_apply(report)
        self.put("copilot/plans/runs/p/results.txt", "corruption\n")
        self.assertFalse(migration.verify(self.root, report)["mechanical_checks_passed"])

    def test_cli_audit_apply_verify(self):
        self.put("plans/archive/p.md")
        script = Path(__file__).with_name("migrate_plans.py")
        for command in ["audit", "apply", "verify"]:
            output = subprocess.run([sys.executable, "-B", str(script), command,
                                     "--project", str(self.root)],
                                    capture_output=True, text=True, check=True)
            result = json.loads(output.stdout)
            if command == "audit":
                self.assertTrue((self.root / "plans/archive/p.md").exists())
                self.assertFalse((self.root / "copilot/plans/docs/p.md").exists())
            else:
                self.assertTrue(result["mechanical_checks_passed"])

    def test_existing_backup_is_preserved(self):
        self.put("plans/active/p.md")
        self.put(".plan-migration/backup/keep.txt", "previous backup")
        report = migration.audit(self.root, [])
        with self.assertRaises(FileExistsError):
            self.run_apply(report)
        self.assertTrue((self.root / "plans/active/p.md").exists())
        self.assertEqual((self.root / ".plan-migration/backup/keep.txt").read_text(),
                         "previous backup")

    def test_replacement_matches_previous_rules(self):
        moves = [{"old": f"copilot/plans/archive/{name}",
                  "new": f"copilot/plans/{container}/{name}"}
                 for name, container in (("p", "runs"), ("p.md", "docs"),
                                         ("p-long", "runs"), ("a space+name.md", "docs"))]
        aliases = ["/alias/project"]
        mapping = {}
        for move in moves:
            for layout in migration.LAYOUTS:
                for prefix in ("", "./", f"{self.root}/", "/alias/project/"):
                    mapping[f"{prefix}{layout}/{Path(move['old']).name}"] = prefix + move["new"]
        old_pattern = re.compile(r"(?<![\w/.-])(?:" + "|".join(
            re.escape(key) for key in sorted(mapping, key=len, reverse=True))
            + r")(?=/|$|[\s\"'`),;:\]}])")
        text = "\n".join(key + suffix for key in mapping for suffix in ("", "/out", "#anchor", "-extra", "\""))
        text += "\n/other/project/plans/active/p ../plans/archive/p ${ROOT}/plans/active/p"
        expected = old_pattern.sub(lambda match: mapping[match[0]], text)
        self.assertEqual(migration.replacement(self.root, aliases, moves)(text), expected)

    def test_progress_does_not_change_report(self):
        self.put("copilot/plans/active/p.md")
        expected = migration.audit(self.root, [])
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), patch.object(
                migration.time, "monotonic", side_effect=[0, 1, 62, 63]):
            actual = migration.audit(self.root, [], progress=True)
        self.assertEqual(actual, expected)
        self.assertIn("current file:", stderr.getvalue())
        self.assertIn("scan finished", stderr.getvalue())

    def make_socket(self, name):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        # A short relative bind path avoids AF_UNIX's pathname length limit.
        previous = Path.cwd()
        try:
            os.chdir(path.parent)
            with socket.socket(socket.AF_UNIX) as sock:
                sock.bind(path.name)
        finally:
            os.chdir(previous)
        return path

    def test_socket_audit_is_read_only_and_apply_requires_opt_in(self):
        path = self.make_socket("copilot/plans/archive/p/tmp/manager.sock")
        report = migration.audit(self.root, [])
        self.assertEqual(report["blockers"], [])
        self.assertEqual([x["path"] for x in report["socket_deletions"]],
                         [str(path.relative_to(self.root))])
        self.assertTrue(path.exists())
        with self.assertRaisesRegex(SystemExit, "--delete-sockets"):
            self.run_apply(report)
        self.assertTrue(path.exists())
        self.assertFalse((self.root / ".plan-migration/backup").exists())
        result = migration.apply(self.root, report, delete_sockets=True)
        self.assertTrue(result["mechanical_checks_passed"], result)
        self.assertFalse(path.exists())
        self.assertFalse((self.root / "copilot/plans/runs/p/tmp/manager.sock").exists())
        self.assertFalse((self.root / ".plan-migration/backup/originals").exists())

    def test_socket_names_are_not_used_to_infer_type(self):
        self.put("copilot/plans/archive/p/manager.sock", "ordinary file")
        socket_path = self.make_socket("copilot/plans/archive/p/unusual-name")
        report = migration.audit(self.root, [])
        self.assertEqual([x["path"] for x in report["socket_deletions"]],
                         [str(socket_path.relative_to(self.root))])
        socket_path.unlink()
        socket_path.write_text("replacement ordinary file")
        (self.root / ".plan-migration").mkdir()
        with self.assertRaisesRegex(SystemExit, "Project changed"):
            migration.apply(self.root, report, delete_sockets=True)
        self.assertEqual(socket_path.read_text(), "replacement ordinary file")

    def test_outside_socket_and_fifo_remain_blockers(self):
        self.put("copilot/plans/archive/p.md")
        path = self.make_socket("outside/socket")
        fifo = self.root / "copilot/plans/archive/p/fifo"
        fifo.parent.mkdir()
        os.mkfifo(fifo)
        report = migration.audit(self.root, [])
        self.assertEqual(len(report["blockers"]), 2)
        self.assertEqual(report["socket_deletions"], [])
        with self.assertRaises(SystemExit):
            migration.apply(self.root, report, delete_sockets=True)
        self.assertTrue(path.exists())

    def test_backup_contains_only_changed_content(self):
        self.put("copilot/plans/archive/p.md", "plans/active/p/output.txt\n")
        self.put("copilot/plans/archive/p/output.txt", "unchanged result\n")
        self.put("copilot/plans/archive/p/PLAN_STATUS.md", "Status: finished\n")
        self.put("references.txt", "plans/active/p.md\n")
        report = migration.audit(self.root, [])
        result = self.run_apply(report)
        self.assertTrue(result["mechanical_checks_passed"], result)
        originals = self.root / ".plan-migration/backup/originals"
        self.assertEqual({str(p.relative_to(originals)) for p in originals.rglob("*") if p.is_file()},
                         {"copilot/plans/archive/p.md", "references.txt"})
        self.assertEqual((self.root / "copilot/plans/runs/p/output.txt").read_text(), "unchanged result\n")

    def test_variable_root_paths_route_documents_and_runs(self):
        self.put("copilot/plans/archive/p.md")
        self.put("copilot/plans/archive/p/result.txt")
        prefixes = ("${REPO_ROOT}/", "$REPO_ROOT/", "${PROJECT_ROOT}/",
                    "$PROJECT_ROOT/", "{repo_root}/")
        paths = [f"{prefix}{layout}/{entry}"
                 for prefix in prefixes for layout in migration.SOURCE_LAYOUTS
                 for entry in ("p.md", "p/result.txt")]
        untouched = ["${OTHER_ROOT}/plans/active/p/result.txt",
                     "../copilot/plans/active/p/result.txt",
                     "/other/project/copilot/plans/active/p/result.txt",
                     "${REPO_ROOT}/plans/active/unknown/result.txt"]
        self.put("paths.txt", "\n".join(paths + untouched))
        report = migration.audit(self.root, [])
        result = self.run_apply(report)
        self.assertTrue(result["mechanical_checks_passed"], result)
        actual = (self.root / "paths.txt").read_text()
        for prefix in prefixes:
            self.assertEqual(actual.count(prefix + "copilot/plans/docs/p.md"), 5)
            self.assertEqual(actual.count(prefix + "copilot/plans/runs/p/result.txt"), 5)
        self.assertTrue(actual.endswith("\n".join(untouched)))

    def test_assembled_run_paths_and_ambiguous_containers(self):
        self.put("plans/active/p/result.txt")
        for layout in migration.SOURCE_LAYOUTS:
            text = (f'run_dir <- file.path(repo_root, "{layout}", plan_id)\n'
                    f"  run_dir = file.path(repo_root, '{layout}', plan_id)\n"
                    f'run_dir\t{{repo_root}}/{layout}/{{plan_id}}\tPlan directory\n'
                    f'input\t{{repo_root}}/{layout}/{{plan_id}}/run/table.tsv\n')
            transform = migration.replacement(self.root, [], migration.audit(self.root, [])["moves"])
            self.assertEqual(transform(text), text.replace(layout, "copilot/plans/runs"))
            untouched = (f'doc <- file.path(repo_root, "{layout}", plan_id)\n'
                         f'run_dir <- file.path(other_root, "{layout}", plan_id)\n'
                         f'run_dir <- file.path(repo_root, "{layout}", paste0(plan_id, ".md"))\n'
                         f'{{repo_root}}/{layout}/{{plan_id}}.md\n'
                         f'../{{repo_root}}/{layout}/{{plan_id}}/run\n'
                         f'{layout}/ {layout}/*.md\n')
            self.assertEqual(transform(untouched), untouched)

    def test_legacy_families_migrate_directly_with_explicit_status(self):
        self.put("plans/legacy-by-family/README.md", "Family overview: plans/legacy-by-family/family/README.md\n")
        self.put("plans/legacy-by-family/family/README.md", "family\n")
        self.put("plans/legacy-by-family/family/source-plans/old.md", "old plan\n")
        self.put("plans/legacy-by-family/standalone.md", "standalone plan\n")
        self.put("references.txt", "plans/legacy-by-family/family/source-plans/old.md\n"
                 "plans/legacy-by-family/standalone.md\nplans/legacy-by-family/README.md\n")
        self.assertEqual(migration.discover(self.root)["projects"], [str(self.root)])
        missing_status = migration.audit(self.root, [])
        self.assertTrue(any("--legacy-status" in x for x in missing_status["blockers"]))
        with self.assertRaises(SystemExit):
            self.run_apply(missing_status)
        report = migration.audit(self.root, [], legacy_status="finished")
        self.assertEqual(report["blockers"], [])
        result = self.run_apply(report)
        self.assertTrue(result["mechanical_checks_passed"], result)
        self.assertTrue((self.root / "copilot/plans/runs/family/source-plans/old.md").exists())
        self.assertFalse((self.root / "copilot/plans/docs/old.md").exists())
        self.assertTrue((self.root / "copilot/plans/docs/standalone.md").exists())
        self.assertEqual((self.root / "copilot/plans/runs/family/PLAN_STATUS.md").read_text(), "Status: finished\n")
        self.assertEqual((self.root / "references.txt").read_text(),
                         "copilot/plans/runs/family/source-plans/old.md\n"
                         "copilot/plans/docs/standalone.md\nplans/legacy-by-family/README.md\n")
        self.assertEqual((self.root / "plans/legacy-by-family/README.md").read_text(),
                         "Family overview: copilot/plans/runs/family/README.md\n")
        second = migration.audit(self.root, [], legacy_status="finished")
        self.assertEqual(second["moves"], [])
        self.assertEqual(second["edits"], [])

    def test_legacy_status_collision_and_nested_discovery(self):
        self.put("plans/legacy-by-family/p/data.txt")
        self.put("plans/legacy-by-family/p/PLAN_STATUS.md", "Status: active\n")
        self.assertTrue(any("Conflicting status" in x for x in
                            migration.audit(self.root, [], legacy_status="finished")["blockers"]))
        report = migration.audit(self.root, [], legacy_status="active")
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["statuses"]["copilot/plans/runs/p/PLAN_STATUS.md"], "Status: active\n")
        self.put("plans/active/p/another.txt")
        self.assertTrue(any("collision" in x.lower() for x in
                            migration.audit(self.root, [], legacy_status="active")["blockers"]))
        self.put("child/plans/legacy-by-family/q/data.txt")
        self.assertEqual(len(migration.discover(self.root)["projects"]), 2)
        report = migration.audit(self.root, [], legacy_status="active")
        self.assertTrue(any(x["path"] == "child" and x["reason"] == "nested project excluded"
                            for x in report["review"]))

    def test_cli_retains_legacy_status_through_apply_and_verify(self):
        self.put("plans/legacy-by-family/family/notes.md")
        script = Path(__file__).with_name("migrate_plans.py")
        for command in ("audit", "apply", "verify"):
            args = [sys.executable, "-B", str(script), command, "--project", str(self.root)]
            if command == "audit":
                args += ["--legacy-status", "finished"]
            result = json.loads(subprocess.run(args, capture_output=True, text=True, check=True).stdout)
            if command == "audit":
                self.assertEqual(result["legacy_status"], "finished")
                self.assertTrue((self.root / "plans/legacy-by-family/family/notes.md").exists())
            else:
                self.assertTrue(result["mechanical_checks_passed"], result)
        self.assertEqual((self.root / "copilot/plans/runs/family/PLAN_STATUS.md").read_text(),
                         "Status: finished\n")

    def test_legacy_index_preserved_and_rewritten_without_readme(self):
        original = "family\tpath\np\tplans/legacy-by-family/p/source-plans/old.md\n"
        self.put("plans/legacy-by-family/family-index.tsv", original)
        self.put("plans/legacy-by-family/p/source-plans/old.md", "original plan\n")
        self.put("index-link.md", "plans/legacy-by-family/family-index.tsv\n")
        report = migration.audit(self.root, [], legacy_status="finished")
        self.assertEqual(report["blockers"], [])
        self.assertEqual(len(report["moves"]), 1)
        self.assertEqual(len(report["statuses"]), 1)
        self.assertTrue(any(edit["path"] == "plans/legacy-by-family/family-index.tsv"
                            and edit["destination"] == edit["path"] for edit in report["edits"]))
        self.assertEqual((self.root / "plans/legacy-by-family/family-index.tsv").read_text(), original)
        result = self.run_apply(report)
        self.assertTrue(result["mechanical_checks_passed"], result)
        self.assertEqual((self.root / "plans/legacy-by-family/family-index.tsv").read_text(),
                         original.replace("plans/legacy-by-family/p", "copilot/plans/runs/p"))
        self.assertEqual((self.root / "index-link.md").read_text(), "plans/legacy-by-family/family-index.tsv\n")
        self.assertEqual((self.root / ".plan-migration/backup/originals/plans/legacy-by-family/family-index.tsv").read_text(), original)
        second = migration.audit(self.root, [], legacy_status="finished")
        self.assertEqual(second["blockers"], [])
        self.assertEqual(second["moves"], [])
        self.assertEqual(second["edits"], [])


if __name__ == "__main__":
    unittest.main()
