from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime, timedelta
from collections import defaultdict
import json, os
import calendar
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATA_PATH = "data/db.json"

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'

# Filtros personalizados para templates (formato brasileiro)
@app.template_filter('date_br')
def format_date_br(date_string):
    """Converte ISO date (2025-10-14) para formato BR (14/10/2025)"""
    if not date_string:
        return ''
    try:
        from datetime import datetime as dt
        date_obj = dt.fromisoformat(date_string.split('T')[0])
        return date_obj.strftime('%d/%m/%Y')
    except:
        return date_string

@app.template_filter('datetime_br')
def format_datetime_br(datetime_string):
    """Converte ISO datetime para formato BR (14/10/2025 15:30)"""
    if not datetime_string:
        return ''
    try:
        from datetime import datetime as dt
        datetime_obj = dt.fromisoformat(datetime_string.replace('Z', '+00:00'))
        return datetime_obj.strftime('%d/%m/%Y %H:%M')
    except:
        return datetime_string

class User(UserMixin):
    def __init__(self, id, nome, tipo='organista', is_admin=False):
        self.id = id
        self.nome = nome
        self.tipo = tipo
        self.is_admin = is_admin
        # Compatibilidade
        self.is_coordenador = is_admin

@login_manager.user_loader
def load_user(user_id):
    db = load_db()
    
    # Verificar se é administrador
    if user_id == 'admin':
        admin = db.get('admin', {})
        return User('admin', admin.get('nome', 'Administrador'), 'admin', True)
    
    # Buscar organista
    organista = next((o for o in db['organistas'] if o['id'] == user_id), None)
    if organista:
        return User(organista['id'], organista['nome'], 'organista', False)
    
    return None

def load_db():
    if not os.path.exists(DATA_PATH):
        return {"organistas":[], "indisponibilidades":[], "escala":[], "escala_rjm":[], "logs":[], 
                "config":{"bimestre":{"inicio":"2025-10-01","fim":"2025-11-30"},
                          "fechamento_publicacao_dias":3}}
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
        # Garantir que escala_rjm existe
        if "escala_rjm" not in db:
            db["escala_rjm"] = []
        return db

def save_db(db):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

@app.get("/")
@login_required
def index():
    db = load_db()
    return render_template("index.html", cfg=db["config"], user=current_user)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = load_db()
        
        # Verificar administrador
        if username == 'admin':
            admin = db.get('admin', {})
            if admin and check_password_hash(admin.get('password_hash', ''), password):
                user = User('admin', admin.get('nome', 'Administrador'), 'admin', True)
                login_user(user, remember=True)
                return redirect(url_for('index'))
        
        # Verificar organista
        organista = next((o for o in db['organistas'] if o['id'] == username), None)
        if organista and 'password_hash' in organista:
            if check_password_hash(organista['password_hash'], password):
                user = User(organista['id'], organista['nome'], 'organista', False)
                login_user(user, remember=True)
                return redirect(url_for('index'))
        
        flash('Usuário ou senha incorretos.', 'error')
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route("/trocar-senha", methods=['GET', 'POST'])
@login_required
def trocar_senha():
    if request.method == 'POST':
        data = request.get_json()
        senha_atual = data.get('senha_atual')
        senha_nova = data.get('senha_nova')
        senha_confirmacao = data.get('senha_confirmacao')
        
        if not senha_atual or not senha_nova or not senha_confirmacao:
            return jsonify({"error": "Todos os campos são obrigatórios."}), 400
        
        if senha_nova != senha_confirmacao:
            return jsonify({"error": "A nova senha e a confirmação não coincidem."}), 400
        
        if len(senha_nova) < 6:
            return jsonify({"error": "A nova senha deve ter no mínimo 6 caracteres."}), 400
        
        db = load_db()
        
        # Verificar senha atual
        if current_user.is_admin:
            admin = db.get('admin', {})
            if not check_password_hash(admin.get('password_hash', ''), senha_atual):
                return jsonify({"error": "Senha atual incorreta."}), 403
            
            # Atualizar senha do admin
            db['admin']['password_hash'] = generate_password_hash(senha_nova)
        else:
            # Organista
            organista = next((o for o in db['organistas'] if o['id'] == current_user.id), None)
            if not organista:
                return jsonify({"error": "Usuário não encontrado."}), 404
            
            if not check_password_hash(organista.get('password_hash', ''), senha_atual):
                return jsonify({"error": "Senha atual incorreta."}), 403
            
            # Atualizar senha do organista
            organista['password_hash'] = generate_password_hash(senha_nova)
        
        # Log da ação
        db["logs"].append({
            "quando": datetime.utcnow().isoformat(),
            "acao": "trocar_senha",
            "por": current_user.id
        })
        
        save_db(db)
        
        return jsonify({"ok": True, "message": "Senha alterada com sucesso!"})
    
    return render_template("trocar_senha.html")

