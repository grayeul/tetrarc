#@file: sidebar.py
#@brief:Builds SideBar for Admin page that allows table editing
from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field
from datetime import datetime, timezone

import rio

from .. import components as comps
from .. import constants, data_models, persistence


class SideBar(rio.Component):
    """
    Represents the sidebar component of the application.

    The sidebar includes:
    - A list of major sections dynamically highlighted based on the active URL
    segment.
    - Spacer to separate content for better layout alignment.
    """

    _is_open: bool = False

    # Make sure the sidebar will be rebuilt when the app navigates to a different
    # page. While Rio automatically detects state changes and rebuilds
    # components as needed, navigating to other pages is not considered a state
    # change, since it's not stored in the component.
    #
    # Instead, we can use Rio's `on_page_change` event to trigger a rebuild of
    # the sidebar when the page changes.
    @rio.event.on_page_change
    def on_page_change(self) -> None:
        """
        Trigger a rebuild of the sidebar when the page changes.
        """
        # Rio comes with a function specifically for this. Whenever Rio is
        # unable to detect a change automatically, use this function to force a
        # refresh.
        self.force_refresh()

    def _on_switcherbar_value_change(
        self, event: rio.SwitcherBarChangeEvent
    ) -> None:
        """
        Handles changes to the SwitcherBar value.

        Navigates to the corresponding page and closes the mobile menu.
        """
        # Navigate to the target page
        self.session.navigate_to(f"/{event.value}")
        # Close the mobile menu
        self._is_open = False

    async def on_press(self, _: rio.PointerEvent) -> None:
        # When the user presses the logout button, display a dialog to confirm
        # the action.
        await self.on_spawn_dialog()

    async def on_spawn_dialog(self) -> None:
        # Display a dialog and wait until the user makes a choice.
        # Since `show_yes_no_dialog` is an asynchronous function, the
        # `on_spawn_dialog` function must also be asynchronous.
        log_out = await self.session.show_yes_no_dialog(
            title="Logout",
            text="Are you sure you want to logout?",
            yes_text="Logout",
            no_text="Cancel",
            yes_color="danger",
            no_color=rio.Color.WHITE,
        )
        if log_out:
            await self.on_logout()

    def checkRoleValid(self,rqroles:list[str]) -> bool:
        """
        Take in a list of required roles, and return True if user has one, or False if has None
        """
        if len(rqroles) == 0:
            return True       # No restriction if no required roles
        uim=self.session[data_models.UserInfoModel]
        pers=self.session[persistence.Persistence]
        myroles=pers.db.getUserRolesById(uim.d['id'])
        for r in rqroles:
            if r in myroles:
                return True
        # If there are required roles, and we don't match any, then no permission
        return False

    def desktop_build(self) -> rio.Component:
        """
        Build the desktop layout.
        """
        # Retrieve the current active page's URL segment
        active_url_segment = self.session.active_page_url.path

        # Create a column to hold the main sections
        content = rio.Column(spacing=1)

        # Add each major section to the sidebar, highlighting the active section
        for section in constants.SIDEBAR_TABLES:
            if not self.checkRoleValid(section.required_roles):
                continue
            content.add(
                # Link the section to the corresponding page
                rio.Link(
                    comps.MajorSection(
                        main_section=section,  # Section data (e.g., name and icon)
                        is_active=section.target_url == active_url_segment,
                    ),
                    section.target_url,
                    open_in_new_tab=False,
                ),
            )


        # Add a spacer to separate the main content for alignment
        content.add(rio.Spacer())

        # Return the complete sidebar layout as a column
        return rio.Column(
            # Add the Rio logo at the top of the sidebar
            #comps.RioLogo(
            #    margin_y=(5 - 4) / 2,  # Vertical margin to adjust logo position
            #    align_x=0,
            #    margin_left=1,
            #),
            # Add the column of main sections
            content,
            align_y=0,
            margin_x=2,
            align_x=0,
            min_width=10,
        )

    def mobile_build(self) -> rio.Component:
        """
        Build the mobile layout.
        """
        active_url_fragment = self.session.active_page_url.name

        # Add the mobile navigation menu when open
        if self._is_open:
            # Add the local navigation buttons
            primary_column = rio.Rectangle(
                content=rio.Column(
                    rio.SwitcherBar(
                        names=[
                            section.main_section_name
                            for section in constants.SIDEBAR_TABLES[:-1]
                        ],
                        values=[
                            section.target_url.lstrip("/")
                            for section in constants.SIDEBAR_TABLES[:-1]
                        ],
                        selected_value=active_url_fragment,
                        allow_none=True,
                        color="primary",
                        orientation="vertical",
                        on_change=self._on_switcherbar_value_change,
                        margin=0.5,
                        align_y=0,
                    ),
                    rio.Button(
                        content=constants.SIDEBAR_TABLES[-1].main_section_name,
                        on_press=self.on_spawn_dialog,
                        color="neutral",
                        align_x=0.5,
                        margin_bottom=1,
                    ),
                ),
                fill=self.session.theme.neutral_color,
                corner_radius=(
                    0,
                    0,
                    self.session.theme.corner_radius_large,
                    self.session.theme.corner_radius_large,
                ),
                shadow_radius=1,
                margin_bottom=1,
            )

        else:
            primary_column = None

        # The navbar should appear above all other components. This is easily
        # done by using a `rio.Overlay` component.
        return rio.Overlay(
            rio.Column(
                rio.Rectangle(
                    content=rio.Row(
                        comps.HamburgerButton(is_open=self.bind()._is_open),
                        spacing=1.1,
                        margin_x=0.6,
                        margin_left=1.2,
                        margin_right=1.2,
                    ),
                    # Set the fill of the rectangle to the neutral color of the theme and
                    # add a FrostedGlassFill
                    fill=rio.FrostedGlassFill(
                        self.session.theme.background_color.replace(
                            opacity=0.7
                        ),
                        blur_size=0.6,
                    ),
                    align_y=0,
                    min_height=4,  # Fixed height of the navbar
                ),
                rio.Switcher(content=primary_column),
                align_y=0,
            ),
        )

    def build(self) -> rio.Component:
        device = self.session[data_models.PageLayout].device

        # See if we are logged in
        try:
            self.session[data_models.UserInfoModel]

        except KeyError:
            # User is not logged in, need empty navbar
            return rio.Column()

        if device == "desktop":
            return self.desktop_build()
        else:
            return self.mobile_build()

