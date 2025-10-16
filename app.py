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
import uuid

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
    def __init__(self, id, nome, tipo='organista', nivel='comum', contexto_id=None, is_admin=False):
        self.id = id
        self.nome = nome
        self.tipo = tipo  # master, admin_regional, encarregado_sub_regional, encarregado_comum, organista
        self.nivel = nivel  # sistema, regional, sub_regional, comum
        self.contexto_id = contexto_id  # ID da regional/sub-regional/comum
        
        # Propriedades de permissão
        self.is_master = (tipo == 'master')
        self.is_admin_regional = (tipo == 'admin_regional')
        self.is_encarregado_sub = (tipo == 'encarregado_sub_regional')
        self.is_encarregado_comum = (tipo == 'encarregado_comum')
        self.is_organista = (tipo == 'organista')
        
        # Compatibilidade com código antigo
        self.is_admin = is_admin or self.is_master or self.is_admin_regional or self.is_encarregado_sub or self.is_encarregado_comum
        self.is_coordenador = self.is_admin

@login_manager.user_loader
def load_user(user_id):
    db = load_db()
    
    # Verificar se é usuário do sistema (master, admins regionais, etc)
    usuarios_sistema = db.get('usuarios', {})
    if user_id in usuarios_sistema:
        usuario = usuarios_sistema[user_id]
        print(f"🔐 [LOAD_USER] Usuário do sistema: {user_id} (tipo: {usuario['tipo']})")
        return User(
            usuario['id'],
            usuario['nome'],
            usuario['tipo'],
            usuario.get('nivel', 'sistema'),
            usuario.get('contexto_id'),  # Corrigido: usar contexto_id direto
            usuario.get('tipo') in ['master', 'admin_regional', 'encarregado_sub_regional', 'encarregado_comum']
        )
    
    # RETROCOMPATIBILIDADE: Suportar admin antigo
    if user_id == 'admin':
        admin = db.get('admin', {})
        if admin:
            return User('admin', admin.get('nome', 'Administrador'), 'master', 'sistema', None, True)
    
    # Buscar organista em todas as comuns
    organista_data = find_organista_in_all_comuns(db, user_id)
    if organista_data:
        print(f"🎹 [LOAD_USER] Organista encontrada: {user_id} - is_admin será FALSE")
        user_obj = User(
            organista_data['organista']['id'],
            organista_data['organista']['nome'],
            'organista',
            'comum',
            organista_data['comum_id'],
            False
        )
        print(f"   Verificação: is_admin={user_obj.is_admin}, tipo={user_obj.tipo}")
        return user_obj
    
    print(f"❌ [LOAD_USER] Usuário não encontrado: {user_id}")
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

# ========== FUNÇÕES AUXILIARES PARA NAVEGAÇÃO HIERÁRQUICA ==========

def get_regional(db, regional_id):
    """Retorna uma regional específica"""
    return db.get('regionais', {}).get(regional_id)

def get_sub_regional(db, regional_id, sub_regional_id):
    """Retorna uma sub-regional específica"""
    regional = get_regional(db, regional_id)
    if not regional:
        return None
    return regional.get('sub_regionais', {}).get(sub_regional_id)

def get_comum(db, regional_id, sub_regional_id, comum_id):
    """Retorna uma comum específica"""
    sub_regional = get_sub_regional(db, regional_id, sub_regional_id)
    if not sub_regional:
        return None
    return sub_regional.get('comuns', {}).get(comum_id)

def find_comum_by_id(db, comum_id):
    """Busca uma comum por ID em toda a hierarquia"""
    for regional_id, regional in db.get('regionais', {}).items():
        for sub_regional_id, sub_regional in regional.get('sub_regionais', {}).items():
            for cid, comum in sub_regional.get('comuns', {}).items():
                # Comparar tanto a chave quanto o ID interno (para compatibilidade)
                if cid == comum_id or comum.get('id') == comum_id:
                    return {
                        'comum': comum,
                        'regional_id': regional_id,
                        'sub_regional_id': sub_regional_id,
                        'comum_id': cid
                    }
    return None

def find_organista_in_all_comuns(db, organista_id):
    """Busca uma organista em todas as comuns"""
    for regional_id, regional in db.get('regionais', {}).items():
        for sub_regional_id, sub_regional in regional.get('sub_regionais', {}).items():
            for comum_id, comum in sub_regional.get('comuns', {}).items():
                organista = next((o for o in comum.get('organistas', []) if o['id'] == organista_id), None)
                if organista:
                    return {
                        'organista': organista,
                        'comum_id': comum_id,
                        'sub_regional_id': sub_regional_id,
                        'regional_id': regional_id
                    }
    
    # RETROCOMPATIBILIDADE: Buscar na estrutura antiga
    if 'organistas' in db:
        organista = next((o for o in db['organistas'] if o['id'] == organista_id), None)
        if organista:
            return {
                'organista': organista,
                'comum_id': 'vila_paula',  # Assumir Vila Paula para estrutura antiga
                'sub_regional_id': 'santa_isabel',
                'regional_id': 'gru'
            }
    
    return None

def get_user_context(user):
    """Retorna o contexto (comum_id, sub_regional_id, regional_id) baseado no usuário"""
    if user.is_master:
        return None  # Master tem acesso a tudo
    
    if user.is_organista:
        return {'comum_id': user.contexto_id}
    
    if user.is_encarregado_comum:
        return {'comum_id': user.contexto_id}
    
    if user.is_encarregado_sub:
        return {'sub_regional_id': user.contexto_id}
    
    if user.is_admin_regional:
        return {'regional_id': user.contexto_id}
    
    return None

def list_all_comuns(db):
    """Lista todas as comuns do sistema"""
    comuns = []
    for regional_id, regional in db.get('regionais', {}).items():
        for sub_regional_id, sub_regional in regional.get('sub_regionais', {}).items():
            for comum_id, comum in sub_regional.get('comuns', {}).items():
                comuns.append({
                    'regional_id': regional_id,
                    'regional_nome': regional.get('nome'),
                    'sub_regional_id': sub_regional_id,
                    'sub_regional_nome': sub_regional.get('nome'),
                    'comum_id': comum_id,
                    'comum_nome': comum.get('nome'),
                    'comum': comum
                })
    return comuns

def get_comum_for_user(db, user, comum_id_param=None):
    """Retorna a comum que o usuário deve acessar"""
    # Se especificou comum_id no parâmetro, usar ele (para Master/Admin)
    if comum_id_param and user.is_master:
        return find_comum_by_id(db, comum_id_param)
    
    if user.is_master:
        # Master usa contexto da sessão ou primeira comum disponível
        comum_id = session.get('comum_id')
        if comum_id:
            result = find_comum_by_id(db, comum_id)
            if result:
                return result
        
        # Se não tem sessão, pegar primeira comum disponível
        for r_id, r_data in db.get("regionais", {}).items():
            for s_id, s_data in r_data.get("sub_regionais", {}).items():
                for c_id, c_data in s_data.get("comuns", {}).items():
                    return {
                        'comum': c_data,
                        'regional_id': r_id,
                        'sub_regional_id': s_id,
                        'comum_id': c_id
                    }
        return None
    
    if user.is_organista or user.is_encarregado_comum:
        return find_comum_by_id(db, user.contexto_id)
    
    # Admin regional/sub-regional: usar primeira comum disponível
    comuns = list_all_comuns(db)
    if comuns:
        return {
            'comum': comuns[0]['comum'],
            'comum_id': comuns[0]['comum_id'],
            'sub_regional_id': comuns[0]['sub_regional_id'],
            'regional_id': comuns[0]['regional_id']
        }
    
    return None

def get_data_from_db(db, user, data_type, comum_id=None):
    """
    Função genérica para buscar dados (escala, indisponibilidades, etc)
    Funciona com estrutura antiga e nova
    """
    if 'regionais' in db:
        comum_data = get_comum_for_user(db, user, comum_id)
        if not comum_data:
            return []
        return comum_data['comum'].get(data_type, [])
    else:
        # ESTRUTURA ANTIGA
        return db.get(data_type, [])

# ========== MIDDLEWARE DE AUTORIZAÇÃO ==========

from functools import wraps

