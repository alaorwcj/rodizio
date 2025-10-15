# 🔄 IMPORTANTE: Como Testar o PDF Atualizado

## ⚠️ O problema pode ser CACHE do navegador!

Se você está vendo o PDF antigo, siga estes passos:

---

## ✅ PASSO A PASSO PARA TESTAR

### 1️⃣ Limpar Cache do Navegador

**Opção A - Atalho rápido**:
- Pressione `Ctrl + Shift + Delete` (Windows/Linux)
- Ou `Cmd + Shift + Delete` (Mac)
- Selecione "Imagens e arquivos em cache"
- Clique em "Limpar dados"

**Opção B - Modo anônimo/privado**:
- Pressione `Ctrl + Shift + N` (Chrome)
- Ou `Ctrl + Shift + P` (Firefox)
- Acesse `http://localhost:8080`

**Opção C - Forçar atualização**:
- Na página, pressione `Ctrl + F5` (Windows)
- Ou `Cmd + Shift + R` (Mac)

---

### 2️⃣ Fazer Login

1. Usuário: `admin`
2. Senha: `123456`
3. Clique em "Entrar"

---

### 3️⃣ Ir para Aba "Escala"

- Clique na aba **"Escala"** no menu superior

---

### 4️⃣ Gerar Nova Escala

1. Clique em **"🎲 Gerar Escala Automaticamente"**
2. Aguarde processar
3. Veja a escala aparecer na tela separada por mês

---

### 5️⃣ Publicar a Escala

1. Clique em **"✅ Publicar Escala"**
2. Confirme quando perguntar
3. Aguarde mensagem de sucesso

---

### 6️⃣ Exportar PDF (NOVO)

1. Clique em **"📄 Exportar PDF"** (botão vermelho no canto superior direito)
2. O PDF vai abrir em nova aba
3. **IMPORTANTE**: Se abrir na mesma aba anterior, feche e clique novamente

---

## 🔍 O QUE VERIFICAR NO PDF

### ✅ Para DOMINGOS:

**Se forem pessoas DIFERENTES**:
```
Data: 12/10
Dia: Domingo
Meia-hora: Yasmin Graziele
Culto: Raquel
```
✅ **Ambas as colunas** devem estar preenchidas com nomes diferentes

**Se for a MESMA pessoa**:
```
Data: 05/10
Dia: Domingo
Meia-hora: Ieda (cobre ambos)
Culto: Ieda (cobre ambos)
```
✅ **Ambas as colunas** devem mostrar o nome com "(cobre ambos)"

### ✅ Para TERÇAS:

```
Data: 07/10
Dia: Terça
Meia-hora: Ieda (cobre os 2)
Culto: Ieda
```
✅ Coluna **Meia-hora** deve ter "(cobre os 2)"  
✅ Coluna **Culto** deve ter o **nome da mesma pessoa**

---

## ❌ Se Ainda Não Funcionar

### Teste 1: Baixar PDF direto

Abra esta URL no navegador:
```
http://localhost:8080/escala/pdf?download=true
```

Isso força o download ao invés de visualização.

---

### Teste 2: Verificar via terminal

```bash
# Gerar e baixar PDF
cd /mnt/f/rodizio

curl -s -c /tmp/cookies.txt -X POST http://localhost:8080/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=123456" > /dev/null

curl -s -b /tmp/cookies.txt -X POST http://localhost:8080/escala/gerar \
  -o /tmp/escala.json

curl -s -b /tmp/cookies.txt -X POST http://localhost:8080/escala/publicar \
  -H "Content-Type: application/json" \
  -d @/tmp/escala.json

curl -b /tmp/cookies.txt http://localhost:8080/escala/pdf \
  -o rodizio_teste.pdf

# Abrir PDF
explorer.exe rodizio_teste.pdf
# Ou no Linux:
xdg-open rodizio_teste.pdf
```

---

### Teste 3: Ver logs do container

```bash
docker-compose logs --tail=50 rodizio-app | grep -i pdf
```

Se houver erro, vai aparecer aqui.

---

## 🎯 O QUE MUDOU NO CÓDIGO

### Antes (ERRADO):
```python
if item["dia_semana"] == "Sunday":
    meia_hora = item.get("meia_hora", "—")
    culto = item.get("culto", "—")
    # ❌ Culto não recebia observação
```

### Agora (CORRETO):
```python
if item["dia_semana"] == "Sunday":
    meia_hora = item.get("meia_hora", "—")
    culto = item.get("culto", "—")
    
    if meia_hora == culto and meia_hora != "—":
        meia_hora = f"{meia_hora} (cobre ambos)"
        culto = meia_hora  # ✅ Repete na coluna Culto
```

---

## 📱 Se Estiver Usando VS Code Simple Browser

O Simple Browser pode cachear. Tente:

1. Fechar o Simple Browser
2. Abrir navegador externo (Chrome, Firefox, Edge)
3. Ir para `http://localhost:8080`
4. Fazer login e testar novamente

---

## 🆘 Último Recurso

Se nada funcionar, vamos rebuildar TUDO:

```bash
cd /mnt/f/rodizio

# Parar e remover tudo
docker-compose down -v

# Rebuildar do zero
docker-compose up -d --build --force-recreate

# Aguardar 5 segundos
sleep 5

# Testar
curl http://localhost:8080/health
```

Depois acesse pelo navegador normal (não Simple Browser).

---

## ✅ CHECKLIST DE VALIDAÇÃO

Após seguir os passos, o PDF deve ter:

- [ ] Coluna "Data" preenchida
- [ ] Coluna "Dia" preenchida
- [ ] Coluna "Meia-hora" preenchida com nome ou "(cobre...)"
- [ ] Coluna "Culto" preenchida com nome ou "(cobre...)"
- [ ] Para domingos: ambas as colunas com informação
- [ ] Para terças: ambas as colunas com o mesmo nome
- [ ] Tabelas separadas por mês (Outubro e Novembro)
- [ ] Cabeçalho cinza com texto branco
- [ ] Linhas alternadas (bege e branco)

---

**Se seguir estes passos e limpar o cache, o PDF estará correto!**

**Versão**: 2.1  
**Atualizado**: 14/10/2025 14:15
