import watcher
import sys

*_,file = sys.argv

config = {
    "proc":watcher.PROCESS,
    "trigger":["python",file],
    "mode":1,
    "path":"./",
    "files":[
        
    ],
}

watch = watcher.Watcher(**config)
watch.start()
watch.observe()