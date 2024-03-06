#!/bin/bash
TIMESTAMP=`date "+%Y%m%d_%H%M%S.%N" `

NAMESPACE=$1
CLUSTER=$2
CLUSTER_URL=$3
CLUSTER_PASSWORD=$4

echo "script 1: Run-> $TIMESTAMP"
echo "Namespace: $NAMESPACE Cluster: $CLUSTER URL: $CLUSTER_URL -- Clave: $CLUSTER_PASSWORD" | tee -a /tmp/prueba_script_1.log

