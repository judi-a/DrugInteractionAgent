# Build stage
FROM continuumio/miniconda3 as builder

WORKDIR /app

# Create and activate the environment
COPY environment.yml .
RUN conda env create -f environment.yml && \
    conda clean -afy

# Install pip packages
RUN conda run -n python_env pip install --no-cache-dir git+https://github.com/bp-kelley/descriptastorus "flaml[automl]"

# Final stage
FROM continuumio/miniconda3

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /opt/conda/envs/python_env /opt/conda/envs/python_env
COPY . .

# Set up the environment
ENV PATH /opt/conda/envs/python_env/bin:$PATH

EXPOSE 9999

# Keep the original command that runs both Jupyter and keeps bash open
CMD [ "/bin/bash", "-c", "source activate python_env && nohup jupyter lab --ip=0.0.0.0 --port=9999 --no-browser --allow-root --NotebookApp.token='' > jupyter.log 2>&1 & bash" ]
