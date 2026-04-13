#!/usr/bin/env python3
# @file: ttdb.py
# @brief: Utility to interact with the tetrarc DB
import sys
import os
import re
import json
import logging
from tetrarc.tetrarcdb import tetrarcDB
from tetrarc import __version__
from tetrarc import __build_date__

class App:
    def __init__(self):
        self.dbfile=None
        logging.basicConfig(level=logging.DEBUG,
           format='%(message)s',
           handlers=[logging.StreamHandler(sys.stdout)])
        self.log=logging.getLogger('tetrarc')
        basedir=os.path.realpath(f"{os.path.dirname(sys.argv[0])}/../..")
        print(f"I'm looking at directory: {basedir}")
        self.cfgfile=f"{basedir}/tetrarc.json"
        self.outfile=None
        self.cfg={}
    def loadCfg(self,cfgfile) -> None:
        with open(cfgfile,'r') as fp: 
           cfg=json.load(fp)
        return cfg
    def parse_args(self,args=None) -> None:
        from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
        parser = ArgumentParser( 
             prog='tdb',
             description=f"v{__version__} - A utility to interact with sqlite3 DB for tetrarc - {__build_date__}",
             formatter_class=ArgumentDefaultsHelpFormatter
             )
        parser.add_argument('-c','--cfgfile', type=str,help='Specify cfgfile',default=self.cfgfile)
        #parser.add_argument('-o','--outfile', type=str,help='Specify output file',default=self.outfile)
        parser.add_argument('-load','--load', type=str,help='Specify csv file to load',default=None)
        parser.add_argument('-dbfile',dest='dbfile', type=str,default='./tetrarc.db',help='specify a different DB file')
        parser.add_argument('-testbooks', action='store_true',help='Dump info on TestBooks')
        parser.add_argument('-testgroups', action='store_true',help='Dump info on TestGroups')
        parser.add_argument('-basictests', action='store_true',help='Dump info on BasicTests')
        parser.add_argument('-dummy1', action='store_true',help='Test routine')
        parser.add_argument('-dummy2', type=str,help='Test routine')

        self.args=parser.parse_args(args)
        self.cfgfile=self.args.cfgfile
        self.cfg=self.loadCfg(self.cfgfile)
        if self.args.dbfile:
            self.dbfile=self.args.dbfile
            self.cfg["dbfile"]=self.dbfile

 
    def getFileFields(self,fname:str,ftype:str) -> list:
        if not os.path.exists(fname):
            self.log.error(f"Unable to find file {fname}")
            sys.exit()
        with open(fname,'r') as fp:
            buflines=fp.readlines()
        if len(buflines)==0 or not buflines[0].startswith(f'#|{ftype}'):
            self.log.error(f"Trying to process wrong type of file, {fname} is not {ftype} file")
            sys.exit()
        rfields=[]
        for ln in buflines:
            if ln.startswith('#') or len(ln.strip())==0:
                continue
            # Use more involved split cmd
            fields = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', ln.strip())
            # But we don't really want double-quotes to be part of the field...
            if ln.find('"')>=0:
                for ix in range(0,len(fields)):
                    if fields[ix][0]=='"' and fields[ix][-1]=='"':
                        fields[ix]=fields[ix][1:-1]
            #fields=ln.strip().split(',')
            rfields.append(fields)
        return rfields
    def loadGenericFile(self,fname:str) -> None:
        if not os.path.exists(fname):
            self.log.error(f"Unable to find file {fname}")
            sys.exit()
        cnt=0
        cnt=self.loadFromCSV(fname)
        if cnt < 0:
            self.log.error(f"Unable to determine valid file type for {fname} [{hdr[2:]}- nothing to load")
            sys.exit()
        self.log.info(f"It appears {cnt} items were added")

    def getExpFieldCnt(self,ftype:str) -> int:
        ftype=ftype.lower()   # Ensure lowercase version of name
        fmap={'users':3,
            'roles':2,
            'test_groups':2,   # name, description
            'basic_tests':3,   # name, shortname,description
            'test_types':3,    # basic_tests_id,arch,environ
            'test_books':5,     # name,start_date,tgt_end_date,status,description
            }
        return fmap[ftype]
    def loadFromCSV(self,fname:str) -> int:
        with open(fname,'r') as fp:
            hdr=fp.readline()
        ftype=hdr[2:].strip()
        fieldlist=self.getFileFields(fname,ftype)
        expFieldCnt=self.getExpFieldCnt(ftype)
        if len(fieldlist[0]) < expFieldCnt:
            self.log.error(f"Expected {expFieldCnt} fields, but found {len(fieldlist[0])}")
            sys.exit()
        cnt=self.db.ingestTabData(fieldlist,ftype)
        return cnt
    def main(self,args=None):
        cfg={}
        self.parse_args(args)
        self.db=tetrarcDB(self.dbfile,cfg=self.cfg)
        if self.args.load:
           self.loadGenericFile(self.args.load)
        if self.args.testbooks:
            rval=self.db.getTestBooks()
            print(f"Got these TestBooks: {rval}")
        if self.args.testgroups:
            rval=self.db.getTestGroups()
            print(f"Got these TestGroups: {rval}")
        if self.args.basictests:
            rval=self.db.getBasicTests()
            print(f"Got these TestGroups: {rval}")
        if self.args.dummy1:
            rval=self.db.getTestGroupAdminPassCnt(1,'RockyLinux-10.2','x86_64')
            print(f"Got {rval} unique passes in testgroup 1")
        if self.args.dummy2:
            book=self.args.dummy2
            print(f"RCs for book: {book} = {self.db.getRCSforBook(book)}")

if __name__ == '__main__':
    app=App()
    app.main()

