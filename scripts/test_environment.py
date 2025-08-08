#!/usr/bin/env python3
#/scripts/test_environment.py

"""
Teste de Ambiente - KyberCorax
Script para verificar se o ambiente está configurado corretamente

Autor: Leonardo - Engenheiro de Dados
"""

import sys
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")

    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("Python 3.8+ é requirido!")
        return False
    else:
        print("Versão Python OK")
        return True
    
def check_system_info():
    """Informações do sistem"""
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")
    print(f"Diretório atual: {Path.cwd()}")

def check_poetry():
    """Verifica se Poetry está instalado"""
    try:
        result = subprocess.run(['poetry', '--version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{result.stdout.strip()}")
            print("Poetry instado corretamente")
            return True
        else:
            print("Poetry não encontrado no PATH")
    except FileNotFoundError:
        print("Poetry não encontrado no PATH")
        return False
    
def check_dependencies():
    """Verifica dependências instaladas"""
    dependencies = ['requests', 'pandas', 'dotenv', 'loguru']

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"{dep} instalado")
        except ImportError:
            print(f"{dep} não instalado")

def check_project_structure():
    """Verifica etrutura do projeto"""
    required_dirs = [
        'dags', 'dbt', 'docker', 'data',
        'streamlit', 'notebooks', 'tests', 
        'docs', 'scripts'
    ]

    print("\n Estrutura do projeto:")
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"{dir_name}/")
        else:
            print(f"{dir_name}/ (não encontrado)")

def test_api_connection():
    """Testa conexão com API Scryfall"""

    try:
        import requests
        response = requests.get('https://api.scryfall.com/sets', timeout=10)

        if response.status_code == 200:
            print("Conexão com API Scrufall OK")
            print(f"Status: {response.status_code}")
            return True
        else:
            print(f"API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro na conexão: {e}")
        return False
    
def main():
    """Função principal"""
    print((" KyberCorax - Teste de Ambiente"))
    print("=" * 50)

    # Verificações básicas
    print("\n Verificações do Sistema:")
    check_system_info()

    print("\n Verificações de Software")
    python_ok = check_python_version()
    poetry_ok = check_poetry()

    if python_ok and poetry_ok:
        print("\n Verificações de Dependências:")
        check_dependencies()

        print("\n Teste de Conectividade:")
        test_api_connection()

    check_project_structure()

    print("\n" + "=" * 50)
    print("Teste completo!")
    print("Se houver erro,  resolva antes de continuar")

if __name__ == "__main__":
    main()