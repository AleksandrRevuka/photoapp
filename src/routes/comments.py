from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.comments import CommentCreate, CommentUpdate
from src.services.roles import admin_moderator_user, admin_moderator
from src.repository import comments as repository_comments
from src.services.auth import auth_service
from src.database.models import User


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/",
    dependencies=[Depends(admin_moderator_user)],
    description="User, Moderator and Administrator have access",
)
async def create_comment(
    picture_id: int,
    body: CommentCreate,
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The create_comment function creates a new comment in the database.

    :param body: CommentCreate: Create a new comment
    :param db: AsyncSession: Pass the database connection to the repository
    :param : Get the comment id from the url
    :return: A comment object
    """

    comment = await repository_comments.create_comment(body, picture_id, current_user.id, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not created")
    return comment


@router.patch(
    "/{comment_id}",
    dependencies=[Depends(admin_moderator_user)],
    description="User, Moderator and Administrator have access",
)
async def update_comment(
    comment_id: int,
    body: CommentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    The update_comment function updates a comment in the database.
        It takes an id of the comment to be updated, and a body containing
        all fields that are to be updated.

    :param comment_id: int: Specify the id of the comment to be updated
    :param body: CommentUpdate: Pass the data from the request body to the function
    :param db: AsyncSession: Get the database session
    :param : Get the comment id from the url
    :return: A comment
    :doc-author: Trelent
    """

    comment = await repository_comments.update_comment(comment_id, body, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not created")
    return comment


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_moderator)],
    description="Moderator and Administrator have access",
)
async def remove_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    The delete_comment function deletes a comment from the database.
        Args:
            comment_id (int): The id of the comment to be deleted.
            db (AsyncSession): An async session object for interacting with the database.

    :param comment_id: int: Identify the comment to be deleted
    :param db: AsyncSession: Pass in the database session
    :param : Specify the id of the comment to be deleted
    :return: A 204 status code
    """
    comment = await repository_comments.delete_comment(comment_id, db)
    return comment


@router.get(
    "/picture/{picture_id}",
    dependencies=[Depends(admin_moderator_user)],
    description="User, Moderator and Administrator have access",
)
async def comments_to_photo(
    picture_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    The comments_to_photo function returns a list of comments to the photo with the given picture_id.
    The skip and limit parameters are used for pagination, where skip is how many comments to skip and limit is how many
    comments to return.

    :param picture_id: int: Get the comments to a specific photo
    :param skip: int: Skip the first n comments
    :param limit: int: Limit the number of comments returned
    :param db: AsyncSession: Get the database session
    :return: A list of comments to a photo
    """

    comments = await repository_comments.get_comments_to_photo(skip, limit, picture_id, db)
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found")
    return comments


@router.get(
    "/user/{user_id}",
    dependencies=[Depends(admin_moderator_user)],
    description="User, Moderator and Administrator have access",
)
async def comments_of_user(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    The get_comments_of_user function returns a list of comments for the user with the given id.
    The function takes in an optional skip and limit parameter to paginate through results.

    :param skip: int: Skip the first n comments
    :param limit: int: Limit the number of comments returned
    :param user_id: int: Get the comments of a specific user
    :param db: AsyncSession: Get the database session
    :param : Get the comments of a specific user
    :return: A list of comments
    """

    comments = await repository_comments.get_comments_of_user(skip, limit, user_id, db)
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found")
    return comments
