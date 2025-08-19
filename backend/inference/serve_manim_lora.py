import os
import re
import json
import tempfile
from typing import Optional, Dict, Any

import torch
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

MODEL_BASE = os.environ.get("MODEL_BASE", "Qwen/Qwen2.5-1.5B-Instruct")
ADAPTER_PATH = os.environ.get("ADAPTER_PATH", "").strip()
ADAPTER_GCS_URI = os.environ.get("ADAPTER_GCS_URI", "").strip()  # e.g., gs://bucket/adapter_dir/

USE_GPU = torch.cuda.is_available()


def _maybe_download_from_gcs(gcs_uri: str) -> str:
    """Download a directory from GCS to a local temp folder; return local path.
    Requires google-cloud-storage when used.
    """
    from google.cloud import storage  # type: ignore
    assert gcs_uri.startswith("gs://")
    # Parse
    without_scheme = gcs_uri[len("gs://"):]
    parts = without_scheme.split("/", 1)
    bucket_name = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = client.list_blobs(bucket, prefix=prefix)
    local_dir = tempfile.mkdtemp(prefix="adapter_")
    for blob in blobs:
        rel = blob.name[len(prefix):].lstrip("/")
        if not rel:
            continue
        local_path = os.path.join(local_dir, rel)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)
    return local_dir


def load_model_and_tokenizer() -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_BASE, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    base = AutoModelForCausalLM.from_pretrained(
        MODEL_BASE,
        torch_dtype=torch.bfloat16 if USE_GPU else torch.float32,
        device_map="auto" if USE_GPU else None,
    )
    adapter_dir = ADAPTER_PATH
    if (not adapter_dir) and ADAPTER_GCS_URI:
        adapter_dir = _maybe_download_from_gcs(ADAPTER_GCS_URI)
    if not adapter_dir:
        raise RuntimeError("No adapter path provided. Set ADAPTER_PATH or ADAPTER_GCS_URI.")
    model = PeftModel.from_pretrained(base, adapter_dir)
    model.eval()
    return model, tokenizer


model, tokenizer = load_model_and_tokenizer()

app = FastAPI()


class GenerateReq(BaseModel):
    prompt: str
    max_new_tokens: int = 400


def extract_first_json(s: str) -> str:
    for m in re.finditer(r"\{[\s\S]*?\}", s):
        candidate = m.group(0)
        try:
            json.loads(candidate)
            return candidate
        except Exception:
            continue
    idx = s.find("JSON:")
    scan = s[idx + 5 :] if idx != -1 else s
    start = scan.find("{")
    if start == -1:
        raise ValueError("No opening brace found in generated text")
    buf: list[str] = []
    depth = 0
    in_str = False
    esc = False
    for ch in scan[start:]:
        buf.append(ch)
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = "".join(buf)
                    json.loads(candidate)
                    return candidate
    raise ValueError("Could not extract balanced JSON")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate")
def generate(r: GenerateReq) -> Dict[str, Any]:
    schema_hint = os.environ.get("SCHEMA_HINT", "")
    full_prompt = (
        f"Task: Create a structured Manim animation for: {r.prompt}\n"
        f"{schema_hint}\nJSON:"
    )
    inputs = tokenizer(full_prompt, return_tensors="pt")
    if USE_GPU:
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        gen_ids = model.generate(
            **inputs,
            max_new_tokens=r.max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    cont = tokenizer.decode(
        gen_ids[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )
    json_text = extract_first_json(cont.strip())
    return {"json": json.loads(json_text)}


