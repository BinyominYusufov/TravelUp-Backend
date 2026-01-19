from accounts.models import Permission

def generate_and_save_model_level_permissions(models, session):
    actions = ["add", "read", "edit", "delete"]
    permissions = []
    for model in models:
        for action in actions:
            permissions.append({
                "name":f"{model}:{action}",
                "description": f"Can {action} {model}"
            })
    session.execute(Permission.__table__.insert(), permissions)
    session.commit()