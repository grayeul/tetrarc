# @file: testGroupList.py
# @brief: This component produces ListView of all of the tests in a given group
from __future__ import annotations

from dataclasses import KW_ONLY, field
from .. import data_models,persistence
import typing as t
import functools
from operator import itemgetter

import rio

from .. import components as comps

class TestGroupList(rio.Component):
    """
    This returns a ListView of the tests for the given testgroup
    """
    arch: str
    testgroup: str
    rcname: str
    editmode: bool = False
    testsForGroup: list[dict] = [{"name":"default","id":0}]
    active_testid: int = 0
    orderDesc: bool = False
    sortkey:str ='testorder'

    def changeArch(self,event):
        uim=self.session[data_models.UserInfoModel]
        uim.d['arch']=event.value
    def changeSort(self,sortkey:str):
        if self.sortkey == sortkey:
            self.orderDesc = not self.orderDesc
        else:
            self.orderDesc = False
            self.sortkey=sortkey
    def gotoAddResult(self,testid) -> None:
        uim=self.session[data_models.UserInfoModel]
        book=uim.d['book']
        self.session.navigate_to(f"/app/addresults-page/{book}/{self.rcname}/{testid}")
    def gotoEditResult(self,testid) -> None:
        self.session.navigate_to(f"/app/admin/BasicTests/{testid}")
    def testRow(self,test:dict) -> list[rio.Component]:
        name=test["shortname"]
        blocking = test.get("blocking",False)
        uim=self.session[data_models.UserInfoModel]
        book=uim.d['book']
        try:
            testid=test["id"]
        except:
            testid=0
            #print(f"Building a row, with testdict={self.testdict} edit={self.editmode}")
        description=test["description"]
        user_sess = self.session[data_models.UserSessionModel]
        passes=test.get("passes",0)
        fails=test.get("fails",0)
        adminpass=test.get("adminpass",False)
        addbtn=rio.Column(rio.Spacer(),
                          rio.Button("Submit",
                             on_press=functools.partial(self.gotoAddResult,testid))
                         )
        editbtn=rio.Column(rio.Spacer(),
                          rio.Button("Edit",
                             on_press=functools.partial(self.gotoEditResult,testid))
                          )
        rval=[]
        if not self.editmode:
            rval.append(rio.Checkbox(is_on=blocking,key=f"blocking{book}/{testid}",
                            is_sensitive=False,align_x=0.5))
        rval.extend( [
                     rio.Link(
                         rio.Button(name,align_x=0,style='plain-text'),
                         f"/app/results/{book}/{testid}"),
                     rio.Markdown(description,align_x=0,min_width=40)
                     ]
                   )
        if self.editmode:
            rval.append( 
                   rio.Column(rio.Spacer(),
                              rio.Button("Edit",
                              on_press=functools.partial(self.gotoEditResult,testid))
                   )
                )
        else:
            if 'lead' in user_sess.d['roles']:
                allowcheck=True
            else:
                allowcheck=False
            rval.append(rio.Checkbox(is_on=adminpass,key=f"adminpass{book}/{testid}",
                        is_sensitive=False,on_change=None))
            rval.append(rio.Text(str(passes),style="text",align_x=0.5))
            rval.append(rio.Text(str(fails),style="text",align_x=0.5))
            rval.append( 
                   rio.Column(rio.Spacer(),
                              rio.Button("Submit",
                              on_press=functools.partial(self.gotoAddResult,testid))
                   )
                )
        return rval

    def getGrid(self,tests:list[dict],book:str,arch:str,rcname:str) -> rio.Component:
        pers=self.session[persistence.Persistence]
        uim=self.session[data_models.UserInfoModel]
        user_sess = self.session[data_models.UserSessionModel]
        # Add the passes and fails
        for test in tests:
            passes=pers.db.getTestPassCnt(test['id'],book,arch,rcname)
            fails=pers.db.getTestFailCnt(test['id'],book,arch,rcname)
            adminpass=pers.db.getTestAdminPass(test['id'],book,arch,rcname)
            test['passes']=passes
            test['fails']=fails
            test['adminpass']=adminpass
        # Now build the component grid
        hdrstyle="heading3"
        if self.editmode:
            hdrRow=[
                 rio.Row(
                     rio.Button(rio.Text("OrgSrt",style='text',align_x=0),
                        style="plain-text",align_x=0,
                        on_press=functools.partial(self.changeSort,'testorder')),
                     rio.Button(rio.Text('Name',style=hdrstyle),style='plain-text',
                        grow_x=True,
                        on_press=functools.partial(self.changeSort,'shortname')),
                align_x=0),
            ]
        else:
            hdrRow=[ 
                 rio.Row(
                     rio.Button(rio.Text("OrgSrt",style='text',align_x=0),
                        style="plain-text",align_x=0,
                        on_press=functools.partial(self.changeSort,'testorder')),
                   rio.Button(rio.Text('Blocking',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'blocking'))
                    ) ]
            hdrRow.append(
                 rio.Button(rio.Text('Name',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'shortname'))
                    )
        hdrRow.extend([
                 rio.Button(rio.Text('Description',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'description')),
                    ]
                 )
        if self.editmode:
            # Edit mode should only be possible if already checked admin privileges...
            hdrRow.append( rio.Text("Edit",style=hdrstyle ))
        else:
            hdrRow.extend([
                 rio.Button(rio.Text('Admin\nPass',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'adminpass')),
                 rio.Button(rio.Text('Num\nPasses',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'passes')),
                 rio.Button(rio.Text('Num\nFails',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'fails')),
                 ]
            )
        if 'admin' in user_sess.d['roles'] or 'tester' in user_sess.d['roles']:
            if not self.editmode:
               hdrRow.append( rio.Text("Submit\nNew",align_x=0.5,style=hdrstyle ))
        testGridContents=[hdrRow]

        # Now build up each test row
        sortedtests= sorted(tests,key=itemgetter(self.sortkey),reverse=self.orderDesc)
        maintests=[self.testRow(x) for x in sortedtests]
        margin=0.3
        testGridContents.extend(maintests)
        testGrid = rio.Grid(*testGridContents,row_spacing=1.1,column_spacing=0.3)
        return testGrid
        
    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        uim=self.session[data_models.UserInfoModel]
        return self.getGrid(self.testsForGroup,uim.d['book'],self.arch,self.rcname)

