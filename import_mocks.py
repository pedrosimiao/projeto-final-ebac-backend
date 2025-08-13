import json # 1. Importa o módulo json para trabalhar com arquivos JSON.
import requests # 2. Importa o módulo requests para fazer requisições HTTP para sua API.
import logging # 3. Importa o módulo logging para registrar mensagens de log (informações, avisos, erros).
import os # 4. Importa o módulo os para interagir com o sistema operacional (ex: caminhos de arquivos).
import time # Importar o módulo time # 5. Importa o módulo time, que permite adicionar pausas, útil para depuração ou lidar com problemas de conexão.
import django # 6. Importa o módulo django.

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "config.settings"
)  # 'config' é o nome do seu projeto # 7. Configura a variável de ambiente DJANGO_SETTINGS_MODULE. Isso é essencial para que o Django saiba qual arquivo de configurações usar, permitindo que o script acesse configurações como MEDIA_ROOT.
django.setup() # 8. Inicializa o ambiente Django. Necessário para que partes do Django (como settings) possam ser acessadas fora do ambiente de servidor web do Django.

from django.conf import settings # 9. Importa o objeto settings do Django, que contém todas as configurações do seu projeto.

API_BASE = "http://localhost:8000/api" # 10. Define a URL base para sua API. Atualmente aponta para o localhost, o que é ideal para desenvolvimento local.
DEFAULT_PASSWORD = "password123" # 11. Define uma senha padrão para todos os usuários mock. Este é um ponto que você quer otimizar/segurar no futuro.
MEDIA_ROOT = settings.MEDIA_ROOT # Obter MEDIA_ROOT das configurações do Django # 12. Obtém o caminho para o diretório de mídia configurado no Django (onde as imagens são armazenadas).

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
) # 13. Configura o sistema de log básico:
#    - level=logging.INFO: Registra mensagens informativas, avisos e erros.
#    - format: Define o formato das mensagens de log (data/hora, nível, mensagem).


def create_user(user_data):
    """Cria um único usuário via /signup/.""" # 14. Docstring: Descreve a função.
    try: # 15. Inicia um bloco try-except para lidar com possíveis erros.
        resp = requests.post(
            f"{API_BASE}/signup/", # 16. Faz uma requisição POST para o endpoint de cadastro (/signup/).
            json={ # 17. Envia os dados do usuário no corpo da requisição como JSON.
                "first_name": user_data["firstName"],
                "last_name": user_data["lastName"],
                "username": user_data["username"],
                "email": user_data["email"],
                "password": DEFAULT_PASSWORD, # 18. Usa a senha padrão.
                "confirm_password": DEFAULT_PASSWORD, # 19. Confirma a senha.
            },
        )
        resp.raise_for_status() # 20. Levanta uma exceção HTTPError se a requisição retornar um status de erro (4xx ou 5xx).
        response_data = resp.json() # 21. Analisa a resposta JSON da API.
        logging.info(f"Usuário {user_data['username']} criado com sucesso.") # 22. Registra uma mensagem de sucesso.
        return response_data # 23. Retorna os dados da resposta, que provavelmente incluem o ID do usuário criado.
    except requests.exceptions.HTTPError as err: # 24. Captura erros HTTP (ex: 400 Bad Request, 500 Internal Server Error).
        print(
            f"❌ Erro ao criar usuário {user_data['username']}: {err.response.status_code} - {err.response.text}"
        ) # 25. Imprime uma mensagem de erro no console.
        logging.error(
            f"Erro ao criar usuário {user_data['username']}: {err.response.status_code} - {err.response.text}"
        ) # 26. Registra o erro no log.
        return None # 27. Retorna None em caso de erro.
    except requests.exceptions.ConnectionError as err: # 28. Captura erros de conexão (ex: servidor não está rodando).
        print(f"❌ Erro de conexão ao criar usuário {user_data['username']}: {err}") # 29. Imprime erro de conexão.
        logging.error(
            f"Erro de conexão ao criar usuário {user_data['username']}: {err}"
        ) # 30. Registra erro de conexão.
        return None # 31. Retorna None.


