# Cliente MCP para Odoo

Este documento explica como usar o cliente MCP para se conectar ao servidor Odoo MCP e testar os recursos disponíveis.

## Requisitos

- Python 3.6+
- Biblioteca `requests`

## Instalação

```bash
pip install requests
```

## Arquivos Incluídos

- `mcp_client_example.py`: Implementação do cliente MCP para Odoo
- `mcp_client_test.py`: Script de linha de comando para testar recursos específicos

## Como Usar o Cliente MCP

### Exemplo Básico

```python
from mcp_client_example import OdooMCPClient

# Inicializa o cliente (ajuste a URL conforme necessário)
client = OdooMCPClient("http://localhost:8080")

# Lista todos os modelos disponíveis
models = client.list_models()
print(models)

# Obtém informações sobre um modelo específico
model_info = client.get_model_info("res.partner")
print(model_info)

# Busca um registro específico
record = client.get_record("res.partner", 1)
print(record)

# Busca registros com um domínio específico
search_result = client.search_records("res.partner", [["is_company", "=", True]])
print(search_result)

# Executa um método personalizado
method_result = client.execute_method("res.partner", "search_count", [[["is_company", "=", True]]])
print(method_result)

# Busca funcionários pelo nome
employees = client.search_employee("Admin")
print(employees)

# Busca férias em um intervalo de datas
holidays = client.search_holidays("2023-01-01", "2023-12-31")
print(holidays)
```

### Usando o Script de Linha de Comando

O script `mcp_client_test.py` fornece uma interface de linha de comando para testar os recursos do servidor Odoo MCP.

```bash
# Mostrar ajuda
python mcp_client_test.py --help

# Listar todos os modelos disponíveis
python mcp_client_test.py --url http://localhost:8080 list-models

# Obter informações sobre um modelo específico
python mcp_client_test.py model-info res.partner

# Obter um registro específico
python mcp_client_test.py record res.partner 1

# Buscar registros com um domínio específico
python mcp_client_test.py search res.partner '[[\"is_company\", \"=\", true]]'

# Executar um método personalizado
python mcp_client_test.py execute res.partner search_count --args '[[\"is_company\", \"=\", true]]'

# Buscar funcionários pelo nome
python mcp_client_test.py search-employee Admin

# Buscar férias em um intervalo de datas
python mcp_client_test.py search-holidays 2023-01-01 2023-12-31
```

## Recursos Disponíveis

### Recursos (Resources)

O servidor Odoo MCP fornece os seguintes recursos:

- `odoo://models`: Lista todos os modelos disponíveis no sistema Odoo
- `odoo://model/{model_name}`: Obtém informações sobre um modelo específico
- `odoo://record/{model_name}/{record_id}`: Obtém um registro específico pelo ID
- `odoo://search/{model_name}/{domain}`: Busca registros que correspondem a um domínio

### Ferramentas (Tools)

O servidor Odoo MCP fornece as seguintes ferramentas:

- `execute_method`: Executa um método personalizado em um modelo Odoo
- `search_employee`: Busca funcionários pelo nome
- `search_holidays`: Busca férias dentro de um intervalo de datas

## Formatação de Parâmetros

### Domínio de Busca

O parâmetro de domínio pode ser formatado das seguintes maneiras:

- Lista: `[["field", "operator", value], ...]`
- Objeto: `{"conditions": [{"field": "...", "operator": "...", "value": "..."}]}`
- String JSON de qualquer um dos formatos acima

Exemplos:
- `[["is_company", "=", true]]`
- `{"conditions": [{"field": "date_order", "operator": ">=", "value": "2025-03-01"}]}`
- `[["date_order", ">=", "2025-03-01"], ["date_order", "<=", "2025-03-31"]]`

## Tratamento de Erros

O cliente MCP trata erros de conexão e retorna um dicionário com uma chave `error` contendo a mensagem de erro. Verifique sempre se a resposta contém uma chave `error` antes de processar os resultados.

```python
result = client.list_models()
if "error" in result:
    print(f"Erro: {result['error']}")
else:
    # Processa os resultados
    print(result)
```

## Configuração do Servidor

Para que o cliente MCP funcione corretamente, o servidor Odoo MCP deve estar em execução. Consulte o README principal para obter instruções sobre como configurar e iniciar o servidor.