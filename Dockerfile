# use the AWS base image for python 3.12
FROM public.ecr.aws/lambda/python:3.12

# install build-essentials compiler and tools
RUN microdnf update -y && microdnf install -y gcc-c++ make

# copy files
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the libs in requirements.txt file
RUN pip install -r requirements.txt

# Copy PDF file
COPY Lei_geral_protecao_dados_pessoais_1ed.pdf ${LAMBDA_TASK_ROOT}/Lei_geral_protecao_dados_pessoais_1ed.pdf

# Copy the function code
COPY simplerag.py ${LAMBDA_TASK_ROOT}

# set permissions to make the file executable
RUN chmod +x simplerag.py

#set CMD to you handler
CMD ["simplerag.lambda_handler"]