def update_user_profile(user_id, user_data, headers):
    """Atualiza o perfil do usuário com os campos adicionais, incluindo imagens.""" # 32. Docstring.
    url = f"{API_BASE}/users/{user_id}/update_profile/" # 33. Constrói a URL para a API de atualização de perfil.
    files = {} # 34. Dicionário para armazenar os arquivos a serem enviados (imagens).
    data = { # 35. Dicionário para armazenar os dados do formulário (texto).
        "first_name": user_data.get("firstName", ""), # 36. Usa .get() para acessar os campos, com um valor padrão vazio se não existirem (evita KeyError).
        "last_name": user_data.get("lastName", ""),
        "bio": user_data.get("bio", ""),
        "occupation": user_data.get("occupation", ""),
        "location": user_data.get("location", ""),
        "birth_date": user_data.get("birth_date", ""),
    }

    profile_picture_path = user_data.get("profile_picture") # 37. Obtém o caminho da imagem de perfil dos dados mock.
    cover_image_path = user_data.get("cover_image") # 38. Obtém o caminho da imagem de capa.

    if profile_picture_path and os.path.exists(
        os.path.join(MEDIA_ROOT, profile_picture_path)
    ): # 39. Verifica se o caminho da imagem de perfil existe e se o arquivo realmente existe no sistema.
        files["profile_picture"] = open(
            os.path.join(MEDIA_ROOT, profile_picture_path), "rb"
        ) # 40. Abre o arquivo da imagem em modo binário de leitura ('rb') e o adiciona ao dicionário 'files'.
    else:
        print(
            f"⚠️ Arquivo de imagem de perfil não encontrado: {profile_picture_path}, pulando."
        ) # 41. Aviso se o arquivo de imagem de perfil não for encontrado.
        logging.warning(
            f"Arquivo de imagem de perfil não encontrado: {profile_picture_path}, pulando."
        )

    if cover_image_path and os.path.exists(os.path.join(MEDIA_ROOT, cover_image_path)): # 42. Similar ao anterior, para a imagem de capa.
        files["cover_image"] = open(os.path.join(MEDIA_ROOT, cover_image_path), "rb") # 43. Abre o arquivo da imagem de capa.
    else:
        print(
            f"⚠️ Arquivo de imagem de capa não encontrado: {cover_image_path}, pulando."
        ) # 44. Aviso se o arquivo de imagem de capa não for encontrado.
        logging.warning(
            f"Arquivo de imagem de capa não encontrado: {cover_image_path}, pulando."
        )

    try:
        resp = requests.patch(url, data=data, files=files, headers=headers) # 45. Faz uma requisição PATCH (para atualização parcial) para a API, enviando dados e arquivos.
        resp.raise_for_status() # 46. Levanta exceção para status de erro.
        logging.info(f"Perfil do usuário {user_id} atualizado.") # 47. Registra sucesso.
        # Fechar os arquivos após o envio # 48. Comentário: Lógica para fechar arquivos.
        for f in files.values(): # 49. Itera sobre os arquivos que foram abertos.
            if not f.closed: # 50. Verifica se o arquivo ainda está aberto.
                f.close() # 51. Fecha o arquivo. Isso é crucial para liberar recursos.
        return True # 52. Retorna True em caso de sucesso.
    except requests.exceptions.HTTPError as err: # 53. Captura erros HTTP.
        print(
            f"❌ Erro ao atualizar perfil do usuário {user_id}: {err.response.status_code} - {err.response.text}"
        ) # 54. Imprime erro.
        logging.error(
            f"Erro ao atualizar perfil do usuário {user_id}: {err.response.status_code} - {err.response.text}"
        ) # 55. Registra erro.
        # Fechar os arquivos em caso de erro também # 56. Comentário: Garante que os arquivos sejam fechados mesmo em erro.
        for f in files.values(): # 57. Itera e fecha os arquivos.
            if not f.closed:
                f.close()
        return False # 58. Retorna False em caso de erro.
    except requests.exceptions.ConnectionError as err: # 59. Captura erros de conexão.
        print(f"❌ Erro de conexão ao atualizar perfil do usuário {user_id}: {err}") # 60. Imprime erro.
        logging.error(
            f"Erro de conexão ao atualizar perfil do usuário {user_id}: {err}"
        ) # 61. Registra erro.
        return False # 62. Retorna False.


