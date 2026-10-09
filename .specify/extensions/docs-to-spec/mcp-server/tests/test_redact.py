from docs_to_spec_mcp.redact import _luhn_ok, redact


def _luhn_complete(prefix: str) -> str:
    for digit in "0123456789":
        if _luhn_ok(prefix + digit):
            return prefix + digit
    raise AssertionError("unreachable")


def test_plain_requirement_untouched():
    text = "When the user saves a draft, the system shall show a confirmation within 2 seconds."
    out, counts = redact(text)
    assert out == text and counts == {}


def test_github_token():
    fake = "ghp_" + "a" * 36
    out, counts = redact(f"use {fake} here")
    assert fake not in out and counts["github_token"] == 1


def test_secret_assignment_keeps_key():
    out, counts = redact("api_key = not-a-real-value")
    assert out.startswith("api_key = [REDACTED:secret]") and counts["secret"] == 1


def test_card_needs_valid_checksum():
    valid = _luhn_complete("4" + "1" * 14)
    out, counts = redact(f"card {valid}")
    assert valid not in out and counts["card"] == 1
    invalid = valid[:-1] + str((int(valid[-1]) + 1) % 10)
    assert redact(f"ref {invalid}")[1].get("card") is None


def test_pan_format():
    fake = "A" * 5 + "0" * 4 + "A"
    assert redact(f"id {fake}")[1]["pan"] == 1


def test_aadhaar_format():
    fake = "2" + "0" * 11
    assert redact(f"id {fake}")[1]["aadhaar"] == 1


def test_url_credentials():
    out, counts = redact("https://user:pass@example.com/x")
    assert "user:pass" not in out and counts["url_credentials"] == 1
