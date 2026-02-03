import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Main_System.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_view_only_user():
    # 1. Create Group
    group_name = 'ViewOnly'
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Group '{group_name}' created.")
    else:
        print(f"Group '{group_name}' already exists.")

    # 2. Create User
    username = 'viewonly'
    password = 'viewonly123'
    email = 'viewonly@example.com'

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"User '{username}' already exists.")
    else:
        user = User.objects.create_user(username=username, email=email, password=password)
        print(f"User '{username}' created.")

    # 3. Add User to Group
    if not user.groups.filter(name=group_name).exists():
        user.groups.add(group)
        print(f"User '{username}' added to '{group_name}' group.")
    else:
        print(f"User '{username}' is already in '{group_name}' group.")

    print("Done.")

if __name__ == '__main__':
    create_view_only_user()