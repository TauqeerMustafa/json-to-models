#!/usr/bin/env python3
"""
json-to-models: Convert JSON structures to TypeScript, Pydantic, and Go structs.
"""
import argparse, json, sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

__version__ = "1.0.0"

def infer_type(val, lang="ts"):
    if val is None:
        return "any" if lang == "ts" else "Optional[Any]" if lang == "pydantic" else "interface{}"
    if isinstance(val, bool):
        return "boolean" if lang == "ts" else "bool"
    if isinstance(val, int):
        return "number" if lang == "ts" else "int"
    if isinstance(val, float):
        return "number" if lang == "ts" else "float" if lang == "pydantic" else "float64"
    if isinstance(val, str):
        return "string" if lang in ["ts", "go"] else "str"
    if isinstance(val, list):
        elem_t = infer_type(val[0], lang) if val else ("any" if lang == "ts" else "Any" if lang == "pydantic" else "interface{}")
        return f"{elem_t}[]" if lang == "ts" else f"list[{elem_t}]" if lang == "pydantic" else f"[]{elem_t}"
    if isinstance(val, dict):
        return "Record<string, any>" if lang == "ts" else "dict[str, Any]" if lang == "pydantic" else "map[string]interface{}"
    return "any"

def generate_typescript(data, name="Model"):
    lines = [f"export interface {name} {{"]
    for k, v in data.items():
        t = infer_type(v, "ts")
        lines.append(f"  {k}: {t};")
    lines.append("}")
    return "\n".join(lines)

def generate_pydantic(data, name="Model"):
    lines = ["from pydantic import BaseModel", "from typing import Any, Optional\n", f"class {name}(BaseModel):"]
    for k, v in data.items():
        t = infer_type(v, "pydantic")
        lines.append(f"    {k}: {t}")
    return "\n".join(lines)

def generate_go(data, name="Model"):
    lines = [f"type {name} struct {{"]
    for k, v in data.items():
        t = infer_type(v, "go")
        capitalized = k.replace("_", " ").title().replace(" ", "")
        lines.append(f"    {capitalized} {t} `json:\"{k}\"`")
    lines.append("}")
    return "\n".join(lines)

SAMPLE_JSON = {"id": 101, "name": "Tauqeer Mustafa", "active": True, "skills": ["Python", "AI"], "meta": {"role": "Engineer"}}

def main():
    parser = argparse.ArgumentParser(description="🔄 json-to-models: Code model generator from JSON")
    parser.add_argument("--lang", choices=["ts", "pydantic", "go"], default="ts", help="Target language (default: ts)")
    parser.add_argument("--name", default="UserSchema", help="Model / interface name")
    args = parser.parse_args()
    
    if args.lang == "ts":
        out = generate_typescript(SAMPLE_JSON, args.name)
    elif args.lang == "pydantic":
        out = generate_pydantic(SAMPLE_JSON, args.name)
    else:
        out = generate_go(SAMPLE_JSON, args.name)
        
    print("=" * 60)
    print(f"🔄 GENERATED {args.lang.upper()} MODEL: {args.name}")
    print("=" * 60)
    print(out)
    print("=" * 60)

if __name__ == "__main__":
    main()
