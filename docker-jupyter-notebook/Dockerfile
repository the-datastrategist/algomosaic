# jupyter image
FROM jupyter/scipy-notebook

# create working dictionary
RUN rm -r work
RUN mkdir algomosaic

# add persistent python path (for local imports)
ENV PYTHONPATH "${PYTHONPATH}:/home/jovyan/algomosaic"

# jupyter notebook entry
RUN pip install jupyter -U && pip install jupyterlab
EXPOSE 8888
ENTRYPOINT ["jupyter","lab","--ip=0.0.0.0","--allow-root"]