@app.get("/organistas")
@login_required
def list_organistas():
    db = load_db()
    # Remover password_hash antes de enviar
    organistas = [{k: v for k, v in o.items() if k != 'password_hash'} for o in db["organistas"]]
    return jsonify(organistas)

@app.post("/organistas")
@login_required
def add_organista():
    # Apenas administrador pode adicionar
    if not current_user.is_admin:
        return jsonify({"error": "Apenas o administrador pode adicionar organistas."}), 403
    
    db = load_db()
    payload = request.get_json()
    # payload esperado: {"id":"...", "nome":"...", "tipos":[], "dias_permitidos":[], "regras_especiais":{}, "password":"..."}
    
    # Verifica duplicata
    if any(o["id"] == payload["id"] for o in db["organistas"]):
        return jsonify({"error": "Organista com esse ID já existe."}), 400
    
    # Hash da senha
    if 'password' in payload:
        payload['password_hash'] = generate_password_hash(payload['password'])
        del payload['password']
    else:
        # Senha padrão se não fornecida
        payload['password_hash'] = generate_password_hash('123456')
    
    db["organistas"].append(payload)
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "add_organista",
        "por": current_user.id,
        "payload": {k: v for k, v in payload.items() if k != 'password_hash'}
    })
    save_db(db)
    
    # Remover password_hash antes de retornar
    response_payload = {k: v for k, v in payload.items() if k != 'password_hash'}
    return jsonify({"ok": True, "organista": response_payload})

@app.put("/organistas/<org_id>")
@login_required
def update_organista(org_id):
    # Apenas administrador pode editar
    if not current_user.is_admin:
        return jsonify({"error": "Apenas o administrador pode editar organistas."}), 403
    
    db = load_db()
    payload = request.get_json()
    
    organista = next((o for o in db["organistas"] if o["id"] == org_id), None)
    if not organista:
        return jsonify({"error": "Organista não encontrado."}), 404
    
    # Se tiver nova senha, fazer hash
    if 'password' in payload:
        payload['password_hash'] = generate_password_hash(payload['password'])
        del payload['password']
    
    organista.update(payload)
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "update_organista",
        "por": current_user.id,
        "payload": {"id": org_id, "changes": {k: v for k, v in payload.items() if k != 'password_hash'}}
    })
    save_db(db)
    
    # Remover password_hash antes de retornar
    response = {k: v for k, v in organista.items() if k != 'password_hash'}
    return jsonify({"ok": True, "organista": response})

@app.delete("/organistas/<org_id>")
@login_required
def delete_organista(org_id):
    # Apenas administrador pode remover
    if not current_user.is_admin:
        return jsonify({"error": "Apenas o administrador pode remover organistas."}), 403
    
    db = load_db()
    before = len(db["organistas"])
    db["organistas"] = [o for o in db["organistas"] if o["id"] != org_id]
    after = len(db["organistas"])
    
    if before == after:
        return jsonify({"error": "Organista não encontrado."}), 404
    
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "delete_organista",
        "por": current_user.id,
        "payload": {"id": org_id}
    })
    save_db(db)
    return jsonify({"ok": True})

