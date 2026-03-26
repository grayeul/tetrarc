#@file: constants.py
#@brief: Holds definitions of SideBarTables - used in admin page for editing
from . import data_models

# Create the SideBarTables
SIDEBAR_TABLES: list[data_models.SideBarTable] = [
    data_models.SideBarTable("Dashboard", "material/home", "/app/home"),
    data_models.SideBarTable("BasicTestsPage", "material/table", "/app/admin/BasicTests",["admin"]),
    data_models.SideBarTable("TestBooksPage", "material/table", "/app/admin/TestBooks",["admin"]),
]
