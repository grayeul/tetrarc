#@file: constants.py
#@brief: Holds definitions of SideBarTables - used in admin page for editing
from . import data_models

# Create the SideBarTables
SIDEBAR_TABLES: list[data_models.SideBarTable] = [
    data_models.SideBarTable("LastTestBook", "material/home", "{LastBook}"),
    data_models.SideBarTable("BasicTestsPage", "material/table", "/app/admin/BasicTests/0",["admin"]),
    data_models.SideBarTable("TestBooksPage", "material/table", "/app/admin/TestBooks/0",["admin"]),
    data_models.SideBarTable("UserAdmin", "material/passkey", "/app/admin/UserAdmin",["admin"]),
]
