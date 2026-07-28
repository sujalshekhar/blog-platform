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
    db.close()
    print("Seed complete!")

if __name__ == "__main__":
    seed()
