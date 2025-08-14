import os
import subprocess
import json
import re
import sys

def run_pipgrip_tree(source, out_txt):
    if source == "pyproject":
        print("Detected : pyproject.toml")
        cmd = "pipgrip --tree . > " + out_txt
    elif source == "requirements":
        print("Detected : requirements.txt")
        cmd = "pipgrip --tree -r requirements.txt > " + out_txt
    else:
        print("Invalid source.")
        sys.exit(1)
    subprocess.run(cmd, shell=True, check=True)
    return out_txt

LINE_PARSE_RE = re.compile(r'^(?P<prefix>(?:\|   |    )*)(?P<edge>\|--|\+--)?\s*(?P<body>.+)$')
BODY_RE = re.compile(r'^(?P<name>[^\s(<>!=~]+)\s*(?P<spec>[<>=!~][^()]*)?\s*\((?P<installed>[^)]+)\)\s*$')

def parse_pip_dependencies(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {"dependencies": []}

    dependencies = []
    stack = []

    def depth_from_prefix(prefix: str, edge: str | None) -> int:
        groups = re.findall(r'(?:\|   |    )', prefix)
        base = len(groups)
        return base + (1 if edge else 0)

    def create_dep(body: str) -> dict:
        m = BODY_RE.match(body.strip())
        if m:
            name = m.group("name").strip()
            spec = (m.group("spec") or "").strip()
            installed = m.group("installed").strip()
            return {
                "package_name": name,
                "installed_version": installed,
                "required_version": spec or "Any",
                "dependencies": []
            }
        return {
            "package_name": body.strip(),
            "installed_version": "",
            "required_version": "Any",
            "dependencies": []
        }

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(". "):
            continue

        m = LINE_PARSE_RE.match(line)
        if not m:
            continue

        prefix = m.group("prefix") or ""
        edge = m.group("edge")
        body = m.group("body")

        dep = create_dep(body)
        depth = depth_from_prefix(prefix, edge)

        while stack and stack[-1]["depth"] >= depth:
            stack.pop()

        if stack:
            stack[-1]["node"]["dependencies"].append(dep)
        else:
            dependencies.append(dep)

        stack.append({"depth": depth, "node": dep})

    return {"dependencies": dependencies}

if __name__ == "__main__":
    has_pyproject = os.path.exists("pyproject.toml")
    has_requirements = os.path.exists("requirements.txt")

    if not has_pyproject and not has_requirements:
        print("No pyproject.toml or requirements.txt found.")
        sys.exit(1)

    if has_pyproject:
        deps_txt = run_pipgrip_tree("pyproject", "py_deps.txt")
        result = parse_pip_dependencies(deps_txt)
        with open("py_dep.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print("py_dep.json saved.")

    if has_requirements:
        deps_txt = run_pipgrip_tree("requirements", "req_deps.txt")
        result = parse_pip_dependencies(deps_txt)
        with open("req_dep.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print("req_dep.json saved.")

