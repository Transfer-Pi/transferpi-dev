# build script for transferpi

build (){
    pyinstaller $1.py $2
    cp dist/$1/* dist/bin/  -r
    rm -rf dist/$1
    rm $1.spec
}


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
    if [[ $# == 1 ]]
    then 
        rm -rf dist/bin/*
        build "manage" "--icon=dist/data/logo.ico"
        build "add"
        build "get"
        build "list"
        build "remove"
        build "fileserver"
        build "tunnel"
        
        rm -rf build
    else
        build $2
        rm -rf build
    fi
elif [[ $1 == "test" ]]
then
    echo "Testing CLI Tools"
    echo "* Running add"
    ./dist/bin/add
    echo "* Running get"
    ./dist/bin/get
    echo "* Running list"
    ./dist/bin/list
    echo "* Running remove"
    ./dist/bin/remove
    echo "* Running manage"
    ./dist/bin/manage

    echo "Testing CLI Tools With Basic Arguments"
    echo "* Running add"
    ./dist/bin/add build.sh
    echo "* Running get"
    ./dist/bin/get WheTes
    echo "* Running list"
    ./dist/bin/list 
    echo "* Running remove"
    ./dist/bin/remove A

else
    echo "Please Provide Build Options"
fi


