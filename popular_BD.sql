
INSERT INTO usuario
(id, password, last_login, is_superuser, email, nome, is_active, is_staff)
VALUES(
1, 'pbkdf2_sha256$1000000$MZbCncvPHth00YxLY9867c$Mm7sBlCLAHj4qCwbxq60LzEBVFcE+WyuuqCxfY7xb4A=', '2025-10-07 18:15:21.379825', 1,
'admin@admin', 'Admin', 1, 1)

INSERT INTO usuario
(id, password, last_login, is_superuser, email, nome, is_active, is_staff)
VALUES(
3, 'pbkdf2_sha256$1000000$MZbCncvPHth00YxLY9867c$Mm7sBlCLAHj4qCwbxq60LzEBVFcE+WyuuqCxfY7xb4A=', '2025-10-07 18:15:21.379825', 1,
'afonso@admin', 'Afonso', 1, 1)



INSERT INTO rexapp_categoria
(id, nome)
VALUES(1, 'Console');



INSERT INTO rexapp_fabricante
(id, nome)
VALUES(1, 'Microsoft');
INSERT INTO rexapp_fabricante
(id, nome)
VALUES(2, 'Sony');
INSERT INTO rexapp_fabricante
(id, nome)
VALUES(3, 'Sony');
INSERT INTO rexapp_fabricante
(id, nome)
VALUES(4, 'Nintendo');