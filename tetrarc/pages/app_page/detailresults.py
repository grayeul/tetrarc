# @file: detailresults.py
# @brief: This page will display information for a given TestBook
# It uses Dynamic (Parametric) Routes
from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t
import functools
from operator import itemgetter

import rio

from ... import components as comps
from ... import data_models,persistence
# Note - this shows up under URL:  app/results/book_name/testid
@rio.page(
    name="DetailResultsPage",
    url_segment="results/{book_name:path}/{testid:path}",
)
class DetailResultsPage(rio.Component):
    """
    A page to display the Detailed results for a given test
    """
    book_name: str
    testid: int
    arch: str = "x86_64"
    orderDesc: bool =True
    sortkey:str ='submitted'

    def changeArch(self,event):
        uim=self.session[data_models.UserInfoModel]
        print(f"Changing arch to => {event}")
        uim.d['arch']=event.value
    def changeSort(self,sortkey:str):
        if self.sortkey == sortkey:
            self.orderDesc = not self.orderDesc
        else:
            self.orderDesc = False
            self.sortkey=sortkey

    @rio.event.on_populate
    def on_populate(self) -> None:
        # Update based on session info
        uim=self.session[data_models.UserInfoModel]
        self.arch=uim.d['arch']
        
    def resultRow(self,x:dict) -> list[list[rio.Component]]:
        "Returns a list of a list of components, to be added to a Grid"
        pers=self.session[persistence.Persistence]
        fill=rio.Color.from_gray(0.25, 1.0)
        margin=0.3
        pfcolor="success"
        if x['status'] == 'fail':
           pfcolor="danger"
        elif x['status']== 'partial':
            pfcolor="warning"
        if x['adminpass']:
            pfcolor='success'
            x['status']='*ADMIN_PASS*'
        row1=[rio.Card(content=rio.Text(x['submitted'].strftime('%c'),margin=margin),
                         corner_radius=0,color="neutral"),
                     rio.Card(content=rio.Text(pers.db.getUserById(x['user_id'])['name'],margin=margin),
                         corner_radius=0,color="neutral"),
                     rio.Card(content=rio.Text(x['status'],margin=margin),
                         corner_radius=0,color=pfcolor),
                     rio.Card(content=rio.Text(x['deploy_type'],margin=margin),
                         corner_radius=0,color="neutral"),
                     ]
        #row2=[rio.Rectangle(content=rio.Text('Comments:'),fill=fill),rio.Text("These are comments")]
        return row1
    def build(self) -> rio.Component:
        pers=self.session[persistence.Persistence]
        uim=self.session[data_models.UserInfoModel]
        uim.d['book']=self.book_name
        self.log=pers.log
        curtest=pers.db.getBasicTestById(self.testid)
        testname=curtest['name']
        results=pers.db.getTestResults(self.testid,self.book_name,self.arch)
        sortedresults = sorted(results,key=itemgetter(self.sortkey),reverse=self.orderDesc)
        # Add Header:
        hdrstyle="heading2"
        hdrRow=[
                 rio.Button(rio.Text('Timestamp',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'submitted')),
                 rio.Button(rio.Text('User',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'user_id')),
                 rio.Button(rio.Text('Pass/Fail',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'status')),
                 rio.Button(rio.Text('DeployType',style=hdrstyle),style='plain-text',
                    on_press=functools.partial(self.changeSort,'deploy_type')),
                 ]
        
        resultGridContents=[hdrRow]
        baseresults=[self.resultRow(x) for x in sortedresults]
        margin=0.3
        comments=[rio.Card(content=rio.Markdown(f"### Comments:\n{x['comments']}",
                                 margin_left=2.0,wrap=True),
                           margin=0,corner_radius=0,color="neutral")
                           for x in sortedresults]
        # Now interleave the two lists:
        interleaved = [ val for pair in zip(baseresults,comments) for val in pair ]
        resultGridContents.extend(interleaved)
        resultGrid=rio.Grid(*resultGridContents,row_spacing=0.1,column_spacing=0.3)
        #resultGrid.add(rio.Text("NewResult with a really long set of text, not sure where it will go"),row=1,column=0,width=3)
        return rio.Column(
            rio.Link(
                rio.Button(rio.Text(self.book_name,style='heading1'),align_x=0,style='plain-text'),
                f"/app/book/{self.book_name}"),
            rio.Text(f"Detailed Test Results for test {testname} ({self.testid})", style="heading3"),
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
            resultGrid, 
            # Now params for the column:
            spacing=0,
            min_width=60,
            margin_bottom=4,
            align_x=0.5,
            align_y=0,
        )
