from typing import Optional, Dict, Any
from app.core.supabase import supabase, supabase_admin
from app.schemas.user import User

async def delete_user_from_supabase(user_id: str) -> Dict[str, Any]:
    if not user_id:
        return {"success": False, "error": "user_id is required"}
    # Delete from profiles first
    try:
        profile_resp = supabase.table("profiles").delete().eq("id", user_id).execute()
        if hasattr(profile_resp, 'error') and profile_resp.error:
            return {"success": False, "error": f"profiles: {profile_resp.error}"}
    except Exception as e:
        return {"success": False, "error": f"profiles: {str(e)}"}
    # Delete from auth.users using admin client
    try:
        admin_resp = supabase_admin.auth.admin.delete_user(user_id)
        # For some supabase-py versions, admin_resp may not have error, so just check for exception
    except Exception as e:
        return {"success": False, "error": f"auth.users: {str(e)}"}
    return {"success": True, "error": None}

async def fetch_users_from_supabase(
    limit: int = 10,
    offset: int = 0,
    search: Optional[str] = None
) -> Dict[str, Any]:
    import logging
    query = supabase.table("profiles")
    if search:
        # Search on email, first_name, or last_name (case-insensitive, partial match)
        query = query.or_(
            f"email.ilike.%25{search}%25,first_name.ilike.%25{search}%25,last_name.ilike.%25{search}%25"
        )
    try:
        query = query.select("*").range(offset, offset + limit - 1)
        response = query.execute()
    except AttributeError as e:
        import logging
        logging.error(f"Supabase query does not support .range: {e}")
        response = query.select("*").execute()  # fallback: no pagination
    if hasattr(response, 'error') and response.error:
        return {"users": [], "total": 0, "error": str(response.error)}
    users = response.data or []
    total = len(users)
    return {"users": users, "total": total, "error": None}