def require_context(comum_id=None, sub_regional_id=None, regional_id=None):
    """
    Decorator para verificar se o usuário tem permissão para acessar o contexto especificado
    Master tem acesso a tudo
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Não autenticado"}), 401
            
            # Master tem acesso total
            if current_user.is_master:
                return f(*args, **kwargs)
            
            # Verificar contexto baseado no nível do usuário
            if comum_id:
                # Acesso a uma comum específica
                if current_user.is_organista or current_user.is_encarregado_comum:
                    # Buscar a comum para obter todos os IDs possíveis
                    db = load_db()
                    comum_result = find_comum_by_id(db, comum_id)
                    if comum_result:
                        comum_id_dict = comum_result['comum_id']
                        comum_id_interno = comum_result['comum'].get('id', '')
                        # Comparar com todas as variações possíveis
                        if current_user.contexto_id != comum_id and current_user.contexto_id != comum_id_dict and current_user.contexto_id != comum_id_interno:
                            return jsonify({"error": "Sem permissão para acessar esta comum"}), 403
                    else:
                        return jsonify({"error": "Comum não encontrada"}), 404
                elif current_user.is_encarregado_sub:
                    # Encarregado sub pode acessar qualquer comum da sua sub-regional
                    # Precisa verificar se a comum pertence à sua sub-regional
                    pass  # Implementar verificação se necessário
                elif current_user.is_admin_regional:
                    # Admin regional pode acessar qualquer comum da sua regional
                    pass  # Implementar verificação se necessário
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_nivel(nivel_minimo='organista'):
    """
    Decorator para verificar nível mínimo de acesso
    Hierarquia: master > admin_regional > encarregado_sub_regional > encarregado_comum > organista
    """
    niveis = {
        'organista': 1,
        'encarregado_comum': 2,
        'encarregado_sub_regional': 3,
        'admin_regional': 4,
        'master': 5
    }
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({"error": "Não autenticado"}), 401
            
            nivel_atual = niveis.get(current_user.tipo, 0)
            nivel_requerido = niveis.get(nivel_minimo, 999)
            
            if nivel_atual < nivel_requerido:
                return jsonify({"error": f"Acesso negado. Requer nível: {nivel_minimo}"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== ROTAS ==========

@app.get("/")
@login_required
def index():
    db = load_db()
    
    print(f"\n🏠 [INDEX] Carregando página inicial")
    print(f"  Usuário: {current_user.id} (tipo: {current_user.tipo})")
    if current_user.tipo == 'master':
        print(f"  Sessão Master: regional={session.get('regional_id')}, sub={session.get('sub_regional_id')}, comum={session.get('comum_id')}")
    
    # RETROCOMPATIBILIDADE: Buscar config da estrutura correta
    config = {}
    
    if 'regionais' in db:
        # NOVA ESTRUTURA: Pegar config da comum do usuário
        comum_data = get_comum_for_user(db, current_user)
        if comum_data:
            print(f"  ✅ Comum encontrada: {comum_data['comum'].get('nome')} (ID: {comum_data['comum_id']})")
            config = comum_data['comum'].get('config', {})
            # Converter 'periodo' para 'bimestre' para retrocompatibilidade com template
            if 'periodo' in config and 'bimestre' not in config:
                config['bimestre'] = config['periodo']
    else:
        # ESTRUTURA ANTIGA
        config = db.get("config", {})
    
    # Garantir que existe bimestre mesmo vazio
    if 'bimestre' not in config:
        config['bimestre'] = {
            'inicio': '2025-10-01',
            'fim': '2025-12-31'
        }
    
    import time
    return render_template("index.html", cfg=config, user=current_user, timestamp=int(time.time()))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = load_db()
        
        # RETROCOMPAT: Redirecionar "admin" para "admin_master"
        if username == 'admin':
            username = 'admin_master'
        
        # Verificar usuários do sistema (nova estrutura)
        usuarios_sistema = db.get('usuarios', {})
        if username in usuarios_sistema:
            usuario = usuarios_sistema[username]
            if check_password_hash(usuario.get('password_hash', ''), password):
                user = User(
                    usuario['id'],
                    usuario['nome'],
                    usuario['tipo'],
                    usuario.get('nivel', 'sistema'),
                    usuario.get('regional_id') or usuario.get('sub_regional_id') or usuario.get('comum_id'),
                    usuario.get('tipo') in ['master', 'admin_regional', 'encarregado_sub_regional', 'encarregado_comum']
                )
                login_user(user, remember=True)
                return redirect(url_for('index'))
        
        # RETROCOMPAT: Verificar campo "admin" antigo (se ainda existir)
        if username == 'admin_master':
            admin = db.get('admin', {})
            if admin and check_password_hash(admin.get('password_hash', ''), password):
                user = User('admin_master', admin.get('nome', 'Administrador'), 'master', 'sistema', None, True)
                login_user(user, remember=True)
                return redirect(url_for('index'))
        
        # Verificar organista (buscar em todas as comuns)
        organista_data = find_organista_in_all_comuns(db, username)
        if organista_data:
            organista = organista_data['organista']
            if 'password_hash' in organista and check_password_hash(organista['password_hash'], password):
                user = User(
                    organista['id'],
                    organista['nome'],
                    'organista',
                    'comum',
                    organista_data['comum_id'],
                    False
                )
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

# ========== ENDPOINTS DE HIERARQUIA (REGIONAL/SUB-REGIONAL/COMUM) ==========

@app.get("/api/comuns")
@login_required
def api_list_comuns():
    """Lista todas as comuns que o usuário tem acesso"""
    db = load_db()
    
    if current_user.is_master:
        # Master vê todas
        comuns = list_all_comuns(db)
    elif current_user.is_organista or current_user.is_encarregado_comum:
        # Organista/Encarregado vê apenas sua comum
        comum_data = find_comum_by_id(db, current_user.contexto_id)
        comuns = [comum_data] if comum_data else []
    else:
        # Admin regional / Encarregado sub-regional
        comuns = list_all_comuns(db)  # Por enquanto, mostrar todas
    
    return jsonify(comuns)

@app.get("/api/contexto")
@login_required
def api_get_contexto():
    """Retorna o contexto atual do usuário"""
    return jsonify({
        "tipo": current_user.tipo,
        "nivel": current_user.nivel,
        "contexto_id": current_user.contexto_id,
        "is_master": current_user.is_master,
        "is_admin": current_user.is_admin
    })

@app.get("/organistas")
@login_required
def list_organistas():
    """Lista organistas - com suporte para estrutura antiga e nova"""
    db = load_db()
    
    # NOVA ESTRUTURA: Buscar na comum do usuário
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if comum_result:
            organistas = comum_result['comum'].get('organistas', [])
        else:
            organistas = []
    else:
        # ESTRUTURA ANTIGA: Retrocompatibilidade
        organistas = db.get("organistas", [])
    
    # Remover password_hash antes de enviar
    organistas = [{k: v for k, v in o.items() if k != 'password_hash'} for o in organistas]
    return jsonify(organistas)

@app.post("/organistas")
@login_required
def add_organista():
    """Adiciona organista - com suporte para estrutura antiga e nova"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas o administrador pode adicionar organistas."}), 403
    
    db = load_db()
    payload = request.get_json()
    
    # Hash da senha
    if 'password' in payload:
        payload['password_hash'] = generate_password_hash(payload['password'])
        del payload['password']
    else:
        payload['password_hash'] = generate_password_hash('123456')
    
    # NOVA ESTRUTURA: Adicionar na comum do usuário
    if 'regionais' in db:
        if current_user.is_master:
            # Master: DEVE especificar o comum no payload
            comum_id = payload.get('comum_id')
            if not comum_id:
                return jsonify({"error": "Selecione o comum onde a organista atuará"}), 400
        else:
            # Encarregado: usa o contexto dele
            comum_id = current_user.contexto_id
        
        comum_data = find_comum_by_id(db, comum_id)
        if not comum_data:
            return jsonify({"error": f"Comum '{comum_id}' não encontrada"}), 404
        
        # Verificar duplicata na comum
        organistas = comum_data['comum'].get('organistas', [])
        if any(o["id"] == payload["id"] for o in organistas):
            return jsonify({"error": "Organista com esse ID já existe."}), 400
        
        # Adicionar organista
        organistas.append(payload)
        
        # Atualizar no banco
        regional = db['regionais'][comum_data['regional_id']]
        sub_regional = regional['sub_regionais'][comum_data['sub_regional_id']]
        sub_regional['comuns'][comum_id]['organistas'] = organistas
    else:
        # ESTRUTURA ANTIGA: Retrocompatibilidade
        if any(o["id"] == payload["id"] for o in db.get("organistas", [])):
            return jsonify({"error": "Organista com esse ID já existe."}), 400
        db["organistas"].append(payload)
    
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "add_organista",
        "por": current_user.id,
        "comum_id": current_user.contexto_id if 'regionais' in db else None,
        "payload": {k: v for k, v in payload.items() if k != 'password_hash'}
    })
    save_db(db)
    
    response_payload = {k: v for k, v in payload.items() if k != 'password_hash'}
    return jsonify({"ok": True, "organista": response_payload})

@app.put("/organistas/<org_id>")
@login_required
def update_organista(org_id):
    """Atualiza organista - com suporte para estrutura antiga e nova"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas o administrador pode editar organistas."}), 403
    
    db = load_db()
    payload = request.get_json()
    
    # Se tiver nova senha, fazer hash
    if 'password' in payload:
        payload['password_hash'] = generate_password_hash(payload['password'])
        del payload['password']
    
    organista = None
    
    # NOVA ESTRUTURA: Buscar na comum
    if 'regionais' in db:
        organista_data = find_organista_in_all_comuns(db, org_id)
        if not organista_data:
            return jsonify({"error": "Organista não encontrado."}), 404
        
        # Atualizar organista
        organista = organista_data['organista']
        organista.update(payload)
        
        # Atualizar no banco (precisamos reconstruir o caminho)
        comum_data = find_comum_by_id(db, organista_data['comum_id'])
        if comum_data:
            regional = db['regionais'][comum_data['regional_id']]
            sub_regional = regional['sub_regionais'][comum_data['sub_regional_id']]
            # Organista já foi atualizado por referência, só precisamos salvar
    else:
        # ESTRUTURA ANTIGA: Retrocompatibilidade
        organista = next((o for o in db.get("organistas", []) if o["id"] == org_id), None)
        if not organista:
            return jsonify({"error": "Organista não encontrado."}), 404
        organista.update(payload)
    
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "update_organista",
        "por": current_user.id,
        "payload": {"id": org_id, "changes": {k: v for k, v in payload.items() if k != 'password_hash'}}
    })
    save_db(db)
    
    response = {k: v for k, v in organista.items() if k != 'password_hash'}
    return jsonify({"ok": True, "organista": response})

@app.delete("/organistas/<org_id>")
@login_required
def delete_organista(org_id):
    """Remove organista - com suporte para estrutura antiga e nova"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas o administrador pode remover organistas."}), 403
    
    db = load_db()
    removed = False
    
    # NOVA ESTRUTURA: Buscar e remover da comum
    if 'regionais' in db:
        organista_data = find_organista_in_all_comuns(db, org_id)
        if not organista_data:
            return jsonify({"error": "Organista não encontrado."}), 404
        
        # Remover organista
        comum_data = find_comum_by_id(db, organista_data['comum_id'])
        if comum_data:
            regional = db['regionais'][comum_data['regional_id']]
            sub_regional = regional['sub_regionais'][comum_data['sub_regional_id']]
            organistas = sub_regional['comuns'][comum_data['comum_id']]['organistas']
            sub_regional['comuns'][comum_data['comum_id']]['organistas'] = [
                o for o in organistas if o['id'] != org_id
            ]
            removed = True
    else:
        # ESTRUTURA ANTIGA: Retrocompatibilidade
        before = len(db.get("organistas", []))
        db["organistas"] = [o for o in db.get("organistas", []) if o["id"] != org_id]
        after = len(db["organistas"])
        removed = (before != after)
    
    if not removed:
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
    """Lista indisponibilidades - com suporte para estrutura antiga e nova"""
    db = load_db()
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_data = get_comum_for_user(db, current_user)
        if not comum_data:
            return jsonify([])
        
        items = comum_data['comum'].get('indisponibilidades', [])
    else:
        # ESTRUTURA ANTIGA
        items = db.get("indisponibilidades", [])
    
    # Se for organista, só vê suas próprias
    if not current_user.is_admin:
        items = [i for i in items if i["id"] == current_user.id]
    else:
        # Admin pode filtrar por organista ou ver todas
        organista = request.args.get("id")
        if organista:
            items = [i for i in items if i["id"] == organista]
    
    return jsonify(items)

