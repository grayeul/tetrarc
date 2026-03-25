from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field

import rio

from .. import components as comps
from .. import data_models, persistence

@rio.page(
    name="PendingApproval",
    url_segment="pending",
)
class PendingPage(rio.Component):
    """
    A Page to show account has been requested, but not approved
    """

    def build(self) -> rio.Component:

        return rio.Card(
            rio.Column(
                rio.Text("Account Requested", style="heading1", justify="center"),
                # Create the Markdown info
                rio.Markdown(
                    """
                    #Now you wait

                    An account has been requested for you.
                    You will receive an email once it is approved, and 
                    then will be able to login.
                    """,
                    default_language="text"
                ),
                rio.Button("Home",
                    # Alignment must be set to keep from filling available space
                    align_x=0,align_y=0.5,
                    on_press=self.gohome)
        )
      )

    def gohome(self) -> None:
        "A Button handle to simply navigate back to home"
        self.session.navigate_to("/")
