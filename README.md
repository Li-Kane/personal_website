# kdWidgets
This is a project for creating server-side widgets and sending their data over websockets to connected clients. Using custom message protocols and callbacks, developers can create a dynamic GUI. More details can be found in this doc: [link](https://karanadynamics.sharepoint.com/:w:/s/RD/EacxFTOlxNNDvYLDWKgXab4BZfUlFfp8f0KgmUUUb4ehUg?e=qrHHXv)

## Setup
For the library itself, there are 3 dependencies:
1. [uWebSockets](https://github.com/uNetworking/uWebSockets)
2. [ZLIB](https://github.com/madler/zlib)
3. [nlohmann_json](https://github.com/nlohmann/json)

ZLIB and nlohmann_JSON are already installed, therefore just uWebSockets needs to be installed. These are the general steps I followed to clone the repository, install it, and add the relevant files to CMAKE paths.
1. Clone the repo at https://github.com/uNetworking/uWebSockets.git (make sure to include --recurse-submodules flag to include uSockets dependency)
2. Cd into uWebSockets and run `make`
3. Cd into uSockets and run `make`
4. Move uWebSockets/src into include path (uWebSockets is header-only, and all the files are in /src)
5. Move uWebsockets/uSockets/src/libuSockets.h to include path
6. Move uWebSockets/uSockets/uSockets.a to the search path
7. Update src/CMakeLists.txt to find the uWebSockets headers from steps 4 and 5, as well as find the uSockets.a library.

Once this is done, the project can be compiled and run from root:
```
mkdir build
cd build
cmake ..
make
```

## Running
From inside build, examples can be run like so:
```
./examples/chatroom
./examples/iframe
./examples/simulation
./examples/widgetList
```

## Bindings
Bindings are currently incomplete. But as a proof of concept, they are located in /bindings. This is how to do it if it was working (from root):
```
# create a venv
python -m venv .venv
source .venv/bin/activate
pip install . -C cmake.define.BUILD_BINDINGS=true

# run a minimal example
cd python
python ./test.py
```