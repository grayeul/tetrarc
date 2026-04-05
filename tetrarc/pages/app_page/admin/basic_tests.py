#@file: basic_tests.py
#@brief: Constructs page for editing the BasicTests tables

from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

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
    curTest: dict = {}
    t_link: str = ""

    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        if self.active_testid == 0:
            curTest=None
        else:
            curTest=pers.db.getBasicTest(self.active_testid)
            print(f"Found BasicTest{self.active_testid}: {curTest}")
        TopRow=rio.Column(
            rio.Row(
                rio.Dropdown(label="TestGroup",
                   #options={"First Group":0,"Second Group":1,"Third Group":2},
                   options={x['name']:x['name'] 
                         for x in self.testgroups} 
                            if len(self.testgroups)>0 
                            else {"Tmp":"Tmp"},
                   #selected_value=mygrp),
                   selected_value=self.bind().groupName),
                rio.Spacer()
            ))
        if curTest is None:
            TopRow=TopRow.add(
                rio.Row(
                rio.Spacer(),
                rio.Button("Add New Test"),
                margin=0.5)
             )
        else:
            TopRow=TopRow.add(
                rio.Row(
                rio.Text("Test: "),
                rio.Text(curTest['name']),
                rio.Spacer(),
                rio.Button("Add New Test"),
                margin=0.5)
            )
        if curTest is None:
           formgrid=rio.Text("")
        else:
            t_name=curTest['name']
            t_shortname=curTest['shortname']
            t_testorder=str(curTest['testorder'])
            t_description=curTest['description']
            #t_link=curTest['link_to_procedure']
            t_created=curTest['created'].strftime("%c")
            t_created_by=pers.db.getUserById(curTest['created_by']).get('username','unknown')
            t_last_modified=curTest['last_modified'].strftime("%c")
            t_last_modified_by=pers.db.getUserById(curTest['last_modified_by']).get('username','unknown')

            formgrid=rio.Grid(row_spacing=1,column_spacing=1)
            rx=0;cx=0
            formgrid.add(rio.TextInput(t_name,label="name"),row=rx,column=cx)
            cx+=1
            formgrid.add(rio.MultiLineTextInput(t_description,label="description"),
                row=rx,column=cx,height=2)
            cx=0
            rx+=1
            formgrid.add(rio.TextInput(t_shortname,label="shortname"),row=rx,column=cx)
            rx+=1
            formgrid.add(rio.TextInput(t_testorder,label="testorder"),row=rx,column=cx)
            cx+=1
            formgrid.add(rio.TextInput(self.bind().t_link,label="link"),row=rx,column=cx)
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
        buttonBar=rio.Row(
            rio.Spacer(),
            rio.Button("Save",margin=1),
            rio.Button("Cancel",margin=1),
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
            comps.TestGroupList(
                arch="x86_64",
                editmode=True,
                testgroup=self.groupName,
                active_testid=self.bind().active_testid,
                testsForGroup=pers.db.getTestsForGroup(self.groupName))
        )

    @rio.event.on_populate
    async def on_populate(self) -> None:
        """
        This will be used to populate our initial data
        """
        # MyUserData should be available from __init__.py
        #mud=self.session[dm.MyUserData]
        #uim=self.session[dm.UserInfoModel]
        pers=self.session[persistence.Persistence]
        self.testgroups = pers.db.getTestGroups()
        self.testgroupNames=[x['name'] for x in self.testgroups]
        print(f"My active_testid is: {self.active_testid}")
        print(f"GroupNames: {self.testgroupNames}")
        mygrp="Empty"
        if len(self.testgroups) > 0:
            mygrp=self.testgroups[0]['name']
        if self.active_testid == 0:
            self.curTest=None
        else:
            self.curTest=pers.db.getBasicTest(self.active_testid)
            grpid=self.curTest['test_group_id']
            for ix in range(0,len(self.testgroups)):
                if self.testgroups[ix]['id']==grpid:
                    mygrp=self.testgroups[ix]['name']
                    break
            self.t_link=self.curTest['link_to_procedure']
        self.groupName=mygrp

