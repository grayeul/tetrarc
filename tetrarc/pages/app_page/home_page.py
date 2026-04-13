from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t
import logging

import rio

from ... import components as comps
from ... import persistence

@rio.page(
    name="Home",
    url_segment="home",
)
class HomePage(rio.Component):
    """
    Simple Home page - showing currently active TestBooks
    """

    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        self.log=logging.getLogger("tetrarc")
        books=pers.db.getTestBooks()
        blist=[ comps.BookSum(x['name'],x['description'],x['status'],x['rcs']) for x in books]

        return rio.Column(
            rio.Markdown(
                """
# TETRARC
##  TEst TRAcking for Rocky Candidates

A site for managing and monitoring Rocky Linux Testing Team 
efforts supporting Release Candidates
            """,
                min_width=60,
                align_x=0.5,
            ),
            rio.Row( *blist ,
                spacing=2,
                align_x=0.5,
            ),
            rio.Text(
                """
                Currently active TestBooks for RockyLinux
            """,
                style="dim",
                justify="left",
            ),
            spacing=2,
            min_width=60,
            align_x=0.5,
            align_y=0,
        )

