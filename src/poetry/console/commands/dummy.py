from __future__ import annotations

import os

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option


class DummyCommand(Command):
    name = "dummy"
    description = "Just a dummy command for understanding command coding"

    arguments: ClassVar[list[Argument]] = [
        argument(
            name="message",
            description="Optional additional message to be displayed",
            optional=True,
        ),
    ]
    options: ClassVar[list[Option]] = [
        option(
            long_name="caps",
            short_name="c",
            description="Output the version number only",
        ),
        option(
            long_name="display",
            short_name="d",
            description="Displays the installed poetry version",
        ),
    ]

    help = """\
This is a dummy command for experimenting with the poetry command API.
It has an optional argument, which is the string to be displayed in the terminal at the end.
It has an option "caps", short "c", that makes the passed argument to be displayed higher case
(caps lock).
"""

    def handle(self) -> int:
        # Print a message to the terminal
        self.line(text="Hey! You called the mighty Dummy Command!")

        # Get the argument passed (or not)
        message = self.argument("message")

        if message:
            # Get the text of the message
            txt_msg = message

            # Check if the option was passed
            if self.option("caps"):
                txt_msg = txt_msg.upper()

            self.line(text=txt_msg)

        if self.option("display"):
            # Calls the command line above
            os.system("poetry --version")

        return 0
