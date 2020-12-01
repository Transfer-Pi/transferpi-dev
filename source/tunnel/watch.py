import watcher

config = {
    "proc":watcher.PROCESS,
    "trigger":["python","./serve.py","debug"],
    "mode":1,
    "path":"./",
    "files":[
        
    ],
}

watch = watcher.Watcher(**config)
watch.start()
watch.observe()