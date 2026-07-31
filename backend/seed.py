import os
import sys

# Ensure we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.enums.role import UserRole
from app.core.security import hash_password

def seed():
    db = SessionLocal()
    
    # Create ADMIN
    admin_user = db.query(User).filter_by(email="admin@example.com").first()
    if not admin_user:
        admin_user = User(
            first_name="System",
            last_name="Admin",
            email="admin@example.com",
            password_hash=hash_password("adminpassword123"),
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        print("Created Admin: admin@example.com / adminpassword123")
    else:
        print("Admin already exists: admin@example.com / adminpassword123")
        
    # Create APPROVER
    approver_user = db.query(User).filter_by(email="approver@example.com").first()
    if not approver_user:
        approver_user = User(
            first_name="Content",
            last_name="Approver",
            email="approver@example.com",
            password_hash=hash_password("approverpassword123"),
            role=UserRole.APPROVER
        )
        db.add(approver_user)
        print("Created Approver: approver@example.com / approverpassword123")
    else:
        print("Approver already exists: approver@example.com / approverpassword123")
        
    db.commit()
    
    # Refresh to ensure we have IDs
    db.refresh(admin_user)
    db.refresh(approver_user)
    
    # Create USER
    normal_user = db.query(User).filter_by(email="user@example.com").first()
    if not normal_user:
        normal_user = User(
            first_name="Test",
            last_name="User",
            email="user@example.com",
            password_hash=hash_password("userpassword123"),
            role=UserRole.USER
        )
        db.add(normal_user)
        db.commit()
        db.refresh(normal_user)
        print("Created User: user@example.com / userpassword123")
    else:
        print("User already exists: user@example.com / userpassword123")

    from app.models.blog import Blog
    from app.enums.blog_status import BlogStatus
    from app.enums.blog_type import BlogType
    from app.models.chat import Chat
    from app.models.message import Message
    import random
    from datetime import datetime, timedelta, timezone

    blog_count = db.query(Blog).count()
    if blog_count < 100:
        print("Seeding 100 blogs...")
        statuses = [BlogStatus.DRAFT, BlogStatus.PENDING, BlogStatus.APPROVED, BlogStatus.REJECTED]
        authors = [admin_user, approver_user, normal_user]
        blog_types = [BlogType.ARTICLE, BlogType.TUTORIAL, BlogType.NEWS, BlogType.OPINION]
        
        for i in range(1, 101):
            status = random.choices(statuses, weights=[10, 20, 60, 10])[0] # 60% approved
            author = random.choice(authors)
            blog_type = random.choice(blog_types)
            
            cover_image_url = f"https://picsum.photos/seed/blog{i}/800/400"
            
            blog = Blog(
                blog_group_id=0,
                version=1,
                title=f"Sample Blog Post #{i}",
                content=f"<p>This is the content for sample blog post #{i}. It has some <strong>rich text</strong>.</p><br/><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam in dui mauris.</p>" * 3,
                cover_image_url=cover_image_url,
                status=status,
                blog_type=blog_type,
                author_id=author.id,
                is_active_version=True,
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
            )
            
            if status in [BlogStatus.APPROVED, BlogStatus.REJECTED]:
                blog.approved_by = approver_user.id
                blog.approved_at = blog.created_at + timedelta(hours=random.randint(1, 24))
                
            db.add(blog)
            db.commit()
            db.refresh(blog)
            
            # Set blog_group_id to its own ID
            blog.blog_group_id = blog.id
            db.commit()
            
            # If approved, randomly add chat messages
            if status == BlogStatus.APPROVED and random.random() > 0.3:
                chat = Chat(blog_group_id=blog.id)
                db.add(chat)
                db.commit()
                db.refresh(chat)
                
                # Seed 10 to 60 messages to test pagination
                num_messages = random.randint(10, 60)
                for j in range(num_messages):
                    msg_author = random.choice(authors)
                    msg = Message(
                        chat_id=chat.id,
                        author_id=msg_author.id,
                        content=f"This is a sample comment #{j+1} for blog post #{i}. Testing the real-time chat pagination features!",
                        created_at=blog.created_at + timedelta(hours=random.randint(25, 100) + j)
                    )
                    db.add(msg)
                db.commit()
        print("Seeded 100 blogs and chats.")
    else:
        print(f"Blogs already seeded (count: {blog_count}).")

    db.close()
    print("Seed complete!")

if __name__ == "__main__":
    seed()
