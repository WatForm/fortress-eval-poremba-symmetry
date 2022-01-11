mkdir -p libs

cd ../fortress/
sbt dist
cd -

cp ../fortress/debug/target/universal/fortressdebug-*.zip libs/
cd libs
unzip fortressdebug-*.zip

cd -

