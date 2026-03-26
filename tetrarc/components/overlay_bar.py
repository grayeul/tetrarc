from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field

import rio

from .. import components as comps
from .. import data_models as dm


class OverlayBar(rio.Component):
    """
    A component that represents the overlay bar at the top of the dashboard.

    The OverlayBar contains:
    - A "Dashboard" title.
    - Frosted glass styling for the background with customizable opacity and blur.

    """

    _page_name: str = "BasicTestsPage"

    @rio.event.on_page_change
    def get_page_name(self) -> None:
        """
        Get the name of the active page and set it as the page name.
        """
        if self.session.active_page_url.name == "admin":
            self._page_name = "BasicTestsPage"
            self.force_refresh()

        else:
            self._page_name = self.session.active_page_url.name.capitalize()
            self.force_refresh()

    def build(self) -> rio.Component:
        # Build the overlay bar layout
        # See if we are logged in
        try:
            self.session[dm.UserInfoModel]

        except KeyError:
            # User is not logged in, need empty navbar
            #self.session.navigate_to("/")
            return rio.Column(margin_y=3)

        mud=self.session[dm.MyUserData]
        org=mud.cfg.get("orgname","")
        return rio.Overlay(
            rio.Rectangle(
                # Row layout to arrange items horizontally
                content=rio.Row(
                    rio.Text(f"{org}-{self._page_name}", font_size=2, font_weight="bold"),
                    rio.Spacer(),  # Spacer to push items to the right
                    spacing=2,
                    margin_right=2 + self.session.scroll_bar_size,
                ),
                fill=rio.FrostedGlassFill(
                    self.session.theme.background_color.replace(opacity=0.7),
                    blur_size=0.6,
                ),
                align_y=0,
                min_height=5,
                margin_left=14,
            ),
        )