@app.get("/indisponibilidades")
@login_required
def list_indisp():
    db = load_db()
    
    # Se for organista, só vê suas próprias
    if not current_user.is_admin:
        items = [i for i in db["indisponibilidades"] if i["id"] == current_user.id]
    else:
        # Admin pode filtrar por organista ou ver todas
        organista = request.args.get("id")
        items = [i for i in db["indisponibilidades"] if (not organista or i["id"]==organista)]
    
    return jsonify(items)

@app.post("/indisponibilidades")
@login_required
def add_indisp():
    db = load_db()
    payload = request.get_json()
    
    # Organista só pode marcar para si mesmo, admin pode marcar para qualquer um
    if not current_user.is_admin:
        payload["id"] = current_user.id
    elif "id" not in payload:
        return jsonify({"error": "ID da organista é obrigatório para administrador."}), 400
    
    # payload esperado: {"data":"2025-10-05","motivo":"..."}
    # valida período configurado
    d = payload["data"]
    ini = db["config"]["bimestre"]["inicio"]
    fim = db["config"]["bimestre"]["fim"]
    if not (ini <= d <= fim):
        return jsonify({"error":"Data fora do período configurado."}), 400
    
    payload["autor"] = current_user.id
    
    # upsert simples (impede duplicata)
    dup = next((x for x in db["indisponibilidades"] if x["id"]==payload["id"] and x["data"]==d), None)
    if dup:
        dup.update(payload)
        dup["status"] = dup.get("status","confirmada")
    else:
        payload["status"] = "confirmada"
        db["indisponibilidades"].append(payload)
    
    db["logs"].append({
        "quando":datetime.utcnow().isoformat(), 
        "acao":"add_indisponibilidade", 
        "por":current_user.id, 
        "payload":payload
    })
    save_db(db)
    return jsonify({"ok":True})

@app.delete("/indisponibilidades/<org_id>/<data_iso>")
@login_required
def del_indisp(org_id, data_iso):
    # Organista só pode remover suas próprias, admin pode remover qualquer uma
    if not current_user.is_admin and org_id != current_user.id:
        return jsonify({"error":"Você só pode remover suas próprias indisponibilidades."}), 403
    
    db = load_db()
    before = len(db["indisponibilidades"])
    db["indisponibilidades"] = [i for i in db["indisponibilidades"] if not (i["id"]==org_id and i["data"]==data_iso)]
    after = len(db["indisponibilidades"])
    
    if before == after:
        return jsonify({"error":"Não encontrado"}), 404
    
    db["logs"].append({
        "quando":datetime.utcnow().isoformat(), 
        "acao":"del_indisponibilidade", 
        "por":current_user.id, 
        "payload":{"id":org_id,"data":data_iso}
    })
    save_db(db)
    return jsonify({"ok":True})

@app.get("/admin/indisponibilidades/todas")
@login_required
def admin_all_indisp():
    """Admin vê todas indisponibilidades organizadas por organista"""
    if not current_user.is_admin:
        return jsonify({"error": "Acesso negado"}), 403
    
    db = load_db()
    # Agrupar por organista
    result = {}
    for indisp in db["indisponibilidades"]:
        org_id = indisp["id"]
        if org_id not in result:
            organista = next((o for o in db["organistas"] if o["id"] == org_id), None)
            result[org_id] = {
                "nome": organista["nome"] if organista else org_id,
                "indisponibilidades": []
            }
        result[org_id]["indisponibilidades"].append(indisp)
    
    return jsonify(result)

@app.get("/admin/config")
@login_required
def get_config():
    """Retorna configurações do sistema"""
    if not current_user.is_admin:
        return jsonify({"error": "Acesso negado"}), 403
    
    db = load_db()
    return jsonify(db["config"])

@app.put("/admin/config")
@login_required
def update_config():
    """Admin atualiza configurações do sistema"""
    if not current_user.is_admin:
        return jsonify({"error": "Acesso negado"}), 403
    
    db = load_db()
    payload = request.get_json()
    
    db["config"].update(payload)
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "update_config",
        "por": current_user.id,
        "payload": payload
    })
    save_db(db)
    
    return jsonify({"ok": True, "config": db["config"]})

