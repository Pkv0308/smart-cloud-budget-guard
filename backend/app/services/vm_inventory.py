from sqlalchemy.dialects.postgresql import insert
from backend.app.database import SessionLocal
from sqlalchemy.sql import func
#importing Resource class from models.py
from backend.app. database.models import Resource
from sqlalchemy import select


# insert/update resources
def upsert_resources(vm_items: list[dict])->int:
    """
    Normalize Azure VM items and insert/update into the resources table.
    Returns the number of rows processed.
    """

    db=SessionLocal()
    try:
        for vm in vm_items:
            tags=vm.get("tags",{})
            stmt=insert(Resource).values(
                vm_name=vm["name"],
                location=vm["location"],
                power_state=vm["power_state"],
                environment=tags.get("Environment","Unknown"),
                owner=tags.get("Owner","Unknown"),
                project=tags.get("Project","Unknown"),
                tags=tags,
            )
            stmt=stmt.on_conflict_do_update(
                index_elements=["vm_name"],
                set_={
                    "location":stmt.excluded.location,
                    "power_state":stmt.excluded.power_state,
                    "environment":stmt.excluded.environment,
                    "owner":stmt.excluded.owner,
                    "project":stmt.excluded.project,
                    "tags":stmt.excluded.tags,
                    "last_synced_at":func.now(),
                },
            )
            db.execute(stmt)
        db.commit()
        return len(vm_items)
    finally:
        db.close()


def get_all_resources()->list[dict]:
    """Returns persisted VM resources from the Postgres DB as plain dicts"""
    db=SessionLocal()
    try:
        rows=db.execute(select(Resource)).scalars().all()
        return [
            {
                "vm_name":r.vm_name,
                "vm_location":r.location,
                "power_state":r.power_state,
                "environment":r.environment,
                "owner":r.owner,
                "project":r.project,
                "tags":r.tags,
                "last_synced_at":r.last_synced_at.isoformat() if r.last_synced_at else None,

            }
            for r in rows
        ]
    finally:
        db.close()