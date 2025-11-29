import datetime
import uuid

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql


class Base(orm.DeclarativeBase):
    pass


class FeedORM(Base):
    """
    ORM model for Feed entity
    """

    __tablename__ = "feeds"

    feed_id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    account_id = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
        index=True,
    )
    has_followed = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=False,
        default=False,
    )
    has_liked = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable=False,
        default=False,
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.now,
        index=True,
    )
    updated_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False),
        nullable=True,
        onupdate=datetime.datetime.now,
    )
    text = sqlalchemy.Column(
        sqlalchemy.Text,
        nullable=False,
    )
    likes_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0,
    )
    views_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0,
    )

    # Relationships
    images = orm.relationship(
        "ImageORM",
        back_populates="feed",
        # No cascade deletion - images will have feed_id set to NULL via DB foreign key constraint
        # Database has ondelete="SET NULL" configured, so images won't be deleted
        cascade="save-update",
        order_by="ImageORM.order",
    )
    likes = orm.relationship(
        "LikeORM",
        back_populates="feed",
        cascade="all, delete-orphan",
    )
    views = orm.relationship(
        "ViewORM",
        back_populates="feed",
        cascade="all, delete-orphan",
    )


class ImageORM(Base):
    """
    ORM model for Image entity
    """

    __tablename__ = "images"

    image_id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    feed_id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        sqlalchemy.ForeignKey("feeds.feed_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    uploader = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=False,
        index=True,
    )
    url = sqlalchemy.Column(
        sqlalchemy.String(2048),
        nullable=False,
    )
    blurhash = sqlalchemy.Column(
        sqlalchemy.String(255),
        nullable=True,
    )
    uploaded_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.now,
        index=True,
    )
    order = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
        default=0,
    )

    # Relationships
    feed = orm.relationship(
        "FeedORM",
        back_populates="images",
    )


class LikeORM(Base):
    """
    ORM model for Like entity
    """

    __tablename__ = "likes"

    feed_id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        sqlalchemy.ForeignKey("feeds.feed_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    account_id = sqlalchemy.Column(
        sqlalchemy.String(255),
        primary_key=True,
        nullable=False,
        index=True,
    )
    liked_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.now,
        index=True,
    )

    # Relationships
    feed = orm.relationship(
        "FeedORM",
        back_populates="likes",
    )

    __table_args__ = (
        sqlalchemy.Index("idx_likes_feed_account", "feed_id", "account_id"),
    )


class FollowerORM(Base):
    """
    ORM model for Follower entity
    """

    __tablename__ = "followers"

    follower = sqlalchemy.Column(
        sqlalchemy.String(255),
        primary_key=True,
        nullable=False,
        index=True,
    )
    follow_for = sqlalchemy.Column(
        sqlalchemy.String(255),
        primary_key=True,
        nullable=False,
        index=True,
    )
    followed_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.now,
        index=True,
    )

    __table_args__ = (
        sqlalchemy.Index("idx_followers_follower", "follower"),
        sqlalchemy.Index("idx_followers_follow_for", "follow_for"),
        sqlalchemy.Index("idx_followers_composite", "follower", "follow_for"),
    )


class ViewORM(Base):
    """
    ORM model for View entity
    """

    __tablename__ = "views"

    feed_id = sqlalchemy.Column(
        postgresql.UUID(as_uuid=True),
        sqlalchemy.ForeignKey("feeds.feed_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    account_id = sqlalchemy.Column(
        sqlalchemy.String(255),
        primary_key=True,
        nullable=False,
        index=True,
    )
    viewed_at = sqlalchemy.Column(
        sqlalchemy.DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.now,
        index=True,
    )

    # Relationships
    feed = orm.relationship(
        "FeedORM",
        back_populates="views",
    )

    __table_args__ = (
        sqlalchemy.Index("idx_views_feed_account", "feed_id", "account_id"),
    )
