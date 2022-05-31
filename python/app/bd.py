##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2021/2022 ===============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors: 
##   João Dionísio <uc2019217030@student.uc.pt>
##   Liu Haolong <uc20182880188@student.uc.pt>
##   Dário Manhanga <uc2018303352@student.uc.pt>
##   University of Coimbra

 
from itertools import product
from multiprocessing import parent_process
from flask import Flask, jsonify, request
import logging, psycopg2, time, config
import jwt
import datetime
from datetime import datetime


app = Flask(__name__)

app.config['SECRET_KEY'] =  'segredo' #for encoding/decoding jwt tokens
app.config['ALGORITHM'] ='HS256' #for decoding jwt tokens


##########################################################
## ENDPOINTS
##########################################################


@app.route('/dbproj/') 
def landing_page():
    return """

    Hello World (Python Native)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2022 Team<br/>
    <br/>
    """

##   Adiciona subscricao em campanha
##   http://localhost:8080/dbproj/produtos/subscribe/<campanha_id>    methods=['PUT']  
@app.route("/dbproj/produtos/subscribe/<campanha_id>", methods=['PUT'])
def subscricao(campanha_id):
    logger.info("###              DEMO: PUT /dbproj/produtos/subscribe/<campanha_id>           ###")

    conn = db_connection()
    cur = conn.cursor()
    payload=[]
    payload= request.get_json()

    if "token" in payload:
        token = payload["token"]
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
        except:
            return jsonify({'message':'Token invalido'}),403

        username = data["user_name"]                
        cur.execute("SELECT utilizador_user_name FROM comprador WHERE utilizador_user_name = %s", (username,))
        comprador=cur.fetchall()
        if len(comprador) == 0:
            return 'Precisa ser comprador\n'
    else:
        return 'token needed to create new order\n'

    logger.info("---- submissão em uma campanha  ----")
    logger.debug(f'payload: {payload}')

    cur.execute("select ativo from campanha where id = %s", (campanha_id))
    checkAtivo = cur.fetchall()
    if not checkAtivo[0][0]:
        return 'Campanha inativa\n'

    statement1 = """INSERT INTO comprador_campanha (comprador_utilizador_user_name, campanha_id)
        VALUES (%s,%s)"""
    values1 = (username, campanha_id)
    try:
        cur.execute(statement1, values1)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'O utilizador já se inscreveu na campanha\n'
        return result

    cur.execute("select MAX(id) from cupao")
    cupaoAtual = cur.fetchall()

    statement2 = """INSERT INTO comprador_cupao (comprador_utilizador_user_name, cupao_id)
        VALUES (%s,%s)"""
    values2 = (username, cupaoAtual[0])

    statement3 = """INSERT INTO campanha_cupao (campanha_id, cupao_id)
        VALUES (%s,%s)"""
    values3 = (campanha_id, cupaoAtual[0])

    try:
        cur.execute(statement2, values2)
        cur.execute(statement3, values3)
        cur.execute("commit")
        cur.execute("select id, validade from cupao where id = %s", (cupaoAtual[0],))
        tmp = cur.fetchall()
        result = {'status':200, 'results':{'coupon_id':tmp[0][0], 'expiration_date':tmp[0][1]}}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500, 'message':error}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


