$env:Path = "C:\Users\Max\tools\git\cmd;C:\Program Files\GitHub CLI;" + $env:Path
gh repo create audio-brief-ai --public --source=. --push
