#!/bin/bash
echo "Iniciando o túnel público (HTTPS)..."
echo "Aguarde o link aparecer abaixo (ex: https://...lhr.life)"
echo "--------------------------------------------------------"
ssh -R 80:localhost:8000 localhost.run
