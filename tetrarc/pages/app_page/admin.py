#@file: admin_page.py
#@brief: Constructs page for admin tasks

from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from ... import components as comps

@rio.page(
    name="AdminPage",
    url_segment="admin",
)
class AdminPage(rio.Component):
    """
    A sample page, containing recent news articles about the company.
    """

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("TopRecent News", style="heading1"),
            comps.SideComponent(),
            spacing=2,
            min_width=60,
            margin_bottom=4,
            align_x=0,
            align_y=0,
        )

