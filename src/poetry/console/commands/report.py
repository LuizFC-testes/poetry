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

    def _report_version(self):
        with open(self.full_filepath, 'w') as f:
            sys.stdout = f
            self._header("Poetry Version")
            os.system(f"poetry --version >> {self.full_filepath}")
            self._newline()
            sys.stdout = self.default_stdout

    def _report_configuration(self):
        with open(self.full_filepath, 'a') as f:
            sys.stdout = f
            self._header("Poetry Configuration")
            os.system(f"poetry config --list >> {self.full_filepath}")
            self._newline()
            sys.stdout = self.default_stdout

    def _report_sysconfig(self):
        with open(self.full_filepath, 'a') as f:
            sys.stdout = f
            self._header("Python Sysconfig")
            os.system(f"python -m sysconfig >> {self.full_filepath}")
            self._newline()
            sys.stdout = self.default_stdout

    def _report_pyproject(self):
        pass

    def _report_runtime_logs(self):
        command : str = self.argument("report-command")
        with open(self.full_filepath, 'a') as f:
            sys.stdout = f
            self._header("Poetry Runtime Logs")
            os.system(f"poetry -vvv {command} >> {self.full_filepath}")
            self._newline()
            sys.stdout = self.default_stdout

    def _report_all(self):
        self._report_version()
        self._report_configuration()
        self._report_sysconfig()
        if self.option("include-pyproject-toml"):
            self._report_pyproject()
        self._report_runtime_logs()

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