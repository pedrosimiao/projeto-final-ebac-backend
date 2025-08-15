# accounts/management/commands/seed_data.py

# Ferramentas Python Padrão

# tradutor de JSON (leitura listas de usuários e posts)
import json

# interação com o sistema operacional 
# (construção de caminhos de pastas, navegação e verificação de arquivos)
import os

# Generate cryptographically strong pseudo-random numbers suitable for
# managing secrets such as account authentication, tokens, and similar.
import secrets

import string


# Ferramentas do Django

# BaseCommand: superclasse herdada por comandos customizado do Django 
# CommandError: erros específicos do comando
from django.core.management.base import BaseCommand, CommandError

# acesso as configurações do projeto, settings.py 
# (MEDIA_ROOT, USE_TZ, etc.)
from django.conf import settings

# Timezone-related classes and functions.
from django.utils import timezone

from django.db import transaction

# para FileField.save()
from django.core.files import File

from accounts.models import User
from posts.models import Post

# Um dicionário para mapear os IDs dos usuários do JSON para os IDs reais gerados pelo Django
OLD_TO_NEW_USER_IDS = {}

# dicionário para as senhas geradas para cada mock user
MOCK_USER_PASSWORDS = {}

SEED_SOURCE_MEDIA_DIR = settings.MEDIA_ROOT

# Command
# comando de gerenciamento customizado 
# herda de BaseCommand. 

class Command(BaseCommand):
    # python manage.py help seed_data
    help = 'Seeds the database with mock user and post data, handling local images and specific dates.'

    # add_arguments: método configurando as opções (argumentos)
    # que o comando pode receber quando executado no terminal
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', # `--clear`: Um argumento opcional.
            action='store_true', # `action='store_true'`: Significa que se você incluir `--clear`, ele será `True`; caso contrário, `False`.
            help='Clear all existing users (except superusers) and posts before seeding.', # Ajuda para o argumento.
        )

    # handle: central do comando
    # *args e **kwargs: captura de argumentos posicionais ou nomeados
    def handle(self, *args, **kwargs): # *args não está sendo usado        
        self.stdout.write(self.style.NOTICE('Starting database seeding...'))
        # self.stdout.write(): mensagem no terminal
        # self.style.NOTICE(): mensagem mais visível no terminal.

        # Caminhos para arquivos JSON de mock na raiz do projeto
        # os.path.join(): função do módulo OS que junta partes de um caminho de forma segura,
        # independentemente do sistema operacional (Windows usa '\', Linux/macOS usa '/').
        # settings.BASE_DIR: Uma variável do Django que aponta para o diretório raiz do seu projeto.
        users_json_path = os.path.join(settings.BASE_DIR, 'convertedUsers.json')
        posts_json_path = os.path.join(settings.BASE_DIR, 'convertedPosts.json')
        
        # Caminho para o arquivo de senhas geradas (será ignorado pelo Git)
        passwords_file_path = os.path.join(settings.BASE_DIR, 'mock_passwords.txt')

        # Carregar dados dos JSONs
        users_data = self._load_json(users_json_path) # Chama a função auxiliar para carregar usuários
        posts_data = self._load_json(posts_json_path) # Chama a função auxiliar para carregar posts

        if kwargs['clear']: # verifica se o argumento `--clear` foi passado
            self._clear_existing_data() # função para limpar o banco

        # --- SEEDING DE USUÁRIOS ---
        self.stdout.write(self.style.NOTICE('\n Creating and updating users...'))
        with transaction.atomic(): # transação atômica. Se algo der errado aqui, tudo será desfeito.
            for user_data in users_data: # Loop: Itera sobre cada dicionário de usuário carregado do JSON.
                self._seed_user(user_data) # Chama a função auxiliar para semear um único usuário.

        # --- SEEDING DE POSTS ---
        self.stdout.write(self.style.NOTICE('\n Creating posts...'))
        with transaction.atomic(): # transação atômica para posts.
            for post_data in posts_data: # Loop: Itera sobre cada dicionário de post carregado do JSON.
                self._seed_post(post_data) # Chama a função auxiliar para semear um único post.
                # loop de usuários finalizado,
                # então OLD_TO_NEW_USER_IDS está completo

        # --- SALVAR SENHAS ---
        self._save_passwords_to_file(passwords_file_path) # Chama a função para salvar as senhas geradas.

        self.stdout.write(self.style.SUCCESS('\nDatabase seeding completed successfully!'))
        self.stdout.write(self.style.WARNING(f'\nMock user passwords saved to: {passwords_file_path} (add this file to .gitignore!)'))
        # `self.style.SUCCESS()` e `self.style.WARNING()`: Mensagens coloridas para feedback.
        # `f-string`: format strings, chaves `{}` para inserir variáveis.





