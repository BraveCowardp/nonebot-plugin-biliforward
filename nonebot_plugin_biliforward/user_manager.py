from .db import WhiteListDatabase
#todo
class User_manager:

    def __init__(self, user_tuple, group_id):
        self.user_tuple = user_tuple
        self.group_id = group_id

    @property
    def group_id():
        return self.group_id

    def add_user(user):
        self.user_tuple = self.user_tuple + (user,)

    def del_user(user):
        user_list = list(self.user_tuple)
        user_list.remove(user)
        self.user_tuple = tuple(user_list)

    def generate_list():
        for user in self.user_tuple:
            yield user

    def __str__():
        for user in self.user_tuple:
            print(f"- {user}/n")
    
def __user_list2user_tuple__(user_list):
    return tuple(user_list)

def load_from_database(database: WhiteListDatabase, group_id):  
    user_list = database.get_user_list_by_group_id(group_id)
    user_tuple = __user_list2user_tuple__(user_list)
    return User_manager(user_tuple, group_id)

def save2database(manager: User_manager, database: WhiteListDatabase, ):
    group_id = manager.group_id
    for user_id in manager.generate_list():
        if database.get_whitelist(group_id, user_id) == None:
            to_insert = WhiteList(
                group_id: group_id,
                bili_user_id: user_id,
                nick_name: "idk"
            )
            database.insert_whitelist_info(to_insert)
    
    