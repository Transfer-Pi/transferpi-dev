import watcher

file = './tunnel.py'

config = {
    "proc":watcher.PROCESS,
    "trigger":["python",file,"debug"],
    "mode":1,
    "path":"./",
    "files":[
        
    ],
}

watch = watcher.Watcher(**config)
watch.start()
watch.observe()