@app.post("/indisponibilidades")
@login_required
def add_indisp():
    """Adiciona indisponibilidade - com suporte para estrutura antiga e nova"""
    db = load_db()
    payload = request.get_json()
    
    # Organista só pode marcar para si mesmo, admin pode marcar para qualquer um
    if not current_user.is_admin:
        payload["id"] = current_user.id
    elif "id" not in payload:
        return jsonify({"error": "ID da organista é obrigatório para administrador."}), 400
    
    payload["autor"] = current_user.id
    payload["status"] = "confirmada"
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_data = get_comum_for_user(db, current_user)
        if not comum_data:
            return jsonify({"error": "Comum não encontrada."}), 404
        
        # Validar período
        d = payload["data"]
        config = comum_data['comum'].get('config', {})
        periodo = config.get('periodo', config.get('bimestre', {}))
        ini = periodo.get("inicio", "2025-01-01")
        fim = periodo.get("fim", "2025-12-31")
        if not (ini <= d <= fim):
            return jsonify({"error":"Data fora do período configurado."}), 400
        
        # upsert (impede duplicata)
        indisps = comum_data['comum'].get('indisponibilidades', [])
        dup = next((x for x in indisps if x["id"]==payload["id"] and x["data"]==d), None)
        if dup:
            dup.update(payload)
        else:
            indisps.append(payload)
        
        # Atualizar no banco
        regional = db['regionais'][comum_data['regional_id']]
        sub_regional = regional['sub_regionais'][comum_data['sub_regional_id']]
        sub_regional['comuns'][comum_data['comum_id']]['indisponibilidades'] = indisps
    else:
        # ESTRUTURA ANTIGA
        d = payload["data"]
        ini = db["config"]["bimestre"]["inicio"]
        fim = db["config"]["bimestre"]["fim"]
        if not (ini <= d <= fim):
            return jsonify({"error":"Data fora do período configurado."}), 400
        
        dup = next((x for x in db.get("indisponibilidades", []) if x["id"]==payload["id"] and x["data"]==d), None)
        if dup:
            dup.update(payload)
        else:
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
        return jsonify({"error": "Você só pode remover suas próprias indisponibilidades."}), 403

    db = load_db()

    removed = False

    # NOVA ESTRUTURA: dados aninhados em regionais/sub-regionais/comuns
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if not comum_result:
            return jsonify({"error": "Comum não encontrada."}), 404

        regional = db['regionais'][comum_result['regional_id']]
        sub_regional = regional['sub_regionais'][comum_result['sub_regional_id']]
        comum = sub_regional['comuns'][comum_result['comum_id']]

        indisps = comum.get('indisponibilidades', [])
        before = len(indisps)
        indisps = [i for i in indisps if not (i.get('id') == org_id and i.get('data') == data_iso)]
        after = len(indisps)
        removed = (before != after)

        # Persistir alterações no caminho correto
        comum['indisponibilidades'] = indisps
        sub_regional['comuns'][comum_result['comum_id']] = comum
        regional['sub_regionais'][comum_result['sub_regional_id']] = sub_regional
        db['regionais'][comum_result['regional_id']] = regional

    else:
        # ESTRUTURA ANTIGA: lista no topo do arquivo
        indisps = db.get('indisponibilidades', [])
        before = len(indisps)
        db['indisponibilidades'] = [i for i in indisps if not (i.get('id') == org_id and i.get('data') == data_iso)]
        after = len(db['indisponibilidades'])
        removed = (before != after)

    if not removed:
        return jsonify({"error": "Não encontrado"}), 404

    # Log e salvar
    db.setdefault('logs', []).append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "del_indisponibilidade",
        "por": current_user.id,
        "payload": {"id": org_id, "data": data_iso}
    })
    save_db(db)
    return jsonify({"ok": True})

@app.get("/admin/indisponibilidades/todas")
@login_required
def admin_all_indisp():
    """Admin vê todas indisponibilidades organizadas por organista"""
    if not current_user.is_admin:
        return jsonify({"error": "Acesso negado"}), 403
    
    db = load_db()
    comum_result = get_comum_for_user(db, current_user)
    
    if not comum_result:
        return jsonify({"error": "Contexto não encontrado"}), 404
    
    # Extrair o objeto comum
    comum_data = comum_result['comum']
    
    # Agrupar por organista
    result = {}
    for indisp in comum_data.get("indisponibilidades", []):
        org_id = indisp["id"]
        if org_id not in result:
            organista = next((o for o in comum_data.get("organistas", []) if o["id"] == org_id), None)
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
    comum_result = get_comum_for_user(db, current_user)
    
    if not comum_result:
        return jsonify({"error": "Contexto não encontrado"}), 404
    
    # Extrair o objeto comum
    comum_data = comum_result['comum']
    config = comum_data.get("config", {})
    
    # Retrocompatibilidade: se tem 'periodo', também fornecer como 'bimestre'
    if 'periodo' in config and 'bimestre' not in config:
        config['bimestre'] = config['periodo']
    
    return jsonify(config)

@app.put("/admin/config")
@login_required
def update_config():
    """Admin atualiza configurações do sistema"""
    if not current_user.is_admin:
        return jsonify({"error": "Acesso negado"}), 403
    
    db = load_db()
    comum_result = get_comum_for_user(db, current_user)
    
    if not comum_result:
        return jsonify({"error": "Contexto não encontrado"}), 404
    
    # Extrair o objeto comum do resultado
    comum_data = comum_result['comum']
    
    payload = request.get_json()
    
    print(f"💾 [API] PUT /admin/config")
    print(f"  👤 Usuário: {current_user.id}")
    print(f"  📦 Payload recebido: {payload}")
    
    # Converter 'bimestre' para 'periodo' se vier do frontend antigo
    if 'bimestre' in payload and 'periodo' not in payload:
        payload['periodo'] = payload['bimestre']
        del payload['bimestre']
    
    if "config" not in comum_data:
        comum_data["config"] = {}
    
    comum_data["config"].update(payload)
    
    print(f"  ✅ Config atualizada: {comum_data['config']}")
    
    db["logs"].append({
        "quando": datetime.utcnow().isoformat(),
        "acao": "update_config",
        "por": current_user.id,
        "payload": payload
    })
    save_db(db)
    
    return jsonify({"ok": True, "config": comum_data["config"]})

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
        "dia_semana": "Sunday",  # CORRIGIDO: usar inglês para compatibilidade
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
            "dia_semana": "Tuesday",  # CORRIGIDO: usar inglês para compatibilidade
            "unica": escolhido["nome"]  # Usar nome ao invés de ID
        }
    else:
        logs.append(f"{data_str}: ⚠️ NENHUM candidato para Terça!")
        return {
            "data": data_str,
            "dia_semana": "Tuesday",  # CORRIGIDO: usar inglês para compatibilidade
            "unica": None
        }

def validar_regras_especiais(organista, data, tipo):
    """Regra especial desativada: elegibilidade depende apenas de indisponibilidade e tipos/dias permitidos."""
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
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if not comum_result:
            return jsonify({"error": "Comum não encontrada."}), 404
        
        comum_data = comum_result['comum']
        regional_id = comum_result['regional_id']
        sub_regional_id = comum_result['sub_regional_id']
        comum_id = comum_result['comum_id']
        
        # Salvar escala na comum
        comum_data["escala"] = escala
        comum_data["escala_publicada_em"] = datetime.utcnow().isoformat()
        comum_data["escala_publicada_por"] = current_user.id
        
        # Atualizar no banco
        db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
        
        db.setdefault("logs", []).append({
            "quando": datetime.utcnow().isoformat(),
            "acao": "publicar_escala",
            "por": current_user.id,
            "comum_id": comum_id,
            "payload": {"total_dias": len(escala)}
        })
    else:
        # ESTRUTURA ANTIGA
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
    """Retorna a escala atual publicada - com suporte para estrutura antiga e nova"""
    db = load_db()
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_data = get_comum_for_user(db, current_user)
        if not comum_data:
            return jsonify({"escala": [], "estatisticas": {}})
        
        escala = comum_data['comum'].get('escala', [])
        organistas = comum_data['comum'].get('organistas', [])
        publicada_em = comum_data['comum'].get('escala_publicada_em')
        publicada_por = comum_data['comum'].get('escala_publicada_por')
    else:
        # ESTRUTURA ANTIGA
        escala = db.get("escala", [])
        organistas = db.get("organistas", [])
        publicada_em = db.get("escala_publicada_em")
        publicada_por = db.get("escala_publicada_por")
    
    if not escala:
        return jsonify({
            "escala": [],
            "estatisticas": {}
        })
    
    stats = calcular_estatisticas(escala, organistas)
    
    return jsonify({
        "escala": escala,
        "publicada_em": publicada_em,
        "publicada_por": publicada_por,
        "estatisticas": stats["por_organista"]
    })

