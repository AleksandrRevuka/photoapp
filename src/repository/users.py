
import cloudinary.uploader
from libgravatar import Gravatar
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import NoResultFound
from fastapi import UploadFile

from src.database.models import User, Comment, Picture, InvalidToken
from src.schemas.user import UserModel, UserProfile
from src.conf.config import init_cloudinary


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    """
    The get_user_by_email function takes in an email address and a database session.
    It then queries the database for a user with that email address, returning the first result if it exists.

    :param email: str: Specify the type of the email parameter
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object if the user exists in the database
    """
    query = select(User).filter_by(email=email)
    result = await db.execute(query)
    user = result.scalars().first()
    return user


async def create_user(body: UserModel, db: AsyncSession) -> User:
    """
    The create_user function takes a UserModel object and a database session as arguments.
    It then creates an instance of the Gravatar class, passing in the user's email address.
    The get_image() method is called on this instance to retrieve the user's avatar image from Gravatar.com,
    and it is assigned to the avatar variable. The model_dump() method of UserModel returns a dictionary containing all
    the fields that are required for creating an instance of User (except for id). This dictionary is unpacked into
    keyword arguments for creating new_user using Python's ** operator.

    :param body: UserModel: Create a new user
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    """
    g = Gravatar(body.email)
    avatar = g.get_image()
    
    existing_user = (await db.execute(select(User).limit(1))).scalar()
    
    if existing_user is None:
        new_user = User(**body.model_dump(), avatar=avatar, roles="admin")
    else:
        new_user = User(**body.model_dump(), avatar=avatar)
        
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, refresh_token: str | None, db: AsyncSession) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Pass the user object to the function
    :param refresh_token: str: Update the refresh token in the database
    :param db: AsyncSession: Access the database
    :return: The updated user
    """
    if refresh_token:
        user.refresh_token = refresh_token
        await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function takes an email address and a database session as arguments.
    It then queries the database for a user with that email address, and sets their confirmed field to True.
    Finally, it commits the change to the database.

    :param email: str: Specify the email address of the user to be confirmed
    :param db: AsyncSession: Pass in the database session
    :return: None
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        await db.commit()


async def edit_my_profile(email: str, file: UploadFile, name: str, db: AsyncSession) -> User | None:
    """
    The edit_my_profile function takes in an email, a file, and a name.
    It then gets the user by their email from the database. If there is no user with that email, it returns None.
    If there is a user with that given email address, it sets their username to be equal to the name parameter if one was 
    provided.
    Then it initializes cloudinary and uploads the file using cloudinary's uploader module (which uses Cloudinary's API). 
    The public_id of this image will be &quot;avatar/{user's username}&quot;. This means that all images uploaded for each 
    individual avatar will have unique
    
    :param email: str: Get the user from the database
    :param file: UploadFile: Upload the file to cloudinary
    :param name: str: Change the username of the user
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object if the user exists and none otherwise
    """
    user = await get_user_by_email(email, db)
    if user:
        if name:
            user.username = name
        init_cloudinary()
        r = cloudinary.uploader.upload(file.file, public_id=f"avatar/{user.username}", overwrite=True)
        src_url = cloudinary.CloudinaryImage(f"avatar/{user.username}").build_url(
                width=250, height=250, crop="fill", version=r.get("version")
            )
        user.avatar = src_url
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise e
    return None


async def change_password(user: User, password: str, db: AsyncSession) -> User:
    """
    The change_password function takes in a user, body, and db.
    The function then sets the password of the user to be equal to the confirm_password field of body.
    It then adds this new information into our database and commits it.
    Finally, we refresh our database with this new information.

    :param user: User: Get the user object from the database
    :param body: ResetPassword: Get the new password from the request body
    :param db: AsyncSession: Access the database
    :return: The user object with the new password
    """
    user.password = password
    try:
        await db.commit()
        return user
    except Exception as e:
        await db.rollback()
        raise e


async def get_user_username(username: str, db: AsyncSession) -> User | None:
    """
    The get_user_username function takes in a username and an AsyncSession object.
    It then queries the database for a user with that username, returning the User object if it exists, or None otherwise.
    
    :param username: str: Specify the username of the user we want to retrieve
    :param db: AsyncSession: Pass the database session into the function
    :return: The user object if the username exists in the database, else none
    """
    
    try:
        result = await db.execute(select(User).filter(User.username == username))
        user = result.scalar_one_or_none()
        return user
    except NoResultFound:
        return None
    
    
async def get_all_users(skip:int, limit: int, db: AsyncSession) -> list[User]:
    """
    The get_all_users function returns a list of all users in the database.
        
    
    :param skip:int: Skip the first n users in the database
    :param limit: int: Limit the number of results returned
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of user objects
    """
    query = select(User).offset(skip).limit(limit)
    users = await db.execute(query)
    result = users.scalars().all()
    return list(result)

async def  get_user_profile(user: User, db: AsyncSession):
    """
    The get_user_profile function takes a user object and an async database session as arguments.
    It then returns a UserProfile object with the following attributes:
        id, roles, username, email, avatar (url), is_active (boolean), pictures_count (int), comments_count(int)
        created_at(datetime.datetime), updated_at(datetime.datetime)
    
    :param user: User: Pass the user object to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: A userprofile object
    """
    
    if user:
        
        pictures = select(func.count()).where(Picture.user_id == user.id)
        pictures_result = await db.execute(pictures)
        pictures_count = pictures_result.scalar()

        comments = select(func.count()).where(Comment.user_id == user.id)
        comments_result = await db.execute(comments)
        comments_count = comments_result.scalar()
        
        user_profile = UserProfile(
            id=user.id,
            roles=user.roles,
            username=user.username,
            email=user.email,
            avatar=user.avatar,
            is_active=user.is_active,
            pictures_count=pictures_count,
            comments_count=comments_count,
            created_at=user.created_at,
            updated_at=user.updated_at,
            confirmed=user.confirmed
        )
        return user_profile
    return None

async def ban_user(email: str, db: AsyncSession) -> User | None:
    user = await get_user_by_email(email, db)
    if user:
        user.is_active = False
   
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise e
    return None


async def activate_user(email: str, db: AsyncSession) -> User | None:
    """
    The activate_user function takes an email and a database session as arguments.
    It then queries the database for a user with that email address, and if it finds one, 
    it sets its is_active attribute to True. It then commits the change to the database 
    and returns the updated user object.
    
    :param email: Find the user in the database
    :param db: AsyncSession: Pass in the database session so that we can use it to query the database
    :return: A user or none
    """
    user = await get_user_by_email(email, db)
    if user:
        user.is_active = True
   
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise e
    return None


async def invalidate_token(token: str, db: AsyncSession):
    """
    The invalidate_token function takes a token and an AsyncSession object as arguments.
    It creates an InvalidToken object with the given token, adds it to the database, commits
    the changes to the database, and refreshes invalid_token. If any of these steps fail for 
    any reason (e.g., if there is already a row in the invalid_tokens table with that token), 
    then all of them are rolled back.
    
    :param token: str: Specify the token that is to be invalidated
    :param db: AsyncSession: Pass the database session to the function
    :return: The invalid_token object
    """
    invalid_token = InvalidToken(token=token)
    try:
        db.add(invalid_token)
        await db.commit()
        await db.refresh(invalid_token)
    except Exception as e:
        await db.rollback()
        raise e
    
    
async def is_validate_token(token: str, db: AsyncSession):
    """
    The is_validate_token function checks if the token is valid or not.
        Args:
            token (str): The user's authentication token.
            db (AsyncSession): The database session object.
    
    :param token: str: Check if the token is valid or not
    :param db: AsyncSession: Pass the database session to the function
    :return: True if the token is in the database
    """
    qwery = select(InvalidToken).filter(InvalidToken.token == token)
    result = await db.execute(qwery)

    invalid_token = result.scalar_one_or_none()

    if invalid_token:
        return True
    return False