def gerar_escala_automatica(db):
    """
    Algoritmo de geração de escala bimestral
    Retorna lista de alocações com log de decisões
    """
    config = db["config"]
    inicio = datetime.fromisoformat(config["bimestre"]["inicio"])
    fim = datetime.fromisoformat(config["bimestre"]["fim"])
    organistas = db["organistas"]
    indisponibilidades = {(i["id"], i["data"]) for i in db["indisponibilidades"]}
    
    escala = []
    logs_decisao = []
    
    # Contadores para justiça na distribuição
    contador_meia_hora = defaultdict(int)
    contador_culto = defaultdict(int)
    contador_terca = defaultdict(int)
    
    # Gerar todas as datas do período (Domingos e Terças)
    current_date = inicio
    while current_date <= fim:
        dia_semana = current_date.weekday()
        
        # Domingo (6) ou Terça (1)
        if dia_semana == 6:  # Domingo
            escala_dia = gerar_alocacao_domingo(
                current_date, organistas, indisponibilidades, 
                contador_meia_hora, contador_culto, logs_decisao
            )
            if escala_dia:
                escala.append(escala_dia)
                
        elif dia_semana == 1:  # Terça
            escala_dia = gerar_alocacao_terca(
                current_date, organistas, indisponibilidades,
                contador_terca, logs_decisao
            )
            if escala_dia:
                escala.append(escala_dia)
        
        current_date += timedelta(days=1)
    
    return escala, logs_decisao

def gerar_alocacao_domingo(data, organistas, indisponibilidades, contador_meia_hora, contador_culto, logs):
    """Aloca organistas para um domingo (Meia-hora + Culto)"""
    data_str = data.strftime('%Y-%m-%d')
    dia = data.day
    mes = data.month
    
    # Candidatos para Meia-hora
    candidatos_mh = []
    for org in organistas:
        if "Domingo" not in org["dias_permitidos"]:
            continue
        if "Meia-hora" not in org["tipos"]:
            continue
        if (org["id"], data_str) in indisponibilidades:
            logs.append(f"{data_str}: {org['nome']} indisponível (meia-hora)")
            continue
        
        # Verificar regras especiais
        if not validar_regras_especiais(org, data, "Meia-hora"):
            logs.append(f"{data_str}: {org['nome']} não atende regra especial")
            continue
            
        candidatos_mh.append(org)
    
    # Candidatos para Culto
    candidatos_culto = []
    for org in organistas:
        if "Domingo" not in org["dias_permitidos"]:
            continue
        if "Culto" not in org["tipos"]:
            continue
        if (org["id"], data_str) in indisponibilidades:
            logs.append(f"{data_str}: {org['nome']} indisponível (culto)")
            continue
            
        if not validar_regras_especiais(org, data, "Culto"):
            continue
            
        candidatos_culto.append(org)
    
    # Ordenar por quem tocou menos (justiça)
    candidatos_mh.sort(key=lambda o: contador_meia_hora[o["id"]])
    candidatos_culto.sort(key=lambda o: contador_culto[o["id"]])
    
    meia_hora = None
    culto = None
    
    # Alocar Meia-hora
    org_meia_hora = None
    if candidatos_mh:
        org_meia_hora = candidatos_mh[0]
        meia_hora = org_meia_hora["nome"]  # Usar nome ao invés de ID
        contador_meia_hora[org_meia_hora["id"]] += 1
        logs.append(f"{data_str}: {org_meia_hora['nome']} → Meia-hora (tocou {contador_meia_hora[org_meia_hora['id']]}x)")
    else:
        logs.append(f"{data_str}: ⚠️ NENHUM candidato para Meia-hora!")
    
    # Alocar Culto
    org_culto = None
    if candidatos_culto:
        org_culto = candidatos_culto[0]
        culto = org_culto["nome"]  # Usar nome ao invés de ID
        contador_culto[org_culto["id"]] += 1
        logs.append(f"{data_str}: {org_culto['nome']} → Culto (tocou {contador_culto[org_culto['id']]}x)")
    else:
        logs.append(f"{data_str}: ⚠️ NENHUM candidato para Culto!")
    
    # RN05: Se não há meia-hora, quem está no culto cobre (SE puder tocar meia-hora também)
    if not meia_hora and culto and org_culto:
        # Só cobre se a pessoa do culto TAMBÉM pode tocar meia-hora
        if "Meia-hora" in org_culto["tipos"]:
            meia_hora = culto
            logs.append(f"{data_str}: ℹ️ Culto cobre Meia-hora (RN05)")
        else:
            logs.append(f"{data_str}: ⚠️ Culto NÃO pode cobrir Meia-hora (não habilitado para esta fase)")
    
    # RN06: Se não há culto, quem está na meia-hora cobre (SE puder tocar culto também)
    if not culto and meia_hora and org_meia_hora:
        # Só cobre se a pessoa da meia-hora TAMBÉM pode tocar culto
        if "Culto" in org_meia_hora["tipos"]:
            culto = meia_hora
            logs.append(f"{data_str}: ℹ️ Meia-hora cobre Culto (RN06)")
        else:
            logs.append(f"{data_str}: ⚠️ Meia-hora NÃO pode cobrir Culto (não habilitado para esta fase)")
    
    return {
        "data": data_str,
        "dia_semana": "Domingo",
        "meia_hora": meia_hora,
        "culto": culto
    }

