#!/bin/bash
cd /Users/adamdimitrov/Development/cruisedetective
/usr/bin/env python3 update_cruisedetective.py
git add ratings.json
git commit -m "Automated update of ratings.json"
git push origin main