# Funções Auxiliares
# (handle) delega tarefas específicas para funções auxiliares 
# _ por convenção, indicação para uso interno da classe

    def _load_json(self, file_path):
        """Helper para carregar dados de um arquivo JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # `with open(...) as f:`: Um "context manager" do Python.
                # Ele garante que o arquivo seja automaticamente fechado, mesmo se houver erros.
                # `'r'`: Modo de leitura.
                # `encoding='utf-8'`: Garante que caracteres especiais (acentos, etc.) sejam lidos corretamente.
                return json.load(f) # `json.load()`: A função do módulo `json` que lê o conteúdo do arquivo e o converte em um objeto Python (lista de dicionários, neste caso).
        except FileNotFoundError: # Se o arquivo não for encontrado.
            raise CommandError(f'Error: JSON file not found at {file_path}. Please check the path.')
            # `raise CommandError()`: Levanta um erro específico do Django, que será exibido de forma amigável no terminal e interromperá o comando.
        except json.JSONDecodeError: # Se o arquivo JSON estiver mal formatado.
            raise CommandError(f'Error: Could not decode JSON from {file_path}. Invalid JSON format.')



    def _clear_existing_data(self):
        """Limpa todos os usuários (exceto superusuários) e posts existentes."""
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        with transaction.atomic(): # limpeza atomizada
            # Post.objects.all().delete(): Usa o ORM do Django. 
            # Post.objects.all(): todos os posts, .delete() os remove
            # posts primeiro porque eles têm uma FK para usuários
            Post.objects.all().delete()
            
            # `User.objects.filter(is_superuser=False).delete()`: todos os usuários que não são superusuários e os deleta
            User.objects.filter(is_superuser=False).delete()
            # para adicionar outros modelos (Comments, Follows) e deletá-los aqui, seguir a ordem de dependência.
        self.stdout.write(self.style.WARNING('Existing users and posts cleared.'))



    def _generate_random_password(self, length=12):
        """Gera uma senha aleatória segura."""
        characters = string.ascii_letters + string.digits + string.punctuation
        
        # combinando letras (case insensitive), números e pontuação para senha forte
        password = ''.join(secrets.choice(characters) for i in range(length))
        # `secrets.choice()`: Escolhe um caractere aleatório de forma segura (criptograficamente).
        # `''.join(...)`: Junta os caracteres escolhidos em uma única string.
        return password



    def _seed_user(self, user_data):
        """Cria ou atualiza um único usuário e seu perfil."""
        old_mock_id = str(user_data['id']) # ID do mock JSON (UUID string)
        username = user_data['username']
        email = user_data['email']

        # verificação de existência do usuário, 
        # prevenção de duplicatas por username ou email
        existing_user = User.objects.filter(username=username).first() or \
                        User.objects.filter(email=email).first()

        if existing_user:
            self.stdout.write(self.style.WARNING(f"User '{username}' or '{email}' already exists. Skipping creation, attempting profile update."))
            user = existing_user
            OLD_TO_NEW_USER_IDS[old_mock_id] = user.pk # Mapeia o ID mock para o ID existente
        else:
            try:
                # gerar senha e armazenar em MOCK_USER_PASSWORDS
                password = self._generate_random_password()
                MOCK_USER_PASSWORDS[username] = password

                # cria o user
                # joined_at será definido automaticamente por auto_now_add=True
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=user_data.get('firstName', ''),
                    last_name=user_data.get('lastName', '')
                )
                self.stdout.write(self.style.SUCCESS(f"Created user: {username} (ID: {user.pk})"))
                OLD_TO_NEW_USER_IDS[old_mock_id] = user.pk # Mapeia o ID mock para o ID recém-criado

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating user {username} ({email}): {e}"))
                return # Pula o restante do processamento para este usuário se a criação falhou

        # Update campos de perfil e datas (sobrescrição de auto_now_add)
        try:
            # lógica de sobrescrição do campo joined_at (auto_now_add=True)
            if 'joined_at' in user_data and user_data['joined_at']:
                # Converte o string ISO para datetime, substituindo 'Z' por '+00:00' para compatibilidade
                desired_joined_at = timezone.datetime.fromisoformat(user_data['joined_at'].replace('Z', '+00:00'))
                
                # se o datetime for "naive", torne-o "aware"
                if settings.USE_TZ and timezone.is_naive(desired_joined_at):
                    desired_joined_at = timezone.make_aware(desired_joined_at)
                # se já for aware (string ISO has +00:00), não chame make_aware novamente

                if user.joined_at != desired_joined_at:
                    user.joined_at = desired_joined_at

            user.birth_date = user_data.get('birth_date')            
            user.bio = user_data.get('bio', '')
            user.occupation = user_data.get('occupation', '')
            user.location = user_data.get('location', '')
            
            # Tratamento de Imagens Locais: Profile Picture e Cover Image
            profile_pic_filename = user_data.get('profile_picture')
            cover_img_filename = user_data.get('cover_image')

            # imagem de perfil
            if profile_pic_filename:
                # caminho completo para a imagem na pasta de origem (media local, mapeada via .:/app no docker)
                source_path = os.path.join(SEED_SOURCE_MEDIA_DIR, 'profile_pictures', profile_pic_filename)
                
                if os.path.exists(source_path):
                    with open(source_path, 'rb') as f:
                        # .save(): Django salva no MEDIA_ROOT (volume persistente)
                        user.profile_picture.save(profile_pic_filename, File(f), save=False)
                        self.stdout.write(self.style.SUCCESS(f"Profile picture '{profile_pic_filename}' atributed to {user.username}."))
                else:
                    user.profile_picture = None
                    self.stdout.write(self.style.WARNING(f"Profile picture NOT FOUND in SOURCE for '{source_path}'. Skipping to {user.username}."))
            
            else:
                user.profile_picture = None


            # imagem de capa
            if cover_img_filename:
                source_path = os.path.join(SEED_SOURCE_MEDIA_DIR, 'cover_images', cover_img_filename)
                
                # verifica se o arquivo existe fisicamente em /media/cover_images/cover-image.jpg
                if os.path.exists(source_path):
                    with open(source_path, 'rb') as f:
                        # .save(): Django salva no MEDIA_ROOT (volume persistente)
                        user.cover_image.save(cover_img_filename, File(f), save=False)
                        self.stdout.write(self.style.SUCCESS(f"Cover image '{cover_img_filename}' atributed to {user.username}."))
                else:
                    user.cover_image = None
                    self.stdout.write(self.style.WARNING(f"Cover image NOT FOUND in SOURCE for '{source_path}'. Skipping to {user.username}."))
            else:
                user.cover_image = None

            # salva todos os campos atualizados
            update_fields_list = ['bio', 'occupation', 'location', 'birth_date', 'profile_picture', 'cover_image']
            if 'joined_at' in user_data and user_data['joined_at']:
                update_fields_list.append('joined_at')

            user.save(update_fields=update_fields_list)
            self.stdout.write(self.style.SUCCESS(f"Profile updated to user: {username}"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erro updating profile to user: {username}: {e}"))



    def _seed_post(self, post_data):
        """Cria um único post."""
        old_mock_id = str(post_data['id'])
        old_user_mock_id = str(post_data['user'])
        new_user_id = OLD_TO_NEW_USER_IDS.get(old_user_mock_id)

        if not new_user_id:
            self.stdout.write(self.style.WARNING(f"User ID mock '{old_user_mock_id}' not fouund for post ID {old_mock_id}. Skipping post."))
            return

        try:
            user_instance = User.objects.get(pk=new_user_id)

            if Post.objects.filter(user=user_instance, content=post_data.get('content', '')).exists():
                self.stdout.write(self.style.WARNING(f"Post content '{post_data.get('content', '')[:50]}...' already exists for user {user_instance.username}. Skipping."))
                return

            post = Post.objects.create(
                user=user_instance,
                content=post_data.get('content', ''),
            )

            # # lógica de sobrescrição do campo created_at (auto_now_add=True)
            if 'created_at' in post_data and post_data['created_at']:
                desired_created_at = timezone.datetime.fromisoformat(post_data['created_at'].replace('Z', '+00:00'))
                
                if settings.USE_TZ and timezone.is_naive(desired_created_at):
                    desired_created_at = timezone.make_aware(desired_created_at)

                if post.created_at != desired_created_at:
                    post.created_at = desired_created_at

            # Tratamento de post.image
            post_image_filename = post_data.get('image')
            if post_image_filename:
                # caminho relativo /media/post_images/post-image.jpg
                source_path = os.path.join(SEED_SOURCE_MEDIA_DIR, 'post_images', post_image_filename)
                
                # verifica se o arquivo existe fisicamente em /media/post_images/post-image.jpg
                if os.path.exists(source_path):
                    with open(source_path, 'rb') as f:
                        post.image.save(post_image_filename, File(f), save=False)
                        self.stdout.write(self.style.SUCCESS(f"Post image '{post_image_filename}' attached to post ID {old_mock_id}."))
                else:
                    post.image = None
                    self.stdout.write(self.style.WARNING(f"Post image NOT FOUND at SOURCE for '{source_path}'. Skipping to post ID {old_mock_id}."))
            else:
                post.image = None # None se não houver nome de arquivo no JSON


            # aalva os campos do post com referência de imagem e a 'created_at' se modificada
            update_fields_list = ['content', 'image'] 
            if 'created_at' in post_data and post_data['created_at']:
                update_fields_list.append('created_at')

            post.save(update_fields=update_fields_list)
            self.stdout.write(self.style.SUCCESS(f"Post created with ID {post.pk} for user: {user_instance.username}"))

        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"User created with real ID '{new_user_id}' not found to post ID {old_mock_id}. Skipping post."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating post ID {old_mock_id}: {e}"))



    def _save_passwords_to_file(self, file_path):
            """
            Salva os usernames e senhas geradas em um arquivo de texto.
            """
            try:
                # Abre o arquivo no modo de escrita ('w'). Se não existir, ele é criado; se existir, é sobrescrito.
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("--- Mock users passwords ---\n")
                    f.write("Add to .gitignore!\n\n")
                    # Itera sobre o dicionário de senhas geradas e escreve cada par username:senha
                    for username, password in MOCK_USER_PASSWORDS.items():
                        f.write(f"{username}: {password}\n")
                self.stdout.write(self.style.SUCCESS(f"Senhas geradas salvas em {file_path}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro ao salvar senhas no arquivo {file_path}: {e}"))