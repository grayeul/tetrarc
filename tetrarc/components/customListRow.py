#@file: customListRow.py
#@brief: Creates a CustomListItem based on test info from basic_tests
from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t
import functools

import rio

from .. import components as comps
from .. import data_models

class CustomListRow(rio.Component):
    """
    Provides a CustomListItem that holds info about a given test
    """

    arch: str
    testdict:dict
    editmode:bool = False
    hdr:bool = False

    def gotoAddResult(self,testid) -> None:
        self.session.navigate_to(f"/app/newresults-page/{self.arch}/{testid}")
    def gotoEditResult(self,testid) -> None:
        self.session.navigate_to(f"/app/admin/BasicTests/{testid}")
    def build(self) -> rio.Component:
        name=self.testdict["name"]
        try:
            testid=self.testdict["id"]
        except:
            testid=0
            print(f"Building a row, with testdict={self.testdict} edit={self.editmode}")
        description=self.testdict["description"]
        user_sess = self.session[data_models.UserSessionModel]
        passes=self.testdict.get("passes",0)
        fails=self.testdict.get("fails",0)
        #return rio.SimpleListItem(text=name,key=name)
        if self.hdr:
           style='heading3'
        else:
            style='text'
        addbtn=rio.Button("Submit",
                          on_press=functools.partial(self.gotoAddResult,testid))
        editbtn=rio.Button("Edit",
                          on_press=functools.partial(self.gotoEditResult,testid))
        baserow= rio.Row(rio.Text(name,style=style),
                      rio.Text(description,style=style)
                      )
        if self.editmode:
             baserow=baserow.add(rio.Text('Edit',style=style) if self.hdr else editbtn)
             baserow.proportions=[1,3,0.5]
        elif 'admin' in user_sess.d['roles'] or 'tester' in user_sess.d['roles']:
             baserow=baserow.add(rio.Text(str(passes),style=style))
             baserow=baserow.add(rio.Text(str(fails),style=style))
             baserow=baserow.add(rio.Text('Submit New',style=style) if self.hdr else addbtn)
             baserow.proportions=[1,3,0.5,0.5,0.5]
        else:
             baserow=baserow.add(rio.Text(str(passes),style=style))
             baserow=baserow.add(rio.Text(str(fails),style=style))
             baserow.proportions=[1,3,1,1]
             
        return rio.CustomListItem( baserow )
        

