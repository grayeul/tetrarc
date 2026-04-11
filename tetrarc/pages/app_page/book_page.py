# @file: book_page.py
# @brief: This page will display information for a given TestBook
# It uses Dynamic (Parametric) Routes
from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from ... import components as comps
from ... import data_models,persistence
# Note - this shows up under URL:  app/book/book_name
@rio.page(
    name="TestBookPage",
    url_segment="book/{book_name:path}",
)
class BookPage(rio.Component):
    """
    A page to display the key information for a  given TestBook
    """
    book_name: str
    arch: str = "x86_64"

    def changeArch(self,event):
        uim=self.session[data_models.UserInfoModel]
        print(f"Changing arch to => {event}")
        uim.d['arch']=event.value

    @rio.event.on_populate
    def on_populate(self) -> None:
        # Update based on session info
        uim=self.session[data_models.UserInfoModel]
        self.arch=uim.d['arch']
        
    def getHeaderCnt(self,testgroup:str) -> str:
        """
        Takes the name of a testgroup, and returns a string to use in the header.
        It will look like: 'Name - pass/total'
        """
        pers=self.session[persistence.Persistence]
        groupid=pers.db.getGroupId(testgroup)
        testsForGroup=pers.db.getTestsForGroup(testgroup)
        passcnt=pers.db.getTestGroupAdminPassCnt(groupid,self.book_name,self.arch)
        rval=f"{testgroup}  - {passcnt}/{len(testsForGroup)}"
        return rval

    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        uim=self.session[data_models.UserInfoModel]
        uim.d['book']=self.book_name
        self.log=pers.log
        groups=pers.db.getTestGroups()
        colOfCards=[
              rio.Card( content=rio.Revealer(
                                   header=self.getHeaderCnt(x['name']),
                                   content=rio.Column(
                                      #rio.Text(x['name'],style="heading2"),
                                      rio.Text(x['description'],style='text'),
                                      rio.Separator(),
                                      rio.Card(rio.Column(
                                          comps.TestGroupList(
                                              arch=self.arch,
                                              testgroup=x['name'],
                                              testsForGroup=pers.db.getTestsForGroup(x['name'])
                                              ),
                                          # Next line are args for Column
                                          margin=1,spacing=0),
                                    color="neutral"),
                                   margin=1,spacing=0),
                                   header_style='heading2',
                                   is_open=True
                                 ),
                       # Next line is margin/spacing between each card (group)
                       margin=0.5 )
              for x in groups ]

        return rio.Column(
            rio.Text(self.book_name, style="heading1"),
            rio.Text("Basic Tests to be performed", style="heading3"),
            rio.Row(
                rio.Dropdown(label="arch",
                         options={"x86_64":"x86_64",
                                  "aarch64":"aarch64",
                                  "ppc64le":"ppc64le",
                                  "s390x":"s390x"},
                          selected_value=self.bind().arch,
                          on_change=self.changeArch),
                   rio.Spacer()
                   ),
            rio.Column(*colOfCards),
            # Now params for the column:
            spacing=0,
            min_width=60,
            margin_bottom=4,
            align_x=0.5,
            align_y=0,
        )