@app.delete("/escala/delete")
@login_required
def deletar_escala():
    """Deleta a escala atual - com suporte para estrutura antiga e nova"""
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Sem permissão"}), 403
    
    db = load_db()
    
    try:
        # NOVA ESTRUTURA
        if 'regionais' in db:
            comum_data = get_comum_for_user(db, current_user)
            if not comum_data:
                return jsonify({"success": False, "error": "Comum não encontrada"}), 404
            
            # Verificar se há escala
            escala_atual = comum_data['comum'].get('escala', [])
            if not escala_atual:
                return jsonify({"success": False, "error": "Não há escala para deletar"}), 400
            
            # Deletar escala
            comum_data['comum']['escala'] = []
            comum_data['comum']['escala_publicada_em'] = None
            comum_data['comum']['escala_publicada_por'] = None
            
            # Navegar até o local correto e salvar
            regional = db['regionais'][comum_data['regional_id']]
            sub_regional = regional['sub_regionais'][comum_data['sub_regional_id']]
            sub_regional['comuns'][comum_data['comum_id']] = comum_data['comum']
            
        else:
            # ESTRUTURA ANTIGA
            if not db.get('escala'):
                return jsonify({"success": False, "error": "Não há escala para deletar"}), 400
            
            db['escala'] = []
            db['escala_publicada_em'] = None
            db['escala_publicada_por'] = None
        
        save_db(db)
        
        return jsonify({
            "success": True,
            "message": "Escala deletada com sucesso"
        })
        
    except Exception as e:
        print(f"❌ Erro ao deletar escala: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.put("/escala/editar/<data_iso>")
@login_required
def editar_dia_escala(data_iso):
    """Permite editar alocação de um dia específico"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas administrador pode editar escala."}), 403
    
    db = load_db()
    payload = request.get_json()
    alocacao = payload.get("alocacao", payload)  # Aceita ambos formatos
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if not comum_result:
            return jsonify({"error": "Comum não encontrada."}), 404
        
        comum_data = comum_result['comum']
        regional_id = comum_result['regional_id']
        sub_regional_id = comum_result['sub_regional_id']
        comum_id = comum_result['comum_id']
        
        escala = comum_data.get("escala", [])
        
        # Encontrar o dia na escala
        dia = next((d for d in escala if d["data"] == data_iso), None)
        if not dia:
            return jsonify({"error": "Data não encontrada na escala."}), 404
        
        # Atualizar alocações
        if "meia_hora" in alocacao:
            dia["meia_hora"] = alocacao["meia_hora"]
        if "culto" in alocacao:
            dia["culto"] = alocacao["culto"]
        if "unica" in alocacao:
            dia["unica"] = alocacao["unica"]
        
        # Salvar de volta
        comum_data["escala"] = escala
        db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
        
        db.setdefault("logs", []).append({
            "quando": datetime.utcnow().isoformat(),
            "acao": "editar_escala",
            "por": current_user.id,
            "comum_id": comum_id,
            "payload": {"data": data_iso, "alteracoes": payload}
        })
    else:
        # ESTRUTURA ANTIGA
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
    # Normalizar nomes de dias para português para contagem
    def dia_normalizado(d):
        m = {
            'Sunday': 'Domingo', 'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
            'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado',
            'Domingo': 'Domingo', 'Segunda': 'Segunda', 'Terça': 'Terça', 'Quarta': 'Quarta',
            'Quinta': 'Quinta', 'Sexta': 'Sexta', 'Sábado': 'Sábado'
        }
        return m.get(d, d)

    stats = {
        "total_dias": len(escala),
        "domingos": sum(1 for d in escala if dia_normalizado(d.get("dia_semana")) == "Domingo"),
        "tercas": sum(1 for d in escala if dia_normalizado(d.get("dia_semana")) == "Terça"),
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
        dia_semana_pt = dia_normalizado(dia.get("dia_semana"))
        if dia_semana_pt == "Domingo":
            if dia.get("meia_hora") and dia["meia_hora"] in stats["por_organista"]:
                stats["por_organista"][dia["meia_hora"]]["meia_hora"] += 1
                stats["por_organista"][dia["meia_hora"]]["total"] += 1
            
            if dia.get("culto") and dia["culto"] in stats["por_organista"]:
                stats["por_organista"][dia["culto"]]["culto"] += 1
                stats["por_organista"][dia["culto"]]["total"] += 1
        
        elif dia_semana_pt == "Terça":
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
        
        # NOVA ESTRUTURA
        if 'regionais' in db:
            comum_result = get_comum_for_user(db, current_user)
            if not comum_result:
                return jsonify({"erro": "Comum não encontrada"}), 404
            
            comum_data = comum_result['comum']
            comum_nome = comum_data.get('nome', 'Comum')
            escala = comum_data.get("escala", [])
        else:
            # ESTRUTURA ANTIGA
            comum_nome = "Vila Paula"
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
        
        # Meses em português
        meses_pt = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        
        title = Paragraph(
            f"Rodízio de Organistas - {comum_nome}",
            title_style
        )
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Agrupar por mês
        escala_por_mes = {}
        
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
                    'nome': f"{meses_pt[data.month]}/{data.year}",
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
        response.headers['Content-Disposition'] = f'attachment; filename=Rodizio_Organistas_{datetime.now().strftime("%Y%m%d")}.pdf'
        
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
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if not comum_result:
            return jsonify({"error": "Comum não encontrada."}), 404
        
        comum_data = comum_result['comum']
        regional_id = comum_result['regional_id']
        sub_regional_id = comum_result['sub_regional_id']
        comum_id = comum_result['comum_id']
        
        config = comum_data.get('config', {})
        # Suportar tanto 'periodo' quanto 'bimestre'
        periodo_config = config.get('periodo', config.get('bimestre'))
        
        if not periodo_config or not periodo_config.get('inicio') or not periodo_config.get('fim'):
            return jsonify({"error": "Período não configurado. Configure nas Configurações."}), 400
        
        inicio = datetime.fromisoformat(periodo_config["inicio"])
        fim = datetime.fromisoformat(periodo_config["fim"])
    else:
        # ESTRUTURA ANTIGA
        config = db.get("config", {})
        periodo_config = config.get('periodo', config.get('bimestre', {}))
        
        if not periodo_config or not periodo_config.get('inicio') or not periodo_config.get('fim'):
            return jsonify({"error": "Período não configurado."}), 400
        
        inicio = datetime.fromisoformat(periodo_config["inicio"])
        fim = datetime.fromisoformat(periodo_config["fim"])
    
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
    
    # Salvar escala RJM
    if 'regionais' in db:
        comum_data["escala_rjm"] = escala_rjm
        db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
    else:
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
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if not comum_result:
            return jsonify({"escala_rjm": []}), 200
        
        comum_data = comum_result['comum']
        return jsonify({"escala_rjm": comum_data.get("escala_rjm", [])}), 200
    else:
        # ESTRUTURA ANTIGA
        return jsonify({"escala_rjm": db.get("escala_rjm", [])}), 200

@app.delete("/rjm/delete")
@login_required
def deletar_escala_rjm():
    """Deleta a escala RJM atual - com suporte para estrutura antiga e nova"""
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Sem permissão"}), 403
    
    db = load_db()
    
    try:
        # NOVA ESTRUTURA
        if 'regionais' in db:
            comum_data = get_comum_for_user(db, current_user)
            if not comum_data:
                return jsonify({"success": False, "error": "Comum não encontrada"}), 404
            
            # Verificar se há escala RJM
            escala_rjm_atual = comum_data['comum'].get('escala_rjm', [])
            if not escala_rjm_atual:
                return jsonify({"success": False, "error": "Não há escala RJM para deletar"}), 400
            
            # Deletar escala RJM
            comum_data['comum']['escala_rjm'] = []
            
            # Navegar até o local correto e salvar
            regional = db['regionais'][comum_data['regional_id']]
            sub_regional = regional['sub_regionais'][comum_data['sub_regional_id']]
            sub_regional['comuns'][comum_data['comum_id']] = comum_data['comum']
            
        else:
            # ESTRUTURA ANTIGA
            if not db.get('escala_rjm'):
                return jsonify({"success": False, "error": "Não há escala RJM para deletar"}), 400
            
            db['escala_rjm'] = []
        
        save_db(db)
        
        return jsonify({
            "success": True,
            "message": "Escala RJM deletada com sucesso"
        })
        
    except Exception as e:
        print(f"❌ Erro ao deletar escala RJM: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

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
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if not comum_result:
            return jsonify({"error": "Comum não encontrada."}), 404
        
        comum_data = comum_result['comum']
        regional_id = comum_result['regional_id']
        sub_regional_id = comum_result['sub_regional_id']
        comum_id = comum_result['comum_id']
        
        escala_rjm = comum_data.get("escala_rjm", [])
        
        contador_atualizados = 0
        for alt in alteracoes:
            item_id = alt.get("id")
            organista = alt.get("organista", "")
            
            # Encontrar e atualizar o item
            for item in escala_rjm:
                if item["id"] == item_id:
                    item["organista"] = organista
                    contador_atualizados += 1
                    break
        
        # Salvar de volta
        comum_data["escala_rjm"] = escala_rjm
        db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
        
        db.setdefault("logs", []).append({
            "quando": datetime.utcnow().isoformat(),
            "acao": "atualizar_escala_rjm_multiplos",
            "quem": current_user.id,
            "comum_id": comum_id,
            "total_alteracoes": contador_atualizados
        })
    else:
        # ESTRUTURA ANTIGA
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
    
    # NOVA ESTRUTURA
    if 'regionais' in db:
        comum_result = get_comum_for_user(db, current_user)
        if not comum_result:
            return jsonify({"error": "Comum não encontrada."}), 404
        
        comum_data = comum_result['comum']
        comum_nome = comum_data.get('nome', 'Comum')
        escala_rjm = comum_data.get("escala_rjm", [])
    else:
        # ESTRUTURA ANTIGA
        comum_nome = "Vila Paula"
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
    
    subtitle = Paragraph(f"{comum_nome} - Domingos 10:00", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Mapeamento de meses para português
    meses_pt = {
        1: 'JANEIRO', 2: 'FEVEREIRO', 3: 'MARÇO', 4: 'ABRIL',
        5: 'MAIO', 6: 'JUNHO', 7: 'JULHO', 8: 'AGOSTO',
        9: 'SETEMBRO', 10: 'OUTUBRO', 11: 'NOVEMBRO', 12: 'DEZEMBRO'
    }
    
    # Agrupar por mês
    meses = defaultdict(list)
    for item in escala_rjm:
        data = datetime.fromisoformat(item["data"])
        mes_ano_key = f"{data.year}-{data.month:02d}"  # Para ordenação
        mes_ano_nome = f"{meses_pt[data.month]} {data.year}"
        meses[mes_ano_key] = {
            'nome': mes_ano_nome,
            'itens': meses.get(mes_ano_key, {}).get('itens', []) + [item]
        }
    
    # Criar tabela para cada mês (ordenado)
    for mes_ano_key in sorted(meses.keys()):
        mes_data = meses[mes_ano_key]
        mes_ano_nome = mes_data['nome']
        itens = mes_data['itens']
        
        elements.append(Paragraph(f"<b>{mes_ano_nome}</b>", styles['Heading2']))
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

# ========== TROCAS (Solicitações de Substituição/Troca) ==========

def _get_comum_context_for_current_user(db):
    """Helper para obter comuns e chaves de contexto do usuário atual"""
    comum_result = get_comum_for_user(db, current_user)
    if not comum_result:
        return None, None, None, None
    return (
        comum_result['comum'],
        comum_result['regional_id'],
        comum_result['sub_regional_id'],
        comum_result['comum_id']
    )

def _ensure_trocas_array(comum_data):
    if 'trocas' not in comum_data or not isinstance(comum_data['trocas'], list):
        comum_data['trocas'] = []
    return comum_data['trocas']

def _organista_nome_by_id(comum_data, org_id):
    for org in comum_data.get('organistas', []):
        if org.get('id') == org_id:
            return org.get('nome', org_id)
    return org_id

def _dia_escala_by_data(comum_data, data_iso):
    for d in comum_data.get('escala', []):
        if d.get('data') == data_iso:
            return d
    return None

def _rjm_item_by_data(comum_data, data_iso):
    for d in comum_data.get('escala_rjm', []):
        if d.get('data') == data_iso:
            return d
    return None

def _find_troca(trocas, troca_id):
    return next((t for t in trocas if t.get('id') == troca_id), None)

def _add_historico(troca, acao, por):
    troca.setdefault('historico', []).append({
        'quando': datetime.utcnow().isoformat(),
        'acao': acao,
        'por': por
    })

@app.get("/trocas")
@login_required
def listar_trocas():
    """Lista trocas da comum atual. Admin vê todas. Organista vê as envolvidas."""
    db = load_db()
    if 'regionais' not in db:
        # Estrutura antiga: manter compatibilidade mínima
        trocas = db.get('trocas', [])
        if current_user.is_admin:
            return jsonify(trocas)
        return jsonify([t for t in trocas if t.get('solicitante_id') == current_user.id or t.get('alvo_id') == current_user.id])

    comum_data, regional_id, sub_regional_id, comum_id = _get_comum_context_for_current_user(db)
    if not comum_data:
        return jsonify([])

    trocas = _ensure_trocas_array(comum_data)
    if current_user.is_admin:
        return jsonify(trocas)
    return jsonify([t for t in trocas if t.get('solicitante_id') == current_user.id or t.get('alvo_id') == current_user.id])

@app.post("/trocas")
@login_required
def criar_troca():
    """Cria nova solicitação de troca/substituição"""
    payload = request.get_json() or {}
    tipo = payload.get('tipo')  # 'culto' | 'rjm'
    data_iso = payload.get('data')  # YYYY-MM-DD
    slot = payload.get('slot')  # 'meia_hora' | 'culto' | 'unica'
    modalidade = payload.get('modalidade', 'substituicao')
    alvo_id = payload.get('alvo_id')  # opcional
    motivo = payload.get('motivo', '')

    if tipo not in ['culto', 'rjm']:
        return jsonify({"error": "tipo inválido (use 'culto' ou 'rjm')"}), 400
    if not data_iso:
        return jsonify({"error": "data é obrigatória"}), 400
    if tipo == 'culto' and slot not in ['meia_hora', 'culto']:
        return jsonify({"error": "slot inválido para 'culto' (meia_hora ou culto)"}), 400
    if tipo == 'rjm' and slot not in [None, '', 'unica']:
        return jsonify({"error": "slot inválido para 'rjm' (use 'unica' ou deixe em branco)"}), 400

    db = load_db()
    if 'regionais' not in db:
        return jsonify({"error": "Recurso indisponível na estrutura antiga"}), 400

    comum_data, regional_id, sub_regional_id, comum_id = _get_comum_context_for_current_user(db)
    if not comum_data:
        return jsonify({"error": "Comum não encontrada"}), 404

    # Validar propriedade do slot
    current_nome = current_user.nome
    if tipo == 'culto':
        dia = _dia_escala_by_data(comum_data, data_iso)
        if not dia:
            return jsonify({"error": "Data não encontrada na escala"}), 404
        slot_value = dia.get(slot)
        if slot_value != current_nome:
            return jsonify({"error": "Você não está escalado(a) nesse slot para solicitar troca"}), 403
    else:
        item = _rjm_item_by_data(comum_data, data_iso)
        if not item:
            return jsonify({"error": "Data não encontrada na RJM"}), 404
        if item.get('organista') != current_nome:
            return jsonify({"error": "Você não está escalado(a) nesta data na RJM"}), 403
        slot = 'unica'

    trocas = _ensure_trocas_array(comum_data)
    # Evitar duplicidade pendente para mesmo dia/slot
    if any(t for t in trocas if t.get('status') in ['pendente', 'aceita'] and t.get('data') == data_iso and t.get('tipo') == tipo and t.get('slot') == slot and t.get('solicitante_id') == current_user.id):
        return jsonify({"error": "Já existe uma solicitação pendente para este dia e slot"}), 400

    troca = {
        'id': str(uuid.uuid4()),
        'criado_em': datetime.utcnow().isoformat(),
        'atualizado_em': datetime.utcnow().isoformat(),
        'status': 'pendente',
        'modalidade': modalidade,
        'tipo': tipo,
        'data': data_iso,
        'slot': slot,
        'solicitante_id': current_user.id,
        'solicitante_nome': current_user.nome,
        'alvo_id': alvo_id or '',
        'alvo_nome': _organista_nome_by_id(comum_data, alvo_id) if alvo_id else '',
        'motivo': motivo,
        'historico': []
    }
    _add_historico(troca, 'criada', current_user.id)
    trocas.append(troca)

    # Persistir
    db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
    db.setdefault('logs', []).append({
        'quando': datetime.utcnow().isoformat(),
        'acao': 'criar_troca',
        'por': current_user.id,
        'payload': {k: v for k, v in troca.items() if k not in ['historico']}
    })
    save_db(db)
    return jsonify({"ok": True, "troca": troca})

@app.post("/trocas/<troca_id>/aceitar")
@login_required
def aceitar_troca(troca_id):
    db = load_db()
    if 'regionais' not in db:
        return jsonify({"error": "Recurso indisponível na estrutura antiga"}), 400
    comum_data, regional_id, sub_regional_id, comum_id = _get_comum_context_for_current_user(db)
    if not comum_data:
        return jsonify({"error": "Comum não encontrada"}), 404
    trocas = _ensure_trocas_array(comum_data)
    troca = _find_troca(trocas, troca_id)
    if not troca:
        return jsonify({"error": "Troca não encontrada"}), 404
    if troca.get('status') not in ['pendente']:
        return jsonify({"error": "Troca não está pendente"}), 400

    # Se já tem alvo definido, apenas o alvo pode aceitar; se não tem, qualquer organista pode aceitar
    if troca.get('alvo_id'):
        if troca['alvo_id'] != current_user.id:
            return jsonify({"error": "Apenas o destinatário pode aceitar esta solicitação"}), 403
    else:
        # Atribuir o alvo como quem aceitou
        troca['alvo_id'] = current_user.id
        troca['alvo_nome'] = current_user.nome

    troca['status'] = 'aceita'
    troca['atualizado_em'] = datetime.utcnow().isoformat()
    _add_historico(troca, 'aceita', current_user.id)

    db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
    save_db(db)
    return jsonify({"ok": True, "troca": troca})

@app.post("/trocas/<troca_id>/recusar")
@login_required
def recusar_troca(troca_id):
    db = load_db()
    if 'regionais' not in db:
        return jsonify({"error": "Recurso indisponível na estrutura antiga"}), 400
    comum_data, regional_id, sub_regional_id, comum_id = _get_comum_context_for_current_user(db)
    if not comum_data:
        return jsonify({"error": "Comum não encontrada"}), 404
    trocas = _ensure_trocas_array(comum_data)
    troca = _find_troca(trocas, troca_id)
    if not troca:
        return jsonify({"error": "Troca não encontrada"}), 404
    if troca.get('status') not in ['pendente']:
        return jsonify({"error": "Troca não está pendente"}), 400
    # Somente destinatário (definido) ou admin podem recusar
    if not current_user.is_admin and troca.get('alvo_id') != current_user.id:
        return jsonify({"error": "Sem permissão para recusar"}), 403

    troca['status'] = 'recusada'
    troca['atualizado_em'] = datetime.utcnow().isoformat()
    _add_historico(troca, 'recusada', current_user.id)
    db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
    save_db(db)
    return jsonify({"ok": True, "troca": troca})

@app.post("/trocas/<troca_id>/cancelar")
@login_required
def cancelar_troca(troca_id):
    db = load_db()
    if 'regionais' not in db:
        return jsonify({"error": "Recurso indisponível na estrutura antiga"}), 400
    comum_data, regional_id, sub_regional_id, comum_id = _get_comum_context_for_current_user(db)
    if not comum_data:
        return jsonify({"error": "Comum não encontrada"}), 404
    trocas = _ensure_trocas_array(comum_data)
    troca = _find_troca(trocas, troca_id)
    if not troca:
        return jsonify({"error": "Troca não encontrada"}), 404
    if troca.get('status') not in ['pendente', 'aceita']:
        return jsonify({"error": "Apenas trocas pendentes/aceitas podem ser canceladas"}), 400
    if troca.get('solicitante_id') != current_user.id and not current_user.is_admin:
        return jsonify({"error": "Sem permissão para cancelar"}), 403

    troca['status'] = 'cancelada'
    troca['atualizado_em'] = datetime.utcnow().isoformat()
    _add_historico(troca, 'cancelada', current_user.id)
    db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
    save_db(db)
    return jsonify({"ok": True, "troca": troca})

@app.post("/trocas/<troca_id>/aprovar")
@login_required
def aprovar_troca(troca_id):
    """Admin aplica a troca na escala/RJM e marca como aprovada"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas administrador pode aprovar"}), 403
    db = load_db()
    if 'regionais' not in db:
        return jsonify({"error": "Recurso indisponível na estrutura antiga"}), 400
    comum_data, regional_id, sub_regional_id, comum_id = _get_comum_context_for_current_user(db)
    if not comum_data:
        return jsonify({"error": "Comum não encontrada"}), 404
    trocas = _ensure_trocas_array(comum_data)
    troca = _find_troca(trocas, troca_id)
    if not troca:
        return jsonify({"error": "Troca não encontrada"}), 404

    if troca.get('status') not in ['aceita']:
        return jsonify({"error": "Troca precisa estar 'aceita' para aprovar"}), 400
    if not troca.get('alvo_nome'):
        return jsonify({"error": "Troca aceita sem destinatário definido"}), 400

    # Aplicar na escala apropriada
    if troca['tipo'] == 'culto':
        dia = _dia_escala_by_data(comum_data, troca['data'])
        if not dia:
            return jsonify({"error": "Data não encontrada na escala"}), 404
        if troca['slot'] not in ['meia_hora', 'culto']:
            return jsonify({"error": "Slot inválido"}), 400
        dia[troca['slot']] = troca['alvo_nome']
        # Sinalizar que esta alocação veio de uma troca (para UI)
        proveniencia = dia.setdefault('_proveniencia', {})
        proveniencia[troca['slot']] = 'troca'
    else:
        item = _rjm_item_by_data(comum_data, troca['data'])
        if not item:
            return jsonify({"error": "Data não encontrada na RJM"}), 404
        item['organista'] = troca['alvo_nome']
        # Sinalizar proveniência na RJM
        proveniencia = item.setdefault('_proveniencia', {})
        proveniencia['unica'] = 'troca'

    troca['status'] = 'aprovada'
    troca['atualizado_em'] = datetime.utcnow().isoformat()
    _add_historico(troca, 'aprovada', current_user.id)

    # Persistir e logar
    db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
    db.setdefault('logs', []).append({
        'quando': datetime.utcnow().isoformat(),
        'acao': 'aprovar_troca',
        'por': current_user.id,
        'payload': {'troca_id': troca_id}
    })
    save_db(db)
    return jsonify({"ok": True, "troca": troca})

