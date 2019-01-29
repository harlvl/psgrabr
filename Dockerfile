FROM qxf2rohand/qxf2_pom_essentials	

ENV TERM xterm
ENV PYTHONPATH $PYTHONPATH:/app
ENV SCRAPY_SETTINGS_MODULE psgrabr.settings
RUN mkdir -p /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app