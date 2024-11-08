from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from cleo.helpers import argument
from cleo.helpers import option
from poetry.core.version.exceptions import InvalidVersionError
from tomlkit.toml_document import TOMLDocument

from poetry.console.commands.command import Command


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument
    from cleo.io.inputs.option import Option
    from poetry.core.constraints.version import Version

class FooCommand(Command):
    name = "foo"
    description = (
        "Just a dummy command for understanding command coding"
    )

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
            description="Output the version number only"
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
        self.line(
            text="Hey! You called the mighty Foo Command!"
        )

        # Get the argument passed (or not)
        message = self.argument("message")

        if message:
            # Get the text of the message
            txt_msg = message.to_string()

            # Check if the option was passed
            if self.option("caps"):
                txt_msg = txt_msg.upper()

            self.line(
                text=txt_msg
            )

        return 0