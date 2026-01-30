```markdown
# SPTrans - Projeto Golden Record Cartões 🚀

Sistema de alta performance para unificação e consulta de dados de cartões de transporte, seguindo os padrões de **Clean Architecture** e **Golden Record**.

## 📋 Pré-requisitos
* **Python:** Versão **3.11.0** ou superior (testado na v3.11.x).
* **Docker & Docker Compose:** Para execução do banco de dados MongoDB.
* **Sistema Operacional:** Windows 10/11, Linux ou macOS.

---

## 🏗️ Estrutura do Projeto
O projeto utiliza a separação em camadas para garantir manutenibilidade:
- `src/domain`: Entidades e regras de negócio.
- `src/application`: Casos de uso (Business Logic).
- `src/infrastructure`: Persistência e Repositórios.
- `src/presentation`: Controllers FastAPI e Segurança.

---

## 🚀 Guia de Instalação e Execução

### 1. Preparar o Ambiente Virtual (venv)
É altamente recomendado o uso de um ambiente isolado para evitar conflitos de dependências:

**No Windows:**
```bash
# Cria o ambiente
python -m venv venv

# Ativa o ambiente
.\venv\Scripts\activate
```

### 2. Instalar Dependências
Com a `venv` ativa, instale as bibliotecas conforme o `requirements.txt`:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Infraestrutura (Docker)
Inicie o container do MongoDB (porta **27018**, usuário `root`, senha `example`):

```bash
docker-compose up -d
```

Verifique a conexão:
```bash
mongo "mongodb://root:example@localhost:27018/sptrans?authSource=admin"
```

### 4. Testes de Qualidade e Integração
Valide os repositórios e a lógica de negócio antes de subir a API:

```bash
set PYTHONPATH=.
pytest -v
```

### 5. Benchmark de Performance
Execute o script para validar o uso de índices (**IXSCAN**) com 10.000 registros:

```bash
python scripts/performance_check.py
```

### 6. Seed de Dados de Performance
Insere **100 cartões de teste** para o CPF `12345678900`:

```bash
python -m scripts.seed_performance
```

### 7. Execução da API
Inicie o servidor para disponibilizar os endpoints:

```bash
python src/main.py
```

Acesse a documentação Swagger:  
`http://localhost:8000/docs` [(localhost in Bing)](https://www.bing.com/search?q="http%3A%2F%2Flocalhost%3A8000%2Fdocs")

---

## 🔒 Segurança e LGPD
O sistema aplica automaticamente políticas de privacidade na camada de saída:

* **Mascaramento**: O nome do titular é anonimizado (ex: `Nome *** sobrenome`).
* **Data Protection**: Dados internos de auditoria do MongoDB não são expostos ao usuário final.

---

## 📊 Exemplos de Uso da API

### Listar cartões por CPF
```http
GET http://localhost:8000/v1/cartoes/pessoas/12345678900/cartoes?page=1&limit=10
```

Resposta esperada:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "total_pages": 10
}
```

---

### 💡 Nota para o Laudo (Assinatura Técnica)
No final do seu documento, você pode reforçar o motivo da escolha da versão do Python:

> "A escolha pelo **Python 3.11** deve-se às otimizações de performance do interpretador (*Specializing Adaptive Interpreter*) e ao suporte nativo a tipagens complexas, garantindo que o processamento de grandes volumes de dados de bilhetagem ocorra com o menor consumo de memória possível."
```
---

