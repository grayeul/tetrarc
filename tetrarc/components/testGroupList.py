# @file: testGroupList.py
# @brief: This component produces ListView of all of the tests in a given group
from __future__ import annotations

from dataclasses import KW_ONLY, field
from .. import data_models,persistence
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
        #print(f"Building a ListView, from testsForGroup: {self.testsForGroup} - edit={self.editmode}")
        pers=self.session[persistence.Persistence]
        uim=self.session[data_models.UserInfoModel]
        for test in self.testsForGroup:
            passes=pers.db.getTestPassCnt(test['id'],uim.d['book'],self.arch)
            fails=pers.db.getTestFailCnt(test['id'],uim.d['book'],self.arch)
            print(f"For test {test['id']} => {passes} / {fails}")
            test['passes']=passes
            test['fails']=fails
            if test['id'] == 6:
                print(f"In testGroupList => {test}")
        dirOfRows=[comps.CustomListRow(testdict=x,key=x['name'],arch=self.arch,
                    editmode=self.editmode) 
                       for x in self.testsForGroup]
        #print(f"Now building the listview")
        hdr={"shortname":"Name","description":"Description","passes":"NumPasses","fails":"NumFails",
             "submit":"Submit Result"}
        rlist = rio.ListView(
            comps.CustomListRow(testdict=hdr,key='hdr',hdr=True,arch=self.arch,editmode=self.editmode),
            *dirOfRows,
            #*[comps.CustomListRow(testdict=x,key=x['name'],arch=self.arch,editmode=self.editmode) 
            #    for x in self.testsForGroup],
            selection_mode="none")
        return rlist 
