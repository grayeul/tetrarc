from datetime import datetime, date, timedelta, timezone
from pathlib import Path
import logging

from . import data_models as data_models
from .tetrarcdb import tetrarcDB as tetrarcDB

# Define the UserPersistence dataclass to handle database operations
class Persistence:
    """
    A class to handle database operations for tetrarc

    User data is stored in the 'users' table, and session data is stored in the
    'user_sessions' table.

    ## Attributes

    `db`: An instance of tetrarcdb that is used for db access
    """

    def __init__(self, appcfg:dict) -> None:
        """
        Initialize the Persistence instance and ensure necessary tables exist.
        """
        self.cfg=appcfg
        self.log=logging.getLogger("tetrarc")
        self.log.info(f"Persistence setup: {self.cfg}")
        self.log.setLevel(self.cfg["loglevel"])
        self.log.info(f"Logging has been set to lvl: {logging.getLevelName(self.log.level)}")
        dbfile=self.cfg["dbfile"]
        self.roles=[]
        self.db = tetrarcDB(dbfile,self.cfg)

    async def create_user(self, userInfo: dict) -> None:
        """
        Add a new user to the database.

        ## Parameters

        `userInfo`: A dict of user info, with at least: username,name,email,password
        """
        self.log.info(f"Adding new user to DB: {userInfo}")
        return self.db.addUser(userInfo)
        
    async def get_user_by_username(
        self,
        username: str,
    ) -> data_models.UserInfoModel:
        """
        Retrieve a user from the database by username.

        ## Parameters

        `username`: The username of the user to retrieve.

        ## Raises

        `KeyError`: If there is no user with the specified username.
        """
        # Look up the user in the database
        user=self.db.getUserByUsername(username)
        if user:
            return data_models.UserInfoModel(user)
        # If no user was found, signal that with a KeyError
        raise KeyError(username)

    async def get_user_by_id(
        self,
        id: int,
    ) -> data_models.UserInfoModel:
        """
        Retrieve a user from the database by user ID.

        ## Parameters

        `id`: The db id of the user to retrieve.

        ## Raises

        `KeyError`: If there is no user with the specified ID.
        """
        # Look up the user in the database
        user=self.db.getUserById(id)
        if user:
            return data_models.UserInfoModel(user)

        # If no user was found, signal that with a KeyError
        raise KeyError(id)

    async def create_session(
        self,
        user_id: int,
    ) -> data_models.UserSessionModel:
        """
        Create a new user session and store it in the database.

        ## Parameters

        `user_id`: The db id of the user for whom to create the session.
        """
        # First check if there is an existing session for this user in db,
        #   If so -- use/update that one.
        # Create the new session object
        user_sess=self.db.newUserSession(user_id)
        # Look up roles
        user_roles=self.db.getUserRolesById(user_id)
        # Add to the session
        user_sess["roles"]=user_roles
        # Return the freshly created session dictionary
        return data_models.UserSessionModel(user_sess)

    async def clear_user_sessions(
        self,
        user_id:int,
    ) -> None:
        """
        Deletes any sessions in db for the given user 'id'
        ## Parameters

        `user_id`: The db id of the user whose sessions are to be deleted

        """
        self.db.deleteUserSessionsByUserId(user_id)

    async def delete_user_session(
        self,
        user_sess:dict
    ) -> None:
        """
        Delete the session from the DB - for now only one session per user
        ## Parameters

        `user_sess`: The session to be deleted

        """
        self.db.deleteUserSessionByAuthToken(user_sess['auth_token'])

    async def update_session_duration(
        self,
        user_sess:dict,
        new_valid_until: datetime,
    ) -> None:
        """
        Extend the duration of an existing session. This will update the
        session's validity timestamp both in the given object and the database.

        ## Parameters

        `user_sess`: The session whose duration to extend.

        `new_valid_until`: The new timestamp until which the session should be
            considered valid.
        """
        print(f"Now trying to update user session for ID: {user_sess['id']} until: {new_valid_until}")
        self.db.updateUserSession(user_sess['id'],new_valid_until)
        # Update the session object
        user_sess['valid_until'] = new_valid_until


    async def get_session_by_auth_token(
        self,
        auth_token: str,
    ) -> data_models.UserSessionModel:
        """
        Retrieve a user session from the database by authentication token.

        ## Parameters

        `auth_token`: The auth_token of the session to retrieve.

        ## Raises

        `KeyError`: If there is no session with the specified authentication
        token.
        """

        user_sess=self.db.getUserSessionByAuthToken(auth_token)
        if not user_sess:
            # If no session was found, signal that with a KeyError
            raise KeyError(auth_token)
        # Update/re-check the roles (in case they changed)
        user_roles=self.db.getUserRolesById(user_sess['user_id'])
        user_sess['roles']=user_roles
        return data_models.UserSessionModel(user_sess)

