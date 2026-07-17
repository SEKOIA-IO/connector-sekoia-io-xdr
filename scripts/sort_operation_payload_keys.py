#!/usr/bin/env python3
"""Sort dictionary keys returned by build_payload methods in operation files."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

import libcst as cst

from scripts.utils.cli_utils import configure_script_logger

DEFAULT_GLOB = "sekoia-io-xdr/**/*.py"
logger = configure_script_logger(Path(__file__).name)


def _string_key(element: cst.DictElement) -> str | None:
    key = element.key
    if not isinstance(key, cst.SimpleString):
        return None
    try:
        return str(ast.literal_eval(key.value))
    except (ValueError, SyntaxError):
        return None


class BuildPayloadDictSorter(cst.CSTTransformer):
    def __init__(self) -> None:
        self._in_build_payload = 0
        self.changed = False

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        if node.name.value == "build_payload":
            self._in_build_payload += 1

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef:
        if original_node.name.value == "build_payload":
            self._in_build_payload -= 1
        return updated_node

    def leave_Return(
        self,
        original_node: cst.Return,
        updated_node: cst.Return,
    ) -> cst.Return:
        if self._in_build_payload <= 0:
            return updated_node

        if not isinstance(updated_node.value, cst.Dict):
            return updated_node

        elements: list[cst.DictElement] = []
        for element in updated_node.value.elements:
            if not isinstance(element, cst.DictElement):
                return updated_node
            if _string_key(element) is None:
                return updated_node
            elements.append(element)

        sorted_elements = sorted(elements, key=lambda elem: _string_key(elem) or "")
        if [id(e) for e in elements] == [id(e) for e in sorted_elements]:
            return updated_node

        self.changed = True
        return updated_node.with_changes(
            value=updated_node.value.with_changes(elements=sorted_elements)
        )


def process_file(file_path: Path, check_only: bool) -> tuple[bool, bool]:
    original = file_path.read_text(encoding="utf-8")
    module = cst.parse_module(original)
    transformer = BuildPayloadDictSorter()
    updated_module = module.visit(transformer)

    if not transformer.changed:
        return False, False

    if not check_only:
        file_path.write_text(updated_module.code, encoding="utf-8")
        return True, True

    return True, False


def sort_operation_payload_keys(
    check_only: bool = False, pattern: str = DEFAULT_GLOB
) -> int:
    files = sorted(Path.cwd().glob(pattern))
    changed_files: list[Path] = []

    for file_path in files:
        if "__pycache__" in file_path.parts:
            continue

        changed, written = process_file(file_path, check_only=check_only)
        if changed:
            changed_files.append(file_path)
            if written:
                logger.info(
                    f"Success: sorted build_payload dict keys in {file_path}",
                    extra={"color": "green"},
                )

    if check_only:
        if changed_files:
            logger.error(
                "Fail: build_payload dict keys are not sorted in one or more files",
                extra={"color": "red"},
            )
            for path in changed_files:
                logger.info(f" - {path}", extra={"color": None})
            logger.info(
                "Run this command to fix it:\n"
                "uv run python -m scripts.sort_operation_payload_keys",
                extra={"color": None},
            )
            return 1

        logger.info(
            "Success: build_payload dict keys are already sorted",
            extra={"color": "green"},
        )
        return 0

    if not changed_files:
        logger.info(
            "Success: build_payload dict keys are already sorted",
            extra={"color": "green"},
        )
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Sort string-key dictionary literals returned directly by build_payload "
            "methods in operation Python files."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write files; fail if any build_payload dict keys are unsorted.",
    )
    parser.add_argument(
        "--pattern",
        default=DEFAULT_GLOB,
        help=f"Glob to target files (default: {DEFAULT_GLOB})",
    )
    args = parser.parse_args()

    raise SystemExit(
        sort_operation_payload_keys(check_only=args.check, pattern=args.pattern)
    )
