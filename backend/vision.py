"""Photo pass via Azure AI Foundry (AI Services), vision-capable chat deployment.

WHAT THIS MODULE IS ALLOWED TO DO (AUDIT.md D-023):

    Raise a question for the citizen. That is all.

It may NOT set urgency, resolve an indicator, alter a record, or contribute to any
decision. Its entire output is advisory input to detected_inconsistency(), which
turns findings into neutrally-phrased questions that the citizen is free to reject.

WHY THE CONSTRAINT IS THIS TIGHT
--------------------------------
On the very first call made against this deployment, with a 96x96 PNG consisting
of two flat colour bands (green above, brown below -- no rocks, no vegetation, no
water, no texture at all), gpt-4.1-mini replied:

    "The image shows a flowing body of water surrounded by rocks and vegetation,
     which qualifies as a watercourse."

Confident, fluent, specific, entirely invented. That is risk R8 -- confident
scientific error -- demonstrated by the exact model we ship, on the exact task we
were about to trust it with. Everything below follows from that result.

TRI-STATE FINDINGS
------------------
Findings are True or None. NEVER False.

"I did not see litter" is not evidence that there is no litter; it is the absence
of evidence. Recording it as False would let a model's blind spot masquerade as an
observation, and would eventually be used to contradict a citizen who was right.
"""

import base64
import json
import mimetypes
import pathlib
import urllib.error
import urllib.request
from typing import Any

_ENV_PATH = pathlib.Path(__file__).parent / ".env"

# Deliberately narrow and low-inference. The model is asked what is IN FRAME, never
# what it MEANS -- all ecological interpretation lives in field_protocol.py, where
# it is cited. Asking a general-purpose model to interpret stream ecology is the
# failure mode this whole project exists to prevent.
_PROMPT = """You are helping check a photograph submitted with a citizen report about a stream.

Answer ONLY about what is literally visible in this image. Do not infer, do not
describe what a stream usually looks like, and do not fill in detail you cannot
actually see. If the image is unclear, abstract, too small, or ambiguous, say so.
Answering "cannot tell" is the correct and preferred answer whenever you are not
certain. You will not be penalised for it.

Return ONLY this JSON object, with no other text:
{
  "shows_watercourse": "yes" | "no" | "cannot_tell",
  "visible_litter": "yes" | "cannot_tell",
  "appears_turbid": "yes" | "cannot_tell",
  "what_i_literally_see": "<one short sentence, only things actually in the image>"
}

Note: for "visible_litter" and "appears_turbid" there is deliberately no "no"
option. Only report "yes" when you can actually see it; otherwise "cannot_tell".
"""


def _config() -> dict[str, str] | None:
    if not _ENV_PATH.exists():
        return None
    env = dict(
        line.split("=", 1)
        for line in _ENV_PATH.read_text().splitlines()
        if "=" in line and not line.startswith("#")
    )
    need = ("AZURE_AI_ENDPOINT", "AZURE_AI_DEPLOYMENT", "AZURE_AI_API_VERSION",
            "AZURE_AI_KEY")
    return env if all(env.get(k) for k in need) else None


def analyse(photo_path: pathlib.Path | None, timeout: float = 20.0
            ) -> tuple[dict[str, Any] | None, str]:
    """Return (findings, status).

    status is one of: "ok", "unavailable", "no_photo".

    EVERY failure returns (None, "unavailable") -- missing config, network error,
    HTTP error, timeout, malformed JSON, unexpected shape. There is no error path
    that raises into the request handler, because a model problem must never cost
    a citizen their observation (AUDIT.md A4).
    """
    if photo_path is None or not photo_path.exists():
        return None, "no_photo"

    cfg = _config()
    if cfg is None:
        return None, "unavailable"

    try:
        raw = photo_path.read_bytes()
        mime = mimetypes.guess_type(photo_path.name)[0] or "image/jpeg"
        b64 = base64.b64encode(raw).decode()

        url = (cfg["AZURE_AI_ENDPOINT"].rstrip("/") + "/openai/deployments/"
               + cfg["AZURE_AI_DEPLOYMENT"] + "/chat/completions?api-version="
               + cfg["AZURE_AI_API_VERSION"])
        body = {
            "messages": [
                {"role": "system",
                 "content": "You return only valid JSON. You never invent detail."},
                {"role": "user", "content": [
                    {"type": "text", "text": _PROMPT},
                    {"type": "image_url",
                     "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "low"}},
                ]},
            ],
            "max_tokens": 200,
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        req = urllib.request.Request(
            url, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "api-key": cfg["AZURE_AI_KEY"]},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.load(resp)
        text = payload["choices"][0]["message"]["content"]
        parsed = json.loads(text)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError,
            json.JSONDecodeError, KeyError, IndexError, OSError):
        return None, "unavailable"

    return _to_findings(parsed), "ok"


def _to_findings(parsed: dict[str, Any]) -> dict[str, Any]:
    """Map the model's reply to tri-state findings.

    "cannot_tell" and any unexpected value both become None. Only an explicit
    "yes" (or an explicit "no" for the watercourse question, which is the one
    place a negative is meaningful) becomes a usable finding.
    """
    def yes_no_maybe(v: Any) -> bool | None:
        if v == "yes":
            return True
        if v == "no":
            return False
        return None

    def yes_or_none(v: Any) -> bool | None:
        # No False is representable here, on purpose. See the module docstring.
        return True if v == "yes" else None

    return {
        "shows_watercourse": yes_no_maybe(parsed.get("shows_watercourse")),
        "visible_litter": yes_or_none(parsed.get("visible_litter")),
        "appears_turbid": yes_or_none(parsed.get("appears_turbid")),
        "model_description": str(parsed.get("what_i_literally_see", ""))[:300],
        "advisory_only": (
            "Model output. Used only to raise a question for the citizen; it never "
            "sets urgency, resolves an indicator, or decides anything."
        ),
    }
