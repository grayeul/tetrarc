from __future__ import annotations
import typing as t

import hashlib
import os
import secrets
import uuid
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone

import rio


@dataclass
class UserInfoModel:
    def __init__(self,d):
        self.d=d
        # Add default arch, and deploy_type (kept/tracked during session
        self.d['arch']='x86_64'
        self.d['deploy_type']='VM'

@dataclass
class UserSessionModel:
    def __init__(self,d):
        self.d=d

@dataclass
class MyUserData:
    """
    Model for the User data tracked during a session, based on initial config, then potentially updated
    """
    cfgfile:Path       # Path to the primary Config file
    cfg:dict           # Dictionary of config items for access during session
    def __init__(self,cfgfile=Path('tetrarc.json')):
        self.cfgfile=cfgfile
        self.reloadCfg()
    def reloadCfg(self):
        try:
            with self.cfgfile.open() as fp:
                self.cfg=json.load(fp)
        except:
            logging.exception("Error opening config file")
            raise SystemExit

@dataclass
class UserSettings(rio.UserSettings):
    """
    Model for data stored client-side for each user.
    """

    # The (possibly expired) authentication token for this user. If this matches
    # the id of any valid `UserSession`, it is safe to consider the user as
    # authenticated being in that session.
    #
    # This prevents users from having to log-in again each time the page is
    # accessed.
    auth_token: str



@dataclass(frozen=True)
class PageLayout:
   device: t.Literal["desktop", "mobile"]

@dataclass
class SideBarTable:
    main_section_name: str
    icon: str
    target_url: str
    required_roles: list[str] = field(default_factory=list)


