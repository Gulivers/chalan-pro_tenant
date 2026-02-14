#!/bin/bash
# Script para copiar la clave SSH al servidor Hostinger VPS
# Ejecutar: bash copy_key_to_hostinger.sh

echo "Copiando clave SSH al servidor Hostinger..."
echo "Te pedirá la contraseña: 13694344Ho\$"
echo ""

ssh-copy-id -i ~/.ssh/id_ed25519_hostinger.pub ubuntu@72.60.168.62

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Clave copiada exitosamente!"
    echo "Ahora puedes conectarte sin contraseña con:"
    echo "  ssh hostinguer-vps"
else
    echo ""
    echo "❌ Error al copiar la clave. Intenta manualmente:"
    echo "  ssh ubuntu@72.60.168.62"
    echo "  Luego ejecuta en el servidor:"
    echo "  mkdir -p ~/.ssh"
    echo "  echo '$(cat ~/.ssh/id_ed25519_hostinger.pub)' >> ~/.ssh/authorized_keys"
    echo "  chmod 700 ~/.ssh"
    echo "  chmod 600 ~/.ssh/authorized_keys"
fi