def gerar_alocacao_terca(data, organistas, indisponibilidades, contador_terca, logs):
    """Aloca organista para uma terça (uma pessoa cobre ambos)"""
    data_str = data.strftime('%Y-%m-%d')
    
    candidatos = []
    for org in organistas:
        if "Terça" not in org["dias_permitidos"]:
            continue
        # Precisa poder tocar ambos
        if "Meia-hora" not in org["tipos"] or "Culto" not in org["tipos"]:
            continue
        if (org["id"], data_str) in indisponibilidades:
            logs.append(f"{data_str}: {org['nome']} indisponível (terça)")
            continue
            
        if not validar_regras_especiais(org, data, "Terça"):
            continue
            
        candidatos.append(org)
    
    # Ordenar por justiça
    candidatos.sort(key=lambda o: contador_terca[o["id"]])
    
    if candidatos:
        escolhido = candidatos[0]
        contador_terca[escolhido["id"]] += 1
        logs.append(f"{data_str}: {escolhido['nome']} → Terça (tocou {contador_terca[escolhido['id']]}x)")
        
        return {
            "data": data_str,
            "dia_semana": "Terça",
            "unica": escolhido["nome"]  # Usar nome ao invés de ID
        }
    else:
        logs.append(f"{data_str}: ⚠️ NENHUM candidato para Terça!")
        return {
            "data": data_str,
            "dia_semana": "Terça",
            "unica": None
        }

def validar_regras_especiais(organista, data, tipo):
    """Valida regras especiais da organista para a data"""
    regras = organista.get("regras_especiais", {})
    dia = data.day
    mes = data.month
    
    # Ieda: domingos ímpares em outubro, pares em novembro
    if "domingo_outubro_impares" in regras and regras["domingo_outubro_impares"]:
        if mes == 10 and dia % 2 == 0:  # Par em outubro
            return False
    
    if "domingo_novembro_pares" in regras and regras["domingo_novembro_pares"]:
        if mes == 11 and dia % 2 != 0:  # Ímpar em novembro
            return False
    
    # Adicione mais regras conforme necessário
    
    return True

