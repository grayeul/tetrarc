#!/usr/bin/env python3
#
import tetrarc
from fastapi.staticfiles import StaticFiles

fastapp=tetrarc.app.as_fastapi()
# fastapp.mount("/docs", StaticFiles(directory="site",html=True),name="staticdocs") 


