## Local Tunnel

### Config

```json
{
    "subdomain": string, // username
    "account_keys": {
        "private": sha256_string, // A SHA256 hash that can be used for handling tunnel request
        "public": sha256_string // A SHA256 hash that can be used for private sharing
    }, 
    "allowed_hosts": list, // A list of allowed hosts for private sharing
    "server_config": 
    {
        "remote": {
            "host": string, // URL for remote tunnel server
            "port": int // Port for remote tunnel server
        }, 
        "local": {
            "host": string, // Host where the local server will run
            "port": int,  // Port where local server will run
            "n_pools": int, // Maximum number of threads allowed for server
            "chunk_size": int // Chunk size to transfer per second from fileserver
        }, 
        "web": {
            "host": string // URL for transferpi's main server
        }
    }
}
```
