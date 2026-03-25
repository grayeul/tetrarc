#@file: addresult_page.py
#@brief: Enter results from running a test

from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from ... import components as comps
from ... import data_models
from ... import persistence

@rio.page(
    name="NewResultsPage",
    url_segment="newresults-page/{arch:path}/{testid:path}",
)
class NewResultsPage(rio.Component):
    """
    A sample page, containing recent news articles about the company.
    """
    testid: int
    arch:   str
    #deploy_type: str

    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        self.log=pers.log
        self.deploy_type="Bare Metal"
        basictest=pers.db.getBasicTestById(self.testid)
        user_sess = self.session[data_models.UserSessionModel]
        userid=user_sess.d["user_id"]
        self.log.info(f"The user_sess dict is: {user_sess.d}")
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
                                  selected_value=self.arch),row=rix,column=colix)
        colix+=1
        formgrid.add(rio.Dropdown(label="Deploy Type",
                                 options={"Bare Metal":"Bare Metal",
                                      "KVM":"KVM",
                                      "Container":"Container",
                                      "VM":"VM",
                                      "CloudVM":"CloudVM"},
                                  selected_value=self.deploy_type),row=rix,column=colix)
        rix += 1
        colix=0
        formgrid.add(rio.Row(rio.Text("Outcome: ",style="heading3"),rio.SwitcherBar(
            rio.SwitcherBarItem("Pass"),
            rio.SwitcherBarItem("Fail"),
            rio.SwitcherBarItem("Partial"),
            selected_value="Fail",spacing=0.5,key="outcome")),
            row=rix,column=colix,
            )
        rix += 1
        formgrid.add( rio.MultiLineTextInput("",
                      label='comments',key="comments"),
                      row=rix,column=colix,width=2)
        rix += 1
        formgrid.add(rio.Button("Submit Result",align_x=0),
                      row=rix,column=colix)

        return rio.Column(
            rio.Text(f"Add New Result - for test: {basictest['name']}", style="heading1"),
            rio.Text("Test Description",style="heading3"),
            rio.Text(f"    {basictest['description']}",style="text"),
            rio.Separator(),
            rio.Text(f"Submitted by: {username}",style="dim"),
            formgrid,
            spacing=2,
            min_width=60,
            margin_bottom=4,
            align_x=0.5,
            align_y=0,
        )