def authenticate(username_or_email):
    """Obtém o token de autenticação para um usuário via /login/.""" # 63. Docstring.
    try:
        resp = requests.post(
            f"{API_BASE}/login/", # 64. Faz requisição POST para o endpoint de login.
            json={"identifier": username_or_email, "password": DEFAULT_PASSWORD}, # 65. Envia credenciais (identificador e senha padrão).
        )
        resp.raise_for_status() # 66. Levanta exceção para status de erro.
        token = resp.json()["access"] # 67. Extrai o token de acesso da resposta JSON.
        logging.info(f"Usuário {username_or_email} autenticado.") # 68. Registra sucesso.
        return {"Authorization": f"Bearer {token}"} # 69. Retorna o token formatado como um cabeçalho de autorização.
    except requests.exceptions.HTTPError as err: # 70. Captura erros HTTP.
        print(
            f"❌ Erro ao autenticar {username_or_email}: {err.response.status_code} - {err.response.text}"
        ) # 71. Imprime erro.
        logging.error(
            f"Erro ao autenticar {username_or_email}: {err.response.status_code} - {err.response.text}"
        ) # 72. Registra erro.
        return None # 73. Retorna None.
    except requests.exceptions.ConnectionError as err: # 74. Captura erros de conexão.
        print(f"❌ Erro de conexão ao autenticar {username_or_email}: {err}") # 75. Imprime erro.
        logging.error(f"Erro de conexão ao autenticar {username_or_email}: {err}") # 76. Registra erro.
        return None # 77. Retorna None.


