from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from ... import components as comps
from ... import _version as myvers

@rio.page(
    name="About",
    url_segment="about-page",
)
class AboutPage(rio.Component):
    """
    A simple about page
    """

    def build(self) -> rio.Component:
        return rio.Markdown(
            f"""
# Rocky Linux Testing

The Testing Team communicates primarily via the [Testing Channel](https://chat.rockylinux.org/rocky-linux/channels/testing) on Mattermost

## About TETRARC

This TETRARC page is an initial cut at an alternate way to monitor/manage testing
that goes one prior to an official Rocky Release.  We probably need to figure out
how to tie accounts into this -- then users can login, and their individual contributions
can be tracked.

## Goals
One of the goals of this project is to have more control over exactly what we present and record
during testing.  We'd also like to record when a test has been run by multiple people.  It 
will likely take a few iterations to get what we want, but I'm hopeful this will be a viable
replacement option for Mattermost Playbooks.

This is tetrarc v{myvers.__version__} - built {myvers.__build_date__}
            """,
            min_width=60,
            margin_bottom=4,
            align_x=0.5,
            align_y=0,
        )

