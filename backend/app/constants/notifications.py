# Notification Templates
NOTIF_TITLE_NEW_SUBMISSION = "New Blog Submission"
def notif_msg_new_submission(title: str, author_name: str) -> str:
    return f"'{title}' was submitted for review by {author_name}."

NOTIF_TITLE_BLOG_APPROVED = "Blog Approved"
def notif_msg_blog_approved(title: str) -> str:
    return f"Your blog '{title}' has been approved!"

NOTIF_TITLE_BLOG_REJECTED = "Blog Rejected"
def notif_msg_blog_rejected(title: str) -> str:
    return f"Your blog '{title}' has been rejected."

NOTIF_TITLE_FEATURE_STATUS = "Feature Request Update"
def notif_msg_feature_status(title: str, status: str) -> str:
    return f"Your request '{title}' is now {status}."

NOTIF_TITLE_NEW_FEATURE = "New Feature Request"
def notif_msg_new_feature(title: str, user_name: str) -> str:
    return f"New feature requested by {user_name}: '{title}'."
