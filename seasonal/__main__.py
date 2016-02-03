# -*- coding: utf-8 -*-
"""__main__.py

invoke seasonal_cmd when someone types `python -m seasonal`

"""
from .application import seasonal_cmd

exit(seasonal_cmd() or 0)