# ROTA DE GERAÇÃO AUTOMÁTICA REMOVIDA - Sistema agora é 100% manual
# @app.post("/escala/gerar")
# @login_required
# def gerar_escala():
#     """Gera preview da escala (não salva)"""
#     if not current_user.is_admin:
#         return jsonify({"error": "Apenas administrador pode gerar escala."}), 403
#     
#     db = load_db()
#     
#     try:
#         escala, logs = gerar_escala_automatica(db)
#         stats = calcular_estatisticas(escala, db["organistas"])
#         
#         return jsonify({
#             "ok": True,
#             "escala": escala,
#             "logs": logs,
#             "estatisticas": stats["por_organista"]
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.post("/escala/publicar")
@login_required
def publicar_escala():
    """Publica a escala (salva definitivamente)"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas administrador pode publicar escala."}), 403
    
    db = load_db()
    payload = request.get_json()
    
    # Validar escala
    escala = payload.get("escala", [])
    if not escala:
        return jsonify({"error": "Escala vazia."}), 400
    
    # Salvar escala
    db["escala"] = escala
    db["escala_publicada_em"] = datetime.utcnow().isoformat()
    db["escala_publicada_por"] = current_user.id
    
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "publicar_escala",
        "por": current_user.id,
        "payload": {"total_dias": len(escala)}
    })
    
    save_db(db)
    
    return jsonify({"ok": True, "message": "Escala publicada com sucesso!"})

@app.get("/escala/atual")
@login_required
def obter_escala():
    """Retorna a escala atual publicada"""
    db = load_db()
    escala = db.get("escala", [])
    
    if not escala:
        return jsonify({
            "escala": [],
            "estatisticas": {}
        })
    
    stats = calcular_estatisticas(escala, db["organistas"])
    
    return jsonify({
        "escala": escala,
        "publicada_em": db.get("escala_publicada_em"),
        "publicada_por": db.get("escala_publicada_por"),
        "estatisticas": stats["por_organista"]
    })

@app.put("/escala/editar/<data_iso>")
@login_required
def editar_dia_escala(data_iso):
    """Permite editar alocação de um dia específico"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas administrador pode editar escala."}), 403
    
    db = load_db()
    payload = request.get_json()
    alocacao = payload.get("alocacao", payload)  # Aceita ambos formatos
    
    # Encontrar o dia na escala
    dia = next((d for d in db["escala"] if d["data"] == data_iso), None)
    if not dia:
        return jsonify({"error": "Data não encontrada na escala."}), 404
    
    # Atualizar alocações
    if "meia_hora" in alocacao:
        dia["meia_hora"] = alocacao["meia_hora"]
    if "culto" in alocacao:
        dia["culto"] = alocacao["culto"]
    if "unica" in alocacao:
        dia["unica"] = alocacao["unica"]
    
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "editar_escala",
        "por": current_user.id,
        "payload": {"data": data_iso, "alteracoes": payload}
    })
    
    save_db(db)
    
    return jsonify({"ok": True, "dia": dia})

def calcular_estatisticas(escala, organistas):
    """Calcula estatísticas da escala"""
    stats = {
        "total_dias": len(escala),
        "domingos": sum(1 for d in escala if d["dia_semana"] == "Domingo"),
        "tercas": sum(1 for d in escala if d["dia_semana"] == "Terça"),
        "por_organista": {}
    }
    
    # Contar por organista
    for org in organistas:
        org_id = org["id"]
        stats["por_organista"][org_id] = {
            "nome": org["nome"],
            "meia_hora": 0,
            "culto": 0,
            "terca": 0,
            "total": 0
        }
    
    for dia in escala:
        if dia["dia_semana"] == "Domingo":
            if dia.get("meia_hora") and dia["meia_hora"] in stats["por_organista"]:
                stats["por_organista"][dia["meia_hora"]]["meia_hora"] += 1
                stats["por_organista"][dia["meia_hora"]]["total"] += 1
            
            if dia.get("culto") and dia["culto"] in stats["por_organista"]:
                stats["por_organista"][dia["culto"]]["culto"] += 1
                stats["por_organista"][dia["culto"]]["total"] += 1
        
        elif dia["dia_semana"] == "Terça":
            if dia.get("unica") and dia["unica"] in stats["por_organista"]:
                stats["por_organista"][dia["unica"]]["terca"] += 1
                stats["por_organista"][dia["unica"]]["total"] += 1
    
    return stats

