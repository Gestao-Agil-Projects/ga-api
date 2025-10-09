from datetime import datetime
from typing import Any

from ga_api.db.models.users import User


class AdminUtils:

    @staticmethod
    def populate_admin_data(obj: Any, admin: User, update_only: bool = False) -> None:
        if not admin.is_superuser:
            raise Exception("This action can only be performed by superusers")

        if not update_only and hasattr(obj, "created_by_admin_id"):
            obj.created_by_admin_id = admin.id

        if not update_only and hasattr(obj, "created_at"):
            obj.created_at = datetime.now()

        if hasattr(obj, "updated_by_admin_id"):
            obj.updated_by_admin_id = admin.id

        if hasattr(obj, "updated_at"):
            obj.updated_at = datetime.now()
