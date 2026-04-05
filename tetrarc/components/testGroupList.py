# @file: testGroupList.py
# @brief: This component produces ListView of all of the tests in a given group
from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from .. import components as comps

class TestGroupList(rio.Component):
    """
    This returns a ListView of the tests for the given testgroup
    """
    arch: str
    testgroup: str
    editmode: bool = False
    testsForGroup: list[dict] = [{"name":"default","id":0}]
    active_testid: int = 0

    def build(self) -> rio.Component:
        print(f"Building a ListView, from testsForGroup: {self.testsForGroup} - edit={self.editmode}")
        dirOfRows=[comps.CustomListRow(testdict=x,arch=self.arch,
                    editmode=self.editmode) 
                       for x in self.testsForGroup]
        print(f"Now building the listview")
        hdr={"name":"Name","description":"Description","passes":"NumPasses","fails":"NumFails",
             "submit":"Submit Result"}
        rlist = rio.ListView(
            #*[rio.SimpleListItem("Item 1",key="item1")],
            #*[comps.CustomListRow(testdict=self.testsForGroup[0],key="item1")],
            comps.CustomListRow(testdict=hdr,key='hdr',hdr=True,arch=self.arch,editmode=self.editmode),
            *[comps.CustomListRow(testdict=x,key=x['name'],arch=self.arch,editmode=self.editmode) 
                for x in self.testsForGroup],
            selection_mode="none")
        return rlist 
