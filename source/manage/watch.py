import watcher

config = {
    "proc":watcher.PROCESS,
    "trigger":["python","./manage.py"],
    "mode":0,
    "path":"./",
    "files":[
        "manage.py"
    ],
}

watch = watcher.Watcher(**config)
watch.start()
watch.observe()