echo 1 > /proc/sys/vm/overcommit_memory
apt-get update -y
apt install python3-pip -y
python3 -m pip uninstall urllib3 chardet -y
python3 -m pip install urllib3 chardet

apt --fix-broken install -y
apt-get update -y
apt-get install libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 lsb-release wget xdg-utils -y
apt-get install fonts-liberation libu2f-udev -y
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo dpkg -i google-chrome-stable_current_amd64.deb

apt --fix-broken install -y

apt install chromium-chromedriver -y

google-chrome --version
chromedriver --version

python3 -m pip install urllib3 chardet beautifulsoup4 tldextract selenium
python3 -m pip install -r requirements.txt