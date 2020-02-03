FROM ubuntu
RUN apt update
RUN apt install -y curl cron nano python3.7 openssl python3-pip libcurl4-openssl-dev libssl-dev libsm6 libxext6 libxrender-dev libpython3.7-dev libnss3 libnss3-dev
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN python3 -m pip install --install-option="--with-openssl" --install-option="--openssl-dir=/usr/local/opt/openssl" --user pycurl
RUN python3 -m pip install dialog_bot_sdk==2.3.2
RUN mkdir /py
ADD py/ /py/
ADD sh/run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]