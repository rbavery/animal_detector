FROM tensorflow/tensorflow:2.3.4-gpu-jupyter
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8501
# COPY ./app /app
# ENTRYPOINT ["streamlit", "run"]
# CMD ["animal_detector.py"]
