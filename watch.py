import watcher
import sys

*_,file = sys.argv

config = {
    "proc":watcher.PROCESS,
    "trigger":["python",file],
    "mode":0,
    "path":"./",
    "files":[
        file
    ],
}

watch = watcher.Watcher(**config)
watch.start()
watch.observe()