def post_data(endpoint, items, headers, label, created_ids=None):
    """Envia os dados para o endpoint da API.""" # 78. Docstring.

    print(f"📤 Enviando {len(items)} {label} para {endpoint}...") # 79. Mensagem de progresso.
    logging.info(f"Enviando {len(items)} {label} para {endpoint}") # 80. Registra progresso.

    successful_ids = {}  # Dicionário para armazenar os IDs criados com sucesso # 81. Inicializa um dicionário para mapear IDs mock para IDs reais criados na API.

    for item in items: # 82. Itera sobre cada item (post, comentário, etc.) a ser enviado.
        try:
            # Se necessário, substituir IDs originais pelos IDs criados # 83. Comentário: Lógica para mapear IDs.
            if created_ids and label == "posts": # 84. Condição para posts: verifica se created_ids foi fornecido e se estamos processando posts.
                if (
                    isinstance(item.get("user"), str)
                    and item["user"] in created_ids["users"]
                ): # 85. Verifica se o campo 'user' no item mock é uma string (que seria o ID mock do usuário) e se esse ID existe no `created_ids["users"]`.
                    item["user"] = created_ids["users"][item["user"]] # 86. Substitui o ID mock do usuário pelo ID real do usuário criado na API.

            # Verificar se há arquivos (imagens) e enviar como multipart/form-data # 87. Comentário: Lógica para arquivos.
            files = {} # 88. Dicionário para arquivos.
            data = {} # 89. Dicionário para dados do formulário.
            for key, value in item.items(): # 90. Itera sobre os campos de cada item.
                if key == "image" and value: # 91. Se o campo é 'image' e tem um valor.
                    image_path = os.path.join(MEDIA_ROOT, value) # 92. Constrói o caminho completo para a imagem.
                    if os.path.exists(image_path): # 93. Verifica se o arquivo de imagem existe.
                        files["image"] = open(image_path, "rb") # 94. Abre o arquivo e o adiciona a 'files'.
                    else:
                        print(
                            f"⚠️ Arquivo de imagem não encontrado: {image_path}, enviando como texto."
                        ) # 95. Aviso se a imagem não for encontrada.
                        logging.warning(
                            f"Arquivo de imagem não encontrado: {image_path}, enviando como texto."
                        )
                        data["image"] = value  # Enviar o caminho como texto # 96. Se a imagem não for encontrada, envia o caminho como texto (o que provavelmente não é o esperado pela API, mas evita falha).
                elif key == "video" and value: # 97. Similar para arquivos de vídeo.
                    video_path = os.path.join(MEDIA_ROOT, value)
                    if os.path.exists(video_path):
                        files["video"] = open(video_path, "rb")
                    else:
                        print(
                            f"⚠️ Arquivo de vídeo não encontrado: {video_path}, enviando como texto."
                        )
                        logging.warning(
                            f"Arquivo de vídeo não encontrado: {video_path}, enviando como texto."
                        )
                        data["video"] = value  # Enviar o caminho como texto
                else:
                    data[key] = value # 98. Para todos os outros campos, adiciona-os ao dicionário 'data'.

            if files: # 99. Se há arquivos a serem enviados.
                resp = requests.post(
                    f"{API_BASE}/{endpoint}/", data=data, files=files, headers=headers
                ) # 100. Faz uma requisição POST com multipart/form-data.
                # Fechar os arquivos após o envio # 101. Comentário: Lógica para fechar arquivos.
                for f in files.values(): # 102. Fecha os arquivos abertos.
                    if not f.closed:
                        f.close()
            else: # 103. Se não há arquivos.
                resp = requests.post(
                    f"{API_BASE}/{endpoint}/", json=data, headers=headers
                ) # 104. Faz uma requisição POST com JSON.

            try:
                resp.raise_for_status() # 105. Levanta exceção para status de erro.
                response_data = (
                    resp.json()
                )  # Obter a resposta da API (pode conter o ID criado) # 106. Obtém a resposta JSON.
                logging.info(f"{label[:-1].capitalize()} criado com sucesso.") # 107. Registra sucesso.

                # Armazenar o ID criado para referência futura # 108. Comentário: Armazena IDs.
                if "id" in response_data and created_ids is not None: # 109. Se a resposta contém um 'id' (o ID real do objeto criado na API).
                    successful_ids[item.get("id")] = response_data["id"] # 110. Mapeia o ID mock original (se existir) para o ID real.

            except requests.exceptions.HTTPError as err: # 111. Captura erros HTTP.
                print(
                    f"❌ Erro ao criar {label[:-1]}: {err.response.status_code} - {err.response.text}"
                ) # 112. Imprime erro.
                logging.error(
                    f"Erro ao criar {label[:-1]}: {err.response.status_code} - {err.response.text}"
                ) # 113. Registra erro.
            except json.JSONDecodeError as err: # 114. Captura erros de decodificação JSON (se a resposta não for um JSON válido).
                print(f"❌ Erro ao decodificar JSON: {err}") # 115. Imprime erro.
                logging.error(f"Erro ao decodificar JSON: {err}") # 116. Registra erro.

        except requests.exceptions.ConnectionError as err: # 117. Captura erros de conexão para o item atual.
            print(f"❌ Erro de conexão ao criar {label[:-1]}: {err}") # 118. Imprime erro.
            logging.error(f"Erro de conexão ao criar {label[:-1]}: {err}") # 119. Registra erro.
            time.sleep(5)  # Esperar um pouco antes de tentar novamente # 120. Pausa por 5 segundos antes de tentar o próximo item, útil para problemas de conexão intermitentes.
            # Aqui você pode adicionar lógica para reconectar ou interromper após várias tentativas # 121. Comentário: Sugere melhorias na resiliência.
    return successful_ids # 122. Retorna o mapeamento de IDs mocks para IDs reais.


def load_json(filename):
    """Carrega dados de um arquivo JSON.""" # 123. Docstring.
    with open(filename, encoding="utf-8") as f: # 124. Abre o arquivo no modo leitura com encoding UTF-8 (boa prática).
        return json.load(f) # 125. Carrega o conteúdo JSON do arquivo.


