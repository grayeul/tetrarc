# @file: __init__.py
# @brief: This is the initialization file for the tetrarc app

import sys
import typing as t
from datetime import datetime, timedelta, timezone
from pathlib import Path
import logging

import rio

from ._version import __version__,__build_date__
from . import components as comps
from . import data_models, persistence, theme


async def on_app_start(app: rio.App) -> None:
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)])
    app.log = logging.getLogger('tetrarc')

    # Create a persistence instance. This class hides the gritty details of
    # database interaction from the app.

    # This is wonky -- but not sure of a better way just yet to get info
    appcfg=app.default_attachments[0].cfg
    app.name=appcfg.get('orgname','tetrarc') # Default to just tetrarc
    pers = persistence.Persistence(appcfg)

    # Now attach it to the session. This way, the persistence instance is
    # available to all components using `self.session[persistence.Persistence]`
    app.default_attachments.append(pers)
async def on_session_start(rio_session: rio.Session) -> None:
    # A new user has just connected. Check if they have a valid auth token.
    #
    # Any classes inheriting from `rio.UserSettings` will be automatically
    # stored on the client's device when attached to the session. Thus, by
    # retrieving the value here, we can check if the user has a valid auth token
    # stored.
    if rio_session.window_width < 60:
        layout = data_models.PageLayout(device="mobile")
    else:
        layout = data_models.PageLayout(device="desktop")
    rio_session.attach(layout)
    user_settings = rio_session[data_models.UserSettings]

    # Get the persistence instance
    pers = rio_session[persistence.Persistence]

    # Try to find a session with the given auth token
    try:
        user_session = await pers.get_session_by_auth_token(
            user_settings.auth_token,
        )

    # None was found - this auth token is invalid
    except KeyError:
        pass

    # A session was found. Welcome back!
    else:
        # Make sure the session is still valid
        logging.info(f"UserSession: {user_session.d}")
        if user_session.d['valid_until'] > datetime.now(tz=timezone.utc):
            # Attach the session. This way any component that wishes to access
            # information about the user can do so.
            rio_session.attach(user_session)

            # For a user to be considered logged in, a `UserInfo` also needs to
            # be attached.
            userinfo = await pers.get_user_by_id(user_session.d['user_id'])
            rio_session.attach(userinfo)

            # Since this session has only just been used, let's extend its
            # duration. This way users don't get logged out as long as they keep
            # using the app.
            await pers.update_session_duration(
                user_session.d,
                new_valid_until=datetime.now(tz=timezone.utc)
                + timedelta(days=7),
            )





# Define a theme for Rio to use.
#
# You can modify the colors here to adapt the appearance of your app or website.
# The most important parameters are listed, but more are available! You can find
# them all in the docs
#
# https://rio.dev/docs/api/theme
theme = theme.THEME


# Create the Rio app
app = rio.App(
    name='tetrarc',
    default_attachments=[data_models.MyUserData(),
                        data_models.UserSettings(auth_token='')
                         ],
    # This function will be called once the app is ready.
    #
    # `rio run` will also call it again each time the app is reloaded.
    on_app_start=on_app_start,
    on_session_start=on_session_start,
    build=comps.RootComponent,
    theme=theme,
    icon=Path(__file__).parent/"images/rockylogo48x48.png",
    assets_dir=Path(__file__).parent / "assets",
)
