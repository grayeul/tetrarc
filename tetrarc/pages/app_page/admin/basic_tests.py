#@file: basic_tests.py
#@brief: Constructs page for editing the BasicTests tables

from __future__ import annotations

from dataclasses import KW_ONLY, field
from datetime import datetime
import typing as t
import functools

import rio

from .... import components as comps
from .... import data_models as dm
from .... import persistence

@rio.page(
    name="BasicTestsPage",
    url_segment="BasicTests/{active_testid:path}",
)
class BasicTestsPage(rio.Component):
    """
    This page holds the info to edit individual lists, and shows a ListView of lists in the group
    """
    groupName: str = "First Group"
    testgroups: list[dict] = []
    active_testid: int = 0
    curTest: dict|None = None
    t_link: str = ""
    confdel_is_open: bool = False

    def addNewTest(self):
        pers=self.session[persistence.Persistence]
        user_sess=self.session[dm.UserSessionModel]
        myuid=user_sess.d['user_id']
        print(f"Adding a new test and my user_id is: {myuid}")
        self.active_testid = -1
        self.curTest={
           "name":" ",
           "description":" ",
           "shortname":" ",
           "testorder":1,
           "link_to_procedure":" ",
           "notes":"",
           "blocking":False,
           "created":datetime.now(),
           "created_by":myuid,
           "last_modified":datetime.now(),
           "last_modified_by":myuid,
           "test_group_id": pers.db.getGroupId(self.groupName)
        }
        self.changes=self.curTest.copy()
        # Force a change here, to get it registered
        self.changes['testorder'] = 0

    def toggleBlocking(self,event:Event):
        print(f"Toggling blocking: event says: {event}")
        #self.curTest['blocking'] = event.is_on
        self.changes['blocking'] = event.is_on
        print(f"Changes now show: {self.changes}")

    def lostfocus(self,ctype:str,event:Event):
        print(f"Ctype: {ctype}, event: {event}")
        oldval=self.curTest.get(ctype,event.text)
        if oldval != event.text:
             print(f"See change from: {oldval} to {event.text}")
             self.changes[ctype]=event.text
        else:
            print(f"No changes for {ctype}")
    def cancelEdits(self):
        pers=self.session[persistence.Persistence]
        print("Cancelling in-progress edits")
        self.groupName = pers.db.getGroupById(self.curTest['test_group_id'])
        # When cancelling, do we want to revert changes, or just go back to 0 (refresh)?
        self.session.navigate_to("/app/admin/BasicTests/0")
        #self.force_refresh()
    def saveEdits(self):
        pers=self.session[persistence.Persistence]
        user_sess=self.session[dm.UserSessionModel]
        grpid=pers.db.getGroupId(self.groupName)
        #self.changes=self.curTest.copy()
        self.changes['last_modified'] = datetime.now()
        self.changes['last_modified_by'] = user_sess.d['user_id']
        self.changes['test_group_id'] = grpid
        print("Saving in-progress edits")
        print(f"Changes for id: {self.active_testid} are: {self.changes}")
        if self.active_testid < 0:
            pers.db.addNewBasicTest(self.changes)
        else:
            pers.db.updateBasicTest(self.active_testid,self.changes)
        self.session.navigate_to("/app/admin/BasicTests/0")
    def deleteTest(self):
        print(f"Preparing to delete test id: {self.active_testid}")
        pers=self.session[persistence.Persistence]
        self.confdel_is_open = False
        pers.db.deleteBasicTest(self.active_testid)
        self.session.navigate_to("/app/admin/BasicTests/0")

    def confirmDelPress(self):
        self.confdel_is_open = not self.confdel_is_open

    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        uim=self.session[dm.UserInfoModel]
        #if uim.d.get('curgroup',None):
        #    self.groupName=uim.d['curgroup']
        #self.changes={}
        if self.active_testid == "new":
            self.addNewTest()
        if self.active_testid == 0:
            carTest=None
        else:
            carTest=pers.db.getBasicTest(self.active_testid)
            print(f"Found BasicTest{self.active_testid}: {carTest}")
        TopRow=rio.Column(
            rio.Row(
                rio.Dropdown(label="TestGroup",
                   options={x['name']:x['name'] 
                         for x in self.testgroups} 
                            if len(self.testgroups)>0 
                            else {"Tmp":"Tmp"},
                   selected_value=self.bind().groupName),
                rio.Spacer()
            ))
        if self.curTest is None:
            TopRow=TopRow.add(
                rio.Row(
                rio.Spacer(),
                rio.Button("Add New Test",on_press=self.addNewTest),
                margin=0.5)
             )
        else:
            TopRow=TopRow.add(
                rio.Row(
                rio.Spacer(),
                rio.Button("Add New Test",on_press=self.addNewTest),
                margin=0.5)
            )
        if self.curTest is None:
           formgrid=rio.Text("")
        else:
            print(f"In build, my curTest is: {self.curTest}")
            #self.curTest['blocking']=False
            t_name=self.curTest['name']
            t_shortname=self.curTest['shortname']
            t_testorder=str(self.curTest['testorder'])
            t_blocking=self.curTest['blocking']
            t_description=self.curTest['description']
            t_link=self.curTest['link_to_procedure']
            if t_link is None:
                t_link=' '
            t_created=self.curTest['created'].strftime("%c")
            t_created_by=pers.db.getUserById(self.curTest['created_by']).get('username','unknown')
            t_last_modified=self.curTest['last_modified'].strftime("%c")
            t_last_modified_by=pers.db.getUserById(self.curTest['last_modified_by']).get('username','unknown')

            formgrid=rio.Grid(row_spacing=1,column_spacing=1)
            rx=0;cx=0
            formgrid.add(rio.TextInput(t_name,label="name",
                    on_lose_focus=functools.partial(self.lostfocus,'name')),
                    row=rx,column=cx)
            cx+=1
            formgrid.add(rio.MultiLineTextInput(t_description,label="description",
                    on_lose_focus=functools.partial(self.lostfocus,'description')),
                    row=rx,column=cx,height=3)
            cx=0
            rx+=1
            formgrid.add(rio.TextInput(t_shortname,label="shortname",
                    on_lose_focus=functools.partial(self.lostfocus,'shortname')),
                    row=rx,column=cx)
            rx+=1
            formgrid.add(rio.Row(
                           rio.Checkbox(is_on=t_blocking,on_change=self.toggleBlocking),
                           rio.Text("Release Blocking",margin=0.5),rio.Spacer(),
                           margin=0.5),
                    row=rx,column=cx)
            rx+=1
            formgrid.add(rio.TextInput(t_testorder,label="testorder",
                    on_lose_focus=functools.partial(self.lostfocus,'testorder')),
                     row=rx,column=cx)
            cx+=1
            formgrid.add(rio.TextInput(t_link,label="link",
                    on_lose_focus=functools.partial(self.lostfocus,'link_to_procedure')),
                     row=rx,column=cx)
            rx+=1
            cx=0
            formgrid.add(rio.TextInput(t_created_by,label="created_by",is_sensitive=False),
                 row=rx,column=cx)
            cx+=1
            formgrid.add(rio.TextInput(t_created,label="created",is_sensitive=False),
                 row=rx,column=cx)
            rx+=1
            cx=0
            formgrid.add(rio.TextInput(t_last_modified_by,label="last_modified_by",is_sensitive=False),
                  row=rx,column=cx)
            cx+=1
            formgrid.add(rio.TextInput(t_last_modified,label="last_modified",is_sensitive=False),
                  row=rx,column=cx)
        haveDelete=True if self.active_testid>0 else False
        confirmDel=rio.Popup(
              anchor=rio.Button("Delete Test",on_press=self.confirmDelPress,
                                 margin=1,is_sensitive=haveDelete),
              content=rio.Card(rio.Column(
                   rio.Text("Are you sure you want to delete?"),
                   rio.Row(rio.Button("Yes",on_press=self.deleteTest),
                           rio.Button("No",on_press=self.confirmDelPress)) ),
                   min_width=10,min_height=2),
               modal=True,
               is_open=self.confdel_is_open,
               position="top")
        buttonBar=rio.Row(
            confirmDel, 
            rio.Spacer(),
            rio.Button("Save",on_press=self.saveEdits,margin=1),
            rio.Button("Cancel",on_press=self.cancelEdits,margin=1),
            )
        return rio.Column(
            rio.Card(
               rio.Column(
                 rio.Text(f"Table Editing [{self.active_testid}]", style="heading1"),
                 TopRow,
                 formgrid,
                 buttonBar,
                 spacing=2,
                 min_width=60,
                 margin_bottom=1,
                 align_x=0.5,
                 align_y=0,
              ),
            ),
            rio.Separator(),
            rio.Spacer(min_height=1),
            rio.Card(comps.TestGroupList(
                arch="x86_64",
                editmode=True,
                testgroup=self.groupName,
                active_testid=self.bind().active_testid,
                testsForGroup=pers.db.getTestsForGroup(self.groupName)),
                color="neutral")
        )

    @rio.event.on_populate
    async def on_populate(self) -> None:
        """
        This will be used to populate our initial data
        """
        # MyUserData should be available from __init__.py
        #mud=self.session[dm.MyUserData]
        uim=self.session[dm.UserInfoModel]
        uim.d['book']=uim.d.get('book','dummy')
        pers=self.session[persistence.Persistence]
        self.testgroups = pers.db.getTestGroups()
        if uim.d.get('curgroup',None) is None:
            if len(self.testgroups) > 0:
                uim.d['curgroup']=self.testgroups[0]['name']
            else:
                uim.d['curgroup']='Empty'
        #sess.add(uim)
        print(f"Now in on_populate uim.d is: {uim.d}")
        print(f"and uim.d.get => {uim.d.get('curgroup',None)}")
        self.testgroupNames=[x['name'] for x in self.testgroups]
        print(f"My active_testid is: {self.active_testid}")
        print(f"GroupNames: {self.testgroupNames}")
        self.groupName=uim.d['curgroup']
        if self.active_testid == 0:
            self.curTest=None
        else:
            self.curTest=pers.db.getBasicTest(self.active_testid)
            grpid=self.curTest['test_group_id']
            for ix in range(0,len(self.testgroups)):
                if self.testgroups[ix]['id']==grpid:
                    mygrp=self.testgroups[ix]['name']
                    self.groupName=mygrp
                    break
            #self.t_link=self.curTest['link_to_procedure']
        #self.groupName=mygrp

