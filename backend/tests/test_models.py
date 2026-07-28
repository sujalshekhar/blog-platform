import datetime
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.blog import Blog
from app.models.chat import Chat
from app.models.message import Message
from app.models.notification import Notification
from app.models.feature_request import FeatureRequest
from app.enums.role import UserRole
from app.enums.blog_status import BlogStatus
from app.enums.feature_status import FeatureStatus
from app.enums.notification_type import NotificationType


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_user(db: Session, email: str, first_name: str = "Test") -> User:
    user = User(
        first_name=first_name,
        last_name="User",
        email=email,
        password_hash="hashed_pw",
        role=UserRole.USER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def make_blog(db: Session, user: User, group_id: int = 1) -> Blog:
    blog = Blog(
        blog_group_id=group_id,
        version=1,
        title="Test Blog",
        content="Some content",
        status=BlogStatus.DRAFT,
        author_id=user.id,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_create_user(db_session: Session) -> None:
    user = User(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        password_hash="hashedpassword123",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.first_name == "Jane"
    assert user.email == "jane.doe@example.com"
    assert user.role == UserRole.ADMIN
    assert repr(user) == (
        f"<User(id={user.id}, first_name='Jane', email='jane.doe@example.com', role=ADMIN)>"
    )


def test_user_default_role(db_session: Session) -> None:
    user = User(
        first_name="John",
        email="john.doe@example.com",
        password_hash="anotherhash456",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.role == UserRole.USER
    assert user.last_name is None


def test_create_blog(db_session: Session) -> None:
    user = make_user(db_session, "author@example.com", "Author")
    blog = make_blog(db_session, user, group_id=10)

    assert blog.id is not None
    assert blog.blog_group_id == 10
    assert blog.version == 1
    assert blog.status == BlogStatus.DRAFT
    assert blog.author_id == user.id
    assert blog.is_active_version is True
    assert "Blog" in repr(blog)


def test_create_chat(db_session: Session) -> None:
    chat = Chat(blog_group_id=20)
    db_session.add(chat)
    db_session.commit()
    db_session.refresh(chat)

    assert chat.id is not None
    assert chat.blog_group_id == 20
    assert "Chat" in repr(chat)


def test_create_message(db_session: Session) -> None:
    user = make_user(db_session, "msg_user@example.com")
    chat = Chat(blog_group_id=30)
    db_session.add(chat)
    db_session.commit()
    db_session.refresh(chat)

    msg = Message(chat_id=chat.id, author_id=user.id, content="Hello world")
    db_session.add(msg)
    db_session.commit()
    db_session.refresh(msg)

    assert msg.id is not None
    assert msg.content == "Hello world"
    assert "Message" in repr(msg)


def test_create_notification(db_session: Session) -> None:
    user = make_user(db_session, "notif_user@example.com")

    notif = Notification(
        user_id=user.id,
        type=NotificationType.BLOG_APPROVED,
        content="Your blog was approved.",
    )
    db_session.add(notif)
    db_session.commit()
    db_session.refresh(notif)

    assert notif.id is not None
    assert notif.is_read is False
    assert notif.type == NotificationType.BLOG_APPROVED
    assert "Notification" in repr(notif)


def test_create_feature_request(db_session: Session) -> None:
    user = make_user(db_session, "feat_user@example.com")

    fr = FeatureRequest(
        title="Dark mode",
        description="Please add dark mode.",
        status=FeatureStatus.PENDING,
        requested_by=user.id,
    )
    db_session.add(fr)
    db_session.commit()
    db_session.refresh(fr)

    assert fr.id is not None
    assert fr.priority == 3
    assert fr.status == FeatureStatus.PENDING
    assert "FeatureRequest" in repr(fr)


def test_user_relationships(db_session: Session) -> None:
    user = make_user(db_session, "rel_user@example.com")
    blog = make_blog(db_session, user, group_id=40)

    notif = Notification(
        user_id=user.id,
        type=NotificationType.BLOG_PENDING,
        content="Blog pending review.",
    )
    db_session.add(notif)

    fr = FeatureRequest(
        title="New feature",
        description="Need this feature.",
        status=FeatureStatus.PENDING,
        requested_by=user.id,
    )
    db_session.add(fr)
    db_session.commit()

    db_session.refresh(user)
    assert any(b.id == blog.id for b in user.blogs_authored)
    assert any(n.id == notif.id for n in user.notifications)
    assert any(f.id == fr.id for f in user.feature_requests)
