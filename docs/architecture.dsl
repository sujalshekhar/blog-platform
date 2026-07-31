workspace "Blog Platform" "A collaborative blogging and discussion platform" {

    model {
        user = person "Platform User" "Can be a Reader, Author, Admin, or Approver."

        blogPlatform = softwareSystem "Blog Platform" "Allows users to write, review, publish, and discuss blog posts." {
            
            webApp = container "Single Page Application" "Provides the user interface for the blog platform." "React, TypeScript" "Web Browser"
            
            apiApp = container "API Server" "Provides blog management, user authentication, and real-time chat functionality." "FastAPI, Python" {
                authController = component "Auth Controller" "Handles login and JWT issuance."
                blogController = component "Blog Controller" "Handles CRUD operations for blogs."
                chatController = component "Chat & WebSocket Controller" "Handles real-time chat broadcasts."
                blogService = component "Blog Service" "Business logic for blog lifecycle and cache invalidation."
                chatService = component "Chat Service" "Business logic for persisting chat history."
                repository = component "Data Repository" "Database access layer."
            }
            
            database = container "Primary Database" "Stores user accounts, blog posts, revisions, and chat history." "PostgreSQL" "Database"
            
            cache = container "Key-Value Cache" "Caches approved blog details for fast read performance." "Redis"
        }

        # Relationships between users and the system
        user -> webApp "Visits the platform, reads blogs, and participates in chat using"
        
        # Relationships between containers
        webApp -> apiApp "Makes API calls, SSE subscriptions, and WebSocket connections to" "JSON/HTTPS/WSS"
        apiApp -> database "Reads from and writes to" "SQLAlchemy/SQL/TCP"
        apiApp -> cache "Reads from, invalidates, and caches approved blogs" "Redis Protocol/TCP"

        # Relationships inside API Server
        authController -> repository "Reads and validates user data"
        blogController -> blogService "Delegates business logic, queues background tasks"
        chatController -> chatService "Delegates real-time chat persistence"
        blogService -> repository "Reads and writes blog revisions (ACID compliant)"
        chatService -> repository "Reads and writes chat message history"
        blogService -> cache "Reads from and invalidates cache entries on blog updates"
        
        # Detailed internal relationships
        apiApp -> apiApp "Uses BackgroundTasks to execute non-blocking operations like SSE broadcasts and cache invalidation" "FastAPI"
    }

    views {
        systemContext blogPlatform "SystemContext" {
            include *
            autoLayout
            description "The system context view for the Blog Platform."
        }

        container blogPlatform "Containers" {
            include *
            autoLayout
            description "The container view for the Blog Platform."
        }
        
        component apiApp "Components" {
            include *
            autoLayout
            description "The component diagram for the FastAPI application."
        }

        theme default
        
        styles {
            element "Web Browser" {
                shape WebBrowser
            }
            element "Database" {
                shape Cylinder
            }
        }
    }
}
