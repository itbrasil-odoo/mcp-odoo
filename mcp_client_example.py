#!/usr/bin/env python3
"""
MCP Client Example para Odoo MCP Server

Este script demonstra como um cliente MCP pode se conectar ao servidor Odoo MCP
e testar os recursos disponíveis.
"""

import json
from typing import Any, Dict, List, Optional

import requests


class OdooMCPClient:
    """Cliente para interagir com o servidor Odoo MCP"""

    def __init__(self, server_url: str = "http://localhost:8080"):
        """
        Inicializa o cliente MCP

        Args:
            server_url: URL do servidor MCP (padrão: http://localhost:8080)
        """
        self.server_url = server_url
        self.base_url = f"{server_url}/mcp"

    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz uma requisição para o servidor MCP

        Args:
            endpoint: Endpoint da API
            data: Dados da requisição

        Returns:
            Resposta do servidor
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {"Content-Type": "application/json"}

        try:
            # Add timeout to prevent hanging requests (security best practice)
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return {"error": str(e)}

    def get_resource(self, resource_uri: str) -> Dict[str, Any]:
        """
        Obtém um recurso do servidor MCP

        Args:
            resource_uri: URI do recurso (ex: odoo://models)

        Returns:
            Dados do recurso
        """
        data = {"resource_uri": resource_uri}
        return self._make_request("resource", data)

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Executa uma ferramenta no servidor MCP

        Args:
            tool_name: Nome da ferramenta
            **kwargs: Parâmetros da ferramenta

        Returns:
            Resultado da execução da ferramenta
        """
        data = {"tool": tool_name, "parameters": kwargs}
        return self._make_request("tool", data)

    # Métodos específicos para recursos

    def list_models(self) -> Dict[str, Any]:
        """Lista todos os modelos disponíveis no sistema Odoo"""
        return self.get_resource("odoo://models")

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Obtém informações detalhadas sobre um modelo específico

        Args:
            model_name: Nome do modelo (ex: res.partner)
        """
        return self.get_resource(f"odoo://model/{model_name}")

    def get_record(self, model_name: str, record_id: int) -> Dict[str, Any]:
        """
        Obtém um registro específico pelo ID

        Args:
            model_name: Nome do modelo (ex: res.partner)
            record_id: ID do registro
        """
        return self.get_resource(f"odoo://record/{model_name}/{record_id}")

    def search_records(self, model_name: str, domain: List) -> Dict[str, Any]:
        """
        Busca registros que correspondem a um domínio

        Args:
            model_name: Nome do modelo (ex: res.partner)
            domain: Domínio de busca (ex: [["is_company", "=", true]])
        """
        # Converte o domínio para JSON string
        domain_str = json.dumps(domain)
        return self.get_resource(f"odoo://search/{model_name}/{domain_str}")

    # Métodos específicos para ferramentas

    def execute_method(
        self, model: str, method: str, args: List = None, kwargs: Dict = None
    ) -> Dict[str, Any]:
        """
        Executa um método personalizado em um modelo Odoo

        Args:
            model: Nome do modelo (ex: res.partner)
            method: Nome do método a ser executado
            args: Argumentos posicionais
            kwargs: Argumentos nomeados
        """
        return self.execute_tool(
            "execute_method",
            model=model,
            method=method,
            args=args or [],
            kwargs=kwargs or {},
        )

    def search_employee(self, name: str, limit: int = 20) -> Dict[str, Any]:
        """
        Busca funcionários pelo nome

        Args:
            name: Nome (ou parte do nome) a ser buscado
            limit: Número máximo de resultados a retornar (padrão: 20)
        """
        return self.execute_tool("search_employee", name=name, limit=limit)

    def search_holidays(
        self, start_date: str, end_date: str, employee_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Busca férias dentro de um intervalo de datas

        Args:
            start_date: Data inicial no formato YYYY-MM-DD
            end_date: Data final no formato YYYY-MM-DD
            employee_id: ID do funcionário (opcional)
        """
        params = {"start_date": start_date, "end_date": end_date}
        if employee_id is not None:
            params["employee_id"] = employee_id
        return self.execute_tool("search_holidays", **params)


def main():
    """Função principal para demonstrar o uso do cliente MCP"""

    # Inicializa o cliente (ajuste a URL conforme necessário)
    client = OdooMCPClient("http://localhost:8080")

    print("=== Testando recursos do Odoo MCP Server ===\n")

    # Teste 1: Listar modelos
    print("1. Listando modelos disponíveis:")
    models_result = client.list_models()
    print(json.dumps(models_result, indent=2))
    print("\n" + "-" * 50 + "\n")

    # Teste 2: Obter informações de um modelo específico
    print("2. Obtendo informações do modelo 'res.partner':")
    model_info = client.get_model_info("res.partner")
    print(json.dumps(model_info, indent=2))
    print("\n" + "-" * 50 + "\n")

    # Teste 3: Buscar um registro específico
    print("3. Buscando registro de parceiro com ID 1:")
    record = client.get_record("res.partner", 1)
    print(json.dumps(record, indent=2))
    print("\n" + "-" * 50 + "\n")

    # Teste 4: Buscar registros com um domínio
    print("4. Buscando empresas (is_company=True):")
    search_result = client.search_records("res.partner", [["is_company", "=", True]])
    print(json.dumps(search_result, indent=2))
    print("\n" + "-" * 50 + "\n")

    # Teste 5: Executar um método personalizado
    print("5. Executando método 'search_count' no modelo 'res.partner':")
    method_result = client.execute_method(
        "res.partner", "search_count", [[["is_company", "=", True]]]
    )
    print(json.dumps(method_result, indent=2))
    print("\n" + "-" * 50 + "\n")

    # Teste 6: Buscar funcionários
    print("6. Buscando funcionários com nome contendo 'Admin':")
    employees = client.search_employee("Admin")
    print(json.dumps(employees, indent=2))
    print("\n" + "-" * 50 + "\n")

    # Teste 7: Buscar férias
    print("7. Buscando férias entre 2023-01-01 e 2023-12-31:")
    holidays = client.search_holidays("2023-01-01", "2023-12-31")
    print(json.dumps(holidays, indent=2))
    print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
