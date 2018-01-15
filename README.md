## Google Play APKs Analysis

[![Build Status](https://travis-ci.org/APK-insight/gplay-apk-analysis.svg?branch=master)](https://travis-ci.org/APK-insight/gplay-apk-analysis) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

### Setup

* Clone from repo

    ```bash
    $ git clone https://github.com/18z/gplay_apk_analysis.git
    ```

* Create and install required packages

    ```bash
    $ cd gplay-apk-analysis
    $ make install_basics
    ```

* Source virtualenv and install python modules

    ```bash
    $ source bin/activate
    $ make install_python_modules
    ```

* Create your dbpath

    ```bash
    $ mkdir -p ~/data/db
    ```

* Start mongod with

    ```bash
    $ mongod --dbpath ~/data/db
    ```

* Fill in infos

    ```bash
    # https://play.google.com/store/apps/details?id=com.evozi.deviceid&hl=zh_TW
    # Find Google Service Framework ID for android id in config.py
    cp core/config.py.example core/config.py; vim core/config.py
    cp core/db/db.conf.example core/db/db.conf; vim core/db/db.conf
    vim web.py
    ```

### How to use

* Download apks from googleplay
    ```bash
    $ python download.py 5 (number of apk to download for each category)
    ```
* Download apks from m.apk
    ```bash
    $ python mapk.py
    ```
* Download apks from apkpure by single thread
    ```bash
    $ python APKPure_crawler.py
    ```
* Download apks from apkpure by threads
    ```bash
    $ python mutithread_download_apk.py
    ```
* Download apks from apkpure with temporary stop (avoid from memory crash)
    ```bash
    $ python sequence_download_apkpure.py
    ```
* Submit apks to virustotal
    ```bash
    $ python vt.py
    ```
* Submit apks to virustotal by threads
    ```bash
    $ python mutithread_vt.py
    ```
* Submit apk's url to virustotal by threads
    ```bash
    $ python url_vt.py
    ```
* Launch web interface to review results!
    ```bash
    $ python web.py
    ```

* Browse gplay_apk_analysis notbook with jupyter
    ```bash
    $ jupyter notebook --port 9999
    $ jupyter notebook --ip="ipaddr" --port 10000
    ```

* Start eve api service
    ```bash
    $ python eVe/run.py
    ```
### System request
* Python
    ```bash
    $ 2.7
    ```
* MongoDB
    ```bash
    $ 3.4
    ```
* OS
    ```bash
    $ MAC OS 10 or up
    $ Windows 7 or up
    $ Ubuntu 16.04  
    ```
