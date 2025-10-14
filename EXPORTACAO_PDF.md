# 📄 Exportação de Escala em PDF - Rodízio de Organistas

## ✨ Nova Funcionalidade Implementada

Agora você pode **exportar a escala em formato PDF profissional**, igual ao modelo que você enviou!

---

## 🎯 Como Usar

### 1. Gerar a Escala

1. Faça login como **admin** (`admin` / `123456`)
2. Vá na aba **"Escala"**
3. Clique em **"🎲 Gerar Escala Automaticamente"**
4. Revise a escala gerada
5. Clique em **"✅ Publicar Escala"**

### 2. Exportar PDF

1. Na mesma aba **"Escala"**
2. Clique no botão **"📄 Exportar PDF"** (botão vermelho no canto superior direito)
3. O PDF será aberto em nova aba/baixado automaticamente

---

## 📋 Formato do PDF

O PDF é gerado com **layout profissional**, similar ao modelo enviado:

### Características:

✅ **Título centralizado**: "Rodízio de Organistas - Vila Paula (Outubro e Novembro 2025)"

✅ **Separação por mês**: Outubro/2025 e Novembro/2025 em tabelas separadas

✅ **Colunas**:
- **Data**: Formato dd/mm (ex: 05/10)
- **Dia**: Domingo ou Terça
- **Meia-hora**: Nome da organista (com observação se cobrir ambos)
- **Culto**: Nome da organista

✅ **Formatação visual**:
- Cabeçalho cinza escuro com texto branco
- Linhas alternadas (bege e branco)
- Grades visíveis
- Texto legível e organizado

✅ **Observações automáticas**:
- **Domingo**: Se a mesma organista cobre ambos, mostra "(cobre ambos)"
- **Terça-feira**: Mostra "(cobre os 2)" indicando que é a mesma pessoa

### Exemplo de Saída:

```
┌─────────────────────────────────────────────────────────────────────┐
│     Rodízio de Organistas - Vila Paula (Outubro e Novembro 2025)   │
└─────────────────────────────────────────────────────────────────────┘

Outubro/2025
┌────────┬─────────┬────────────────────────┬─────────────────────┐
│  Data  │   Dia   │      Meia-hora         │       Culto         │
├────────┼─────────┼────────────────────────┼─────────────────────┤
│ 05/10  │ Domingo │ Ieda (cobre ambos)     │ Ieda                │
│ 07/10  │ Terça   │ Ieda (cobre os 2)      │ Ieda                │
│ 12/10  │ Domingo │ Yasmin Graziele        │ Raquel              │
│ 14/10  │ Terça   │ Milena (cobre os 2)    │ Milena              │
│  ...   │   ...   │         ...            │  ...                │
└────────┴─────────┴────────────────────────┴─────────────────────┘

Novembro/2025
┌────────┬─────────┬────────────────────────┬─────────────────────┐
│  Data  │   Dia   │      Meia-hora         │       Culto         │
├────────┼─────────┼────────────────────────┼─────────────────────┤
│ 02/11  │ Domingo │ Yasmin Castro          │ Ieda                │
│ 04/11  │ Terça   │ Milena (cobre os 2)    │ Milena              │
│  ...   │   ...   │         ...            │  ...                │
└────────┴─────────┴────────────────────────┴─────────────────────┘
```

---

## 🖨️ Para Imprimir

1. Clique em **"📄 Exportar PDF"**
2. O PDF abrirá em nova aba
3. Use **Ctrl+P** (ou Cmd+P no Mac)
4. Selecione sua impressora
5. Ajuste configurações se necessário:
   - Orientação: **Paisagem** (landscape) - já vem configurado
   - Tamanho: A4
   - Margens: Normais
6. Clique em **"Imprimir"**

---

## 💾 Para Salvar

### Opção 1: Salvar diretamente do navegador
1. Clique em **"📄 Exportar PDF"**
2. O navegador pode perguntar onde salvar
3. Escolha a pasta e salve

### Opção 2: Salvar da visualização
1. PDF abre em nova aba
2. Clique no ícone de **download/salvar**
3. Salve onde desejar

**Nome do arquivo**: `Rodizio_Organistas_202510.pdf`

---

## 📧 Para Enviar por Email

1. Exporte o PDF
2. Salve no computador
3. Anexe no email para as organistas
4. Todas verão o mesmo formato profissional

---

## 🎨 Personalização

O PDF está configurado para:
- **Página**: A4 paisagem (horizontal)
- **Fonte**: Helvetica
- **Cores**: Cinza para cabeçalhos, bege/branco para linhas
- **Margens**: 1cm em todos os lados

Se quiser alterar cores ou estilo, edite o arquivo `app.py` na função `exportar_escala_pdf()`.

---

## 🔄 Atualização Automática

Sempre que você:
- Gerar nova escala
- Editar manualmente
- Publicar alterações

O PDF exportado refletirá **automaticamente** as mudanças mais recentes.

---

## ✅ Diferenças entre Tela e PDF

| Característica | Na Tela | No PDF |
|---|---|---|
| **Edição** | ✅ Admin pode editar | ❌ Somente leitura |
| **Estatísticas** | ✅ Mostra contadores | ❌ Não inclui |
| **Logs** | ✅ Mostra decisões | ❌ Não inclui |
| **Formato** | Interativo | Imprimível |
| **Uso** | Gerenciamento | Distribuição |

---

## 💡 Casos de Uso

### 1. Distribuição para Organistas
- Gere o PDF
- Envie por email ou WhatsApp
- Todas recebem versão profissional

### 2. Quadro de Avisos
- Imprima o PDF
- Cole no quadro da igreja
- Fácil visualização

### 3. Arquivo
- Salve PDFs mensais/bimestrais
- Mantenha histórico organizado
- Consulta futura

### 4. Backup
- PDF serve como backup visual
- Independente do sistema
- Sempre acessível

---

## 🆘 Problemas Comuns

### PDF não abre
**Solução**: Certifique-se de ter um visualizador de PDF instalado (Adobe Reader, navegador moderno)

### PDF em branco
**Solução**: Verifique se há escala publicada. Gere e publique primeiro.

### Formatação errada
**Solução**: Use navegador atualizado (Chrome, Firefox, Edge)

### Nome errado no PDF
**Solução**: Edite a escala e exporte novamente

---

## 🚀 Próximas Melhorias Sugeridas

- [ ] Exportação para **Excel** (.xlsx)
- [ ] Envio automático por **email**
- [ ] Personalização de **cores e logo**
- [ ] Inclusão de **estatísticas** no PDF
- [ ] **QR Code** para acesso online
- [ ] Geração de **calendário** (formato mensal)

---

## 📞 Comandos Úteis

### Testar geração de PDF via terminal
```bash
# Login
curl -c /tmp/cookies.txt -X POST http://localhost:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=123456"

# Baixar PDF
curl -b /tmp/cookies.txt http://localhost:8080/escala/pdf \
  -o escala.pdf

# Ver se foi criado
ls -lh escala.pdf
```

---

**Versão**: 2.1  
**Data**: Outubro 2025  
**Funcionalidade**: Exportação PDF implementada ✅
