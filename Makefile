install_basics:
	sudo apt-get update
	sudo apt-get install -y python-virtualenv libfreetype6-dev python-dev libfuzzy-dev
	virtualenv . --distribute
	sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
	echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
	sudo apt-get update
	sudo apt-get install -y mongodb-org

install_python_modules:
	pip install androguard
	pip install -r requirements.txt

clean:
	find -name "*.pyc" -exec rm {} \;
	rm -rf bin/ lib/ local/ include/
