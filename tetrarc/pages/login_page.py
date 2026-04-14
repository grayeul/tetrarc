from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field
import logging
import bcrypt

import rio

from .. import components as comps
from .. import data_models, persistence


def guard(event: rio.GuardEvent) -> str | None:
    """
    A guard which only allows the user to access this page if they are not
    logged in yet. If the user is already logged in, the login page will be
    skipped and the user will be redirected to the home page instead.
    """
    # Check if the user is authenticated by looking for a user session
    try:
        event.session[data_models.UserInfoModel]

    # User is not logged in, no redirection needed
    except KeyError:
        return None

    # User is logged in, redirect to the home page
    return "/app/home"


@rio.page(
    name="Login",
    url_segment="",
    guard=guard,
)
class LoginPage(rio.Component):
    """
    Login page for accessing the website.
    """

    # These are used to store the currently entered values from the user
    username: str = ""
    password: str = ""

    error_message: str = ""
    popup_open: bool = False

    _currently_logging_in: bool = False

    async def login(self, _: rio.TextInputConfirmEvent | None = None) -> None:
        """
        Handles the login process when the user submits their credentials.

        It will check if the user exists and if the password is correct. If the
        user exists and the password is correct, the user will be logged in and
        redirected to the home page.
        """
        try:
            # Inform the user that something is happening
            self._currently_logging_in = True
            self.force_refresh()
            cip = self.session.http_headers.get('x-real-ip','UnavailableProxy')

            #  Try to find a user with this name
            pers = self.session[persistence.Persistence]

            try:
                user_info = await pers.get_user_by_username(
                    username=self.username
                )
            except KeyError:
                self.error_message = "Invalid username. Please try again or create a new account."
                logging.getLogger("userlogs").warning(f"Attempt to sign in from {cip} as unknown user: {self.username}")
                return

            user_info_d=user_info.d
            # Make sure their password matches
            #if not user_info.password_equals(self.password):
            #    self.error_message = "Invalid password. Please try again or create a new account."
            #    return
            if type(user_info_d['password']) == str:
                user_info_d['password'] = user_info_d['password'].encode('utf-8')
            if not bcrypt.checkpw(self.password.encode('utf-8'),user_info_d['password']):
                self.error_message = "Invalid password. Please try again or create a new account."
                logging.getLogger("userlogs").warning(f"Attempt to sign in from {cip} as {self.username} with bad password")
                return
                
            self.log.debug(f"Now userinfo: {user_info_d}")
            if user_info_d['pending_approval']:
                 # We are still waiting for approval:
                 logging.getLogger("userlogs").warning(f"Attempt {self.username} from {cip} - still pending approval")
                 self.session.navigate_to("/pending")
                 return
            # The login was successful
            self.error_message = ""
            logging.getLogger("userlogs").info(f"Successful login: {self.username} from {cip}")

            # Clean out any old sessions
            await pers.clear_user_sessions(user_info_d['id'])

            # Create and store a session
            user_session = await pers.create_session(
                user_id=user_info_d['id'],
            )
            user_session_d=user_session.d

            # Attach the session and userinfo. This indicates to any other
            # component in the app that somebody is logged in, and who that is.
            self.log.debug(f"user_session is: {user_session_d}")
            self.session.attach(user_session)
            self.session.attach(user_info)

            # Permanently store the session token with the connected client.
            # This way they can be recognized again should they reconnect later.
            settings = self.session[data_models.UserSettings]
            settings.auth_token = user_session_d["auth_token"]
            self.session.attach(settings)

            # The user is logged in - no reason to stay here
            self.session.navigate_to("/app/home")

        # Done
        finally:
            self._currently_logging_in = False

    def on_open_popup(self) -> None:
        """
        Opens the sign-up popup when the user clicks the sign-up button
        """
        self.popup_open = True

    def build(self) -> rio.Component:
        # Create a banner with the error message if there is one
        self.log=logging.getLogger("tetrarc")
        # Determine the layout based on the window width
        desktop_layout = self.session.window_width > 30

        return rio.Card(
            rio.Column(
                rio.Text("Login", style="heading1", justify="center"),
                # Show error message if there is one
                #
                # Banners automatically appear invisible if they don't have
                # anything to show, so there is no need for a check here.
                rio.Banner(
                    text=self.error_message,
                    style="danger",
                    margin_top=1,
                ),
                # Create the login form consisting of a username and password
                # input field, a login button and a sign up button
                rio.TextInput(
                    text=self.bind().username,
                    label="Username",
                    # ensure the login function is called when the user presses enter
                    on_confirm=self.login,
                ),
                rio.TextInput(
                    text=self.bind().password,
                    label="Password",
                    # Mark the password field as secret so the password is
                    # hidden while typing
                    is_secret=True,
                    # Ensure the login function is called when the user presses
                    # enter
                    on_confirm=self.login,
                ),
                rio.Row(
                    rio.Button(
                        "Login",
                        on_press=self.login,
                        is_loading=self._currently_logging_in,
                    ),
                    # Create a sign up button that opens a pop up with a sign up
                    # form
                    rio.Popup(
                        anchor=rio.Button(
                            "Request an Account",
                            on_press=self.on_open_popup,
                        ),
                        content=comps.UserSignUpForm(
                            # Bind `popup_open` to the `popup_open` attribute of
                            # the login page. This way the page's attribute will
                            # always have the same value as that of the form,
                            # even when one changes.
                            popup_open=self.bind().popup_open,
                        ),
                        position="fullscreen",
                        is_open=self.popup_open,
                        color="none",
                    ),
                    spacing=2,
                ),
                spacing=1,
                margin=2 if desktop_layout else 1,
            ),
            margin_x=0.5,
            align_y=0.5,
            align_x=0.5 if desktop_layout else None,
            min_width=24 if desktop_layout else 0,
        )

