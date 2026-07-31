-- Database initialization script for Blog Platform
-- Contains all necessary Enums, Tables, Indexes, and Constraints.

-- 1. Create Enums
CREATE TYPE user_role AS ENUM ('USER', 'APPROVER', 'ADMIN');
CREATE TYPE blog_status AS ENUM ('DRAFT', 'PENDING', 'APPROVED', 'REJECTED');
CREATE TYPE feature_status AS ENUM ('PENDING', 'ACCEPTED', 'DECLINED', 'COMPLETED');
CREATE TYPE blog_type AS ENUM ('ARTICLE', 'TUTORIAL', 'NEWS', 'OPINION');
CREATE TYPE notification_type AS ENUM (
    'BLOG_PENDING', 
    'BLOG_APPROVED', 
    'BLOG_REJECTED', 
    'FEATURE_REQUESTED', 
    'FEATURE_UPDATED'
);

-- 2. Create Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'USER',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_users_email ON users (email);


-- 3. Create Blogs Table
CREATE TABLE blogs (
    id SERIAL PRIMARY KEY,
    blog_group_id INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    cover_image_url TEXT,
    status blog_status NOT NULL DEFAULT 'DRAFT',
    blog_type blog_type NOT NULL DEFAULT 'ARTICLE',
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    approved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMP WITH TIME ZONE,
    is_active_version BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_blogs_blog_group_id ON blogs (blog_group_id);
CREATE INDEX ix_blogs_author_id ON blogs (author_id);
CREATE INDEX ix_blogs_status ON blogs (status);


-- 4. Create Chats Table
CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    blog_group_id INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_chats_blog_group_id UNIQUE (blog_group_id)
);


-- 5. Create Messages Table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_messages_chat_id ON messages (chat_id);
CREATE INDEX ix_messages_author_id ON messages (author_id);


-- 6. Create Feature Requests Table
CREATE TABLE feature_requests (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status feature_status NOT NULL DEFAULT 'PENDING',
    priority INTEGER NOT NULL DEFAULT 3,
    category VARCHAR(100),
    requested_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_feature_requests_status ON feature_requests (status);
CREATE INDEX ix_feature_requests_requested_by ON feature_requests (requested_by);


-- 7. Create Notifications Table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type notification_type NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_notifications_user_id ON notifications (user_id);