##   Adiciona campanha
##   http://localhost:8080/dbproj/produtos/campaign     methods=['POST']
@app.route("/dbproj/produtos/campaign", methods=['POST'])
def get_campanha():
    logger.info("###              DEMO: POST /dbproj/produtos/campaign           ###")

    conn = db_connection()
    cur = conn.cursor()
    payload=[]
    payload= request.get_json()

    cur.execute("SELECT ativo FROM campanha where ativo = true")
    tmp = cur.fetchall()

    if len(tmp)!=0:
        now = datetime.now()
        cur.execute("SELECT * FROM campanha WHERE ativo = TRUE AND fim < %s", (now,)) #se está dentro de validade
        tmp = cur.fetchall()
        if len(tmp) == 0:
            return jsonify({'status':400, 'message':'Existe uma campanha ativa\n'})
        else:
            cur.execute("UPDATE campanha SET ativo = FALSE where ativo = TRUE")

    if "token" in payload:
        token = payload["token"]
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
        except:
            return jsonify({'status':400, 'message':'Token invalido\n'})

        username = data["user_name"]                #verificar se é admin
        cur.execute("SELECT utilizador_user_name FROM administrador WHERE utilizador_user_name = %s", (username,))
        administrador=cur.fetchall()
        if len(administrador) == 0:
           return jsonify({'status':400, 'message':'Precisa de ser admin\n'})
    else:
        return jsonify({'status':400, 'message':'Token necessario\n'})

    logger.info("---- nova campanha  ----")
    logger.debug(f'payload: {payload}')

    statement = """INSERT INTO campanha (descricao, inicio, fim, n_cupoes, desconto, administrador_utilizador_user_name, ativo, n_cupoes_emitidos)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""

    at = datetime.now()

    values = (payload["descricao"], at, payload["fim"], payload["n_cupoes"],payload["desconto"], username, "true", 0)
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        cur.execute("SELECT Max(Id) FROM campanha")
        content = cur.fetchall()
        result = {'status':200, 'id':content[0]}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500, 'message':'Failed!'}
        return result
    finally:
        if conn is not None:
            conn.close()
    
    conn.close ()

    return jsonify(result)

##   Devolve todas as notificacoes do utilizador especificado no token
##   http://localhost:8080/dbproj/product       methods=['GET']
@app.route("/dbproj/notificacao/", methods=['GET'], strict_slashes=True)               
def get_all_notificacao():
    logger.info("###              DEMO: GET /dbproj/notificacao/             ###");

    conn = db_connection()
    payload = request.get_json()
    cur = conn.cursor()
    
    if "token" in payload:
        token = payload["token"]
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
        except:
            return jsonify({'status':400, 'message':'Token invalido'})

        username = data["user_name"]
    else:
        return jsonify({'status':400, 'message':'Presisa-se token'})


    cur.execute("SELECT descricao, data FROM notificacao WHERE utilizador_user_name = %s", (username,))
    rows = cur.fetchall()

    payload = []
    payload.append({'status':200})
    logger.debug("---- produto  ----")
    for row in rows:
        logger.debug(row)
        content = {'descricao': row[0], 'data': row[1]}
        payload.append(content) 
    
    return jsonify(payload)

##   Devolve o nome de utilizador e o email de todos os utilizadores
##   http://localhost:8080/dbproj/user      methods=['GET']
@app.route("/dbproj/user/", methods=['GET'], strict_slashes=True)               
def get_all_user():
    logger.info("###              DEMO: GET /dbproj/user             ###");

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT user_name, email FROM utilizador")
    rows = cur.fetchall()

    payload = []
    payload.append({'status':200})
    logger.debug("---- user  ----")
    for row in rows:
        logger.debug(row)
        content = {'utilizador user_name': row[0], 'email': row[1]}
        payload.append(content)
    
    return jsonify(payload)

##   Devolve o id e o nome do vendedor de todos os produtos
##   http://localhost:8080/dbproj/product       methods=['GET']
@app.route("/dbproj/product/", methods=['GET'], strict_slashes=True)               
def get_all_produto():
    logger.info("###              DEMO: GET /dbproj/product             ###");

    conn = db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, vendedor_utilizador_user_name FROM produto")
    rows = cur.fetchall()

    payload = []
    payload.append({'status':200})
    logger.debug("---- produto  ----")
    for row in rows:
        logger.debug(row)
        content = {'id': row[0], 'vendedor_user_name': row[1]}
        payload.append(content)
    
    return jsonify(payload)


##   Devolve as estatisticas das campanhas
##   http://localhost:8080/dbproj/report/campaign       methods=['GET']
@app.route("/dbproj/report/campaign", methods=['GET'])
def get_stats_campanha():
    logger.info("###              DEMO: GET /dbproj/report/campaign          ###")

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- Get estatisticas de campanha ----")

    cur.execute("SELECT json_build_object( 'campaign_id' , id , 'generated_coupons' , n_cupoes_emitidos, 'used_coupons' , (SELECT COUNT(*) FROM cupao_encomenda AS ce INNER JOIN campanha_cupao AS cc ON ce.cupao_id = cc.cupao_id WHERE cc.campanha_id = id), 'total_discount_value', (SELECT COALESCE(SUM(quantidade * preco * (desconto/100)), -1) FROM produto AS p INNER JOIN produto_encomenda AS pe ON pe.produto_id = id INNER JOIN cupao_encomenda AS ce ON ce.encomenda_n_encomenda = pe.encomenda_n_encomenda INNER JOIN cupao AS c ON c.id = ce.cupao_id INNER JOIN campanha_cupao AS cc ON ce.cupao_id = cc.cupao_id WHERE cc.campanha_id = campanha.id)) FROM campanha  ")

    rows = cur.fetchall()
    payload = []


    if not rows:    
        content = {'Erro' : "400"}
        payload.append(content)
    else:
        payload.append({'status':200})
        for row in rows:
            logger.debug(row)
            content = {'results':row[0]}
            payload.append(content)


    conn.close ()
    return jsonify(payload)

##   Devolve as estatisticas das encomendas
##   http://localhost:8080/proj/report/year     methods=['GET']
@app.route("/proj/report/year", methods=['GET'])                                
def get_stats():
    logger.info("###              DEMO: GET /proj/report/year           ###")

    conn = db_connection()
    cur = conn.cursor()   

    cur.execute("SELECT json_build_object('month', EXTRACT(MONTH FROM data), 'orders',  COUNT(*), 'total_value', (SELECT SUM(preco*pe.quantidade) FROM produto INNER JOIN produto_encomenda AS pe ON id = pe.produto_id INNER JOIN encomenda AS e ON e.n_encomenda = pe.encomenda_n_encomenda AND EXTRACT(MONTH FROM e.data) = EXTRACT(MONTH FROM data))) FROM encomenda GROUP BY EXTRACT(MONTH FROM data)") #por o preco só deste mes
    rows = cur.fetchall()
    payload = []

    if not rows:    
        content = {'Erro' : "400"}
        payload.append(content)
    else:
        payload.append({'status':200})
        for row in rows:
            logger.debug(row)
            content = {'results':row[0]}
            payload.append(content)

    conn.close ()
    return jsonify(payload)


##   Devolve os dados estatisticos de um produto especificado pelo seu id
##   http://localhost:8080/dbproj/produtos/<produtoid>      methods=['GET']
@app.route("/dbproj/produtos/<produtoid>", methods=['GET'])                                
def get_produto(produtoid):
    logger.info("###              DEMO: GET /dbproj/produtos/<produtoid>           ###")

    logger.debug(f'produto: {produtoid}')

    conn = db_connection()
    cur = conn.cursor()   


    cur.execute("SELECT produto.stock, produto.titulo, produto.descricao, json_agg( DISTINCT CONCAT(pv.data, ' - ', pv.preco)), COALESCE(AVG(classificacao),-1), json_agg(DISTINCT COALESCE(comentario,'None')) FROM produto LEFT OUTER JOIN rating ON rating.produto_id = id LEFT OUTER JOIN produtoversoes AS pv ON pv.produto_id = id where id = %s GROUP BY (id)", (produtoid,) )

    rows = cur.fetchall()
    payload = []

    
    if not rows:
        payload.append({'status':400})
        content = {'Erro' : "Nenhum produto encontrado"}
        payload.append(content)
    else:
        payload.append({'status':200})
        for row in rows:
            logger.debug(row)
            content = {'stock':row[0], 'titulo': row[1], 'descricao': row[2], 'preco': row[3], 'rating': row[4], 'comentario': row[5]}
            payload.append(content)

    conn.close ()
    return jsonify(payload)


##   Regista um utilizador. admin = 1 (administrador) || admin = 2 (comprador) || admin = 3 (vendedor)
##   http://localhost:8080/dbproj/user/     methods=['POST','GET']
@app.route("/dbproj/user/", methods=['POST','GET'], strict_slashes=True) 
def add_user():
    logger.info("###              DEMO: POST /dbproj/user/            ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    if "user_name" not in payload or "email" not in payload or "password" not in payload or "admin" not in payload:
        return jsonify({'status':400, 'message':'user_name, email, password and admin needed to create new user\n'})
    
    if "token" in payload:
        token = payload["token"]
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
        except:
            return jsonify({'status':400, 'message':'token invalido\n'})

        username = data["user_name"]               
        cur.execute("SELECT utilizador_user_name FROM administrador WHERE utilizador_user_name = %s", (username,))
        admin=cur.fetchall()


    if payload["admin"] == 1:
        if "token" not in payload:
            return jsonify({'status':400, 'message':'Necessario token\n'})
        if len(admin)!=0:

            cur.execute("INSERT INTO utilizador (user_name, password, email) VALUES (%s,%s,%s)", (payload["user_name"], payload["password"],payload["email"]))

            logger.info("---- new administrador  ----")          
            logger.debug(f'payload: {payload}')

            statement = """
                        INSERT INTO administrador (utilizador_user_name)
                                VALUES (%s)"""

            values = (payload["user_name"])
        else:
            return jsonify({'status':400, 'message':'Necessario ser admin\n'}) 

    elif payload["admin"] == 2:

        cur.execute("INSERT INTO utilizador (user_name, password, email) VALUES (%s,%s,%s)", (payload["user_name"], payload["password"],payload["email"]))
        logger.info("---- new comprador  ----")          
        logger.debug(f'payload: {payload}')

        statement = """
                    INSERT INTO comprador (utilizador_user_name, morada)
                            VALUES (%s, %s)"""

        values = (payload["user_name"], payload["morada"])
    elif payload["admin"] == 3:
        if "token" not in payload:
            return jsonify({'status':400, 'message':'Necessario ser Admin\n'})
        
        if len(admin)!=0:
            cur.execute("INSERT INTO utilizador (user_name, password, email) VALUES (%s,%s,%s)", (payload["user_name"], payload["password"],payload["email"]))
            logger.info("---- new vendedor  ----")          
            logger.debug(f'payload: {payload}')

            statement = """
                        INSERT INTO vendedor (utilizador_user_name, nif, morada_de_envio)
                                VALUES (%s,%s,%s)"""

            values = (payload["user_name"],payload["nif"], payload["morada"])
        else:
            return jsonify({'status':400, 'message':'Necessario ser Admin\n'})
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = {'status':200, 'user_name': payload["user_name"]}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500, 'message':error}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


##   Adiciona um produto
##   http://localhost:8080/dbproj/product/      methods=['POST','GET']
@app.route("/dbproj/product/", methods=['POST','GET'], strict_slashes=True) 
def add_product():
    logger.info("###              DEMO: POST /dbproj/product/            ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    

    if "type" not in payload or "preco" not in payload or "stock" not in payload or "titulo" not in payload or "descricao" not in payload or "token" not in payload:
        return jsonify({'status':400, 'message':'token, type, preco, stock and titulo needed to create new product\n'})


    token = payload["token"]
    try:
        data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
    except:
        return jsonify({'status':400, 'message':'token invalido\n'})

    username = data["user_name"]
    cur.execute("SELECT utilizador_user_name FROM vendedor WHERE utilizador_user_name = %s", (username,))
    vendedor=cur.fetchall()
    if len(vendedor)==0:
        return jsonify({'status':400, 'message':'Necessita ser vendedor\n'})

    logger.info("---- new produto  ----")          
    logger.debug(f'payload: {payload}')


    cur.execute("INSERT INTO produto (vendedor_utilizador_user_name, descricao, preco, stock, titulo) VALUES ( %s, %s,%s,%s,%s)", (username, payload["descricao"], float(payload["preco"]), int(payload["stock"]) ,payload["titulo"]))
    cur.execute("INSERT INTO produtoversoes (descricao, preco, titulo,produto_id, data) VALUES ( %s, %s,%s,(SELECT MAX(id) FROM produto),CURRENT_TIMESTAMP)", (payload["descricao"], float(payload["preco"]), payload["titulo"]))


    if payload["type"] == "smartphone":
        if "modelo" not in payload:
            return jsonify({'status':400, 'message':'modelo needed to create new product\n'})

        logger.info("---- new smartphone  ----")    
        statement = """
                INSERT INTO smartphone (modelo, produto_id)
                        VALUES ( %s, (SELECT MAX(id) FROM produto))"""

        values = (payload["modelo"],)
    elif payload["type"] == "computador":
        if "processador" not in payload:
            return jsonify({'status':400, 'message':'processador needed to create new product\n'})


        logger.info("---- new computador  ----") 
        statement = """
                INSERT INTO computador (processador, produto_id)
                        VALUES (%s, (SELECT MAX(id) FROM produto))"""

        values = (payload["processador"],)
    elif payload["type"] == "televisao":
        if "tamanho" not in payload:
            return jsonify({'status':400, 'message':'tamanho needed to create new product\n'})

        logger.info("---- new televisao  ----") 
        statement = """
                INSERT INTO televisao (tamanho, produto_id)
                        VALUES (%s, (SELECT MAX(id) FROM produto))"""

        values = (payload["tamanho"],)

    
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        cur.execute("select MAX(id) from produto")
        tmp = cur.fetchall()
        result = {'status':200, 'id': tmp[0][0]}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {status:500, 'message':error}
    finally:
        if conn is not None:
            conn.close()

    if conn is not None:
        conn.close()

    return jsonify(result)


##   Faz o login
##   http://localhost:8080/dbproj/user      methods=['PUT','GET']
@app.route("/dbproj/user", methods=['PUT','GET'])
def loggin_user():
    logger.info("###              DEMO: PUT /dbproj/user              ###")
    content = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if "user_name" not in content or "password" not in content:                  
       return jsonify({'status':400, 'message':'username and password needed to login\n'})

    logger.info("---- login user ----")
    logger.debug(f'payload: {content}')
    statement = """
                  SELECT * FROM utilizador
                          WHERE user_name = %s and password = %s"""

    values = (content['user_name'],content['password'])
    cur.execute(statement,values)
    row = cur.fetchall()
    payload = []
    if not row :
        payload.append({'status':400})
        content = {'message': "user_name or password wrong"}
        payload.append(content)
    else:
        payload.append({'status':200})
        authToken = jwt.encode({'user_name': content['user_name'],'password':content['password']},app.config['SECRET_KEY'])
        payload.append(authToken) 
        payload.append("GUARDAR ESTE TOKEN PARA OPERACOES FUTURAS")
    conn.close()
    return jsonify(payload)


##   Adiciona pergunta ao produto
##   http://localhost:8080/dbproj/questions/<produtoId>     methods=['POST','GET']
@app.route("/dbproj/questions/<produtoId>", methods=['POST','GET'], strict_slashes=True) 
def add_comment(produtoId):
    logger.info("###              DEMO: POST /dbproj/questions/<produtoId>         ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    if "token" not in payload or "question" not in payload:
        return jsonify({'status':400, 'message':'token and question needed to make a comment\n'})
    
    token = payload["token"]
    try:
        data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
    except: 
       return jsonify({'status':400, 'message':'token invalido\n'})

    username = data["user_name"]
    logger.info("---- new comentario  ----")          
    logger.debug(f'payload: {payload}')

    statement = """INSERT INTO comentario (comentario, data, utilizador_user_name, produto_id)
        VALUES (%s,%s,%s,%s)"""


    ct = datetime.now()

    values = (payload["question"], ct, username,int(produtoId))
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        cur.execute("select max(id) from comentario")
        tmp = cur.fetchall()
        result = {'status':200, 'results': tmp[0][0]}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500, 'message':error}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

##   Adiciona resposta a pergunta ao produto
##   http://localhost:8080/dbproj/questions/<produtoId>/<parent_question_id>    methods=['POST','GET']
@app.route("/dbproj/questions/<produtoId>/<parent_question_id>", methods=['POST','GET'], strict_slashes=True) 
def add_comment_to_comment(produtoId, parent_question_id):
    logger.info("###              DEMO: POST /dbproj/questions/<produtoId>         ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    if "token" not in payload or "question" not in payload:
        return jsonify({'status':400, 'message':'username and password needed to login\n'})
    
    token = payload["token"]
    try:
        data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
    except: 
        return jsonify({'status':400, 'message':'token\n'})

    username = data["user_name"]
    logger.info("---- new comentario  ----")          
    logger.debug(f'payload: {payload}')

    statement = """INSERT INTO comentario (comentario, data, utilizador_user_name, produto_id, comentario_id)
        VALUES (%s,%s,%s,%s,%s)"""


    ct = datetime.now()

    values = (payload["question"], ct, username,int(produtoId), int(parent_question_id))
    try:
        cur.execute(statement, values)
        cur.execute("commit")
        cur.execute("select MAX(id) from comentario")
        tmp = cur.fetchall()
        result = {'status':200, 'id:':tmp[0][0]}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500,'message':error}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)



##   Adiciona encomenda
##   http://localhost:8080/dbproj/order/    methods=['POST','GET']
@app.route("/dbproj/order/", methods=['POST','GET'], strict_slashes=True) 
def add_order():
    logger.info("###              DEMO: POST /dbproj/order/            ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if "token" in payload:
        token = payload["token"]
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
        except:
            return jsonify({'status':400, 'message':'Token invalido'})

        username = data["user_name"]
        cur.execute("SELECT utilizador_user_name FROM comprador WHERE utilizador_user_name = %s", (username,))
        comprador=cur.fetchall()
        if len(comprador) == 0:
            return jsonify({'status':400, 'message':'Necessita ser comprador'})
    else:
        return jsonify({'status':400, 'message':'Token necessario'})

    if "cart" not in payload:
        return jsonify({'status':400, 'message':'cart ncessario para fazer pedido'})

    if "coupon" in payload:
        cur.execute("select * from comprador_cupao where (comprador_utilizador_user_name = %s AND cupao_id = %s)",(username, payload["coupon"]))
        couponUser = cur.fetchall()
        if len(couponUser) == 0:
            return jsonify({'status':400, 'message':'O cupao nao existe ou nao pertence ao utilizador'})
        dataAtual = datetime.now()
        cur.execute("select * from cupao where id = %s AND validade < %s",(payload["coupon"], dataAtual,))
        couponValidade = cur.fetchall()
        if len(couponValidade) == 0:
            return jsonify({'status':400, 'message':'O cupao esta fora de validade'})
        cur.execute("select * from cupao_encomenda where cupao_id = %s",(payload["coupon"],))
        couponUsed = cur.fetchall()
        if len(couponUsed) != 0:
            return jsonify({'status':400, 'message':'O cupao ja foi utilizado'})


    logger.info(payload["cart"][0][0])
    logger.info("---- new order  ---- :")          
    logger.debug(f'payload: {payload}')

    statement = """
                    INSERT INTO encomenda (comprador_utilizador_user_name, data)
                            VALUES (%s, CURRENT_TIMESTAMP) RETURNING n_encomenda"""

    values = (username,)
    n_order = -1
    try:
        cur.execute(statement, values)
        n_order = int(cur.fetchone()[0])
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500, 'message':error}

    if "coupon" in payload:
        cur.execute("INSERT INTO cupao_encomenda (cupao_id, encomenda_n_encomenda) VALUES (%s,%s)",(int(payload["coupon"]),n_order))

        
    for i in range(len(payload["cart"])):
        statement = """
                    INSERT INTO produto_encomenda (produto_id, quantidade, encomenda_n_encomenda) 
                            VALUES (%s, %s, %s);
                    UPDATE produto SET stock = stock - %s where id = %s;"""

        values = (payload["cart"][i][0], payload["cart"][i][1], n_order, payload["cart"][i][1], payload["cart"][i][0])
        try:
            cur.execute(statement, values)
            cur.execute("commit")
            cur.execute("select MAX(n_encomenda) from encomenda")
            tmp = cur.fetchall()
            result = {'status':200, 'results:':tmp[0][0]}
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            result = {'status':500, 'message':error}

    
    if conn is not None:
        conn.close()

    return jsonify(result)
    
##   adiciona feedback ao produto
##   http://localhost:8080/dbproj/rating/<produtoId>    methods=['POST','GET']
@app.route("/dbproj/rating/<produtoId>", methods=['POST','GET'], strict_slashes=True)
def add_feedback(produtoId):
    logger.info("###              DEMO: POST /dbproj/rating/<productId>            ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    if "token" in payload:
        token = payload["token"]
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
        except:
            result = {'status':400, 'message':'Token invalido'}

        username = data["user_name"]                
        cur.execute("SELECT utilizador_user_name FROM comprador WHERE utilizador_user_name = %s", (username,))
        comprador=cur.fetchall()
        if len(comprador) == 0:
            return jsonify({'status':400, 'message':'Necessita ser comprador'})
    else:
        return jsonify({'status':400, 'message':'Necessario token para criar nova avaliacao'})

    if "comentario" not in payload or "rating" not in payload:
        return jsonify({'status':400, 'message':'Comentario e rating necessario'})

    logger.info("---- feedback  ----")
    logger.debug(f'payload: {payload}')

    if payload["rating"] > 5 or payload["rating"] < 0:
        return jsonify({'status':400, 'message':'Rating invalido'})
    
    statement = """
                    INSERT INTO rating(classificacao, comentario, comprador_utilizador_user_name, produto_id) 
                            VALUES ( %s, %s, %s, %s)"""
    values = (int(payload["rating"]),payload["comentario"], username, int(produtoId))

    try:

        cur.execute(statement, values)
        cur.execute("commit")
        result = {'status':200}
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500, 'message':error}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)


##   Altera os detalhes relativos ao produto
##   http://localhost:8080/dbproj/produto/change/<produtoId>    methods=['PUT']
@app.route("/dbproj/produto/change/<produtoId>", methods=['PUT'])
def product_change_details(produtoId):

    logger.info("###              DEMO: PUT /dbproj/produto/{produtoId}              ###");    
    conn = db_connection()
    cur = conn.cursor()
    payload=[]
    payload= request.get_json()

    logger.info("---- new informacao  ----")          
    logger.debug(f'payload: {payload}')

    if "token" in payload:
        token = payload["token"]
        try:
            data = jwt.decode(token,app.config['SECRET_KEY'],app.config['ALGORITHM'])
        except:
            return jsonify({'status':400, 'message':'Token invalido'})

        username = data["user_name"]
        cur.execute("SELECT utilizador_user_name FROM administrador WHERE utilizador_user_name = %s", (username,))
        admin=cur.fetchall()

        if len(admin) == 0:
            return jsonify({'status':400, 'message':'Necessario ser admin'})
    else:
        return jsonify({'status':400, 'message':'Necessario ter token'})

    if "newTitulo" not in payload or "newDescricao" not in payload or "newPreco" not in payload :
            return jsonify({'status':400, 'message':'newTitulo, newDescricao e newPreco necessarios para criar produto'})

    statement = """
                call newProdutoVersao(%s,%s,%s,%s)"""

    values = (payload["newDescricao"], float(payload["newPreco"]),payload["newTitulo"], produtoId)
    

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result={'status':200}
            
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = {'status':500, 'message':error}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(user = config.user,
                            password = config.password,
                            host = config.host,
                            port = config.port,
                            database = config.database)
    return db

##########################################################
## MAIN
##########################################################
if __name__ == "__main__":

    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                              '%H:%M:%S')
                              # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    time.sleep(1) # just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" +
                  "API v1.0 online: http://localhost:8080/dbproj\n\n")




    app.run(host="0.0.0.0", debug=True)