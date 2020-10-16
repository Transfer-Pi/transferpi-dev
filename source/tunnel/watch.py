[import watcher

config = {
    "proc":watcher.PROCESS,
    "trigger":["python3","./tunnel.py"],
    "mode":0,
    "path":"./",
    "files":[
        "tunnel.py"
    ],
}

watch = watcher.Watcher(**config)
watch.start()
watch.observe()