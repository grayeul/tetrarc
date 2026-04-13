from __future__ import annotations

import functools
from dataclasses import KW_ONLY, field
import typing as t

import rio

from .. import components as comps

class BookSum(rio.Component):
    """
    A summary card holding info about a given TestBook
    people.
    """

    # The name of the TestBook
    bookname: str

    # The description of the book
    description: str

    # The status of the book
    status: str

    # List of RC candidates in use
    rcs: list[str]


    def gotoBook(self,bookname):
        "A method to navigate to the correct book page"
        self.session.navigate_to(f"/app/book/{bookname}/base")

    def build(self) -> rio.Component:
        # Wrap everything in a card to make it stand out from the background.
        return rio.Card(
            # A second card, but this one is offset a bit. This allows the outer
            # card to pop out a bit, displaying a nice colorful border at the
            # bottom.
            rio.Card(
                # Combine the quote, name, and company into a column.
                rio.Column(
                    rio.Markdown(f"# {self.bookname}"),
                    rio.Text(
                        f" {self.description}",
                        justify="left",
                    ),
                    rio.Text(
                        f"RC List: {','.join(self.rcs)}",
                        justify="left",
                    ),
                    rio.Text(
                        f"{self.status}",
                        # Dim text and icons are used for less important
                        # information and make the app more visually appealing.
                        style="dim",
                        justify="left",
                    ),
                    spacing=0.4,
                    margin=2,
                    align_y=0.5,
                ),
                margin_bottom=0.2,
                on_press=functools.partial(self.gotoBook,self.bookname)
            ),
            # Important colors such as primary, secondary, neutral and
            # background are available as string constants for easy access.
            color="primary",
            min_width=20,
        )

