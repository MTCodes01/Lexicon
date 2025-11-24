"""
Initialize default data for Lexicon.
Creates default roles, permissions, and system settings.
"""
from sqlalchemy.orm import Session
from api.core import models, crud


def init_default_roles(db: Session) -> None:
    """Initialize default roles."""
    default_roles = [
        {
            "name": "owner",
            "display_name": "Owner",
            "description": "System owner with full access",
            "is_system": True,
        },
        {
            "name": "admin",
            "display_name": "Administrator",
            "description": "Administrator with elevated privileges",
            "is_system": True,
        },
        {
            "name": "user",
            "display_name": "User",
            "description": "Standard user with basic access",
            "is_system": True,
        },
        {
            "name": "service",
            "display_name": "Service Account",
            "description": "Service account for API access",
            "is_system": True,
        },
    ]
    
    for role_data in default_roles:
        existing_role = crud.role_crud.get_by_name(db, role_data["name"])
        if not existing_role:
            role = models.Role(**role_data)
            db.add(role)
            print(f"  ✓ Created role: {role_data['name']}")
    
    db.commit()


def init_default_permissions(db: Session) -> None:
    """Initialize default permissions."""
    default_permissions = [
        # User permissions
        {"name": "users.view", "display_name": "View Users", "resource": "users", "action": "view", "is_system": True},
        {"name": "users.create", "display_name": "Create Users", "resource": "users", "action": "create", "is_system": True},
        {"name": "users.edit", "display_name": "Edit Users", "resource": "users", "action": "edit", "is_system": True},
        {"name": "users.delete", "display_name": "Delete Users", "resource": "users", "action": "delete", "is_system": True},
        
        # Role permissions
        {"name": "roles.view", "display_name": "View Roles", "resource": "roles", "action": "view", "is_system": True},
        {"name": "roles.create", "display_name": "Create Roles", "resource": "roles", "action": "create", "is_system": True},
        {"name": "roles.edit", "display_name": "Edit Roles", "resource": "roles", "action": "edit", "is_system": True},
        {"name": "roles.delete", "display_name": "Delete Roles", "resource": "roles", "action": "delete", "is_system": True},
        
        # Settings permissions
        {"name": "settings.view", "display_name": "View Settings", "resource": "settings", "action": "view", "is_system": True},
        {"name": "settings.edit", "display_name": "Edit Settings", "resource": "settings", "action": "edit", "is_system": True},
        
        # Audit log permissions
        {"name": "audit.view", "display_name": "View Audit Logs", "resource": "audit", "action": "view", "is_system": True},
    ]
    
    for perm_data in default_permissions:
        existing_perm = crud.permission_crud.get_by_name(db, perm_data["name"])
        if not existing_perm:
            permission = models.Permission(**perm_data)
            db.add(permission)
            print(f"  ✓ Created permission: {perm_data['name']}")
    
    db.commit()


def assign_permissions_to_roles(db: Session) -> None:
    """Assign permissions to default roles."""
    # Owner gets all permissions
    owner_role = crud.role_crud.get_by_name(db, "owner")
    if owner_role:
        all_permissions = crud.permission_crud.get_multi(db, limit=1000)
        owner_role.permissions = all_permissions
        print(f"  ✓ Assigned all permissions to owner role")
    
    # Admin gets most permissions (except user management)
    admin_role = crud.role_crud.get_by_name(db, "admin")
    if admin_role:
        admin_perms = [
            "users.view", "roles.view", "settings.view", "settings.edit", "audit.view"
        ]
        permissions = []
        for perm_name in admin_perms:
            perm = crud.permission_crud.get_by_name(db, perm_name)
            if perm:
                permissions.append(perm)
        admin_role.permissions = permissions
        print(f"  ✓ Assigned permissions to admin role")
    
    # User gets basic permissions
    user_role = crud.role_crud.get_by_name(db, "user")
    if user_role:
        user_perms = ["settings.view"]
        permissions = []
        for perm_name in user_perms:
            perm = crud.permission_crud.get_by_name(db, perm_name)
            if perm:
                permissions.append(perm)
        user_role.permissions = permissions
        print(f"  ✓ Assigned permissions to user role")
    
    db.commit()


def init_default_data(db: Session) -> None:
    """Initialize all default data."""
    print("  📝 Initializing default roles...")
    init_default_roles(db)
    
    print("  🔑 Initializing default permissions...")
    init_default_permissions(db)
    
    print("  🔗 Assigning permissions to roles...")
    assign_permissions_to_roles(db)
    
    print("  ✅ Default data initialized successfully!")
