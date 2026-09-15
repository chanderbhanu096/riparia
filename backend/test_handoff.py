"""Offline HTTP contract checks for site evidence, approval and provenance.

Run from backend: .venv/bin/python -m unittest -v test_handoff
Uses a temporary SQLite database and an ephemeral loopback server. No existing
observations are touched and the vision provider is forced to null.
"""

import json
from pathlib import Path
import socket
import tempfile
import threading
import time
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import config
from adapters import store
from api import observations
from domain import field_protocol as fp
from domain.handoff import site_key
from main import app
import uvicorn


class HandoffContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="riparia-test-")
        cls.old_path = store.DB_PATH
        cls.old_provider = config.VISION_PROVIDER
        cls.old_uploads = observations.UPLOADS
        store.DB_PATH = Path(cls.temp.name) / "observations.db"
        observations.UPLOADS = Path(cls.temp.name) / "uploads"
        observations.UPLOADS.mkdir()
        config.VISION_PROVIDER = "null"
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        cls.base = f"http://127.0.0.1:{sock.getsockname()[1]}"
        cls.server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
        cls.thread = threading.Thread(target=cls.server.run,
                                      kwargs={"sockets": [sock]}, daemon=True)
        cls.thread.start()
        deadline = time.monotonic() + 5
        while not cls.server.started and time.monotonic() < deadline:
            time.sleep(0.01)
        if not cls.server.started:
            raise RuntimeError("Temporary test server did not start")

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True
        cls.thread.join(timeout=5)
        store.DB_PATH = cls.old_path
        config.VISION_PROVIDER = cls.old_provider
        observations.UPLOADS = cls.old_uploads
        cls.temp.cleanup()

    def setUp(self):
        with store.connect() as con:
            con.execute("DELETE FROM observations")

    def request(self, path, data=None):
        body = urlencode(data).encode() if data is not None else None
        req = Request(self.base + path, data=body,
                      headers={"Content-Type": "application/x-www-form-urlencoded"})
        try:
            response = urlopen(req, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.loads(response.read()), response.headers

    def create(self, record_class="authentic", site="River test", indicators=None):
        original = {"water_clarity": "clear", "flow": "unsure",
                    "surrounding_land_use": "park", "wildlife_seen": "unsure",
                    "indicators": indicators or []}
        code, result, _ = self.request("/api/observations", {
            "answers_json": json.dumps(original), "record_class": record_class,
            "site_name": site,
        })
        self.assertEqual(code, 200)
        return result["id"], original

    def review(self, oid, approve=False, reviewer="DEMO coordinator", decision="Escalate for local investigation"):
        fingerprint = self.request(f"/api/observations/{oid}")[1]["content_sha256"]
        return self.request(f"/api/observations/{oid}/review", {
            "reviewer": reviewer, "decision": decision,
            "note": "Scripted test assessment, not independent validation.",
            "approved_for_summary": str(approve).lower(),
            "reviewed_content_sha256": fingerprint,
        })

    def clarify(self, oid, option="cyanobacteria"):
        diff = fp.differential_for("green_growth")
        return self.request(f"/api/observations/{oid}/clarify", {
            "question_id": diff["id"], "question": diff["question"],
            "field": "indicators", "indicator": "green_growth",
            "option_key": option, "response": diff["options"][option]["label"],
        })

    def test_review_status_or_free_text_never_implies_approval(self):
        oid, _ = self.create(indicators=["dead_fish"])
        self.assertEqual(self.request(f"/api/observations/{oid}/export")[0], 409)
        self.review(oid, decision="Accepted, validated, approved")
        result = self.request("/api/sites")[1]
        self.assertEqual(result["approved_count"], 0)
        self.assertEqual(result["pending_count"], 1)
        self.assertEqual(result["sites"][0]["high_urgency_count"], 0)
        self.assertEqual(result["sites"][0]["records"], [])
        self.assertEqual(self.request(f"/api/observations/{oid}/export")[0], 409)

    def test_three_classes_stay_separate_and_empty_is_honest(self):
        for kind in store.RECORD_CLASSES:
            oid, _ = self.create(kind)
            self.review(oid, approve=True)
        for kind in store.RECORD_CLASSES:
            result = self.request(f"/api/sites?record_class={kind}")[1]
            self.assertEqual(result["approved_count"], 1)
            self.assertEqual(result["sites"][0]["records"][0]["record_class"], kind)
        self.assertEqual(self.request("/api/sites")[1]["record_class"], "authentic")
        self.assertEqual(self.request("/api/sites?record_class=combined")[0], 422)

    def test_original_clarification_decision_and_history_survive_export(self):
        oid, original = self.create("synthetic", indicators=["green_growth"])
        self.clarify(oid)
        self.review(oid, approve=True, decision="Arrange coordinator review")
        self.review(oid, approve=True, reviewer="Second DEMO reviewer", decision="Escalate for site visit")
        code, payload, headers = self.request(f"/api/observations/{oid}/export")
        self.assertEqual(code, 200)
        rec = payload["records"][0]
        self.assertEqual(rec["original_answers"], original)
        self.assertEqual(rec["clarifications"][0]["option_key"], "cyanobacteria")
        self.assertEqual(rec["review"]["decision"], "Escalate for site visit")
        self.assertEqual(rec["review"]["history"][0]["decision"], "Arrange coordinator review")
        self.assertEqual(rec["review"]["reviewed_content_sha256"], rec["provenance"]["reviewed_content_sha256"])
        self.assertIn("attachment", headers["Content-Disposition"])
        self.assertEqual(headers["Cache-Control"], "no-store")
        self.assertEqual(store.get(oid)["answers"], original)

    def test_clarification_after_approval_requires_new_review(self):
        oid, original = self.create(indicators=["green_growth"])
        self.review(oid, approve=True)
        self.assertEqual(self.request("/api/sites")[1]["approved_count"], 1)
        self.clarify(oid)
        result = self.request(f"/api/observations/{oid}")[1]
        self.assertFalse(result["summary_eligibility"]["eligible"])
        self.assertEqual(self.request("/api/sites")[1]["approved_count"], 0)
        self.assertEqual(self.request(f"/api/observations/{oid}/export")[0], 409)
        self.review(oid, approve=True)
        self.assertEqual(self.request(f"/api/observations/{oid}/export")[0], 200)
        self.assertEqual(store.get(oid)["answers"], original)

    def test_reviewer_cannot_approve_changes_they_have_not_seen(self):
        oid, _ = self.create(indicators=["green_growth"])
        snapshot = self.request(f"/api/observations/{oid}")[1]["content_sha256"]
        self.clarify(oid)
        review_data = {"reviewer": "DEMO coordinator", "decision": "Use in summary",
                       "approved_for_summary": "true", "reviewed_content_sha256": snapshot}
        self.assertEqual(self.request(f"/api/observations/{oid}/review", review_data)[0], 409)
        del review_data["reviewed_content_sha256"]
        self.assertEqual(self.request(f"/api/observations/{oid}/review", review_data)[0], 400)
        self.assertIsNone(store.get(oid)["review"])

    def test_unapproved_concern_cannot_contaminate_approved_site_evidence(self):
        clean, _ = self.create()
        self.review(clean, approve=True)
        concern, _ = self.create(indicators=["green_growth"])
        self.clarify(concern)
        result = self.request("/api/sites")[1]["sites"][0]
        self.assertEqual(result["approved_count"], 1)
        self.assertEqual(result["pending_count"], 1)
        self.assertEqual(result["high_urgency_count"], 0)
        self.assertEqual(result["one_health_notes"], [])
        self.assertEqual([rec["id"] for rec in result["records"]], [clean])
        payload = self.request(result["export_url"])[1]
        self.assertEqual([rec["id"] for rec in payload["records"]], [clean])

    def test_fhir_remains_a_proposal_without_fictional_patient_or_exposure(self):
        oid, _ = self.create("synthetic", indicators=["green_growth"])
        self.clarify(oid)
        self.review(oid, approve=True)
        rec = self.request(f"/api/observations/{oid}/export")[1]["records"][0]
        proposal = rec["proposed_fhir_mapping"]
        self.assertEqual(proposal["status"], "proposed mapping")
        self.assertFalse(proposal["validated"])
        self.assertIsNone(proposal["profile"])
        self.assertIsNone(proposal["validator"])
        self.assertEqual([r["resourceType"] for r in proposal["resources"]], ["Location", "Observation", "Provenance"])
        observation = proposal["resources"][1]
        self.assertEqual(observation["status"], "preliminary")
        self.assertTrue(observation["subject"]["reference"].startswith("Location/"))
        self.assertNotIn("effectiveDateTime", observation)
        self.assertNotIn("valueQuantity", observation)
        self.assertEqual(rec["assessment"]["ecological_urgency"]["one_health_notes"],
                         [fp.ONE_HEALTH_READINGS["cyanobacterial_scum"]])

    def test_no_contact_pathway_means_no_fhir_observation(self):
        oid, _ = self.create(indicators=["litter"])
        self.review(oid, approve=True)
        rec = self.request(f"/api/observations/{oid}/export")[1]["records"][0]
        self.assertEqual(rec["proposed_fhir_mapping"]["resources"], [])

    def test_legacy_reviews_and_incomplete_reviewer_identity_do_not_approve(self):
        oid, _ = self.create()
        with store.connect() as con:
            con.execute("UPDATE observations SET review=?, review_status='reviewer_assessed' WHERE id=?",
                        (json.dumps({"reviewer": "Old name", "decision": "Accepted", "at": "2026-09-14T00:00:00Z"}), oid))
        self.assertEqual(self.request("/api/sites")[1]["approved_count"], 0)
        self.assertEqual(self.review(oid, approve=True, reviewer=" ")[0], 400)
        self.assertEqual(self.review(oid, approve=True, decision=" ")[0], 400)
        self.review(oid, approve=True)
        self.assertEqual(store.get(oid)["review"]["history"][0]["reviewer"], "Old name")

    def test_unknown_or_empty_sites_and_unnamed_locations(self):
        self.assertEqual(self.request("/api/sites")[1]["sites"], [])
        self.assertEqual(self.request("/api/sites/missing/export")[0], 404)
        self.assertEqual(self.request("/api/observations/missing/export")[0], 404)
        oid, _ = self.create()
        self.assertEqual(self.request(f"/api/sites/{site_key(store.get(oid))}/export")[0], 409)
        for name in ("", "Unnamed site", "Unnamed reach"):
            one, _ = self.create(site=name)
            two, _ = self.create(site=name)
            self.assertNotEqual(site_key(store.get(one)), site_key(store.get(two)))

    def test_same_camera_filename_cannot_replace_an_earlier_photo(self):
        def upload(content):
            boundary = "riparia-isolated-upload-test"
            body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"answers_json\"\r\n\r\n"
                    '{}\r\n'
                    f"--{boundary}\r\nContent-Disposition: form-data; name=\"record_class\"\r\n\r\n"
                    'evaluation\r\n'
                    f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"image.jpg\"\r\n"
                    "Content-Type: image/jpeg\r\n\r\n").encode()
            body += content + f"\r\n--{boundary}--\r\n".encode()
            req = Request(self.base + "/api/observations", data=body,
                          headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
            with urlopen(req, timeout=5) as response:
                return json.loads(response.read())["observation"]
        # Fixture bytes are intentionally not interpreted: provider=null exercises
        # preservation during a model outage without any paid/external request.
        first = upload(b"first camera fixture")
        second = upload(b"second camera fixture")
        self.assertNotEqual(first["photo_path"], second["photo_path"])
        first_file = observations.UPLOADS / Path(first["photo_path"]).name
        second_file = observations.UPLOADS / Path(second["photo_path"]).name
        self.assertEqual(first_file.read_bytes(), b"first camera fixture")
        self.assertEqual(second_file.read_bytes(), b"second camera fixture")

    def test_static_fallback_cannot_read_outside_its_directory(self):
        from main import DIST
        if not DIST.is_dir():
            self.skipTest("No built frontend mounted")
        self.assertEqual(self.request("/%2e%2e/%2e%2e/backend/main.py")[0], 404)


if __name__ == "__main__":
    unittest.main(verbosity=2)
