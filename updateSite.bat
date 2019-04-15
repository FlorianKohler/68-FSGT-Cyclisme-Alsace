@echo off
git pull
py script.py
git add *
git commit -m "auto push"
git push
pause
