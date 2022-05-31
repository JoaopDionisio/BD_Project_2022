CREATE TABLE produto (
	id				 bigserial,
	descricao			 VARCHAR(512) NOT NULL,
	preco			 FLOAT(8) NOT NULL,
	titulo			 VARCHAR(512) NOT NULL,
	stock			 BIGINT NOT NULL,
	vendedor_utilizador_user_name VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE televisao (
	tamanho	 FLOAT(8),
	produto_id BIGINT,
	PRIMARY KEY(produto_id)
);

CREATE TABLE vendedor (
	nif			 BIGINT NOT NULL,
	morada_de_envio	 VARCHAR(512) NOT NULL,
	utilizador_user_name VARCHAR(512),
	PRIMARY KEY(utilizador_user_name)
);

CREATE TABLE comprador (
	morada		 VARCHAR(512),
	utilizador_user_name VARCHAR(512),
	PRIMARY KEY(utilizador_user_name)
);

CREATE TABLE administrador (
	utilizador_user_name VARCHAR(512),
	PRIMARY KEY(utilizador_user_name)
);

CREATE TABLE encomenda (
	n_encomenda			 bigserial NOT NULL,
	data				 TIMESTAMP NOT NULL,
	comprador_utilizador_user_name VARCHAR(512) NOT NULL,
	PRIMARY KEY(n_encomenda)
);

CREATE TABLE rating (
	classificacao INTEGER NOT NULL,
	comentario	 VARCHAR(512),
	produto_id	 BIGINT NOT NULL,
	comprador_utilizador_user_name VARCHAR(512) NOT NULL,
	PRIMARY KEY(produto_id, comprador_utilizador_user_name)
);

CREATE TABLE comentario (
	id				 bigserial,
	comentario			 VARCHAR(512) NOT NULL,
	data				 TIMESTAMP NOT NULL,
	utilizador_user_name		 VARCHAR(512),
	produto_id			 BIGINT,
	comentario_id			 BIGINT,
	PRIMARY KEY(id)
);

CREATE TABLE notificacao (
	descricao		 VARCHAR(512) NOT NULL,
	data		 TIMESTAMP NOT NULL,
	numero		 bigserial,
	utilizador_user_name VARCHAR(512),
	PRIMARY KEY(numero,utilizador_user_name)
);

CREATE TABLE utilizador (
	user_name VARCHAR(512),
	password	 VARCHAR(512) NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	PRIMARY KEY(user_name)
);

CREATE TABLE computador (
	processador VARCHAR(512),
	produto_id	 BIGINT,
	PRIMARY KEY(produto_id)
);

CREATE TABLE smartphone (
	modelo	 VARCHAR(512),
	produto_id BIGINT,
	PRIMARY KEY(produto_id)
);

CREATE TABLE produtoversoes (
	descricao		 VARCHAR(512) NOT NULL,
	preco		 FLOAT(8) NOT NULL,
	titulo		 VARCHAR(512) NOT NULL,
	produto_id BIGINT NOT NULL,
	data				 TIMESTAMP NOT NULL,
	PRIMARY KEY(produto_id,titulo,preco,descricao)
);


CREATE TABLE produto_encomenda (
	produto_id		 BIGINT  NOT NULL,
	quantidade		BIGINT NOT NULL,		/*Acrescentamos*/
	encomenda_n_encomenda BIGINT NOT NULL,
	PRIMARY KEY(encomenda_n_encomenda,produto_id)
);

CREATE TABLE campanha (
	inicio				 TIMESTAMP,
	fim				 TIMESTAMP NOT NULL,
	n_cupoes				 BIGINT NOT NULL,
	desconto				 FLOAT(8) NOT NULL,
	descricao				 VARCHAR(512) NOT NULL,
	id				 bigserial,
	ativo				 boolean NOT NULL,
	n_cupoes_emitidos			 BIGINT NOT NULL,
	administrador_utilizador_user_name VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE cupao (
	desconto FLOAT(8) NOT NULL,
	validade TIMESTAMP NOT NULL,
	id	 bigserial,
	PRIMARY KEY(id)
);

CREATE TABLE cupao_encomenda (
	cupao_id		 BIGINT,
	encomenda_n_encomenda BIGINT UNIQUE NOT NULL,
	PRIMARY KEY(cupao_id)
);

CREATE TABLE comprador_cupao (
	comprador_utilizador_user_name VARCHAR(512) NOT NULL,
	cupao_id			 BIGINT NOT NULL,
	PRIMARY KEY(cupao_id)
);

CREATE TABLE comprador_campanha (
	comprador_utilizador_user_name VARCHAR(512) NOT NULL,
	campanha_id			 BIGINT NOT NULL,
	PRIMARY KEY(comprador_utilizador_user_name, campanha_id)--combinacao dos dois
);

CREATE TABLE campanha_cupao (
	campanha_id BIGINT NOT NULL,
	cupao_id	 BIGINT NOT NULL,
	PRIMARY KEY(cupao_id)
);

ALTER TABLE produto ADD CONSTRAINT produto_fk1 FOREIGN KEY (vendedor_utilizador_user_name) REFERENCES vendedor(utilizador_user_name);
ALTER TABLE televisao ADD CONSTRAINT televisao_fk1 FOREIGN KEY (produto_id) REFERENCES produto(id);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (utilizador_user_name) REFERENCES utilizador(user_name);
ALTER TABLE comprador ADD CONSTRAINT comprador_fk1 FOREIGN KEY (utilizador_user_name) REFERENCES utilizador(user_name);
ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (utilizador_user_name) REFERENCES utilizador(user_name);
ALTER TABLE encomenda ADD CONSTRAINT encomenda_fk1 FOREIGN KEY (comprador_utilizador_user_name) REFERENCES comprador(utilizador_user_name);
ALTER TABLE rating ADD CONSTRAINT rating_fk1 FOREIGN KEY (produto_id) REFERENCES produto(id);
ALTER TABLE rating ADD CONSTRAINT rating_fk2 FOREIGN KEY (comprador_utilizador_user_name) REFERENCES utilizador(user_name);	/*acrescentamos isto ao diagrama*/
ALTER TABLE comentario ADD CONSTRAINT comentario_fk1 FOREIGN KEY (utilizador_user_name) REFERENCES utilizador(user_name);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk2 FOREIGN KEY (produto_id) REFERENCES produto(id);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk3 FOREIGN KEY (comentario_id) REFERENCES comentario(id);
ALTER TABLE notificacao ADD CONSTRAINT notificacao_fk1 FOREIGN KEY (utilizador_user_name) REFERENCES utilizador(user_name);
ALTER TABLE computador ADD CONSTRAINT computador_fk1 FOREIGN KEY (produto_id) REFERENCES produto(id);
ALTER TABLE smartphone ADD CONSTRAINT smartphone_fk1 FOREIGN KEY (produto_id) REFERENCES produto(id);
ALTER TABLE produtoversoes ADD CONSTRAINT produtoversoes_fk1 FOREIGN KEY (produto_id) REFERENCES produto(id);
ALTER TABLE produto_encomenda ADD CONSTRAINT produto_encomenda_fk1 FOREIGN KEY (produto_id) REFERENCES produto(id);
ALTER TABLE produto_encomenda ADD CONSTRAINT produto_encomenda_fk2 FOREIGN KEY (encomenda_n_encomenda) REFERENCES encomenda(n_encomenda);

ALTER TABLE campanha ADD CONSTRAINT campanha_fk1 FOREIGN KEY (administrador_utilizador_user_name) REFERENCES administrador(utilizador_user_name);
ALTER TABLE cupao_encomenda ADD CONSTRAINT cupao_encomenda_fk1 FOREIGN KEY (cupao_id) REFERENCES cupao(id);
ALTER TABLE cupao_encomenda ADD CONSTRAINT cupao_encomenda_fk2 FOREIGN KEY (encomenda_n_encomenda) REFERENCES encomenda(n_encomenda);
ALTER TABLE comprador_cupao ADD CONSTRAINT comprador_cupao_fk1 FOREIGN KEY (comprador_utilizador_user_name) REFERENCES comprador(utilizador_user_name);
ALTER TABLE comprador_cupao ADD CONSTRAINT comprador_cupao_fk2 FOREIGN KEY (cupao_id) REFERENCES cupao(id);
ALTER TABLE comprador_campanha ADD CONSTRAINT comprador_campanha_fk1 FOREIGN KEY (comprador_utilizador_user_name) REFERENCES comprador(utilizador_user_name);
ALTER TABLE comprador_campanha ADD CONSTRAINT comprador_campanha_fk2 FOREIGN KEY (campanha_id) REFERENCES campanha(id);
ALTER TABLE campanha_cupao ADD CONSTRAINT campanha_cupao_fk1 FOREIGN KEY (campanha_id) REFERENCES campanha(id);
ALTER TABLE campanha_cupao ADD CONSTRAINT campanha_cupao_fk2 FOREIGN KEY (cupao_id) REFERENCES cupao(id);

INSERT INTO utilizador (user_name, password, email) values ('Ricardo', 'ric3000', 'ricardorei@gmail.com');
INSERT INTO administrador (utilizador_user_name) VALUES ('Ricardo');
INSERT INTO utilizador (user_name, password, email) values ('Jose', 'jose3000', 'joserei@gmail.com');
INSERT INTO administrador (utilizador_user_name) VALUES ('Jose');
INSERT INTO utilizador (user_name, password, email) values ('Joao', 'jonas3000', 'joaorei@gmail.com');
INSERT INTO comprador (morada, utilizador_user_name) VALUES ('47, Rua da Alameda', 'Joao');
INSERT INTO utilizador (user_name, password, email) values ('Maria', 'mary3000', 'mariarei@gmail.com');
INSERT INTO comprador (morada, utilizador_user_name) VALUES ('39, Rua do Gas', 'Maria');
INSERT INTO utilizador (user_name, password, email) values ('Tia do Pedroso', 'Adoro o pedroso', 'pedrosao3000@gmail.com');
INSERT INTO vendedor (nif, morada_de_envio, utilizador_user_name) VALUES (39932929, 'rua da mae do pedroso', 'Tia do Pedroso');
INSERT INTO produto (vendedor_utilizador_user_name, descricao, preco, stock, titulo) values ('Tia do Pedroso', 'IPhone smartphone', 10.2, 5, 'IPhone 13');
INSERT INTO produtoversoes (descricao, preco, titulo,produto_id, data) VALUES ( 'IPhone smartphone', 10.2, 'IPhone 13',(SELECT MAX(id) FROM produto),CURRENT_TIMESTAMP);
INSERT INTO smartphone(modelo, produto_id) VALUES ('4.3X', (SELECT MAX(id) FROM produto));



CREATE OR REPLACE PROCEDURE public.newProdutoVersao(descr VARCHAR, prec FLOAT, titul VARCHAR,id_produto numeric)
LANGUAGE 'plpgsql'
AS $BODY$
	declare	
	begin
		lock table produto in exclusive mode;
		lock table produtoversoes in exclusive mode;
		INSERT INTO produtoversoes(descricao,preco,titulo,produto_id, data) VALUES (descr,prec,titul,id_produto, CURRENT_TIMESTAMP);
		
		UPDATE produto
		SET descricao = descr, preco = prec, titulo = titul
		WHERE produto.id = id_produto;
	end;
	
	$BODY$;

create or replace function descontaCupoes() returns trigger
language plpgsql
as $$
	declare
	campanhaId BIGINT = 0;
	numCupoes BIGINT = 0;
	numCupoesEmi BIGINT = 0;
	descontoCupao FLOAT = 0;
	tempoAtual TIMESTAMP;
	tempoFinal TIMESTAMP;
	begin
	lock table campanha in row EXCLUSIVE MODE;
	lock table comprador_campanha in EXCLUSIVE MODE;

	select MAX(campanha_id) from comprador_campanha INTO campanhaId;
	select n_cupoes, n_cupoes_emitidos, fim, desconto from campanha WHERE id = campanhaId into numCupoes, numCupoesEmi, tempoFinal, descontoCupao for update;
	select CURRENT_TIMESTAMP into tempoAtual;

	update campanha set n_cupoes = n_cupoes - 1 where id = campanhaId;
	update campanha set n_cupoes_emitidos = n_cupoes_emitidos + 1 where id = campanhaId;

	insert into cupao (desconto, validade) values (descontoCupao, tempoFinal);

	numCupoes = numCupoes - 1;
	if tempoAtual > tempoFinal then 
		update campanha set ativo = FALSE where id = campanhaId;
	end if;
	
	if numCupoes = 0 then 
		update campanha set ativo = FALSE where id = campanhaId;
	end if;

	return new;
	commit;
end;

$$;

create trigger trig2
after insert on comprador_campanha
execute procedure descontaCupoes();




create or replace function noti_comentario() returns trigger
language plpgsql
as $$		
	begin
		
		if new.comentario_id is NULL then
			INSERT INTO notificacao(descricao, data,utilizador_user_name) VALUES(CONCAT('O seu produto: ', new.produto_id,' tem uma questÃ£o feita por ', new.utilizador_user_name, ' : ', new.comentario),CURRENT_TIMESTAMP,(SELECT vendedor_utilizador_user_name FROM produto WHERE id = new.produto_id));
		else
			INSERT INTO notificacao(descricao, data,utilizador_user_name) VALUES(CONCAT('A sua questao: ', (SELECT comentario FROM comentario WHERE id = new.comentario_id ),' foi respondida por ', new.utilizador_user_name, ' : ', new.comentario),CURRENT_TIMESTAMP, (SELECT utilizador_user_name FROM comentario WHERE id = new.comentario_id));
		end if;
	

	return new;
	commit;
end;

$$;


create trigger trig3
after insert on comentario
for each row
execute procedure noti_comentario();


create or replace function noti_encomenda() returns trigger
language plpgsql
as $$		
	begin
		INSERT INTO notificacao(descricao, data,utilizador_user_name) VALUES(CONCAT('O seu produto: ', new.produto_id,' foi encomendado por ', (SELECT comprador_utilizador_user_name FROM encomenda WHERE n_encomenda = new.encomenda_n_encomenda)),CURRENT_TIMESTAMP,(SELECT vendedor_utilizador_user_name FROM produto WHERE id = new.produto_id));
		INSERT INTO notificacao(descricao, data,utilizador_user_name) VALUES(CONCAT('Efetuo a compra do produto: ', new.produto_id),CURRENT_TIMESTAMP,(SELECT comprador_utilizador_user_name FROM encomenda WHERE n_encomenda = new.encomenda_n_encomenda));

	return new;
	commit;
end;

$$;

create trigger trig4
after insert on produto_encomenda
for each row
execute procedure noti_encomenda();