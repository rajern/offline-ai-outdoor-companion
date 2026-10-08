"""Bounded historical-context judge pilot. No retrieval/model-product imports.

prepare -> preflight -> run -> summarize. Private source-bearing files stay under
knowledge/local. Public gold, historical outputs, production and holdout are never
modified. CLI judge receives only one input through stdin in an empty temp folder.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
LOCAL_DEPS = ROOT / "knowledge/local/judge-pilot-deps"
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))
import yaml
from dotenv import dotenv_values
from jsonschema import Draft202012Validator

CONFIG = ROOT / "evals/retrieval_judge_pilot.v1.json"
PROMPT = ROOT / "evals/retrieval_judge_prompt.v1.md"
SCHEMA = ROOT / "evals/retrieval_judge_output.schema.v1.json"
DEFAULT_RUN = ROOT / "knowledge/local/diagnostics/retrieval-judge-pilot-v1-2026-10-08"
LABELS = ("irrelevant", "potentially_misleading", "jurisdiction_leakage", "optional_observed")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value, *, replace=False):
    if path.exists() and not replace:
        raise ValueError(f"Refusing overwrite: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def protected_files():
    # Explicit directories: NEVER recurse through evals (contains the holdout).
    return (list((ROOT / "backend/outwise").rglob("*.py"))
            + list((ROOT / "frontend").glob("*.tsx"))
            + [ROOT / p for p in ["frontend/api.ts", "evals/retrieval_cases.v1.yaml",
                "evals/retrieval_development.v2.yaml", "evals/retrieval_foundation.lock.json",
                "knowledge/manifests/approved-sources.json", "knowledge/local/knowledge.json",
                "knowledge/local/index.json", "knowledge/local/embeddings.npy"]])


def serialize_blocks(excerpts):
    return [{"block": n, "text": f"[KUNNSKAPSUTDRAG {n}]\nTittel: {e['item']['title']}\n"
             f"Tema: {e['item']['topic']}\nInnhold: {e['item']['text']}"}
            for n, e in enumerate(excerpts, 1)]


def judge_input(case, row):
    # Deliberately omit source locator lists, source quotes, source/candidate IDs,
    # configuration/ranks/scores and historical manual judgments.
    return {"case_id": case["id"], "question": case["question"],
            "jurisdiction": case["jurisdiction"], "expected_result": case["expected_result"],
            "requirements": [{"item": i, "requirement": text}
                             for i, text in enumerate(case["must_have_information"], 1)],
            "semantic_alternatives": case["acceptable_source_sections_or_chunks"],
            "optional_information": case["optional_useful_information"],
            "noise_criteria": case["irrelevant_or_potentially_misleading_information"],
            "knowledge_gap": case["knowledge_gap"], "gold_uncertainty": case["gold_uncertainty"],
            "blocks": serialize_blocks(row["excerpts"])}


def validate_result(result, inp, schema=None):
    schema = schema or read_json(SCHEMA)
    errors = [f"schema:{'/'.join(map(str, e.path))}:{e.validator}"
              for e in Draft202012Validator(schema).iter_errors(result)]
    if errors:
        return errors
    if result["case_id"] != inp["case_id"]:
        errors.append("case_id mismatch")
    expected = [r["item"] for r in inp["requirements"]]
    actual = [r["item"] for r in result["items"]]
    if sorted(actual) != expected or len(set(actual)) != len(actual):
        errors.append("expected exactly one item per requirement")
    blocks = {b["block"]: b["text"] for b in inp["blocks"]}
    entries = result["items"] + [v for label in LABELS for v in result[label]]
    for entry in entries:
        if not entry["reason"].strip():
            errors.append("empty reason")
        for ev in entry["evidence"]:
            if not ev["quote"].strip() or ev["block"] not in blocks or ev["quote"] not in blocks.get(ev["block"], ""):
                errors.append("quote absent from stated block")
        if "decision" not in entry:
            if not entry["evidence"]:
                errors.append("finding lacks evidence")
            continue
        if any(not s.strip() for s in entry["missing_components"]):
            errors.append("blank missing component")
        if entry["decision"] == "covered" and (entry["missing_components"] or not entry["evidence"]):
            errors.append("covered requires evidence and no missing components")
        if entry["decision"] == "not_covered" and not entry["missing_components"]:
            errors.append("not_covered requires missing components")
        if entry["decision"] == "uncertain" and not result["requires_review"]:
            errors.append("uncertain requires_review")
    # Structural consistency is checked; semantic entailment still needs calibration.
    return errors


def coverage(result, inp):
    decisions = [v["decision"] for v in result["items"]]
    unknown = decisions.count("uncertain")
    count = len(decisions)
    gap = inp["expected_result"] == "insufficient_coverage"
    review = result["requires_review"] or bool(unknown)
    return {"covered": decisions.count("covered"), "total": count, "unknown": unknown,
            "coverage": None if review or not count else decisions.count("covered") / count,
            "complete_pass": False if gap or not count else (None if review else all(d == "covered" for d in decisions)),
            "gap": gap, "requires_review": review}


def api_cost(usage, price):
    inp, out = usage["input_tokens"], usage["output_tokens"]
    cached = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0) or 0
    # Reasoning tokens are already included in output_tokens, never double billed.
    writes = (usage.get("input_tokens_details") or {}).get("cache_write_tokens", 0) or 0
    return ((inp - cached - writes) * price["input"] + cached * price["cached_input"]
            + writes * price.get("cache_write", price["input"])
            + out * price["output"]) / 1_000_000


def reservation(inp, prompt, schema, config, model):
    # UTF-8 byte bound is deliberately conservative for byte-based text tokenizers.
    # Include schema, prompt and generous envelope overhead; not reported as usage.
    text = prompt + json.dumps(inp, ensure_ascii=False) + json.dumps(schema, ensure_ascii=False)
    tokens_bound = len(text.encode("utf-8")) + 4096
    price = config["prices_usd_per_million"][model]
    return (tokens_bound * max(price["input"], price["cache_write"])
            + config["max_output_tokens"] * price["output"]) / 1_000_000


def ensure_budget(ledger, amount, cap):
    committed = sum(e.get("charged_or_reserved_usd", 0) for e in ledger)
    if committed + amount > cap:
        raise ValueError("API budget would be exceeded; stop before request")
    return committed


def api_client():
    from openai import OpenAI
    key = dotenv_values(ROOT / ".env", interpolate=False).get("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY missing from project-root .env")
    return OpenAI(api_key=key, base_url="https://api.openai.com/v1", timeout=240, max_retries=0)


def safe_error(error):
    # Never log exception strings/headers/requests (can contain sensitive values).
    return {"type": type(error).__name__, "status_code": getattr(error, "status_code", None),
            "code": getattr(error, "code", None)}


def prepare(directory):
    if directory.exists():
        raise ValueError("Pilot exists; resume it instead of overwriting")
    config = read_json(CONFIG)
    cases = yaml.safe_load((ROOT / "evals/retrieval_development.v2.yaml").read_text(encoding="utf-8"))
    lock = read_json(ROOT / "evals/retrieval_foundation.lock.json")
    if sha(ROOT / "evals/retrieval_development.v2.yaml") != lock["files"]["evals/retrieval_development.v2.yaml"]["sha256"]:
        raise ValueError("Development identity changed")
    if sha(ROOT / "knowledge/local/knowledge.json") != lock["corpus_sha256"]:
        raise ValueError("Corpus identity changed")
    selected = {c["id"]: c for c in cases["cases"][:15] if c["id"] in config["cases"]}
    if set(selected) != set(config["cases"]) or len(selected) != 6:
        raise ValueError("Pilot must select exactly six legacy questions")
    source_hashes, prepared, references = {}, [], {}
    for mode, folder in config["historical_runs"].items():
        base = ROOT / "knowledge/local/diagnostics" / folder
        rows_file, scores_file = base / "retrieved-all.json", base / "scoring.json"
        rows, scores = read_json(rows_file), read_json(scores_file)
        for f in [rows_file, scores_file]:
            source_hashes[str(f.relative_to(ROOT))] = sha(f)
        for row in rows:
            if row["configuration"] != mode or row["case_id"] not in selected:
                continue
            if row["corpus_hash"] != lock["corpus_sha256"] or row["gold_hash"] != lock["gold_legacy_immutable"]:
                raise ValueError("Historical gold/corpus mismatch")
            context_file = base / mode / row["case_id"] / "context.txt"
            context = context_file.read_text(encoding="utf-8")
            blocks = serialize_blocks(row["excerpts"])
            if "\n\n".join(b["text"] for b in blocks) != context or text_sha(context) != row["context_sha256"]:
                raise ValueError("Delivered context identity mismatch")
            for e in row["excerpts"]:
                m = e["item"]["metadata"]
                if not e["item"].get("license") or not m.get("licence_url"):
                    raise ValueError("Source reuse metadata missing")
            payload = judge_input(selected[row["case_id"]], row)
            prepared.append({"configuration": mode, "case_id": row["case_id"],
                             "payload": payload, "context_sha256": row["context_sha256"]})
            references[(mode, row["case_id"])] = scores[mode][row["case_id"]]
            source_hashes[str(context_file.relative_to(ROOT))] = sha(context_file)
    if len(prepared) != 30:
        raise ValueError("Expected 30 historical contexts")
    random.Random(20261008).shuffle(prepared)
    index = []
    for n, entry in enumerate(prepared, 1):
        cid = f"context-{n:02}"
        index.append({"context_id": cid, "case_id": entry["case_id"], "configuration": entry["configuration"],
                      "context_sha256": entry["context_sha256"], "input_sha256": text_sha(json.dumps(entry["payload"], ensure_ascii=False))})
        write_json(directory / "inputs" / f"{cid}.json", entry["payload"])
        write_json(directory / "references" / f"{cid}.json", references[(entry["configuration"], entry["case_id"])])
    prompt, schema = PROMPT.read_text(encoding="utf-8"), read_json(SCHEMA)
    Draft202012Validator.check_schema(schema)
    (directory / "prompt.md").write_text(prompt, encoding="utf-8")
    write_json(directory / "schema.json", schema)
    write_json(directory / "config.json", config)
    write_json(directory / "index.json", index)
    protected = {str(p.relative_to(ROOT)): sha(p) for p in protected_files()}
    code_files = [CONFIG, PROMPT, SCHEMA, Path(__file__).resolve()]
    freeze = {"created_at": datetime.now(timezone.utc).isoformat(), "cases": config["cases"],
              "pilot_contexts": 30, "holdout_read": False, "protected_files": protected,
              "historical_inputs": source_hashes,
              "code_hashes": {str(p.relative_to(ROOT)): sha(p) for p in code_files},
              "private_files": {str(p.relative_to(directory)): sha(p)
                                for p in directory.rglob("*") if p.is_file()},
              "dependencies": {p: version(p) for p in ["openai", "python-dotenv", "jsonschema", "PyYAML"]},
              "reference_origin": config["reference_status"],
              "reuse_review": "Only stored excerpts from approved publishers; licence, attribution and frozen reuse metadata retained locally. No images, whole corpus, new sources or public excerpt publication. Explicit owner permission for API pilot; provider receives necessary excerpts and gold paraphrases only.",
              "conservative_total_api_reservation_usd": sum(reservation(read_json(directory / "inputs" / f"{e['context_id']}.json"), prompt, schema, config, model)
                  for e in index for model in config["api_models"])}
    write_json(directory / "freeze.json", freeze)
    print(json.dumps({"prepared": 30, "cases": config["cases"], "api_reservation": freeze["conservative_total_api_reservation_usd"]}))


def verify_freeze(directory):
    frozen = read_json(directory / "freeze.json")
    for field in ["protected_files", "historical_inputs", "code_hashes"]:
        for name, expected in frozen[field].items():
            if sha(ROOT / name) != expected:
                raise ValueError(f"Frozen {field} identity changed: {name}")
    for name, expected in frozen["private_files"].items():
        if sha(directory / name) != expected:
            raise ValueError(f"Frozen pilot input changed: {name}")
    return frozen


def codex_environment():
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("OPENAI_", "AZURE_OPENAI_")) or key in {"CODEX_API_KEY", "CODEX_ACCESS_TOKEN", "CODEX_THREAD_ID", "CODEX_SESSION_ID", "CODEX_APP_TOOLS_PIPE_PATH", "CODEX_INTERNAL_ORIGINATOR_OVERRIDE"}:
            env.pop(key)
    return env


def codex_command(cli, temp, config, *, output=True):
    flags = {"model_reasoning_effort": '"medium"', "forced_login_method": '"chatgpt"',
             "approval_policy": '"never"', "web_search": '"disabled"',
             "project_doc_max_bytes": "0", "skills.include_instructions": "false",
             "skills.bundled.enabled": "false", "tools.update_plan.enabled": "false",
             "tools.experimental_request_user_input.enabled": "false",
             "model_instructions_file": json.dumps(str(temp / "instructions.md")),
             "features.shell_tool": "false", "features.unified_exec": "false",
             "features.apps": "false", "features.plugins": "false", "features.multi_agent": "false",
             "features.multi_agent_v2": "false", "features.memories": "false", "features.hooks": "false",
             "features.computer_use": "false", "features.browser_use": "false",
             "features.code_mode": "false", "features.code_mode_host": "false",
             "features.skill_search": "false", "features.skip_host_skill_discovery": "true",
             "features.goals": "false", "features.sleep_tool": "false"}
    flags.update(suppress_unstable_features_warning="true", **{
        "features.shell_snapshot": "false", "include_collaboration_mode_instructions": "false"})
    cmd = [cli, "exec", "--ignore-user-config", "--ignore-rules", "--ephemeral", "--strict-config",
           "--skip-git-repo-check", "--sandbox", "read-only", "--model", config["codex_model"],
           "--cd", str(temp), "--color", "never", "--json", "--output-schema", str(temp / "schema.json")]
    for key, value in flags.items():
        cmd += ["-c", key + "=" + value]
    if output:
        cmd += ["--output-last-message", str(temp / "answer.json")]
    return cmd + ["-"]


def codex_call(inp, directory, config, prompt, schema, cli):
    # External temp directory prevents automatic ancestor repository discovery.
    with tempfile.TemporaryDirectory(prefix="outwise-judge-") as name:
        temp = Path(name)
        (temp / "instructions.md").write_text(prompt, encoding="utf-8")
        write_json(temp / "schema.json", schema)
        command = codex_command(cli, temp, config)
        started = time.perf_counter()
        done = subprocess.run(command, input=json.dumps(inp, ensure_ascii=False), cwd=temp,
                              env=codex_environment(), capture_output=True, encoding="utf-8",
                              errors="replace", timeout=config["timeout_seconds"])
        elapsed = time.perf_counter() - started
        events = []
        for line in done.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        raw = {"returncode": done.returncode, "events": events, "stderr": done.stderr,
               "model_requested": config["codex_model"], "reasoning_requested": "medium"}
        answer = read_json(temp / "answer.json") if (temp / "answer.json").is_file() else None
        usage = next((e.get("usage") for e in reversed(events) if e.get("type") == "turn.completed"), None)
        tool_events = [e for e in events if e.get("item", {}).get("type") not in {None, "agent_message", "reasoning", "error"}]
        if done.returncode or answer is None:
            return raw, None, usage, elapsed, ["Codex execution failed"]
        if tool_events:
            return raw, None, usage, elapsed, ["Codex tool/event isolation violation"]
        # --json does not expose a server model/revision. The explicit command and
        # catalog preflight verify requested settings; keep server identity unknown.
        raw["model_identity_limit"] = "CLI requested/catalog model verified; server model/revision not returned by JSONL"
        return raw, answer, usage, elapsed, []


def preflight(directory):
    verify_freeze(directory)
    config = read_json(directory / "config.json")
    result = {"api": {}, "codex": {}}
    try:
        client = api_client()
        for model in config["api_models"]:
            try:
                data = client.models.retrieve(model)
                result["api"][model] = {"available": data.id == model, "id": data.id}
            except Exception as error:
                result["api"][model] = {"available": False, "error": safe_error(error)}
    except Exception as error:
        result["api_error"] = safe_error(error)
    cli = shutil.which("codex")
    if cli:
        status = subprocess.run([cli, "login", "status"], env=codex_environment(), capture_output=True,
                                encoding="utf-8", errors="replace", timeout=30)
        result["codex"] = {"cli": cli, "chatgpt_login": "Logged in using ChatGPT" in status.stdout + status.stderr,
            "version": subprocess.run([cli, "--version"], capture_output=True, encoding="utf-8", timeout=30).stdout.strip()}
        cache = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "models_cache.json"
        if cache.is_file():
            matching = [m for m in read_json(cache).get("models", []) if m.get("slug") == config["codex_model"]]
            result["codex"]["model_catalog_sha256"] = sha(cache)
            result["codex"]["model_configuration_verified"] = bool(matching and any(
                e["effort"] == "medium" for e in matching[0].get("supported_reasoning_levels", [])))
            result["codex"]["model_catalog_id"] = matching[0]["slug"] if matching else None
    else:
        result["codex"] = {"available": False, "reason": "CLI not found"}
    write_json(directory / "preflight.json", result, replace=True)
    print(json.dumps(result))


def run(directory, alternatives):
    verify_freeze(directory)
    config = read_json(directory / "config.json")
    schema, prompt = read_json(directory / "schema.json"), (directory / "prompt.md").read_text(encoding="utf-8")
    pre = read_json(directory / "preflight.json")
    ledger_file = directory / "api-ledger.json"
    ledger = read_json(ledger_file) if ledger_file.exists() else []
    client = None
    for alt in alternatives:
        model = config["codex_model"] if alt == "sol-codex" else {"luna-api": "gpt-6-luna", "sol-api": "gpt-6.1-sol"}[alt]
        if alt != "sol-codex" and not pre.get("api", {}).get(model, {}).get("available"):
            print(f"{alt}: unavailable; no substitutions", flush=True)
            continue
        if alt == "sol-codex" and not (pre["codex"].get("chatgpt_login") and pre["codex"].get("model_configuration_verified")):
            print("sol-codex: ChatGPT authentication unavailable", flush=True)
            continue
        for meta in read_json(directory / "index.json"):
            cid = meta["context_id"]
            outdir = directory / "results" / alt / cid
            record_file = outdir / "record.json"
            if record_file.exists():
                continue  # Completed/failed/uncertain attempts are never silently repurchased.
            inp = read_json(directory / "inputs" / f"{cid}.json")
            begin = time.perf_counter()
            record = {"alternative": alt, "model_requested": model, "reasoning_effort": "medium",
                      "case_id": meta["case_id"], "context_id": cid, "input_sha256": meta["input_sha256"],
                      "billing": "chatgpt_subscription" if alt == "sol-codex" else "api",
                      "usage": None, "estimated_api_cost_usd": None, "success": False}
            try:
                if alt == "sol-codex":
                    raw, answer, usage, elapsed, errors = codex_call(inp, directory, config, prompt, schema, pre["codex"]["cli"])
                    write_json(outdir / "raw.json", raw)
                    record.update(usage=usage, elapsed_seconds=elapsed, execution_errors=errors)
                    if errors:
                        record["validation_errors"] = errors
                        write_json(record_file, record)
                        print(f"{alt} {cid}: blocked; see private raw log", flush=True)
                        break  # Isolation/model failure blocks all further CLI comparisons.
                    record["model_reported"] = None
                    record["model_configuration_verified"] = True
                    record["server_identity_limit"] = raw["model_identity_limit"]
                else:
                    amount = reservation(inp, prompt, schema, config, model)
                    ensure_budget(ledger, amount, config["api_budget_usd"])
                    # Journal reservation BEFORE the network call; crashes retain it.
                    existing = next((e for e in ledger if e["alternative"] == alt and e["context_id"] == cid), None)
                    if existing:
                        raise ValueError("In-flight/failed journal entry requires manual reconciliation; no retry")
                    entry = {"alternative": alt, "context_id": cid, "reserved_usd": amount,
                             "charged_or_reserved_usd": amount, "state": "in_flight"}
                    ledger.append(entry)
                    write_json(ledger_file, ledger, replace=True)
                    client = client or api_client()
                    response = client.responses.create(model=model, reasoning={"effort": "medium"},
                        instructions=prompt, input=json.dumps(inp, ensure_ascii=False), tools=[], store=False,
                        service_tier="default", max_output_tokens=config["max_output_tokens"],
                        text={"format": {"type": "json_schema", "name": "outwise_retrieval_judge", "strict": True, "schema": schema}})
                    raw = response.model_dump(mode="json")
                    write_json(outdir / "raw.json", raw)
                    record.update(usage=raw.get("usage"), model_reported=raw.get("model"),
                                  elapsed_seconds=time.perf_counter() - begin, response_status=raw.get("status"))
                    if record["usage"]:
                        cost = api_cost(record["usage"], config["prices_usd_per_million"][model])
                        record["estimated_api_cost_usd"] = cost
                        entry.update(charged_or_reserved_usd=cost, state="usage_received", usage=record["usage"])
                        write_json(ledger_file, ledger, replace=True)
                    if raw.get("status") != "completed" or raw.get("model") != model:
                        raise ValueError("Incomplete API response or unexpected model")
                    answer = json.loads(response.output_text)
                write_json(outdir / "answer.json", answer)
                errors = validate_result(answer, inp, schema)
                record.update(validation_errors=errors, success=not errors)
                if not errors:
                    record["coverage"] = coverage(answer, inp)
            except Exception as error:
                record.update(error=safe_error(error), elapsed_seconds=time.perf_counter() - begin,
                              validation_errors=record.get("validation_errors", []))
            write_json(record_file, record)
            spent = sum(e["charged_or_reserved_usd"] for e in ledger)
            print(f"{alt} {cid} {meta['case_id']}: {'valid' if record['success'] else 'FAILED'}; API committed ${spent:.6f}", flush=True)
            if not record["success"] and record.get("error", {}).get("status_code") in {401, 403, 404, 429}:
                break
    verify_freeze(directory)


def summarize(directory):
    verify_freeze(directory)
    summary, disagreements = {}, []
    for alt in ["luna-api", "sol-api", "sol-codex"]:
        rows = []
        counts = Counter()
        tokens = Counter()
        cost, seconds = 0.0, 0.0
        for meta in read_json(directory / "index.json"):
            outdir = directory / "results" / alt / meta["context_id"]
            if not (outdir / "record.json").exists():
                continue
            record = read_json(outdir / "record.json")
            counts["attempted"] += 1
            seconds += record.get("elapsed_seconds", 0)
            cost += record.get("estimated_api_cost_usd") or 0
            usage = record.get("usage") or {}
            for k in ["input_tokens", "output_tokens", "total_tokens", "cached_input_tokens"]:
                if isinstance(usage.get(k), int):
                    tokens[k] += usage[k]
            if isinstance(usage.get("reasoning_output_tokens"), int):
                tokens["reasoning_tokens"] += usage["reasoning_output_tokens"]
            for outer, inner, label in [("input_tokens_details", "cached_tokens", "cached_input_tokens"),
                                         ("output_tokens_details", "reasoning_tokens", "reasoning_tokens")]:
                if isinstance((usage.get(outer) or {}).get(inner), int):
                    tokens[label] += usage[outer][inner]
            if not record["success"]:
                counts["invalid_or_failed"] += 1
                counts["validation_errors"] += len(record.get("validation_errors", []))
                continue
            answer = read_json(outdir / "answer.json")
            inp = read_json(directory / "inputs" / f"{meta['context_id']}.json")
            ref = read_json(directory / "references" / f"{meta['context_id']}.json")
            counts["valid"] += 1
            counts["requires_review_contexts"] += int(answer["requires_review"])
            counts["gap_contexts"] += int(inp["expected_result"] == "insufficient_coverage")
            judges = {i["item"]: i for i in answer["items"]}
            for n, reference in enumerate(ref["items"], 1):
                judge = judges[n]
                counts["item_total"] += 1
                if judge["decision"] == "uncertain":
                    counts["uncertain"] += 1
                    continue
                covered = judge["decision"] == "covered"
                counts["resolved"] += 1
                counts["item_agreement"] += int(covered == reference["covered"])
                counts["false_positive_vs_reference"] += int(covered and not reference["covered"])
                counts["false_negative_vs_reference"] += int(not covered and reference["covered"])
                if covered != reference["covered"]:
                    disagreements.append({"alternative": alt, **meta, "item": n,
                        "requirement": inp["requirements"][n-1]["requirement"], "judge": judge, "reference": reference})
            score = coverage(answer, inp)
            if not score["gap"]:
                counts["supported_contexts"] += 1
                if score["complete_pass"] is not None:
                    counts["case_resolved"] += 1
                    reference_pass = bool(ref["items"]) and all(i["covered"] for i in ref["items"])
                    counts["case_agreement"] += int(score["complete_pass"] == reference_pass)
                    counts["false_complete_pass_vs_reference"] += int(score["complete_pass"] and not reference_pass)
            for label in LABELS[:3]:
                counts[label + "_disagreement"] += int(bool(answer[label]) != bool(ref[label]))
                counts[label + "_reference_positive"] += int(bool(ref[label]))
                counts[label + "_judge_positive"] += int(bool(answer[label]))
            rows.append({**meta, "coverage": score,
                         "noise_flags": {label: bool(answer[label]) for label in LABELS[:3]}})
        if alt == "sol-codex" and tokens:
            tokens["total_tokens"] = tokens["input_tokens"] + tokens["output_tokens"]
        summary[alt] = {"counts": dict(counts), "tokens": dict(tokens), "elapsed_seconds": seconds,
                       "estimated_api_cost_usd": None if alt == "sol-codex" else cost,
                       "billing": "ChatGPT subscription; USD not measurable" if alt == "sol-codex" else "API estimated from usage",
                       "rows": rows}
    write_json(directory / "summary.json", {"alternatives": summary, "disagreements": disagreements,
               "reference_caution": "Agent-authored historical references; disagreement is not expert-ground-truth error",
               "holdout_accessed": False}, replace=True)
    print(json.dumps({a: {k:v for k,v in s.items() if k != "rows"} for a,s in summary.items()}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "preflight", "run", "summarize"])
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN)
    parser.add_argument("--alternatives", nargs="+", choices=["luna-api", "sol-api", "sol-codex"],
                        default=["luna-api", "sol-api", "sol-codex"])
    args = parser.parse_args()
    # Restrict source-bearing outputs to the already ignored repository-local tree.
    directory = args.run_dir.resolve()
    if not directory.is_relative_to((ROOT / "knowledge/local").resolve()):
        parser.error("Pilot outputs must remain under ignored knowledge/local")
    if args.command == "prepare": prepare(directory)
    elif args.command == "preflight": preflight(directory)
    elif args.command == "run": run(directory, args.alternatives)
    else: summarize(directory)


if __name__ == "__main__":
    main()
