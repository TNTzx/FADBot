"""Lints everything."""


import os
import os.path as osp
import sys

import pylint.lint as pylint
import pylint.interfaces as pylinterf
import pylint.reporters as pylreport
import pylint.message as pylmsg


def check_if_folder(file_path: str):
    """Checks if a file is a folder."""
    return osp.isdir(file_path)

def check_if_python_file(file_path: str):
    """Checks if a file in a file path is a python file."""
    file_name = osp.split(file_path)[1]
    if osp.splitext(file_name)[1] == ".py":
        return True

    return False


def get_all_python_file_paths(path: str, ignore_list = None) -> str:
    """Gets all python file paths in a directory."""
    if ignore_list is None:
        ignore_list = [
            "__pycache__",
            ".git", ".vscode", "LICENSE", "README.md",
            "requirements.txt",
            "pylint_all.py"
        ]

    all_paths = []

    for file_path in os.listdir(path):
        if file_path in ignore_list:
            continue

        abs_file_path = f"{path}\\{file_path}"

        if check_if_python_file(abs_file_path):
            all_paths.append(abs_file_path)

        if check_if_folder(abs_file_path):
            all_paths += get_all_python_file_paths(abs_file_path)


    return all_paths


# pasted from stack overflow
class CustomReporter(pylreport.BaseReporter):
    """Report messages and layouts."""

    __implements__ = pylinterf.IReporter
    name = "myreporter"
    extension = "myreporter"

    def __init__(self, current_path: str, output = sys.stdout):
        super().__init__(output)
        self.current_path = current_path
        self.messages: list[pylmsg.Message] = []

    def handle_message(self, msg: pylmsg.Message):
        """Manage message of different type and in the context of path."""
        self.messages.append(msg)

    def display_messages(self, layout):
        """Do nothing."""

    def display_reports(self, layout):
        """Do nothing."""

    def _display(self, layout):
        """Do nothing."""


def register(linter: pylint.PyLinter):
    """Register the reporter classes with the linter."""
    linter.register_reporter(CustomReporter)


def lint_all_python_files(root_path: str, clear_console = True, enable_warns: list = None):
    """Lints all python files and prints it to the console."""
    python_file_paths = get_all_python_file_paths(root_path)

    disable_warns = [
        "line-too-long",
        "super-init-not-called", "no-self-use",
        "unused-import", "consider-using-from-import",
        "unused-argument",
        "too-few-public-methods", "too-many-public-methods",
        "too-many-ancestors", "too-many-arguments", "too-many-instance-attributes",
        "too-many-statements", "too-many-branches", "too-many-return-statements",
        "too-many-locals",
        "assigning-non-slot",
        "fixme"
    ]

    if enable_warns is not None:
        new_disable_warns = [warn for warn in disable_warns if warn not in enable_warns]
        disable_warns = new_disable_warns

    pylint_args = [
        "--extension-pkg-whitelist=PyQt5",
        "--variable-rgx=[a-z_][a-z0-9_]{0,30}$",
        "--class-rgx=[A-Z_]?([a-zA-Z0-9]+)$",
        "--function-rgx=[a-z_][a-z0-9_]{0,30}$",
        "--attr-rgx=[a-z_][a-z0-9_]{0,30}$",
        "--argument-rgx=[a-z_][a-z0-9_]{0,30}$",
        "--class-attribute-rgx=[a-z_][a-z0-9_]{0,30}$",
        f"--disable={','.join(disable_warns)}",
    ]

    if clear_console:
        os.system("cls")


    all_reporters: list[CustomReporter] = []

    print(
        "\033[1;31m============STARTING LINTING============\033[0;0m\n"
    )

    for idx, python_file_path in enumerate(python_file_paths):
        abs_path = python_file_path.replace(root_path, '')

        print(
            (
                f"\033[1;36mLINTING FILE ({idx + 1} / {len(python_file_paths)}): "
                f"{abs_path}\033[0;0m"
            )
        )

        current_reporter = CustomReporter(abs_path)
        pylint.Run(
            pylint_args + [python_file_path],
            reporter = current_reporter,
            do_exit = False
        )

        if len(current_reporter.messages) != 0:
            print(f"> ! Found {len(current_reporter.messages)} messages.")

        all_reporters.append(current_reporter)


    print(
        "\033[1;31m============LINTING COMPLETE============"
    )

    for reporter in all_reporters:
        if len(reporter.messages) == 0:
            continue

        print(f"\n\033[1;36m{reporter.current_path}")
        for message in reporter.messages:
            print(
                (
                    "+> [ ]"
                    f"[{message.line}, {message.column}] "
                    f"({message.obj if message.obj != '' else '<module>'}): "
                    f"{message.msg} ({message.msg_id})"
                )
            )


path_here = osp.dirname(osp.realpath(__file__))
lint_all_python_files(path_here, enable_warns = ["unused-import"])
