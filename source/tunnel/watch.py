import watcher

config = {
    "proc":watcher.PROCESS,
    "trigger":["python","./tunnel.py","debug"],
    "mode":1,
    "path":"./",
    "files":[
        "main.py"
    ],
}

watch = watcher.Watcher(**config)
watch.start()
watch.observe()