# 🎹 Como Funciona o Sistema de Rodízio - Explicação Completa

## 📋 Resumo Executivo

O sistema gerencia a escala de organistas dividindo cada culto em **duas fases distintas**:

1. **Meia-hora** → Música antes do início do culto (30 minutos)
2. **Culto** → Música durante o culto principal

---

## 🧩 Lógica de Funcionamento

### 1️⃣ **Geração do Calendário**

O sistema gera automaticamente todas as datas do bimestre:
- **Domingos** → Duas fases (Meia-hora + Culto)
- **Terças-feiras** → Uma organista cobre as duas fases

**Exemplo**:
```
Outubro 2025:
- 05/10 (Domingo) → 2 posições
- 07/10 (Terça) → 1 posição (cobre ambas)
- 12/10 (Domingo) → 2 posições
- 14/10 (Terça) → 1 posição (cobre ambas)
...
```

---

### 2️⃣ **Identificação do Tipo de Dia**

**DOMINGO**:
- ✅ **Meia-hora**: Uma organista
- ✅ **Culto**: Pode ser a mesma ou outra organista
- **Total**: 2 posições (podem ser 1 ou 2 pessoas)

**TERÇA-FEIRA**:
- ✅ **Meia-hora + Culto**: A mesma organista cobre ambas
- **Total**: 1 posição

---

### 3️⃣ **Filtragem de Candidatas**

Para cada fase (Meia-hora ou Culto), o sistema verifica:

#### ✅ Critério 1: Dia da Semana
- Organista pode tocar nesse dia? (Domingo ou Terça)
- **Exemplo**: Raquel só toca domingos (não aparece para terças)

#### ✅ Critério 2: Tipo de Fase
- Organista toca nessa fase?
  - **Meia-hora** → Precisa ter "Meia-hora" nos tipos
  - **Culto** → Precisa ter "Culto" nos tipos
  - **Ambas** → Tem tanto "Meia-hora" quanto "Culto"

**Exemplo**:
```
Yasmin G. → Só toca "Meia-hora"
Raquel → Toca "Meia-hora" e "Culto"
Ieda → Toca "Meia-hora" e "Culto"
```

#### ✅ Critério 3: Indisponibilidade
- Organista marcou que **NÃO** pode naquela data?
- **Bloqueio automático**: Se marcou indisponível, não é escalada

#### ✅ Critério 4: Regras Especiais
- **Ieda**: Domingos ímpares em outubro (5, 7, 19, 21, 27...)
- **Ieda**: Domingos pares em novembro (2, 16, 30...)
- Outras regras customizadas por organista

---

### 4️⃣ **Aplicação da Lógica de Justiça**

O sistema garante **distribuição equilibrada**:

1. **Conta** quantas vezes cada organista já foi escalada no bimestre
2. **Prioriza** quem tocou menos até agora
3. **Equilibra** para que todas participem de forma justa

**Exemplo de contador**:
```
Início do bimestre:
Ieda: 0 alocações
Raquel: 0 alocações
Milena: 0 alocações
Yasmin G.: 0 alocações

Após 1ª semana:
Ieda: 3 (Meia-hora dom + Culto dom + Terça)
Raquel: 0
Milena: 0
Yasmin G.: 0

→ Próximas alocações: prioriza Raquel, Milena ou Yasmin
```

---

### 5️⃣ **Seleção para Cada Fase**

#### **Para DOMINGOS**:

**Fase 1 - Meia-hora**:
1. Filtra candidatas que podem tocar Meia-hora
2. Remove indisponíveis
3. Aplica regras especiais
4. Ordena por quem tocou menos
5. **Escolhe a primeira** da lista

**Fase 2 - Culto**:
1. Filtra candidatas que podem tocar Culto
2. Remove indisponíveis
3. Aplica regras especiais
4. Ordena por quem tocou menos
5. **Escolhe a primeira** da lista
6. **Pode ser a mesma** da Meia-hora se for a mais justa

**Resultado possível**:
- **Caso 1**: Duas pessoas diferentes
  ```
  Meia-hora: Yasmin G.
  Culto: Raquel
  ```

- **Caso 2**: A mesma pessoa nas duas
  ```
  Meia-hora: Ieda (cobre ambos)
  Culto: Ieda
  ```

#### **Para TERÇAS-FEIRAS**:

1. Filtra candidatas que podem tocar **AMBAS** as fases
2. Remove indisponíveis
3. Aplica regras especiais
4. Ordena por quem tocou menos
5. **Escolhe uma** para cobrir as duas

