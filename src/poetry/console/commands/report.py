from __future__ import annotations

import os
import sys

from threading import Thread
from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class ReportCommand(Command):
    name = "report"
    description = "Automatic generation of metadata to fill in Bug Reports"

    arguments: ClassVar[list[Argument]] = [
        argument(
            name="report-command",
            description="Poetry terminal command of the issue to be reported",
            optional=True,
        ),
    ]

    options: ClassVar[list[Option]] = [
        option(
            long_name="include-pyproject-toml",
            short_name="t",
            description="Indicates that the example pyproject.toml must be included",
        ),
    ]

    help = """\
This command executes the commands required for filling in the Bug Report, then saves the output
to a file named bug-report.md to facilitate copying and pasting each section by the user.

Argument:
- command:
    Text identical to the command to be reported, except by the 'poetry' segment. If the command
    has more than one word, it must be inside quotation marks.

Options:
- include-pyproject-toml:
    Indicates that the example pyproject.toml must be included
"""

    reports: ClassVar[dict[str, str]] = {}

    filename = "bug-report.md"

    report_file = sys.stdout

    def _get_filepath(self) -> str:
        """
        Gets the path to the directory where the output file must be saved
        """
        pwd = os.getcwd()
        root = os.path.join(pwd.split("src/poetry")[0], "src", "poetry")
        save_dir = "report"
        return os.path.join(root, save_dir)

    def _get_full_filepath(self) -> str:
        return os.path.join(self._get_filepath(), self.filename)

    def _header(self, text: str, level: int = 1) -> None:
        """
        Prints a text formatted as a markdown header to stdout

        Parameters:
        - text : str
            Text to be printed
        - level : int
            Level of the header
        """
        self.report_file.write("\n" + "#" * level + " " + text)

    def _newline(self) -> None:
        """Prints a newline character to stdout"""
        self.report_file.write("\n")

    def _bold(self, text: str) -> None:
        """
        Prints a text formatted as markdown bold to stdout

        Parameters:
        - text : str
            Text to be printed
        """
        self.report_file.write(f"**{text}**")

    def _italic(self, text: str) -> None:
        """
        Prints a text formatted as markdown italic to stdout

        Parameters:
        - text : str
            Text to be printed
        """
        self.report_file.write(f"*{text}*")

    def _open_code_block(self) -> None:
        self.report_file.write("```")

    def _close_code_block(self) -> None:
        self.report_file.write("```")

    def _code_block(self, text: str) -> None:
        self._open_code_block()
        self.report_file.write(text)
        self._close_code_block()

    def _execute_command(self, command: str, full_filepath: str | None = None) -> str:
        if full_filepath is None:
            full_filepath = self.full_filepath

        os.system(f"{command} > {full_filepath}")
        with open(full_filepath) as f:
            output = f.read()

        return output.strip()

    def _report_version(self) -> None:
        command = "poetry --version"
        self.reports["version"] = self._execute_command(command)

    def _report_configuration(self) -> None:
        command = "poetry config --list"
        self.reports["configuration"] = self._execute_command(command)

    def _report_sysconfig(self) -> None:
        command = "python -m sysconfig"
        self.reports["sysconfig"] = self._execute_command(command)

    def _report_pyproject(self) -> None:
        if self.option("include-pyproject-toml"):
            pass  # FIXME

    def _report_runtime_logs(self) -> None:
        command_exec: str = self.argument("report-command")
        command = f"poetry -vvv {command_exec}"
        self.reports["runtime_logs"] = self._execute_command(command)

    def _report_all(self) -> None:
        threads = [
            Thread(target=self._report_version),
            Thread(target=self._report_configuration),
            Thread(target=self._report_sysconfig),
            Thread(target=self._report_pyproject),
            Thread(target=self._report_runtime_logs),
        ]

        for t in threads:
            t.start()
            t.join()

        with open(self.full_filepath, "w") as f:
            sys.stdout = f

            self._header("Poetry Version")
            self._code_block(self.reports["version"])

            self._header("Poetry Configuration")
            self._code_block(self.reports["configuration"])

            self._header("Python Sysconfig")
            self._code_block(self.reports["sysconfig"])

            if self.option("include-pyproject-toml"):
                pass  # FIXME

            self._header("Runtime Logs")
            self._code_block(self.reports["runtime_logs"])

    def handle(self) -> int:
        self.full_filepath = self._get_full_filepath()

        # Sets the output file as stdout
        folder = self._get_filepath()
        if not os.path.isdir(folder):
            os.mkdir(folder)
            self.line(f"Created the directory {folder}")
        filepath = os.path.join(folder, self.filename)
        with open(filepath, "w") as f:
            # Setting f as output file
            self.report_file = f
            # Generate report file
            self._report_all()

        self.line(f"Saved report file at {filepath}")

        return 0