@app.post("/trocas/<troca_id>/reprovar")
@login_required
def reprovar_troca(troca_id):
    """Admin/Encarregado reprova a troca (não aplica na escala) e marca como recusada"""
    if not current_user.is_admin:
        return jsonify({"error": "Apenas administrador pode reprovar"}), 403
    db = load_db()
    if 'regionais' not in db:
        return jsonify({"error": "Recurso indisponível na estrutura antiga"}), 400
    comum_data, regional_id, sub_regional_id, comum_id = _get_comum_context_for_current_user(db)
    if not comum_data:
        return jsonify({"error": "Comum não encontrada"}), 404
    trocas = _ensure_trocas_array(comum_data)
    troca = _find_troca(trocas, troca_id)
    if not troca:
        return jsonify({"error": "Troca não encontrada"}), 404

    if troca.get('status') not in ['aceita']:
        return jsonify({"error": "Somente trocas 'aceita' podem ser reprovadas"}), 400

    # Não aplica mudanças na escala/RJM, apenas marca como recusada
    troca['status'] = 'recusada'
    troca['atualizado_em'] = datetime.utcnow().isoformat()
    _add_historico(troca, 'reprovada', current_user.id)

    # Persistir e logar
    db['regionais'][regional_id]['sub_regionais'][sub_regional_id]['comuns'][comum_id] = comum_data
    db.setdefault('logs', []).append({
        'quando': datetime.utcnow().isoformat(),
        'acao': 'reprovar_troca',
        'por': current_user.id,
        'payload': {'troca_id': troca_id}
    })
    save_db(db)
    return jsonify({"ok": True, "troca": troca})

