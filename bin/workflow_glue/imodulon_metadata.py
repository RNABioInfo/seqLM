"""Read model-specific PyModulon/iModulonDB component annotations."""
import csv
from pathlib import Path


def read_component_metadata(path, components):
    """Accept CSV/TSV exports keyed by component_id, k, or the first index column."""
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        delimiter = "\t" if "\t" in handle.readline() else ","
        handle.seek(0)
        reader = csv.DictReader(handle, delimiter=delimiter)
        fields = reader.fieldnames or []
        if not fields or len(set(fields)) != len(fields) or "name" not in fields:
            raise ValueError("iModulon table requires unique headers and a name column")
        key = next((field for field in ("component_id", "k") if field in fields), fields[0])
        metadata = {}
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("iModulon table has inconsistent column counts")
            component = row[key].strip()
            if not component or component in metadata or component not in components:
                raise ValueError(f"Unknown, empty, or duplicate iModulon component ID: {component!r}")
            metadata[component] = {
                "name": row["name"].strip(),
                "description": (row.get("function") or row.get("description", "")).strip(),
                "regulator": (row.get("regulator") or row.get("regulator_readable", "")).strip(),
                "category": row.get("category", "").strip(),
            }
    missing = set(components) - set(metadata)
    if missing:
        raise ValueError(f"iModulon table is missing component IDs: {sorted(missing)}")
    return metadata
