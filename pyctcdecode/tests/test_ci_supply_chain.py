# Copyright 2021-present Kensho Technologies, LLC.
import os
import re
import unittest


_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_WORKFLOW_DIR = os.path.join(_REPO_ROOT, ".github", "workflows")
_PACKAGE_DIR = os.path.join(_REPO_ROOT, "pyctcdecode")

_USES_REGEX = re.compile(r"^\s*-?\s*uses:\s*(\S+)", re.MULTILINE)
_SHA_PINNED_REGEX = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")


def _read_workflows():
    contents = {}
    for name in sorted(os.listdir(_WORKFLOW_DIR)):
        if name.endswith((".yml", ".yaml")):
            with open(os.path.join(_WORKFLOW_DIR, name), encoding="utf-8") as f:
                contents[name] = f.read()
    return contents


@unittest.skipUnless(os.path.isdir(_WORKFLOW_DIR), "CI workflows not present")
class TestCISupplyChain(unittest.TestCase):
    def test_actions_pinned_to_commit_sha(self):
        for name, text in _read_workflows().items():
            for action in _USES_REGEX.findall(text):
                if action.startswith("./"):
                    continue
                self.assertRegex(action, _SHA_PINNED_REGEX, "{}: {}".format(name, action))

    def test_no_unpinned_downloads(self):
        for name, text in _read_workflows().items():
            self.assertNotIn("archive/master.zip", text, name)
            self.assertNotIn("uploader.codecov.io", text, name)
            self.assertNotRegex(text, r"curl[^\n]*\n[^\n]*chmod \+x", name)

    def test_workflow_permissions_restricted(self):
        for name, text in _read_workflows().items():
            self.assertRegex(text, r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", name)


class TestKenlmInstallHint(unittest.TestCase):
    def test_install_hint_is_pinned(self):
        for module in ("decoder.py", "language_model.py"):
            with open(os.path.join(_PACKAGE_DIR, module), encoding="utf-8") as f:
                text = f.read()
            self.assertNotIn("archive/master.zip", text, module)
            self.assertIn("pip install kenlm==", text, module)