# ==================== API de Contexto e Hierarquia ====================

@app.get("/api/regionais")
@login_required
def get_regionais():
    """Retorna lista de regionais disponíveis"""
    db = load_db()
    regionais = []
    
    for regional_id, regional_data in db.get("regionais", {}).items():
        regionais.append({
            "id": regional_id,
            "nome": regional_data.get("nome", regional_id.upper())
        })
    
    return jsonify(regionais)

@app.get("/api/regionais/<regional_id>/sub-regionais")
@login_required
def get_sub_regionais(regional_id):
    """Retorna lista de sub-regionais de uma regional"""
    db = load_db()
    regional = db.get("regionais", {}).get(regional_id, {})
    
    sub_regionais = []
    for sub_id, sub_data in regional.get("sub_regionais", {}).items():
        sub_regionais.append({
            "id": sub_id,
            "nome": sub_data.get("nome", sub_id.replace("_", " ").title())
        })
    
    return jsonify(sub_regionais)

@app.get("/api/regionais/<regional_id>/sub-regionais/<sub_regional_id>/comuns")
@login_required
def get_comuns_by_sub(regional_id, sub_regional_id):
    """Retorna lista de comuns de uma sub-regional"""
    db = load_db()
    regional = db.get("regionais", {}).get(regional_id, {})
    sub_regional = regional.get("sub_regionais", {}).get(sub_regional_id, {})
    
    comuns = []
    for comum_id, comum_data in sub_regional.get("comuns", {}).items():
        comuns.append({
            "id": comum_id,
            "nome": comum_data.get("nome", comum_id.replace("_", " ").title())
        })
    
    return jsonify(comuns)

@app.get("/api/contexto/atual")
@login_required
def get_contexto_atual():
    """Retorna o contexto atual do usuário"""
    db = load_db()
    
    # Para Master, retorna contexto da sessão ou primeiro disponível
    if current_user.tipo == 'master':
        regional_id = session.get('regional_id')
        sub_regional_id = session.get('sub_regional_id')
        comum_id = session.get('comum_id')
        
        regional = None
        sub_regional = None
        comum = None
        
        # Se tem contexto na sessão, validar
        if regional_id and sub_regional_id and comum_id:
            regional = get_regional(db, regional_id)
            sub_regional = get_sub_regional(db, regional_id, sub_regional_id)
            comum_result = find_comum_by_id(db, comum_id)
            if comum_result:
                comum = comum_result['comum']
        
        # Se não tem contexto válido, pegar primeiro disponível
        if not comum:
            for r_id, r_data in db.get("regionais", {}).items():
                for s_id, s_data in r_data.get("sub_regionais", {}).items():
                    for c_id, c_data in s_data.get("comuns", {}).items():
                        regional_id = r_id
                        sub_regional_id = s_id
                        comum_id = c_id
                        regional = r_data
                        sub_regional = s_data
                        comum = c_data
                        # Salvar na sessão
                        session['regional_id'] = r_id
                        session['sub_regional_id'] = s_id
                        session['comum_id'] = c_id
                        break
                    if comum:
                        break
                if comum:
                    break
        
        return jsonify({
            "regional": {
                "id": regional_id,
                "nome": regional.get("nome", regional_id.upper()) if regional else regional_id.upper()
            },
            "sub_regional": {
                "id": sub_regional_id,
                "nome": sub_regional.get("nome", sub_regional_id.replace("_", " ").title()) if sub_regional else sub_regional_id
            },
            "comum": {
                "id": comum_id,
                "nome": comum.get("nome", comum_id.replace("_", " ").title()) if comum else comum_id,
                "config": (comum or {}).get("config", {})
            },
            "nivel": current_user.tipo
        })
    
    # Para outros níveis, contexto é fixo
    comum_result = get_comum_for_user(db, current_user)
    if not comum_result:
        return jsonify({"error": "Contexto não encontrado"}), 404
    
    # Extrair dados do resultado
    comum_data = comum_result['comum']
    regional_id = comum_result['regional_id']
    sub_regional_id = comum_result['sub_regional_id']
    comum_id = comum_result['comum_id']
    
    # Buscar dados da regional e sub-regional
    regional = db.get("regionais", {}).get(regional_id, {})
    sub_regional = regional.get("sub_regionais", {}).get(sub_regional_id, {})
    
    return jsonify({
        "regional": {
            "id": regional_id,
            "nome": regional.get("nome", regional_id.upper()) if regional_id else "N/A"
        },
        "sub_regional": {
            "id": sub_regional_id,
            "nome": sub_regional.get("nome", sub_regional_id.replace("_", " ").title()) if sub_regional_id else "N/A"
        },
        "comum": {
            "id": comum_id,
            "nome": comum_data.get("nome", comum_id.replace("_", " ").title()) if comum_data else "N/A",
            "config": comum_data.get("config", {})
        },
        "nivel": current_user.tipo
    })

