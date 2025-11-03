import anvil.server, json
from datetime import datetime
from anvil.files import get_app_file

@anvil.server.callable
def login_user(username, production_key):
    try:
        with open(get_app_file('users_local.json'), 'r') as f:
            users = json.load(f)
    except Exception:
        return False
    for u in users:
        if u.get('username','').lower() == username.lower() and u.get('production_key') == production_key:
            if not u.get('active', True):
                return False
            try:
                exp = datetime.fromisoformat(u.get('expiration_date'))
                if datetime.now() > exp:
                    return False
            except Exception:
                return False
            return True
    return False
