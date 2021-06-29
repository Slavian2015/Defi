FROM python:3.6

RUN mkdir -p /usr/local/WB
RUN pip install pymongo
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install python-binance
RUN pip install pandas-datareader
RUN pip install apscheduler
COPY docker-entrypoint.sh /usr/local/bin/
RUN ln -s /usr/local/bin/docker-entrypoint.sh /entrypoint.sh # backwards compat
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN pip install matplotlib

RUN pip install pytz
RUN pip install dateparser
RUN pip install statsmodels
RUN pip install unicorn-binance-websocket-api
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz
RUN pip install TA-Lib
RUN pip install cython
RUN pip install zigzag

ENTRYPOINT ["docker-entrypoint.sh"]
