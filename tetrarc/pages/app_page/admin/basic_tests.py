#@file: admin_page.py
#@brief: Constructs page for admin tasks

from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from ... import components as comps

@rio.page(
    name="BasicTestsPage",
    url_segment="/app/admin/BasicTests",
)
class BasicTestsPage(rio.Component):
    """
    A sample page, containing recent news articles about the company.
    """

    def build(self) -> rio.Component:
        return rio.Column(
            rio.Text("BasicRecent News", style="heading1"),
            comps.NewsArticle(
                """
## Updates worth mentioning

We could put some kind of news here if wanted, or get rid of this page...
                """
            ),
            spacing=2,
            min_width=60,
            margin_bottom=4,
            align_x=0.5,
            align_y=0,
        )