**Resultado**:
```
Terça-feira:
Meia-hora: Milena (cobre os 2)
Culto: Milena
```

---

### 6️⃣ **Regra de Fallback (Emergência)**

**Situação**: Não há ninguém disponível para a Meia-hora

**Ação**: Sistema automaticamente **repete** a organista do Culto

**Exemplo**:
```
Cenário: Todas indisponíveis para Meia-hora, mas Raquel pode Culto

Resultado:
Meia-hora: Raquel (cobre ambos)
Culto: Raquel
```

---

## ⚖️ Resumo da Lógica em 5 Pontos

1. **Monta o calendário** com todas as datas (Domingos + Terças)

2. **Define o tipo**:
   - Domingo = 2 fases separadas
   - Terça = 1 pessoa cobre as 2

3. **Filtra quem pode**:
   - Dia permitido? ✅
   - Fase permitida? ✅
   - Disponível? ✅
   - Regras especiais OK? ✅

4. **Escolhe com justiça**:
   - Prioriza quem tocou menos
   - Equilibra ao longo do bimestre

5. **Gera a escala**:
   - Duas colunas: Meia-hora | Culto
   - Pode ser mesma pessoa ou não
   - Sempre respeitando regras e disponibilidade

---

## 📊 Exemplo Prático

### Cenário: Domingo 05/10/2025

**Organistas cadastradas**:
- Ieda (Meia-hora + Culto, Domingo + Terça) - Regra: dias ímpares out
- Raquel (Meia-hora + Culto, Domingo) - Regra: só domingos
- Milena (Meia-hora + Culto, Domingo + Terça)
- Yasmin G. (Meia-hora, Domingo)

**Processo**:

#### Fase 1 - Meia-hora:
```
Candidatas possíveis:
✅ Ieda (pode Meia-hora, domingo, dia ímpar OK, 0 alocações)
✅ Raquel (pode Meia-hora, domingo, 0 alocações)
✅ Milena (pode Meia-hora, domingo, 0 alocações)
✅ Yasmin G. (pode Meia-hora, domingo, 0 alocações)

Ordenação por justiça (todas com 0):
Escolhe primeira: Ieda

→ Meia-hora: Ieda
```

#### Fase 2 - Culto:
```
Candidatas possíveis:
❌ Ieda (já alocada, agora tem 1)
✅ Raquel (pode Culto, domingo, 0 alocações)
✅ Milena (pode Culto, domingo, 0 alocações)

Ordenação por justiça:
Escolhe primeira: Raquel

→ Culto: Raquel
```

**Resultado final**:
```
05/10 - Domingo
Meia-hora: Ieda
Culto: Raquel
```

---

## 🎯 Garantias do Sistema

✅ **Equilíbrio**: Todas tocam aproximadamente o mesmo número de vezes  
✅ **Respeito**: Indisponibilidades são sempre respeitadas  
✅ **Regras**: Regras especiais aplicadas automaticamente  
✅ **Justiça**: Sem favoritismo, ordenação sempre por contador  
✅ **Transparência**: Logs mostram cada decisão tomada  
✅ **Flexibilidade**: Admin pode ajustar manualmente depois  

---

## 📈 Estatísticas ao Final do Bimestre

O sistema calcula e mostra:

```
Ieda:
- Meia-hora: 3x
- Culto: 3x
- Terça: 4x
- Total: 10 alocações

Raquel:
- Meia-hora: 2x
- Culto: 3x
- Terça: 0x (não toca terças)
- Total: 5 alocações

Milena:
- Meia-hora: 2x
- Culto: 3x
- Terça: 4x
- Total: 9 alocações

Yasmin G.:
- Meia-hora: 2x
- Culto: 0x (não toca culto)
- Terça: 0x (não toca terças)
- Total: 2 alocações
```

---

## 🔄 Fluxo Completo

```
1. Admin configura bimestre (01/10 a 30/11)
   ↓
2. Organistas marcam indisponibilidades
   ↓
3. Admin clica "Gerar Escala"
   ↓
4. Sistema processa:
   - Cria calendário
   - Para cada data:
     * Filtra candidatas
     * Aplica regras
     * Escolhe por justiça
   ↓
5. Mostra preview com logs
   ↓
6. Admin revisa e pode editar
   ↓
7. Admin publica
   ↓
8. Organistas visualizam escala
   ↓
9. Admin pode exportar PDF
```

---

**Sistema garante**: Duas fases por culto, seleção justa, respeito às regras e distribuição equilibrada ao longo de todo o bimestre! 🎉

**Versão**: 2.1  
**Atualizado**: Outubro 2025