@app.get("/escala/pdf")
@login_required
def exportar_escala_pdf():
    """Exporta a escala em formato PDF"""
    try:
        db = load_db()
        escala = db.get("escala", [])
        
        if not escala:
            return jsonify({"erro": "Nenhuma escala publicada"}), 404
        
        # Criar PDF em memória
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                              rightMargin=1*cm, leftMargin=1*cm,
                              topMargin=1*cm, bottomMargin=1*cm)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Obter período
        primeira_data = datetime.strptime(escala[0]["data"], '%Y-%m-%d')
        ultima_data = datetime.strptime(escala[-1]["data"], '%Y-%m-%d')
        
        title = Paragraph(
            f"Rodízio de Organistas - Vila Paula<br/>(Outubro e Novembro {primeira_data.year})",
            title_style
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Agrupar por mês
        escala_por_mes = {}
        meses_nome = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        dias_semana = {
            'Sunday': 'Domingo',
            'Tuesday': 'Terça',
            'Monday': 'Segunda',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado'
        }
        
        for item in escala:
            data = datetime.strptime(item["data"], '%Y-%m-%d')
            mes_ano = f"{data.year}-{data.month:02d}"
            
            if mes_ano not in escala_por_mes:
                escala_por_mes[mes_ano] = {
                    'nome': f"{meses_nome[data.month]}/{data.year}",
                    'itens': []
                }
            escala_por_mes[mes_ano]['itens'].append(item)
        
        # Renderizar cada mês
        for mes_ano in sorted(escala_por_mes.keys()):
            mes = escala_por_mes[mes_ano]
            
            # Título do mês
            mes_style = ParagraphStyle(
                'MesTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#667eea'),
                spaceAfter=10,
                fontName='Helvetica-Bold'
            )
            elements.append(Paragraph(mes['nome'], mes_style))
            elements.append(Spacer(1, 0.3*cm))
            
            # Tabela do mês
            data_table = [['Data', 'Dia', 'Meia-hora', 'Culto']]
            
            for item in mes['itens']:
                data_obj = datetime.strptime(item["data"], '%Y-%m-%d')
                data_br = data_obj.strftime('%d/%m')
                dia = dias_semana.get(item["dia_semana"], item["dia_semana"])
                
                if item["dia_semana"] == "Sunday":
                    # DOMINGO: Duas fases separadas (Meia-hora e Culto)
                    meia_hora = item.get("meia_hora", "—")
                    culto = item.get("culto", "—")
                else:
                    # TERÇA-FEIRA: Duas fases (podem ser pessoas diferentes)
                    # Compatibilidade: tenta 'meia_hora'/'culto' primeiro, senão usa 'unica'
                    meia_hora = item.get("meia_hora") or item.get("unica", "—")
                    culto = item.get("culto") or item.get("unica", "—")
                
                data_table.append([data_br, dia, meia_hora, culto])
            
            # Estilo da tabela
            table = Table(data_table, colWidths=[3*cm, 3.5*cm, 7*cm, 7*cm])
            table.setStyle(TableStyle([
                # Cabeçalho
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#808080')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Corpo
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('LEFTPADDING', (0, 1), (-1, -1), 8),
                ('RIGHTPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                
                # Grades
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Linhas alternadas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white]),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.8*cm))
        
        # Gerar PDF
        doc.build(elements)
        buffer.seek(0)
        
        # Retornar PDF
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=Rodizio_Organistas_{primeira_data.strftime("%Y%m")}.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ========== ENDPOINTS RJM ==========

