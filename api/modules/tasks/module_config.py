"""
Module configuration for Tasks module.
This file is automatically discovered by the module loader.
"""

module_config = {
    "name": "Tasks",
    "slug": "tasks",
    "version": "1.0.0",
    "description": "Task management system with priorities, due dates, and tags",
    "author": "Lexicon Team",
    "icon": "CheckSquare",
    "color": "#3B82F6",
    
    # API configuration
    "api_router": "routes.py",
    
    # Permissions required by this module
    "permissions": [
        {
            "name": "tasks.view",
            "display_name": "View Tasks",
            "description": "View own and shared tasks",
            "resource": "tasks",
            "action": "view",
        },
        {
            "name": "tasks.create",
            "display_name": "Create Tasks",
            "description": "Create new tasks",
            "resource": "tasks",
            "action": "create",
        },
        {
            "name": "tasks.edit",
            "display_name": "Edit Tasks",
            "description": "Edit own and shared tasks",
            "resource": "tasks",
            "action": "edit",
        },
        {
            "name": "tasks.delete",
            "display_name": "Delete Tasks",
            "description": "Delete own tasks",
            "resource": "tasks",
            "action": "delete",
        },
    ],
    
    # Frontend widgets (for dashboard)
    "widgets": [
        {
            "name": "TaskSummary",
            "description": "Summary of task statistics",
            "sizes": ["small", "medium"],
        },
        {
            "name": "UpcomingTasks",
            "description": "List of upcoming tasks",
            "sizes": ["medium", "large"],
        },
    ],
    
    # Event signals this module emits
    "signals": [
        "task.created",
        "task.updated",
        "task.completed",
        "task.deleted",
    ],
    
    # Module dependencies (other modules required)
    "dependencies": [],
    
    # Settings schema for this module
    "settings_schema": {
        "default_priority": {
            "type": "string",
            "default": "medium",
            "options": ["low", "medium", "high", "urgent"],
        },
        "enable_notifications": {
            "type": "boolean",
            "default": True,
        },
        "notification_advance_minutes": {
            "type": "integer",
            "default": 15,
        },
    },
}