@app.post("/api/contexto/atualizar")
@login_required
def atualizar_contexto():
    """Atualiza o contexto atual do usuário (apenas para Master)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode alterar contexto"}), 403
    
    payload = request.get_json()
    comum_id = payload.get('comum_id')
    
    if not comum_id:
        return jsonify({"error": "comum_id é obrigatório"}), 400
    
    db = load_db()
    
    # Encontrar a comum e seus pais
    regional_id = None
    sub_regional_id = None
    comum_data = None
    
    for r_id, r_data in db.get("regionais", {}).items():
        for s_id, s_data in r_data.get("sub_regionais", {}).items():
            for c_id, c_data in s_data.get("comuns", {}).items():
                if c_id == comum_id:
                    regional_id = r_id
                    sub_regional_id = s_id
                    comum_data = c_data
                    break
            if comum_data:
                break
        if comum_data:
            break
    
    if not comum_data:
        return jsonify({"error": "Comum não encontrada"}), 404
    
    # Salvar na sessão
    session['regional_id'] = regional_id
    session['sub_regional_id'] = sub_regional_id
    session['comum_id'] = comum_id
    session.modified = True
    
    return jsonify({
        "ok": True,
        "message": "Contexto atualizado com sucesso",
        "contexto": {
            "regional_id": regional_id,
            "sub_regional_id": sub_regional_id,
            "comum_id": comum_id,
            "comum_nome": comum_data.get("nome", comum_id)
        }
    })

@app.post("/api/contexto/selecionar")
@login_required
def selecionar_contexto():
    """Permite Master selecionar contexto de trabalho"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode alterar contexto"}), 403
    
    data = request.get_json()
    regional_id = data.get('regional_id')
    sub_regional_id = data.get('sub_regional_id')
    comum_id = data.get('comum_id')
    
    # Validar se contexto existe
    db = load_db()
    comum_result = find_comum_by_id(db, comum_id)
    
    if not comum_result:
        return jsonify({"error": "Contexto inválido"}), 400
    
    comum = comum_result['comum']
    comum_id_final = comum_result['comum_id']  # Usar a chave do dicionário
    
    print(f"🔄 [CONTEXTO] Alterando contexto do Master:")
    print(f"  Regional: {regional_id}")
    print(f"  Sub-Regional: {sub_regional_id}")
    print(f"  Comum solicitada: {comum_id}")
    print(f"  Comum ID final: {comum_id_final}")
    print(f"  Nome: {comum.get('nome')}")
    
    # Salvar na sessão usando a chave do dicionário
    session['regional_id'] = regional_id
    session['sub_regional_id'] = sub_regional_id
    session['comum_id'] = comum_id_final  # IMPORTANTE: usar a chave do dict
    session.modified = True  # Forçar Flask a salvar a sessão
    
    print(f"  ✅ Sessão atualizada!")
    print(f"  Session atual: regional={session.get('regional_id')}, sub={session.get('sub_regional_id')}, comum={session.get('comum_id')}")
    
    return jsonify({
        "success": True,
        "contexto": {
            "regional_id": regional_id,
            "sub_regional_id": sub_regional_id,
            "comum_id": comum_id,
            "comum_nome": comum.get("nome", comum_id)
        }
    })

# ==================== CRUD de Hierarquia (Master Only) ====================

@app.post("/api/regionais")
@login_required
def criar_regional():
    """Criar nova regional"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode criar regionais"}), 403
    
    data = request.get_json()
    regional_id = data.get('id')
    regional_nome = data.get('nome')
    
    if not regional_id or not regional_nome:
        return jsonify({"error": "ID e nome são obrigatórios"}), 400
    
    db = load_db()
    
    if regional_id in db.get("regionais", {}):
        return jsonify({"error": "Regional já existe"}), 400
    
    if "regionais" not in db:
        db["regionais"] = {}
    
    db["regionais"][regional_id] = {
        "nome": regional_nome,
        "sub_regionais": {}
    }
    
    save_db(db)
    
    return jsonify({
        "success": True,
        "regional": {
            "id": regional_id,
            "nome": regional_nome
        }
    })

@app.put("/api/regionais/<regional_id>")
@login_required
def editar_regional(regional_id):
    """Editar regional existente"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode editar regionais"}), 403
    
    data = request.get_json()
    regional_nome = data.get('nome')
    
    if not regional_nome:
        return jsonify({"error": "Nome é obrigatório"}), 400
    
    db = load_db()
    
    if regional_id not in db.get("regionais", {}):
        return jsonify({"error": "Regional não encontrada"}), 404
    
    db["regionais"][regional_id]["nome"] = regional_nome
    save_db(db)
    
    return jsonify({
        "success": True,
        "regional": {
            "id": regional_id,
            "nome": regional_nome
        }
    })

@app.delete("/api/regionais/<regional_id>")
@login_required
def deletar_regional(regional_id):
    """Deletar regional (apenas se vazia)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode deletar regionais"}), 403
    
    db = load_db()
    
    if regional_id not in db.get("regionais", {}):
        return jsonify({"error": "Regional não encontrada"}), 404
    
    regional = db["regionais"][regional_id]
    
    if regional.get("sub_regionais"):
        return jsonify({"error": "Não é possível deletar regional com sub-regionais"}), 400
    
    del db["regionais"][regional_id]
    save_db(db)
    
    return jsonify({"success": True, "message": "Regional deletada"})

@app.post("/api/regionais/<regional_id>/sub-regionais")
@login_required
def criar_sub_regional(regional_id):
    """Criar nova sub-regional"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode criar sub-regionais"}), 403
    
    data = request.get_json()
    sub_id = data.get('id')
    sub_nome = data.get('nome')
    
    if not sub_id or not sub_nome:
        return jsonify({"error": "ID e nome são obrigatórios"}), 400
    
    db = load_db()
    
    if regional_id not in db.get("regionais", {}):
        return jsonify({"error": "Regional não encontrada"}), 404
    
    regional = db["regionais"][regional_id]
    
    if sub_id in regional.get("sub_regionais", {}):
        return jsonify({"error": "Sub-regional já existe"}), 400
    
    if "sub_regionais" not in regional:
        regional["sub_regionais"] = {}
    
    regional["sub_regionais"][sub_id] = {
        "nome": sub_nome,
        "comuns": {}
    }
    
    save_db(db)
    
    return jsonify({
        "success": True,
        "sub_regional": {
            "id": sub_id,
            "nome": sub_nome
        }
    })

@app.put("/api/regionais/<regional_id>/sub-regionais/<sub_id>")
@login_required
def editar_sub_regional(regional_id, sub_id):
    """Editar sub-regional existente"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode editar sub-regionais"}), 403
    
    data = request.get_json()
    sub_nome = data.get('nome')
    
    if not sub_nome:
        return jsonify({"error": "Nome é obrigatório"}), 400
    
    db = load_db()
    
    if regional_id not in db.get("regionais", {}):
        return jsonify({"error": "Regional não encontrada"}), 404
    
    regional = db["regionais"][regional_id]
    
    if sub_id not in regional.get("sub_regionais", {}):
        return jsonify({"error": "Sub-regional não encontrada"}), 404
    
    regional["sub_regionais"][sub_id]["nome"] = sub_nome
    save_db(db)
    
    return jsonify({
        "success": True,
        "sub_regional": {
            "id": sub_id,
            "nome": sub_nome
        }
    })

@app.delete("/api/regionais/<regional_id>/sub-regionais/<sub_id>")
@login_required
def deletar_sub_regional(regional_id, sub_id):
    """Deletar sub-regional (apenas se vazia)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode deletar sub-regionais"}), 403
    
    db = load_db()
    
    if regional_id not in db.get("regionais", {}):
        return jsonify({"error": "Regional não encontrada"}), 404
    
    regional = db["regionais"][regional_id]
    
    if sub_id not in regional.get("sub_regionais", {}):
        return jsonify({"error": "Sub-regional não encontrada"}), 404
    
    sub_regional = regional["sub_regionais"][sub_id]
    
    if sub_regional.get("comuns"):
        return jsonify({"error": "Não é possível deletar sub-regional com comuns"}), 400
    
    del regional["sub_regionais"][sub_id]
    save_db(db)
    
    return jsonify({"success": True, "message": "Sub-regional deletada"})

@app.post("/api/regionais/<regional_id>/sub-regionais/<sub_id>/comuns")
@login_required
def criar_comum(regional_id, sub_id):
    """Criar novo comum"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode criar comuns"}), 403
    
    data = request.get_json()
    comum_id = data.get('id')
    comum_nome = data.get('nome')
    config_fornecida = data.get('config', {})
    
    if not comum_id or not comum_nome:
        return jsonify({"error": "ID e nome são obrigatórios"}), 400
    
    db = load_db()
    
    if regional_id not in db.get("regionais", {}):
        return jsonify({"error": "Regional não encontrada"}), 404
    
    regional = db["regionais"][regional_id]
    
    if sub_id not in regional.get("sub_regionais", {}):
        return jsonify({"error": "Sub-regional não encontrada"}), 404
    
    sub_regional = regional["sub_regionais"][sub_id]
    
    if comum_id in sub_regional.get("comuns", {}):
        return jsonify({"error": "Comum já existe"}), 400
    
    if "comuns" not in sub_regional:
        sub_regional["comuns"] = {}
    
    # Configuração padrão
    config_padrao = {
        "periodo": {
            "inicio": date.today().isoformat(),
            "fim": (date.today() + timedelta(days=60)).isoformat()
        },
        "dias_culto": ["Domingo", "Terça"],
        "horarios": {
            "Domingo": ["09:30", "18:00"],
            "Terça": ["20:00"]
        },
        "fechamento_publicacao_dias": 7
    }
    
    # Mesclar configuração fornecida com padrão
    config_final = {**config_padrao, **config_fornecida}
    
    # Criar comum com estrutura padrão
    sub_regional["comuns"][comum_id] = {
        "nome": comum_nome,
        "organistas": [],
        "indisponibilidades": [],
        "escala": [],
        "escala_rjm": [],
        "config": config_final
    }
    
    save_db(db)
    
    return jsonify({
        "success": True,
        "comum": {
            "id": comum_id,
            "nome": comum_nome
        }
    })

@app.get("/api/regionais/<regional_id>/sub-regionais/<sub_id>/comuns/<comum_id>")
@login_required
def get_comum_details(regional_id, sub_id, comum_id):
    """Buscar detalhes de um comum específico"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode acessar"}), 403
    
    db = load_db()
    comum = find_comum_by_id(db, comum_id)
    
    if not comum:
        return jsonify({"error": "Comum não encontrado"}), 404
    
    return jsonify({
        "id": comum.get("id"),
        "nome": comum.get("nome"),
        "config": comum.get("config", {
            "dias_culto": [],
            "horarios": {},
            "fechamento_publicacao_dias": 7
        })
    })

