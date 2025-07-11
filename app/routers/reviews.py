from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, func
from sqlalchemy.orm import selectinload
from typing import Annotated
from app.backend.db_depends import get_db
from  .auth import get_current_user
from app.schemas import CreateReview
from ..models import Product
from ..models.reviews import Review

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/')
async def all_reviews(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found",
        )
    return reviews.all()

@router.get('/{product_slug}')
async def products_reviews(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        product_slug: str,
):
    product = await db.scalar(select(Product).options(selectinload(Product.reviews)).where(
        Product.slug == product_slug,
        Product.is_active == True
    ))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    reviews = product.reviews
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reviews found",
        )
    return reviews

@router.post('/', status_code=status.HTTP_201_CREATED)
async def add_review(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        review: CreateReview,
):
    if get_user.get('is_customer') or get_user.get('is_admin'):
        product = await db.scalar(select(Product).where(
            Product.is_active == True,
            Product.id == review.product_id
        ))
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found",
            )
        await db.execute(insert(Review).values(
            user_id=get_user.get('id'),
            product_id=review.product_id,
            comment=review.comment,
            grade=review.grade,
        ))
        avg_rating = await db.execute(
            select(func.avg(Review.grade)).where(
                Review.product_id==review.product_id,
                Review.is_active == True
            )
        )
        avg_rating_scalar = avg_rating.scalar()
        product.rating = avg_rating_scalar
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Product update is successful',
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )

@router.delete('/{review_id}')
async def delete_reviews(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        review_id: int,
):
    if get_user.get('is_admin'):
        review = await db.scalar(select(Review).options(selectinload(Review.product)).where(
            Review.id == review_id,
            Review.is_active == True,
        ))
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No review found",
            )
        review.is_active = False
        avg_rating = await db.execute(
            select(func.avg(Review.grade)).where(
                Review.product_id == review.product.id,
                Review.is_active == True
            )
        )
        review.product.rating = avg_rating.scalar()
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'message': 'Review deleted',
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
