
install_deps:
	sudo apt-get update
	sudo apt-get -y install vlan libssl-dev mono-devel libncurses5-dev python-matplotlib python-numpy
	sudo apt-get -y install build-essential autoconf automake libxmu-dev xorg-dev g++ xgraph
	cd ns-2 && tar -xvf ns-allinone-2.34.tar.gz
	cd ns-2/ns-allinone-2.34/ && patch -p1 < ../qjump-ns2/ns-allinone-2.34.ubuntu.patch
	cd ns-2/ns-allinone-2.34/ && ./install
	cd ns-2/ns-allinone-2.34/ns-2.34/ && patch -p1 < ../../qjump-ns2/pfabric.patch && make clean && make
	./bin/make_settings.py

clean:
	rm ${TCL_DIR}/out/*

