# Dockerfile.base
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala as bibliotecas necessárias para a análise (pandas e matplotlib)
# Nota: Você precisará de permissões X-server ou salvar os gráficos 
# para visualizá-los se rodar o script de plotagem no container.
RUN pip install pandas matplotlib

# Copia todos os arquivos Python do projeto para o contêiner
COPY . /app