"""Generate the code reference pages."""

from pathlib import Path
import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

readme_path = Path("README.md")
index_path = Path("docs/index.md")

if readme_path.exists():
    with mkdocs_gen_files.open("index.md", "w") as index_file:
        with open(readme_path, "r") as readme_file:
            index_file.write(readme_file.read())

# Process Python files
for path in sorted(Path("wito").rglob("*.py")):
    module_path = path.relative_to(".").with_suffix("")
    doc_path = path.relative_to(".").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    # Special handling for bridge.py - merge it into interface.py documentation
    if parts[-1] == "bridge":
        continue
    
    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        ident = ".".join(parts)
        # If this is interface.py, include both interface and bridge
        if parts[-1] == "interface":
            fd.write(f"# Interface Documentation\n\n")
            fd.write(f"## Python Interface\n")
            fd.write(f"::: {ident}\n\n")
            fd.write(f"## Bridge\n")
            fd.write(f"::: {'.'.join(parts[:-1] + ('bridge',))}\n\n")
        else:
            fd.write(f"::: {ident}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())

