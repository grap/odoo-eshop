sudo apt-get install libjpeg-dev
sudo apt-get install libfreetype6-dev
sudo apt-get install --reinstall zlibc zlib1g zlib1g-dev
sudo apt-get install python-imaging
sudo pip install Pillow --upgrade
sudo pip install captcha

sudo apt-get install zlib1g-dev
sudo easy_install PIL
sudo easy_install Pillow

sudo apt-get build-dep python-imaging

libjpeg-devel

#jpeg support
sudo apt-get install libjpeg-dev
#tiff support
sudo apt-get install libtiff-dev
#freetype support
sudo apt-get install libfreetype6-dev
#openjpeg200support (needed to compile from source)
wget http://downloads.sourceforge.net/project/openjpeg.mirror/2.0.1/openjpeg-2.0.1.tar.gz
tar xzvf openjpeg-2.0.1.tar.gz
cd openjpeg-2.0.1/
sudo apt-get install cmake
cmake .
sudo make install
#install pillow
pip install pillow
