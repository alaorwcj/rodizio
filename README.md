# 🎹 Sistema de Rodízio de Organistas

Sistema web completo para gerenciamento de escalas de organistas em igrejas, com suporte a múltiplos níveis hierárquicos (Regional → Sub-Regional → Comum).

## � Screenshots

### Dashboard - Administrador
![Dashboard Administrador](images/dashboard-admin.png)
*Visualização completa das próximas 20 escalas com cards coloridos por dia da semana*

### Gerenciamento de Escala - Modo Manual
![Gerenciamento de Escala](images/gerenciamento-escala.png)
*Interface para edição manual de escalas com seleção de organistas por data*

### Dashboard - Organista
![Dashboard Organista](images/dashboard-organista.png)
*Visualização personalizada mostrando apenas os dias de rodízio do organista logado*

### Agenda de Disponibilidade
![Agenda de Disponibilidade](images/agenda-disponibilidade.png)
*Calendário interativo para organistas marcarem indisponibilidade*

> **📝 Nota**: Para adicionar os screenshots reais, salve as imagens na pasta `images/` com os nomes indicados acima. Veja [instruções detalhadas](images/README.md).

## � Índice

- [Screenshots](#-screenshots)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Hierarquia e Permissões](#hierarquia-e-permissões)
- [Funcionalidades](#funcionalidades)
- [Troubleshooting](#troubleshooting)
- [Documentação Adicional](#documentação-adicional)

## ✨ Características

- 🏢 **Gestão Hierárquica**: Suporte a Regional → Sub-Regional → Comum
- 👥 **Múltiplos Perfis**: Master, Administrador Regional, Encarregado Sub-Regional, Encarregado Local e Organista
- 📅 **Escalas Automáticas**: Geração automática de rodízios (Culto Oficial e RJM)
- 📊 **Dashboard Interativo**: Visualização das próximas 20 escalas
- 🌙 **Dark Mode**: Alternância entre tema claro e escuro
- 📱 **Responsivo**: Interface adaptável para desktop e mobile
- 🎨 **Tema Moderno**: Design Azul-Lavanda profissional
- 📄 **Exportação PDF**: Escalas formatadas para impressão
- 🔐 **Autenticação Segura**: Senhas com hash bcrypt

## 🔧 Requisitos

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Portas disponíveis**: 8080 (aplicação)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/alaorwcj/rodizio.git
cd rodizio
```

### 2. Construa e inicie os containers

```bash
docker-compose up --build -d
```

### 3. Acesse a aplicação

Abra seu navegador em: **http://localhost:8080**

### 4. Login inicial

**Usuário Master (Administrador do Sistema):**
- **Usuário**: `admin_master`
- **Senha**: `admin123` (altere imediatamente após primeiro login)

## ⚙️ Configuração

### Configuração Inicial da Hierarquia

1. **Login como Master**: Acesse com `admin_master`
2. **Criar Regional**: Vá em `Administrativo > Hierarquia` e crie a Regional (ex: "Regional GRU")
3. **Criar Sub-Regional**: Dentro da Regional, crie Sub-Regionais (ex: "Santa Isabel")
4. **Criar Comuns**: Dentro da Sub-Regional, crie as Comuns (ex: "Vila Paula")
5. **Configurar Período**: Em cada Comum, configure o período/bimestre das escalas

### Criação de Usuários

**Administrador Regional:**
```
Menu: Administrativo > Usuários > Criar Usuário
Tipo: Administrador Regional
Vincular à Regional criada
```

**Encarregado Sub-Regional:**
```
Menu: Administrativo > Usuários > Criar Usuário
Tipo: Encarregado Sub-Regional
Vincular à Sub-Regional
```

**Encarregado Local (Comum):**
```
Menu: Administrativo > Usuários > Criar Usuário
Tipo: Encarregado Local
Vincular à Comum
```

**Organistas:**
```
Menu: Encarregado Local > Organistas > Cadastrar Organista
Preencher: Nome, Telefone, Dias disponíveis
Senha inicial gerada automaticamente
```

## 📖 Uso

### Para Administradores/Encarregados

#### 1. Gerenciar Organistas
```
Menu: Encarregado Local > Organistas
- Cadastrar novos organistas
- Editar informações
- Definir dias disponíveis (ex: Domingo, Terça, Quinta)
```

#### 2. Criar Escalas (Rodízios)

**Escala de Culto Oficial:**
```
Menu: Rodízios > Culto Oficial > Criar Escala
1. Selecione a data inicial e final
2. Sistema gera automaticamente baseado nos dias de culto
3. Distribui organistas de forma justa e equilibrada
4. Respeita disponibilidade de cada organista
```

**Escala RJM (Reunião de Jovens e Menores):**
```
Menu: Rodízios > RJM > Criar Escala
1. Selecione a data inicial e final
2. Escolha os dias da semana (ex: Terça e Quinta)
3. Sistema distribui organistas disponíveis
```

#### 3. Editar Escalas Manualmente
```
Menu: Rodízios > [Culto/RJM] > Modo Manual
- Clique em qualquer data para alterar o organista
- Troque organistas conforme necessidade
- Adicione ou remova datas
```

#### 4. Exportar para PDF
```
Menu: Rodízios > [Culto/RJM] > Exportar PDF
- Gera PDF formatado com todas as escalas
- Inclui informações da comum e período
- Pronto para impressão
```

### Para Organistas

#### 1. Visualizar Minhas Escalas
```
Menu: Dashboard
Seção "🎹 Meus Dias de Rodízio"
- Veja todas as suas escalas futuras
- Diferencia Culto Oficial de RJM
- Mostra data e dia da semana
```

#### 2. Agendar Disponibilidade
```
Menu: Agenda Organista > Minha Agenda
- Cadastre datas em que não poderá tocar
- Informe o motivo (opcional)
- Sistema considera isso ao gerar escalas
```

#### 3. Trocar Senha
```
Menu: Botão "🔑 Trocar Senha" (canto superior direito)
- Insira senha atual
- Defina nova senha
- Confirme nova senha
```

## 📁 Estrutura do Projeto

```
rodizio/
├── app.py                      # Aplicação Flask principal
├── docker-compose.yml          # Configuração Docker
├── Dockerfile                  # Imagem Docker
├── requirements.txt            # Dependências Python
├── entrypoint.sh              # Script de inicialização
├── README.md                  # Este arquivo
├── data/
│   └── db.json               # Banco de dados JSON
├── templates/
│   ├── index.html            # Interface principal
│   ├── login.html            # Tela de login
│   └── trocar_senha.html     # Tela de troca de senha
├── static/                   # Arquivos estáticos (se houver)
├── docs/                     # Documentação adicional
│   ├── GUIA_USUARIOS.md     # Guia para usuários finais
│   ├── FUNCIONALIDADES.md   # Detalhes das funcionalidades
│   ├── COMO_FUNCIONA.md     # Explicação técnica
│   └── ...                   # Outros documentos
└── images/                   # Imagens e recursos
```

## 🔐 Hierarquia e Permissões

### Níveis de Acesso

| Perfil | Permissões |
|--------|-----------|
| **Master** | Acesso total ao sistema, cria regionais, sub-regionais e comuns |
| **Admin Regional** | Gerencia todas sub-regionais e comuns da regional |
| **Encarregado Sub-Regional** | Gerencia comuns da sub-regional |
| **Encarregado Local** | Gerencia organistas e escalas da comum |
| **Organista** | Visualiza escalas pessoais e gerencia agenda |

### Hierarquia de Dados

```
Sistema (Master)
  └── Regional (Admin Regional)
      └── Sub-Regional (Encarregado Sub-Regional)
          └── Comum (Encarregado Local)
              └── Organistas
                  └── Escalas
```

## 🎯 Funcionalidades

### Dashboard
- Visualização das próximas 20 escalas
- Cards coloridos por dia da semana
- Diferenciação visual entre Culto Oficial e RJM
- Indicador de escalas passadas (opacidade reduzida)

### Gestão de Rodízios
- **Geração Automática**: Algoritmo inteligente distribui organistas
- **Modo Manual**: Edição individual de qualquer data
- **Exportação PDF**: Documentos formatados profissionalmente
- **Visualização**: Cards compactos com 20 datas visíveis

### Agenda de Organistas
- Organistas podem informar indisponibilidade
- Sistema respeita essas datas ao gerar escalas
- Histórico de agendamentos

### Hierarquia Administrativa
- Criação dinâmica de regionais, sub-regionais e comuns
- Configuração individual de períodos/bimestres
- Gestão de horários de cultos por comum

## 🐛 Troubleshooting

### Container não inicia

```bash
# Verificar logs
docker-compose logs -f

# Recriar container
docker-compose down
docker-compose up --build -d
```

### Erro de permissão no db.json

```bash
# Ajustar permissões
chmod 644 data/db.json
```

### Porta 8080 já em uso

Edite `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Mude para outra porta
```

### Esqueci a senha do admin

Execute o script de recuperação:
```bash
docker-compose exec rodizio-app python update_db_passwords.py
```

### Escalas não aparecem

1. Verifique se há organistas cadastrados
2. Confirme que organistas têm dias disponíveis configurados
3. Verifique se o período está configurado na comum
4. Tente criar escala manualmente primeiro

## 📚 Documentação Adicional

Para mais detalhes, consulte a documentação completa na pasta `docs/`:

- **[GUIA_USUARIOS.md](docs/GUIA_USUARIOS.md)**: Manual completo para usuários finais
- **[FUNCIONALIDADES.md](docs/FUNCIONALIDADES.md)**: Descrição detalhada de cada funcionalidade
- **[COMO_FUNCIONA.md](docs/COMO_FUNCIONA.md)**: Explicação técnica do sistema
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**: Soluções para problemas comuns
- **[CHANGELOG.md](docs/CHANGELOG.md)**: Histórico de versões e mudanças

## 🛠️ Comandos Úteis

### Docker

```bash
# Iniciar aplicação
docker-compose up -d

# Parar aplicação
docker-compose down

# Ver logs em tempo real
docker-compose logs -f

# Reconstruir após mudanças
docker-compose up --build -d

# Acessar shell do container
docker-compose exec rodizio-app bash

# Backup do banco de dados
docker-compose exec rodizio-app cp data/db.json data/db_backup_$(date +%Y%m%d_%H%M%S).json
```

### Python (dentro do container)

```bash
# Executar shell Python
docker-compose exec rodizio-app python

# Executar script
docker-compose exec rodizio-app python script.py
```

## 🔄 Atualização

Para atualizar o sistema:

```bash
# 1. Backup do banco de dados
cp data/db.json data/db_backup_$(date +%Y%m%d_%H%M%S).json

# 2. Parar containers
docker-compose down

# 3. Atualizar código
git pull

# 4. Reconstruir e iniciar
docker-compose up --build -d
```

## 🤝 Suporte

Para dúvidas, problemas ou sugestões:

1. Consulte a [Documentação](docs/)
2. Verifique [Issues existentes](https://github.com/alaorwcj/rodizio/issues)
3. Abra um [Novo Issue](https://github.com/alaorwcj/rodizio/issues/new)

## 📄 Licença

Este projeto é de código aberto. Consulte o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

Desenvolvido por **Alaor Rodrigues**

---

**Sistema de Rodízio de Organistas** - Facilitando a gestão musical nas igrejas 🎹✨