@app.put("/api/regionais/<regional_id>/sub-regionais/<sub_id>/comuns/<comum_id>")
@login_required
def editar_comum(regional_id, sub_id, comum_id):
    """Editar comum existente (nome e config)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode editar comuns"}), 403
    
    data = request.get_json()
    comum_nome = data.get('nome')
    config = data.get('config')
    
    if not comum_nome:
        return jsonify({"error": "Nome é obrigatório"}), 400
    
    db = load_db()
    comum = find_comum_by_id(db, comum_id)
    
    if not comum:
        return jsonify({"error": "Comum não encontrado"}), 404
    
    # Atualizar nome
    comum["nome"] = comum_nome
    
    # Atualizar config se fornecido
    if config:
        if "config" not in comum:
            comum["config"] = {}
        
        if "dias_culto" in config:
            comum["config"]["dias_culto"] = config["dias_culto"]
        
        if "horarios" in config:
            comum["config"]["horarios"] = config["horarios"]
        
        if "fechamento_publicacao_dias" in config:
            comum["config"]["fechamento_publicacao_dias"] = config["fechamento_publicacao_dias"]
    
    save_db(db)
    
    return jsonify({
        "success": True,
        "comum": {
            "id": comum_id,
            "nome": comum_nome,
            "config": comum.get("config", {})
        }
    })

@app.delete("/api/regionais/<regional_id>/sub-regionais/<sub_id>/comuns/<comum_id>")
@login_required
def deletar_comum(regional_id, sub_id, comum_id):
    """Deletar comum (apenas se vazio)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode deletar comuns"}), 403
    
    db = load_db()
    
    if regional_id not in db.get("regionais", {}):
        return jsonify({"error": "Regional não encontrada"}), 404
    
    regional = db["regionais"][regional_id]
    
    if sub_id not in regional.get("sub_regionais", {}):
        return jsonify({"error": "Sub-regional não encontrada"}), 404
    
    sub_regional = regional["sub_regionais"][sub_id]
    
    if comum_id not in sub_regional.get("comuns", {}):
        return jsonify({"error": "Comum não encontrado"}), 404
    
    comum = sub_regional["comuns"][comum_id]
    
    # Verificar se tem dados
    if (comum.get("organistas") or comum.get("escala") or 
        comum.get("escala_rjm") or comum.get("indisponibilidades")):
        return jsonify({"error": "Não é possível deletar comum com dados cadastrados"}), 400
    
    del sub_regional["comuns"][comum_id]
    save_db(db)
    
    return jsonify({"success": True, "message": "Comum deletado"})

# ==================== Gerenciamento de Usuários ====================

@app.get("/api/usuarios")
@login_required
def listar_usuarios():
    """Lista todos os usuários (Master only)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode listar usuários"}), 403
    
    db = load_db()
    usuarios = []
    
    for user_id, user_data in db.get("usuarios", {}).items():
        usuarios.append({
            "id": user_id,
            "nome": user_data.get("nome"),
            "tipo": user_data.get("tipo"),
            "email": user_data.get("email", ""),
            "telefone": user_data.get("telefone", ""),
            "contexto_id": user_data.get("contexto_id", ""),
            "ativo": user_data.get("ativo", True)
        })
    
    return jsonify(usuarios)

@app.post("/api/usuarios")
@login_required
def criar_usuario():
    """Cria novo usuário (Master only)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode criar usuários"}), 403
    
    data = request.get_json()
    user_id = data.get('id')
    nome = data.get('nome')
    tipo = data.get('tipo')
    senha = data.get('senha', 'senha123')
    email = data.get('email', '')
    telefone = data.get('telefone', '')
    contexto_id = data.get('contexto_id', '')
    
    if not all([user_id, nome, tipo]):
        return jsonify({"error": "ID, nome e tipo são obrigatórios"}), 400
    
    if tipo not in ['master', 'admin_regional', 'encarregado_sub_regional', 'encarregado_comum']:
        return jsonify({"error": "Tipo de usuário inválido"}), 400
    
    db = load_db()
    
    if user_id in db.get("usuarios", {}):
        return jsonify({"error": "Usuário já existe"}), 400
    
    if "usuarios" not in db:
        db["usuarios"] = {}
    
    db["usuarios"][user_id] = {
        "id": user_id,
        "nome": nome,
        "password_hash": generate_password_hash(senha),
        "tipo": tipo,
        "email": email,
        "telefone": telefone,
        "contexto_id": contexto_id,
        "ativo": True,
        "data_criacao": datetime.now().isoformat()
    }
    
    save_db(db)
    
    return jsonify({
        "success": True,
        "usuario": {
            "id": user_id,
            "nome": nome,
            "tipo": tipo
        }
    })

@app.put("/api/usuarios/<user_id>")
@login_required
def editar_usuario(user_id):
    """Edita usuário existente (Master only)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode editar usuários"}), 403
    
    data = request.get_json()
    
    db = load_db()
    
    if user_id not in db.get("usuarios", {}):
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    usuario = db["usuarios"][user_id]
    
    # Atualizar campos permitidos
    if 'nome' in data:
        usuario['nome'] = data['nome']
    if 'email' in data:
        usuario['email'] = data['email']
    if 'telefone' in data:
        usuario['telefone'] = data['telefone']
    if 'contexto_id' in data:
        usuario['contexto_id'] = data['contexto_id']
    if 'ativo' in data:
        usuario['ativo'] = data['ativo']
    if 'senha' in data and data['senha']:
        usuario['password_hash'] = generate_password_hash(data['senha'])
    
    save_db(db)
    
    return jsonify({
        "success": True,
        "usuario": {
            "id": user_id,
            "nome": usuario['nome']
        }
    })

@app.delete("/api/usuarios/<user_id>")
@login_required
def deletar_usuario(user_id):
    """Deleta usuário (Master only)"""
    if current_user.tipo != 'master':
        return jsonify({"error": "Apenas Master pode deletar usuários"}), 403
    
    if user_id == 'admin_master':
        return jsonify({"error": "Não é possível deletar o usuário Master principal"}), 400
    
    db = load_db()
    
    if user_id not in db.get("usuarios", {}):
        return jsonify({"error": "Usuário não encontrado"}), 404
    
    del db["usuarios"][user_id]
    save_db(db)
    
    return jsonify({"success": True, "message": "Usuário deletado"})

# ==================== Configuração de Dias de Culto por Comum ====================

@app.get("/api/comuns/<comum_id>/config")
@login_required
def get_comum_config(comum_id):
    """Retorna configurações específicas de um comum"""
    db = load_db()
    comum_result = find_comum_by_id(db, comum_id)
    
    print(f"🔍 [API] GET /api/comuns/{comum_id}/config")
    print(f"  👤 Usuário: {current_user.id} (tipo: {current_user.tipo})")
    print(f"  🔑 Contexto: {current_user.contexto_id}")
    
    if not comum_result:
        print(f"  ❌ Comum '{comum_id}' não encontrado")
        return jsonify({"error": "Comum não encontrado"}), 404
    
    # Extrair o objeto comum do resultado
    comum_data = comum_result['comum']
    print(f"  ✅ Comum encontrado: {comum_data.get('nome', comum_id)}")
    
    # Verificar permissão: admins, master e encarregado da comum
    if not getattr(current_user, 'is_admin', False) and current_user.tipo not in ['master', 'encarregado_comum']:
        print(f"  ❌ Tipo de usuário sem permissão: {current_user.tipo}")
        return jsonify({"error": "Sem permissão"}), 403
    
    # Para encarregados, verificar se têm permissão para acessar esta comum
    if current_user.tipo == 'encarregado_comum':
        # Comparar com chave do dicionário E com ID interno (para compatibilidade)
        comum_id_dict = comum_result['comum_id']
        comum_id_interno = comum_data.get('id', '')
        
        if current_user.contexto_id != comum_id and current_user.contexto_id != comum_id_dict and current_user.contexto_id != comum_id_interno:
            print(f"  ❌ Encarregado tentando acessar comum diferente do seu contexto")
            print(f"     Contexto do usuário: {current_user.contexto_id}")
            print(f"     Comum solicitado: {comum_id}")
            print(f"     Comum chave dict: {comum_id_dict}")
            print(f"     Comum ID interno: {comum_id_interno}")
            return jsonify({"error": "Sem permissão para este comum"}), 403
    
    config = comum_data.get("config", {})
    print(f"  ✅ Config retornada: dias_culto={config.get('dias_culto', [])}")
    return jsonify(config)

@app.put("/api/comuns/<comum_id>/config")
@login_required
def update_comum_config(comum_id):
    """Atualiza configurações específicas de um comum"""
    db = load_db()
    comum_result = find_comum_by_id(db, comum_id)
    
    if not comum_result:
        return jsonify({"error": "Comum não encontrado"}), 404
    
    comum = comum_result['comum']
    
    # Verificar permissão: admins, master e encarregado da comum
    if not getattr(current_user, 'is_admin', False) and current_user.tipo not in ['master', 'encarregado_comum']:
        return jsonify({"error": "Sem permissão"}), 403
    
    # Para encarregados, verificar se têm permissão (comparar com múltiplos IDs)
    if current_user.tipo == 'encarregado_comum':
        comum_id_dict = comum_result['comum_id']
        comum_id_interno = comum.get('id', '')
        
        if current_user.contexto_id != comum_id and current_user.contexto_id != comum_id_dict and current_user.contexto_id != comum_id_interno:
            return jsonify({"error": "Sem permissão para este comum"}), 403
    
    data = request.get_json()
    
    if "config" not in comum:
        comum["config"] = {}
    
    # Atualizar configurações
    if 'periodo' in data:
        comum["config"]["periodo"] = data['periodo']
    if 'dias_culto' in data:
        comum["config"]["dias_culto"] = data['dias_culto']
    if 'horarios' in data:
        comum["config"]["horarios"] = data['horarios']
    if 'fechamento_publicacao_dias' in data:
        comum["config"]["fechamento_publicacao_dias"] = data['fechamento_publicacao_dias']
    
    save_db(db)
    
    return jsonify({
        "success": True,
        "config": comum["config"]
    })

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
