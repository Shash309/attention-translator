"""Web demo: translate EN -> FR with all three systems and show the attention heatmap.

python app.py   ->   http://127.0.0.1:5000
"""
import os
import random
import re
import threading
import time

import torch
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

import rule_based
from data import read_split, tokenize
from evaluate import load_checkpoint, translate

ROOT = os.path.dirname(os.path.abspath(__file__))
MAX_CHARS = 300
MAX_TOKENS = 60

app = Flask(__name__, static_folder=os.path.join(ROOT, "web"))
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024  # reject huge request bodies early
device = "cuda" if torch.cuda.is_available() else "cpu"
lock = threading.Lock()  # models aren't thread-safe; serialize inference
models, status = {}, {}


def load_models():
    for name in ("attention", "baseline"):
        path = os.path.join(ROOT, "checkpoints", f"{name}.pt")
        try:
            models[name] = load_checkpoint(path, device)
            status[name] = "ok"
        except FileNotFoundError:
            status[name] = f"missing {os.path.relpath(path, ROOT)} - run: python train.py" + \
                           (" --no-attention" if name == "baseline" else "")
        except Exception as e:  # corrupt / incompatible checkpoint
            status[name] = f"failed to load: {e}"
    try:
        import pickle
        with open(os.path.join(ROOT, rule_based.DICT_PATH), "rb") as f:
            models["rule"] = pickle.load(f)
        status["rule"] = "ok"
    except FileNotFoundError:
        status["rule"] = "missing dictionary - run: python rule_based.py"
    except Exception as e:
        status["rule"] = f"failed to load: {e}"
    # Warm-up pass so the first real request doesn't pay CUDA/cuDNN start-up cost.
    with torch.inference_mode():
        for name in ("attention", "baseline"):
            if name in models:
                translate(models[name][0], "a dog runs .", models[name][1], models[name][2], device, beam=2)


def detok(tokens):
    """Join tokens into readable French: no space before punctuation or after elisions."""
    text = " ".join(tokens)
    text = re.sub(r"\s+([.,!?;:)])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    text = re.sub(r"(\w') ", r"\1", text)
    return text[:1].upper() + text[1:] if text else text


def error(msg, code=400):
    return jsonify({"error": msg}), code


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    info = {}
    for name in ("attention", "baseline"):
        if name in models:
            model, src_vocab, tgt_vocab = models[name]
            info[name] = {"params": sum(p.numel() for p in model.parameters()), "config": model.config,
                          "src_vocab": len(src_vocab), "tgt_vocab": len(tgt_vocab)}
    if "rule" in models:
        info["rule"] = {"entries": len(models["rule"])}
    gpu = torch.cuda.get_device_name(0) if device == "cuda" else None
    return jsonify({"device": device, "gpu": gpu, "torch": torch.__version__, "models": status, "info": info})


@app.get("/api/example")
def example():
    try:
        en, fr = read_split("test")
    except FileNotFoundError:
        return error("test data not downloaded - run: python train.py", 503)
    i = random.randrange(len(en))
    return jsonify({"en": en[i], "fr": fr[i]})


@app.post("/api/translate")
def api_translate():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return error("Request body must be JSON like {\"text\": \"...\"}.")
    text = body.get("text")
    if not isinstance(text, str):
        return error("'text' must be a string.")
    text = " ".join(text.split())  # collapse whitespace / newlines
    if not text:
        return error("Please type an English sentence.")
    if len(text) > MAX_CHARS:
        return error(f"Sentence is too long ({len(text)} characters, max {MAX_CHARS}).")
    tokens = tokenize(text)
    if not any(re.search(r"[a-z]", t) for t in tokens):
        return error("Sentence has no English words to translate.")
    if len(tokens) > MAX_TOKENS:
        return error(f"Sentence is too long ({len(tokens)} words, max {MAX_TOKENS}).")
    try:
        beam = int(body.get("beam", 5))
    except (TypeError, ValueError):
        return error("'beam' must be a whole number.")
    beam = max(1, min(beam, 10))

    result = {"source": tokens, "beam": beam, "results": {}}
    if "attention" in models:
        model, src_vocab, tgt_vocab = models["attention"]
        words = [t for t in tokens if re.search(r"[a-z]", t)]
        unknown = [t for t in words if t not in src_vocab.stoi]
        result["unknown"] = sorted(set(unknown))
        if len(unknown) > len(words) / 2:
            result["warning"] = ("Most of these words aren't in the model's English vocabulary. Is the sentence in "
                                 "English? The model only knows words from Multi30k image captions.")
    with lock, torch.inference_mode():
        for name in ("attention", "baseline"):
            if name not in models:
                result["results"][name] = {"error": status[name]}
                continue
            model, src_vocab, tgt_vocab = models[name]
            t0 = time.perf_counter()
            out, _, attn = translate(model, text, src_vocab, tgt_vocab, device, beam=beam)
            if device == "cuda":
                torch.cuda.synchronize()
            r = {"tokens": out, "text": detok(out), "ms": round((time.perf_counter() - t0) * 1000, 1),
                 "src_ids": src_vocab.encode(tokens), "tgt_ids": tgt_vocab.encode(out)[1:]}
            if attn is not None:
                r["attention"] = [[round(v, 4) for v in row] for row in attn.tolist()]
            result["results"][name] = r
    if "rule" in models:
        t0 = time.perf_counter()
        out = rule_based.translate(text, models["rule"])
        result["results"]["rule"] = {"tokens": out, "text": detok(out), "ms": round((time.perf_counter() - t0) * 1000, 2)}
    else:
        result["results"]["rule"] = {"error": status["rule"]}
    return jsonify(result)


@app.errorhandler(Exception)
def crashed(e):
    if isinstance(e, HTTPException):  # 404, 405, 413 ... keep their own status
        return error(e.description, e.code)
    app.logger.exception(e)
    return error("Something went wrong on the server. Check the terminal for details.", 500)


load_models()

if __name__ == "__main__":
    print(f"device={device} models={status}")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
