# Rotina Telegram Scheduler

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Automação diária de rotinas SQL com notificações via Telegram e sistema de logs rotativos. Este projeto executa consultas SQL agendadas em bancos de dados SQL Server e envia notificações em tempo real sobre o status das operações.

## 📋 Índice

- [Características](#características)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Monitoramento](#monitoramento)
- [Solução de Problemas](#solução-de-problemas)
- [Contribuição](#contribuição)
- [Licença](#licença)

## ✨ Características

- **Agendamento automático**: Execução de rotinas SQL em horários específicos
- **Notificações Telegram**: Alertas em tempo real sobre início, sucesso e falhas
- **Logs rotativos**: Sistema de logging com rotação automática de arquivos
- **Compatibilidade multiplataforma**: Suporte para Windows e sistemas Unix-like
- **Pool de conexões otimizado**: Configuração otimizada para o bot do Telegram
- **Métricas de execução**: Acompanhamento de duração e resultados das operações
- **Tratamento de erros robusto**: Recuperação automática e notificação de falhas

## 🔧 Pré-requisitos

- Python 3.7 ou superior
- SQL Server com driver ODBC 17
- Bot do Telegram configurado
- Acesso ao banco de dados SQL Server

### Dependências Python

```txt
pyodbc>=4.0.0
python-telegram-bot>=13.0,<21.0
APScheduler>=3.9.0
python-dotenv>=0.19.0
```

## 🚀 Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/rotina-telegram-scheduler.git
   cd rotina-telegram-scheduler
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configurações do SQL Server
SQL_SERVER=seu-servidor.database.windows.net
SQL_DATABASE=ContosoRetailDW

# Configurações do Telegram
TELEGRAM_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=-1001234567890
```

### 2. Configuração do Bot Telegram

1. Converse com [@BotFather](https://t.me/botfather) no Telegram
2. Crie um novo bot com `/newbot`
3. Copie o token fornecido para `TELEGRAM_TOKEN`
4. Adicione o bot ao grupo/chat desejado
5. Obtenha o Chat ID e configure em `TELEGRAM_CHAT_ID`

### 3. Configuração do SQL Server

Certifique-se de que:
- O driver ODBC 17 para SQL Server está instalado
- A autenticação Windows está configurada (Trusted_Connection)
- O usuário tem permissões para criar/dropar tabelas no banco

## 🔄 Uso

### Execução Direta

```bash
python rotina_telegram.py
```

### Execução em Background (Linux/macOS)

```bash
nohup python rotina_telegram.py > output.log 2>&1 &
```

### Execução como Serviço (Windows)

Considere usar ferramentas como `NSSM` ou `sc.exe` para executar como serviço Windows.

### Personalização do Agendamento

Por padrão, a rotina executa diariamente às 14:07 (hora de São Paulo). Para alterar:

```python
HOUR, MINUTE = 14, 7  # Altere para o horário desejado
```

## 📁 Estrutura do Projeto

```
rotina-telegram-scheduler/
│
├── rotina_telegram.py      # Script principal
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de configuração
├── README.md              # Esta documentação
├── LICENSE                # Licença do projeto
│
├── logs/                  # Diretório de logs (criado automaticamente)
│   ├── rotina.log        # Log atual
│   ├── rotina.log.1      # Backup 1
│   └── ...               # Backups adicionais
│
└── docs/                  # Documentação adicional
    ├── INSTALLATION.md    # Guia de instalação detalhado
    └── TROUBLESHOOTING.md # Guia de solução de problemas
```

## 📊 Monitoramento

### Logs

Os logs são salvos em `rotina.log` com rotação automática:
- Tamanho máximo: 5MB
- Backups mantidos: 5 arquivos
- Formato: `YYYY-MM-DD HH:MM:SS LEVEL: MESSAGE`

### Notificações Telegram

O bot envia notificações para:
- ✅ Início da execução
- ✅ Sucesso com métricas (duração, linhas processadas)
- ❌ Erros durante a execução
- ❌ Falhas do agendador

### Exemplo de Mensagens

```
[ROUTINA] Início: 2024-01-15 14:07:00
[ROUTINA] Concluída: 2024-01-15 14:07:23 | Duração: 23.4s | Linhas: 1250
[SCHEDULER] Job executado com sucesso às 14:07:23
```

## 🔧 Solução de Problemas

### Erro de Conexão com SQL Server

```python
# Verifique se o driver ODBC está instalado
# Windows: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
# Linux: Instale via package manager
```

### Erros de SSL/TLS

Se encontrar problemas de SSL, ajuste a string de conexão:

```python
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    "Trusted_Connection=yes;"
    "Encrypt=no;"  # Desabilita SSL se necessário
)
```

### Bot Telegram Não Responde

1. Verifique se o token está correto
2. Confirme se o bot foi adicionado ao chat
3. Teste a conectividade de rede
4. Verifique os logs para erros específicos

### Agendador Não Executa

- Verifique o fuso horário configurado
- Confirme se o script está rodando continuamente
- Monitore os logs para mensagens de erro

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Siga o estilo de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação conforme necessário
- Use mensagens de commit descritivas

## 📝 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para suporte e dúvidas:

- 🐛 [Issues](https://github.com/mleandro000/rotina-telegram-scheduler/issues)
- 💬 [Discussions](https://github.com/mleandro000/rotina-telegram-scheduler/discussions)
- 📧 Email: menezesleandro@usp.br
- 📱 WhatsApp: +55 11 94523-4207

---

**Desenvolvido com ❤️ para automatizar suas rotinas SQL**
