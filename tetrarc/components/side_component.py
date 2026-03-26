# @file: side_component.py
# @brief: Component to hold sidebar in admin pages
from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from .. import components as comps
from .. import data_models

class SideComponent(rio.Component):
    """
    This component will be used as the root for the app. This means that it will
    always be visible, regardless of which page is currently active.

    This makes it the perfect place to put components that should be visible on
    all pages, such as a navbar or a footer.

    Additionally, the root will contain a `rio.PageView`. Page views don't have
    any appearance of their own, but they are used to display the content of the
    currently active page. Thus, we'll always see the navbar and footer, with
    the content of the current page sandwiched in between.
    """

    def desktop_build(self) -> rio.Component:
        return rio.Row(
            # The Sidebar contains a `rio.Overlay`, so it will always be on top
            # of all other components.
            comps.SideBar(),
            # The page view will display the content of the current page.
            rio.Column(
                #comps.OverlayBar(),
                rio.PageView(
                    # Make sure the page view takes up all available space.
                    grow_y=True,
                ),
                # Make sure the page view takes up all available space.
                grow_x=True,
            ),
        )

    def mobile_build(self) -> rio.Component:
        return rio.Column(
            # The Sidebar contains a `rio.Overlay`, so it will always be on top
            # of all other components.
            comps.SideBar(),
            # Add a spacer at the top of the page view to ensure the content
            # isn't obscured by the Navbar.
            rio.Spacer(min_height=5, grow_y=False),
            # The page view will display the content of the current page.
            rio.PageView(
                # Make sure the page view takes up all available space.
                grow_y=True,
                grow_x=True,
                margin_x=0.5,
            ),
            margin_bottom=1,
        )

    def build(self) -> rio.Component:
        device = self.session[data_models.PageLayout].device

        if device == "desktop":
            return self.desktop_build()

        return self.mobile_build()


