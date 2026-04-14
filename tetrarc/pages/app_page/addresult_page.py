#@file: addresult_page.py
#@brief: Enter results from running a test

from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t
import logging

import rio

from ... import components as comps
from ... import data_models
from ... import persistence

@rio.page(
    name="AddResultsPage",
    url_segment="addresults-page/{book:path}/{rcname:path}/{testid:path}",
)
class AddResultsPage(rio.Component):
    """
    A page used to add new test results to the DB
    """
    testid: int
    book:   str
    arch:   str='x86_64'   # I think this will be default, until there is a session?
    rcname: str='base'
    deploy_type: str='Bare Metal'
    passfail:    str='Fail'
    comments:    str=''
    adminpass:   bool=False

    def onSubmitResult(self):
        uim=self.session[data_models.UserInfoModel]
        pers=self.session[persistence.Persistence]

        print(f"Submitting new {self.book} result for test: {self.testid}")
        #print(f"For arch: {self.arch} on {self.deploy_type}")
        #print(f"Pass/Fail: {self.passfail}")
        #print(f"Comments: {self.comments}")
        user_sess=self.session[data_models.UserSessionModel]
        uid=user_sess.d['user_id']
        username=user_sess.d['user']['username']
        result={"basic_tests_id":self.testid,
                "book":self.book,
                "user_id":uid,
                "arch":self.arch,
                "rcname":self.rcname,
                "deploy_type":self.deploy_type,
                "status":self.passfail.lower(),
                "adminpass":self.adminpass,
                "comments":self.comments}

        self.log.info(f"UserId: {uid}({username}) now submitting result: {result}")
        pers.db.addTestResult(result)

        #print(f"Now navigating to: /app/book/{self.book}/{self.rcname}")
        self.session.navigate_to(f"/app/book/{self.book}/{self.rcname}")
    def onCancel(self):
        self.session.navigate_to(f"/app/book/{self.book}/{self.rcname}")
    def lostfocus(self,event):
        #print(f"LostFocus: {event}")
        self.comments=event.text
    def changeDeployType(self,event):
        uim=self.session[data_models.UserInfoModel]
        #print(f"Changing arch to => {event}")
        uim.d['deploy_type']=event.value
        self.deploy_type=uim.d['deploy_type']
    def changeArch(self,event):
        uim=self.session[data_models.UserInfoModel]
        #print(f"Changing arch to => {event}")
        uim.d['arch']=event.value
        self.arch=uim.d['arch']

    @rio.event.on_populate
    def on_populate(self) -> None:
        # Setup defaults based on session info
        uim=self.session[data_models.UserInfoModel]
        self.arch=uim.d['arch']
        uim.d['book']=self.book   # This should be set by the page, track it also in session
        self.deploy_type=uim.d['deploy_type']
        
    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        self.log=pers.log
        basictest=pers.db.getBasicTestById(self.testid)
        user_sess = self.session[data_models.UserSessionModel]
        userid=user_sess.d["user_id"]
        #self.log.info(f"The user_sess dict is: {user_sess.d}")
        user=pers.db.getUserById(userid)
        username=user['username']
        # Create a Grid to hold all of the formdata
        formgrid=rio.Grid(row_spacing=1,column_spacing=1)
        rix=0;colix=0
        formgrid.add(rio.Dropdown(label="arch",
                                 options={"x86_64":"x86_64",
                                      "aarch64":"aarch64",
                                      "ppc64le":"ppc64le",
                                      "s390x":"s390x"},
                                  selected_value=self.bind().arch,
                                  on_change=self.changeArch,
                                  align_x=0),
                     row=rix,column=colix)
        colix+=1
        formgrid.add(rio.Dropdown(label="Deploy Type",
                                 options={"Bare Metal":"Bare Metal",
                                      "KVM":"KVM",
                                      "Container":"Container",
                                      "VM":"VM",
                                      "CloudVM":"CloudVM"},
                                  selected_value=self.bind().deploy_type,
                                  on_change=self.changeDeployType),
                     row=rix,column=colix)
        rix += 1
        colix=0
        formgrid.add(rio.Row(rio.Text("Outcome: ",style="heading3"),rio.SwitcherBar(
            rio.SwitcherBarItem("Pass"),
            rio.SwitcherBarItem("Fail"),
            rio.SwitcherBarItem("Partial"),
            selected_value=self.bind().passfail,spacing=0.5,key="outcome",align_x=0)),
            row=rix,column=colix,
            )
        rix += 1
        if 'lead' in user_sess.d['roles']:
            formgrid.add( rio.Row(
                             rio.Text("AdminPass",align_x=0),
                             rio.Checkbox(is_on=self.bind().adminpass,align_x=0),
                             rio.Spacer(),
                             ),
                         row=rix,column=0)
            rix += 1
        formgrid.add( rio.MultiLineTextInput("",
                      label='comments',key="comments",
                      on_lose_focus=self.lostfocus),
                      row=rix,column=colix,width=2)
        rix += 1
        formgrid.add(rio.Row(
                         rio.Button("Submit Result",on_press=self.onSubmitResult,align_x=0),
                         rio.Spacer(),
                         rio.Button("Cancel",on_press=self.onCancel,align_x=0),
                         grow_x=True
                         ),
                      row=rix,column=colix)
        if self.rcname == 'base':
            rcinfo=''
        else:
            rcinfo=f' - {self.rcname}'
        return rio.Column(
            rio.Text(f"Add New Result - for {self.book}{rcinfo}",style='heading1'),
            rio.Text(f"   test: {basictest['name']}", style="heading2",overflow="wrap"),
            rio.Text("Test Description",style="heading3"),
            rio.Text(f"    {basictest['description']}" ,style="text",overflow="wrap"),
            rio.Separator(),
            rio.Text(f"Submitted by: {username}",style="dim"),
            formgrid,
            spacing=2,
            min_width=60,
            margin_bottom=4,
            align_x=0.5,
            align_y=0,
        )

