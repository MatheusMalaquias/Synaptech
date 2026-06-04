#!/bin/bash
# Duplo clique neste arquivo para iniciar o ERP
cd "$(dirname "$0")"
./start.sh start
echo ""
echo "Pressione Enter para fechar..."
read