def main():
    users = load_json("convertedUsers.json") # 126. Carrega os dados dos usuários do arquivo JSON.
    posts = load_json("convertedPosts.json") # 127. Carrega os dados dos posts do arquivo JSON.

    created_ids = {"users": {}, "posts": {}}  # Dicionário para armazenar os IDs criados # 128. Inicializa o dicionário para guardar o mapeamento de IDs.

    print("\n👤 Criando e atualizando usuários...") # 129. Mensagem de progresso.
    for user in users: # 130. Itera sobre cada usuário nos dados mock.
        user_creation_result = create_user(user) # 131. Tenta criar o usuário chamando a função `create_user`.
        if user_creation_result: # 132. Se a criação do usuário foi bem-sucedida.
            # Armazenar o ID do usuário criado # 133. Comentário: Armazena o ID.
            # A linha abaixo parece ter um erro de lógica: user_creation_result["id"] == user_creation_result["id"]
            # Deveria ser: created_ids["users"][user["id"]] = user_creation_result["id"]
            # Ou, se user não tem um 'id' mock, usar o username como chave: created_ids["users"][user["username"]] = user_creation_result["id"]
            created_ids["users"][user_creation_result["id"]] = user_creation_result[
                "id"
            ] # 134. Armazena o ID do usuário criado. **Possível gargalo/erro: Ele está usando o ID real retornado pela API como chave e valor, o que significa que o ID mock não está sendo mapeado para o ID real.** Isso pode causar problemas se os posts referenciam usuários por um ID mock diferente.
            token = authenticate(user["email"]) # 135. Tenta autenticar o usuário recém-criado para obter um token.
            if token: # 136. Se a autenticação foi bem-sucedida.
                if not update_user_profile(user_creation_result["id"], user, token): # 137. Tenta atualizar o perfil do usuário com as informações adicionais e imagens.
                    print(f"⚠️  Não foi possível atualizar perfil de {user['username']}") # 138. Aviso se a atualização do perfil falhar.
                    logging.warning(
                        f"Não foi possível atualizar perfil de {user['username']}"
                    )
            else:
                print(
                    f"⚠️  Não foi possível autenticar {user['email']}, pulando atualização de perfil."
                ) # 139. Aviso se a autenticação falhar.
                logging.warning(
                    f"Não foi possível autenticar {user['email']}, pulando atualização de perfil."
                )
        else:
            print(f"⚠️  Não foi possível criar usuário {user['username']}, pulando.") # 140. Aviso se a criação do usuário falhar.
            logging.warning(
                f"Não foi possível criar usuário {user['username']}, pulando."
            )

    # Criar posts
    print("\n📝 Criando posts...") # 141. Mensagem de progresso.
    logging.info("Criando posts...") # 142. Registra progresso.
    for user in users: # 143. Itera novamente sobre cada usuário.
        headers = authenticate(user["email"]) # 144. Autentica cada usuário individualmente para criar seus posts.
        if headers: # 145. Se a autenticação foi bem-sucedida.
            user_id = user["id"] # 146. Pega o ID do usuário mock.
            user_posts = [
                p
                for p in posts
                if (
                    isinstance(p.get("user"), dict)
                    and p.get("user").get("id") == user_id
                )
                or (isinstance(p.get("user"), str) and p.get("user") == user_id)
            ] # 147. Filtra os posts mock que pertencem ao usuário atual. **Gargalo:** Isso faz uma iteração completa sobre `posts` para cada usuário.
            successful_post_ids = post_data(
                "posts", user_posts, headers, "posts", created_ids
            ) # 148. Chama `post_data` para criar os posts do usuário.
            created_ids["posts"].update(successful_post_ids) # 149. Atualiza o dicionário de IDs de posts com os IDs recém-criados.
        else:
            print(f"⚠️  Não foi possível autenticar {user['email']}, pulando posts.") # 150. Aviso se a autenticação falhar.
            logging.warning(
                f"Não foi possível autenticar {user['email']}, pulando posts."
            )

    print("\n🎉 Usuários e posts criados e perfis atualizados com sucesso!") # 151. Mensagem de conclusão.
    logging.info("Usuários e posts criados e perfis atualizados com sucesso!")


if __name__ == "__main__": # 152. Garante que a função `main()` seja executada apenas quando o script é executado diretamente.
    main()