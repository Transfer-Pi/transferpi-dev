if [[ $1 == "html" ]]
then 
    cd source/fileserver/html
    yarn build
    cd ../../..
    rm -rf dist/data/templates
    cp source/fileserver/html/build dist/data/templates -r
    rm -rf source/fileserver/html/build
elif [[ $1 == "dist" ]]
then 
    pyinstaller source/add/add.py
    pyinstaller source/get/get.py
    pyinstaller source/list/list.py
    pyinstaller source/remove/remove.py
    pyinstaller source/fileserver/fileserver.py
    pyinstaller source/tunnel/tunnel.py
    
    cp dist/add/* dist/bin/  -r
    cp dist/get/* dist/bin/ -r
    cp dist/list/* dist/bin/ -r
    cp dist/remove/* dist/bin/ -r
    cp dist/fileserver/* dist/bin/ -r
    cp dist/tunnel/* dist/bin/ -r

    rm -rf dist/add
    rm -rf dist/get
    rm -rf dist/list
    rm -rf dist/remove
    rm -rf dist/fileserver
    rm -rf dist/tunnel

    rm -rf build
    rm *.spec

else
    echo "Please Provide Build Options"
fi