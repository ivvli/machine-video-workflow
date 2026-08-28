#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
STATE = V2_ROOT / "skills" / "short-video-autopilot" / "scripts" / "pipeline_state.py"
FINALIZE = V2_ROOT / "skills" / "short-video-autopilot" / "scripts" / "finalize_project.py"


class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        (self.workspace / "原始素材" / "待处理" / "演示产品").mkdir(parents=True)
        (self.workspace / "原始素材" / "待处理" / "演示产品" / "clip.mp4").write_bytes(b"demo")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_state(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["python3", str(STATE), *args], text=True, capture_output=True, check=False
        )
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def init_project(self) -> Path:
        result = self.run_state("init", "--workspace", str(self.workspace))
        return Path(json.loads(result.stdout)["project_dir"])

    def register_framefield_ready(self, project: Path, mode: str, revision: int = 7) -> Path:
        framefield = project / "framefield"
        framefield.mkdir(exist_ok=True)
        (framefield / "project.json").write_text(
            json.dumps({"revision": revision}, ensure_ascii=False), encoding="utf-8"
        )
        artifact_name = "framefield_edit_ready" if mode == "edit" else "framefield_preview_ready"
        filename = "framefield-edit-ready.md" if mode == "edit" else "framefield-preview-ready.md"
        marker = "帧场剪辑就绪：通过" if mode == "edit" else "帧场预览就绪：通过"
        report = project / filename
        report.write_text(f"# {marker}\n\n- 工程修订：{revision}\n", encoding="utf-8")
        self.run_state(
            "artifact", "--project", str(project), "--name", artifact_name, "--path", str(report)
        )
        return report

    def test_happy_path_confirmations_and_review_gate(self) -> None:
        project = self.init_project()
        self.run_state("transition", "--project", str(project), "--to", "preflighting")
        preflight = project / "preflight.md"
        preflight.write_text("全部通过", encoding="utf-8")
        self.run_state(
            "artifact", "--project", str(project), "--name", "preflight", "--path", str(preflight)
        )
        for stage in ("analyzing", "copy_review", "awaiting_copy_approval"):
            if stage == "copy_review":
                evidence = project / "evidence-matrix.md"
                evidence.write_text("证据门槛：通过\n", encoding="utf-8")
                self.run_state(
                    "artifact", "--project", str(project), "--name", "evidence_matrix", "--path", str(evidence)
                )
            self.run_state("transition", "--project", str(project), "--to", stage)
        self.run_state("approve", "--project", str(project), "--kind", "copy")
        self.run_state("transition", "--project", str(project), "--to", "awaiting_voice_approval")
        self.run_state("approve", "--project", str(project), "--kind", "voice")
        edit_script = project / "edit-script.md"
        edit_script.write_text("已生成剪辑脚本", encoding="utf-8")
        self.run_state(
            "artifact", "--project", str(project), "--name", "edit_script", "--path", str(edit_script)
        )
        self.run_state(
            "transition", "--project", str(project), "--to", "awaiting_script_approval"
        )
        self.run_state("approve", "--project", str(project), "--kind", "edit_script")
        self.register_framefield_ready(project, "edit")
        self.run_state("transition", "--project", str(project), "--to", "validating")
        preview = project / "preview.mp4"
        preview.write_bytes(b"preview")
        self.run_state(
            "artifact", "--project", str(project), "--name", "preview", "--path", str(preview)
        )
        self.register_framefield_ready(project, "preview")
        self.run_state("transition", "--project", str(project), "--to", "awaiting_upload_approval")
        self.run_state("approve", "--project", str(project), "--kind", "upload")
        final = project / "final.mp4"
        final.write_bytes(b"final")
        self.run_state(
            "artifact", "--project", str(project), "--name", "final", "--path", str(final)
        )
        self.run_state("transition", "--project", str(project), "--to", "awaiting_cover_choice")
        self.run_state(
            "cover-choice", "--project", str(project), "--choice", "scrapbook"
        )
        cover = project / "cover.png"
        cover.write_bytes(b"cover")
        self.run_state(
            "artifact", "--project", str(project), "--name", "cover", "--path", str(cover)
        )
        for stage in ("uploading", "awaiting_manual_publish"):
            self.run_state("transition", "--project", str(project), "--to", stage)
        self.run_state(
            "published", "--project", str(project), "--platform", "抖音",
            "--work-id", "demo-1", "--url", "https://example.invalid/demo",
            "--published-at", "2026-01-01T00:00:00+08:00",
        )
        self.run_state("start-review", "--project", str(project))
        self.run_state("transition", "--project", str(project), "--to", "cleanup_pending")
        state = json.loads((project / "pipeline-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["stage"], "cleanup_pending")
        self.assertEqual(state["confirmations"]["copy"], "approved")
        self.assertEqual(state["confirmations"]["voice"], "approved")
        self.assertEqual(state["confirmations"]["edit_script"], "approved")
        self.assertEqual(state["confirmations"]["upload"], "approved")
        self.assertEqual(state["confirmations"]["cover"], "scrapbook")
        self.assertEqual(state["confirmations"]["manual_publish"], "approved")

    def test_copy_review_requires_passed_evidence_matrix(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "analyzing"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        self.run_state("transition", "--project", str(project), "--to", "copy_review", expected=2)
        evidence = project / "evidence-matrix.md"
        evidence.write_text("证据门槛：未通过\n", encoding="utf-8")
        self.run_state("artifact", "--project", str(project), "--name", "evidence_matrix", "--path", str(evidence))
        self.run_state("transition", "--project", str(project), "--to", "copy_review", expected=2)
        evidence.write_text("证据门槛：通过\n", encoding="utf-8")
        self.run_state("transition", "--project", str(project), "--to", "copy_review")

    def test_upload_requires_explicit_approval_after_preview(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "validating"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        self.run_state("transition", "--project", str(project), "--to", "awaiting_upload_approval", expected=2)
        preview = project / "preview.mp4"
        preview.write_bytes(b"preview")
        self.run_state("artifact", "--project", str(project), "--name", "preview", "--path", str(preview))
        self.run_state("transition", "--project", str(project), "--to", "awaiting_upload_approval", expected=2)
        self.register_framefield_ready(project, "preview")
        self.run_state("transition", "--project", str(project), "--to", "awaiting_upload_approval")
        self.run_state("transition", "--project", str(project), "--to", "exporting", expected=2)
        self.run_state("approve", "--project", str(project), "--kind", "upload")
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["stage"], "exporting")
        self.assertEqual(state["confirmations"]["upload"], "approved")

    def test_cover_choice_is_required_before_cover_creation_and_upload(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "exporting"
        state["confirmations"]["upload"] = "approved"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        self.run_state(
            "transition", "--project", str(project), "--to", "awaiting_cover_choice", expected=2
        )
        final = project / "final.mp4"
        final.write_bytes(b"final")
        self.run_state("artifact", "--project", str(project), "--name", "final", "--path", str(final))
        self.run_state("transition", "--project", str(project), "--to", "awaiting_cover_choice")
        self.run_state("transition", "--project", str(project), "--to", "publishing_prep", expected=2)
        self.run_state(
            "cover-choice", "--project", str(project), "--choice", "user_provided"
        )
        self.run_state("transition", "--project", str(project), "--to", "uploading", expected=2)
        cover = project / "user-cover.png"
        cover.write_bytes(b"cover")
        self.run_state("artifact", "--project", str(project), "--name", "cover", "--path", str(cover))
        self.run_state("transition", "--project", str(project), "--to", "uploading")

    def test_validation_requires_revision_matched_framefield_readiness(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "editing_framefield"
        state["confirmations"]["edit_script"] = "approved"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        self.run_state("transition", "--project", str(project), "--to", "validating", expected=2)
        self.register_framefield_ready(project, "edit", revision=7)
        (project / "framefield" / "project.json").write_text(
            json.dumps({"revision": 8}), encoding="utf-8"
        )
        self.run_state("transition", "--project", str(project), "--to", "validating", expected=2)
        self.register_framefield_ready(project, "edit", revision=8)
        self.run_state("transition", "--project", str(project), "--to", "validating")

    def test_editing_requires_an_approved_edit_script(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "script_generating"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        self.run_state(
            "transition", "--project", str(project), "--to", "editing_framefield", expected=2
        )
        self.run_state(
            "transition", "--project", str(project), "--to", "awaiting_script_approval", expected=2
        )

        edit_script = project / "edit-script.md"
        edit_script.write_text("镜头脚本", encoding="utf-8")
        self.run_state(
            "artifact", "--project", str(project), "--name", "edit_script", "--path", str(edit_script)
        )
        self.run_state(
            "transition", "--project", str(project), "--to", "awaiting_script_approval"
        )
        self.run_state(
            "reject", "--project", str(project), "--kind", "edit_script", "--reason", "镜头顺序需修改"
        )
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["stage"], "script_generating")
        self.assertEqual(state["confirmations"]["edit_script"], "rejected")

    def test_invalid_transition_and_block_resume(self) -> None:
        project = self.init_project()
        self.run_state(
            "transition", "--project", str(project), "--to", "exporting", expected=2
        )
        self.run_state("block", "--project", str(project), "--reason", "缺少产品事实")
        self.run_state("resume", "--project", str(project))
        state = json.loads((project / "pipeline-state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["stage"], "initialized")

    def test_review_rejects_a_project_younger_than_72_hours(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "published_waiting_72h"
        state["publication"]["published_at"] = "2999-01-01T00:00:00+08:00"
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        self.run_state("start-review", "--project", str(project), expected=2)

    def test_auto_revision_stops_after_three_rounds(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "validating"
        state["revision_rounds"] = 3
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
        self.run_state(
            "transition", "--project", str(project), "--to", "editing_framefield", expected=2
        )

    def test_finalize_only_audits_and_never_moves_runtime(self) -> None:
        project = self.init_project()
        state_path = project / "pipeline-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["stage"] = "cleanup_pending"
        state["artifacts"] = {}
        for key, name in {"final": "candidate.mp4", "voice": "candidate.wav", "copy": "locked.md", "review": "report.md"}.items():
            source = project / name
            source.write_bytes(b"non-empty")
            state["artifacts"][key] = str(source)
        (project / "temporary.cache").write_bytes(b"trash")
        state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")

        preview = subprocess.run(
            ["python3", str(FINALIZE), "--workspace", str(self.workspace), "--project", str(project)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertTrue(project.exists())
        audit = json.loads(preview.stdout)
        self.assertEqual(audit["mode"], "audit_only")
        self.assertEqual(audit["file_management"], "user_managed")

        commit = subprocess.run(
            ["python3", str(FINALIZE), "--workspace", str(self.workspace), "--project", str(project), "--commit"],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(commit.returncode, 2)
        self.assertIn("自动归档、移动和清理已禁用", commit.stderr)
        self.assertTrue(project.exists())
        self.assertTrue((project / "temporary.cache").exists())


if __name__ == "__main__":
    unittest.main()
