@echo off
py script.py
git pull
git add *
git commit -m "auto push"
git push
pause