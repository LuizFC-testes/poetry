from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from poetry.core.version.exceptions import InvalidVersionError
from tomlkit.toml_document import TOMLDocument

from poetry.console.commands.command import Command

import os
import sys
from threading import Thread

if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option
    from poetry.core.constraints.version import Version

class ReportCommand(Command):
    name = "report"
    description = (
        "Just a dummy command for understanding command coding"
    )

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
            description="Indicates that the example pyproject.toml must be included"
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

    reports = {}

    filename = "bug-report.md"

    def _get_filepath(self) -> str:
        """
        Gets the path to the directory where the output file must be saved
        """
        pwd = os.getcwd()
        root = os.path.join(pwd.split("src/poetry")[0], "src", "poetry")
        save_dir = "report"
        return os.path.join(root, save_dir)
    
    def _get_full_filepath(self):
        return os.path.join(self._get_filepath(), self.filename)

    def _header(self, text, level=1):
        """
        Prints a text formatted as a markdown header to stdout

        Parameters:
        - text : str
            Text to be printed
        - level : int
            Level of the header 
        """
        print("\n" + "#"*level + " " + text)

    def _newline(self):
        """Prints a newline character to stdout"""
        print("\n")

    def _bold(self, text):
        """
        Prints a text formatted as markdown bold to stdout

        Parameters:
        - text : str
            Text to be printed
        """
        print(f"**{text}**")

    def _italic(self, text):
        """
        Prints a text formatted as markdown italic to stdout

        Parameters:
        - text : str
            Text to be printed
        """
        print(f"*{text}*")

    def _open_code_block(self):
        print("```")

    def _close_code_block(self):
        print("```")

    def _execute_command(self, command, full_filepath=None):
        if full_filepath is None:
            full_filepath = self.full_filepath
            
        os.system(f"{command} > {full_filepath}")
        with open(full_filepath, 'r') as f:
            output = f.read()

        return output.strip()
    
    def _report_version(self):
        command = "poetry --version"
        self.reports["version"] = self._execute_command(command)

    def _report_configuration(self):
        command = "poetry config --list"
        self.reports["configuration"] = self._execute_command(command)

    def _report_sysconfig(self):
        command = "python -m sysconfig"
        self.reports["sysconfig"] = self._execute_command(command)

    def _report_pyproject(self):
        if self.option("include-pyproject-toml"):
            pass #FIXME

    def _report_runtime_logs(self):
        command_exec : str = self.argument("report-command")
        command = f"poetry -vvv {command_exec}"
        self.reports["runtime_logs"] = self._execute_command(command)

    def _report_all(self):
        threads = [
            Thread(target=self._report_version),
            Thread(target=self._report_configuration),
            Thread(target=self._report_sysconfig),
            Thread(target=self._report_pyproject),
            Thread(target=self._report_runtime_logs)
        ]

        for t in threads:
            t.start()
            t.join()

        with open(self.full_filepath, "w") as f:
            sys.stdout = f

            self._header("Poetry Version")
            print(self.reports["version"])
            self._header("Poetry Configuration")
            print(self.reports["configuration"])
            self._header("Python Sysconfig")
            print(self.reports["sysconfig"])
            if self.option("include-pyproject-toml"):
                pass #FIXME
            self._header("Runtime Logs")
            print(self.reports["runtime_logs"])

            sys.stdout = self.default_stdout


    def handle(self) -> int:

        self.full_filepath = self._get_full_filepath()
        
        # Stores the default stdout
        self.default_stdout = sys.stdout

        # Sets the output file as stdout
        folder = self._get_filepath()
        if not os.path.isdir(folder):
            os.mkdir(folder)
            print(f"Created the directory {folder}")
        filepath = os.path.join(folder, self.filename)
        #with open(filepath, 'w') as f:
        # Setting f as sys.stdout
        #sys.stdout = f
        # Generate report file
        self._report_all()
        # Sets stdout back to the default
        sys.stdout = self.default_stdout

        print(f"Saved report file at {filepath}")

        return 0