@app.post("/rjm/criar-vazia")
@login_required
def criar_escala_rjm_vazia():
    """Cria escala RJM vazia com todos os domingos do período"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas administrador pode criar escala RJM."}), 403
    
    db = load_db()
    config = db.get("config", {})
    
    inicio = datetime.fromisoformat(config["bimestre"]["inicio"])
    fim = datetime.fromisoformat(config["bimestre"]["fim"])
    
    # Gerar todos os domingos do período
    escala_rjm = []
    current_date = inicio
    contador_id = 1
    
    while current_date <= fim:
        dia_semana = current_date.weekday()
        
        # Apenas domingos (weekday 6)
        if dia_semana == 6:
            escala_rjm.append({
                "id": f"rjm_{contador_id}",
                "data": current_date.isoformat().split('T')[0],
                "dia_semana": "Sunday",
                "organista": ""
            })
            contador_id += 1
        
        current_date += timedelta(days=1)
    
    db["escala_rjm"] = escala_rjm
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "criar_escala_rjm_vazia",
        "quem": current_user.id,
        "total_domingos": len(escala_rjm)
    })
    
    save_db(db)
    return jsonify({"message": f"Escala RJM criada com {len(escala_rjm)} domingos.", "total": len(escala_rjm)}), 200

@app.get("/rjm/atual")
@login_required
def get_escala_rjm():
    """Retorna a escala RJM atual"""
    db = load_db()
    return jsonify({"escala_rjm": db.get("escala_rjm", [])}), 200

@app.post("/rjm/atualizar-multiplos")
@login_required
def atualizar_escala_rjm_multiplos():
    """Atualiza múltiplas linhas da escala RJM de uma vez"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas administrador pode atualizar escala RJM."}), 403
    
    db = load_db()
    payload = request.get_json()
    alteracoes = payload.get("alteracoes", [])
    
    if not alteracoes:
        return jsonify({"error": "Nenhuma alteração fornecida."}), 400
    
    contador_atualizados = 0
    for alt in alteracoes:
        item_id = alt.get("id")
        organista = alt.get("organista", "")
        
        # Encontrar e atualizar o item
        for item in db.get("escala_rjm", []):
            if item["id"] == item_id:
                item["organista"] = organista
                contador_atualizados += 1
                break
    
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "atualizar_escala_rjm_multiplos",
        "quem": current_user.id,
        "total_alteracoes": contador_atualizados
    })
    
    save_db(db)
    return jsonify({"message": f"{contador_atualizados} itens atualizados com sucesso."}), 200

@app.get("/rjm/pdf")
@login_required
def exportar_pdf_rjm():
    """Exporta a escala RJM em PDF"""
    db = load_db()
    escala_rjm = db.get("escala_rjm", [])
    
    if not escala_rjm:
        return jsonify({"error": "Nenhuma escala RJM para exportar."}), 404
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    title = Paragraph("Escala RJM - Reunião de Jovens e Menores", title_style)
    elements.append(title)
    
    subtitle = Paragraph("Vila Paula - Domingos 10:00", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Agrupar por mês
    meses = defaultdict(list)
    for item in escala_rjm:
        data = datetime.fromisoformat(item["data"])
        mes_ano = data.strftime("%B %Y")
        meses[mes_ano].append(item)
    
    # Criar tabela para cada mês
    for mes_ano, itens in meses.items():
        elements.append(Paragraph(f"<b>{mes_ano.upper()}</b>", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Dados da tabela
        table_data = [['Data', 'Dia', 'Organista']]
        
        for item in itens:
            data = datetime.fromisoformat(item["data"])
            data_formatada = data.strftime("%d/%m/%Y")
            organista = item.get("organista", "-")
            
            table_data.append([
                data_formatada,
                "Domingo",
                organista
            ])
        
        # Criar tabela
        table = Table(table_data, colWidths=[3*cm, 3*cm, 8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
    
    # Gerar PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer.getvalue(), 200, {
        'Content-Type': 'application/pdf',
        'Content-Disposition': f'attachment; filename=escala_rjm_{datetime.now().strftime("%Y%m%d")}.pdf'
    }

@app.get("/health")
def health_check():
    """Endpoint para healthcheck do Docker"""
    try:
        db = load_db()
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "organistas_count": len(db.get("organistas", [])),
            "indisponibilidades_count": len(db.get("indisponibilidades", []))
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
