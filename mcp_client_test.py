#!/usr/bin/env python3
"""
Script para testar a conexão com o servidor Odoo MCP

Este script demonstra como usar o cliente MCP para testar recursos específicos
do servidor Odoo MCP com base em parâmetros de linha de comando.
"""

import argparse
import json
import sys
from mcp_client_example import OdooMCPClient

def print_json(data):
    """Imprime dados JSON formatados"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_resource(client, resource_uri):
    """Testa um recurso específico"""
    print(f"Testando recurso: {resource_uri}")
    result = client.get_resource(resource_uri)
    print_json(result)

def test_tool(client, tool_name, **params):
    """Testa uma ferramenta específica"""
    print(f"Testando ferramenta: {tool_name}")
    print(f"Parâmetros: {params}")
    result = client.execute_tool(tool_name, **params)
    print_json(result)

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Cliente de teste para o servidor Odoo MCP")
    parser.add_argument("--url", default="http://localhost:8080", help="URL do servidor MCP")
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a ser executado")
    
    # Comando para testar recursos
    resource_parser = subparsers.add_parser("resource", help="Testar um recurso")
    resource_parser.add_argument("uri", help="URI do recurso (ex: odoo://models)")
    
    # Comando para listar modelos
    subparsers.add_parser("list-models", help="Listar todos os modelos disponíveis")
    
    # Comando para obter informações de um modelo
    model_info_parser = subparsers.add_parser("model-info", help="Obter informações de um modelo")
    model_info_parser.add_argument("model", help="Nome do modelo (ex: res.partner)")
    
    # Comando para obter um registro
    record_parser = subparsers.add_parser("record", help="Obter um registro específico")
    record_parser.add_argument("model", help="Nome do modelo (ex: res.partner)")
    record_parser.add_argument("id", type=int, help="ID do registro")
    
    # Comando para buscar registros
    search_parser = subparsers.add_parser("search", help="Buscar registros")
    search_parser.add_argument("model", help="Nome do modelo (ex: res.partner)")
    search_parser.add_argument("domain", help="Domínio de busca em formato JSON (ex: '[[\"is_company\", \"=\", true]]')")
    
    # Comando para executar um método
    method_parser = subparsers.add_parser("execute", help="Executar um método")
    method_parser.add_argument("model", help="Nome do modelo (ex: res.partner)")
    method_parser.add_argument("method", help="Nome do método (ex: search_count)")
    method_parser.add_argument("--args", help="Argumentos posicionais em formato JSON (ex: '[[\"is_company\", \"=\", true]]')")
    method_parser.add_argument("--kwargs", help="Argumentos nomeados em formato JSON (ex: '{\"limit\": 10}')")
    
    # Comando para buscar funcionários
    employee_parser = subparsers.add_parser("search-employee", help="Buscar funcionários")
    employee_parser.add_argument("name", help="Nome (ou parte do nome) a ser buscado")
    employee_parser.add_argument("--limit", type=int, default=20, help="Número máximo de resultados")
    
    # Comando para buscar férias
    holiday_parser = subparsers.add_parser("search-holidays", help="Buscar férias")
    holiday_parser.add_argument("start_date", help="Data inicial (YYYY-MM-DD)")
    holiday_parser.add_argument("end_date", help="Data final (YYYY-MM-DD)")
    holiday_parser.add_argument("--employee-id", type=int, help="ID do funcionário (opcional)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Inicializa o cliente
    client = OdooMCPClient(args.url)
    
    # Executa o comando apropriado
    if args.command == "resource":
        test_resource(client, args.uri)
    
    elif args.command == "list-models":
        result = client.list_models()
        print_json(result)
    
    elif args.command == "model-info":
        result = client.get_model_info(args.model)
        print_json(result)
    
    elif args.command == "record":
        result = client.get_record(args.model, args.id)
        print_json(result)
    
    elif args.command == "search":
        domain = json.loads(args.domain)
        result = client.search_records(args.model, domain)
        print_json(result)
    
    elif args.command == "execute":
        args_data = json.loads(args.args) if args.args else []
        kwargs_data = json.loads(args.kwargs) if args.kwargs else {}
        result = client.execute_method(args.model, args.method, args_data, kwargs_data)
        print_json(result)
    
    elif args.command == "search-employee":
        result = client.search_employee(args.name, args.limit)
        print_json(result)
    
    elif args.command == "search-holidays":
        params = {
            "start_date": args.start_date,
            "end_date": args.end_date
        }
        if args.employee_id:
            params["employee_id"] = args.employee_id
        result = client.search_holidays(**params)
        print_json(result)

if __name__ == "__main__":
    main()