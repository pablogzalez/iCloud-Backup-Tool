import argparse
import os
import configparser
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseException
from termcolor import colored
import requests

# Diccionario global para almacenar estadísticas
stats = {
    'items_count': 0,
    'photos_backed_up': 0,
    'videos_backed_up': 0,
    'videos_deleted': 0,
    'recently_deleted_emptied': False
}

VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv']

# Función para enviar un mensaje a través de Telegram
def send_telegram_message(token, chat_id, text):
    """Send a message to a Telegram user or group."""
    BASE_URL = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(BASE_URL, data=payload)
    return response.json()

# Función para obtener credenciales de iCloud desde un archivo de configuración
def get_icloud_credentials_from_config(filename):
    """Retrieve iCloud credentials from a config file."""
    print(colored(f"🔧 Leyendo configuración desde {filename}...", "cyan"))
    config = configparser.ConfigParser()
    config.read(filename)
    return config['ICloud']['username'], config['ICloud']['password']

# Función para autenticarse en iCloud
def authenticate(username, password):
    """Authenticate with iCloud."""
    print(colored("🔐 Iniciando autenticación con iCloud...", "cyan"))
    api = PyiCloudService(username, password)
    handle_2fa(api)
    print(colored("🟢 Autenticación exitosa.", "green"))
    return api

# Función para manejar la autenticación de dos factores
def handle_2fa(api):
    """Handle two-factor authentication if needed."""
    if api.requires_2fa:
        print(colored("🟡 Se requiere autenticación de dos factores.", "yellow"))
        code = input("Introduce el código que recibiste en uno de tus dispositivos: ")
        if not api.validate_2fa_code(code):
            print(colored("🔴 Error al verificar el código de seguridad.", "red"))
            exit(1)

# Función para verificar si un archivo es un video según su extensión
def is_video_file(filename):
    """Check if a given file is a video based on its extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in VIDEO_EXTENSIONS

# Función para vaciar el álbum 'Borrados recientemente' en iCloud
def empty_recently_deleted(api):
    """Empty the 'Recently Deleted' album."""
    print(colored("🔍 Vaciando el álbum 'Borrados recientemente'...", "cyan"))
    recently_deleted = api.photos.albums.get('Recently Deleted')
    for item in recently_deleted:
        item.delete()
    print(colored("🟢 Álbum 'Borrados recientemente' vaciado.", "green"))
    stats['recently_deleted_emptied'] = True

# Función para realizar copia de seguridad de fotos a un directorio local
def backup_photos_to_local(api, album_name, dest_directory):
    """Backup photos to a local directory."""
    print(colored(f"🔍 Buscando el álbum '{album_name}'...", "cyan"))

    if not os.path.exists(dest_directory):
        print(colored(f"📂 Creando directorio de destino: {dest_directory}", "yellow"))
        os.makedirs(dest_directory)

    album_obj = api.photos.albums.get(album_name)
    if not album_obj:
        print(colored(f"🔴 No se encontró el álbum '{album_name}'.", "red"))
        return

    existing_photos = set(os.listdir(dest_directory))
    photos_to_backup = []
    checked_photos_count = 0

    for photo in album_obj.photos:
        checked_photos_count += 1
        if photo.filename not in existing_photos:
            photos_to_backup.append(photo)
        print(f"🔍 Verificando fotos: {checked_photos_count}", end='\r')

    stats['items_count'] = checked_photos_count

    print(colored(f"\n🟢 Checks finished: {checked_photos_count - len(photos_to_backup)}/{checked_photos_count}", "green"))
    print(colored(f"🔵 Fotos o vídeos a realizar backup: {len(photos_to_backup)}", "cyan"))

    for index, photo in enumerate(photos_to_backup, start=1):
        print(f"⏳ Realizando backup {index}/{len(photos_to_backup)}...", end='\r')
        try:
            file_path = os.path.join(dest_directory, photo.filename)
            with open(file_path, 'wb') as file:
                file.write(photo.download().raw.read())
            if is_video_file(photo.filename):
                stats['videos_backed_up'] += 1
            else:
                stats['photos_backed_up'] += 1
        except PyiCloudAPIResponseException:
            print(colored(f"\n🔴 Error al descargar {photo.filename}. Omitiendo...", "red"))
    print(colored("\n🟢 Backup completado.", "green"))

# Función para eliminar videos de iCloud que ya han sido respaldados localmente
def delete_backed_up_videos(api, album_name, dest_directory):
    """Delete videos from iCloud that have already been backed up locally."""
    print(colored(f"🔍 Buscando videos en el álbum '{album_name}' para eliminar...", "cyan"))

    album_obj = api.photos.albums.get(album_name)
    if not album_obj:
        print(colored(f"🔴 No se encontró el álbum '{album_name}'.", "red"))
        return

    existing_files = set(os.listdir(dest_directory))
    deleted_count = 0

    for video in album_obj.photos:
        if video.filename in existing_files and is_video_file(video.filename):
            try:
                video.delete()
                deleted_count += 1
                stats['videos_deleted'] += 1
                print(colored(f"⏳ Eliminando video {deleted_count}: {video.filename} de iCloud...", "yellow"), end='\r')
            except PyiCloudAPIResponseException:
                print(colored(f"\n🔴 Error al eliminar {video.filename} de iCloud. Omitiendo...", "red"))
    print(colored(f"\n🟢 Eliminados {deleted_count} videos de iCloud.","green"))

# Función para mostrar un resumen de las acciones tomadas
def display_summary():
    """Display a summary of actions taken."""
    print("\n" + colored("📊 Resumen:", "blue"))
    print(colored(f"🔵 Items totales: {stats['items_count']}", "blue"))
    print(colored(f"🟢 Fotos realizadas backup: {stats['photos_backed_up']}", "green"))
    print(colored(f"🟢 Vídeos realizados backup: {stats['videos_backed_up']}", "green"))
    print(colored(f"🔴 Vídeos eliminados de iCloud: {stats['videos_deleted']}", "red"))
    if stats['recently_deleted_emptied']:
        print(colored("🟢 Álbum 'Borrados recientemente' vaciado.", "green"))

# Función para generar un mensaje de resumen para la notificación de Telegram
def generate_summary_message():
    """Generate a summary message for the Telegram notification."""
    message = "📊 Resumen:\n\n"
    message += f"🟢 Items totales: {stats['items_count']}\n"
    message += f"🟢 Fotos realizadas backup: {stats['photos_backed_up']}\n"
    message += f"🟢 Vídeos realizados backup: {stats['videos_backed_up']}\n"
    message += f"🔴 Vídeos eliminados de iCloud: {stats['videos_deleted']}\n"
    message += f"🟢 Álbum 'Borrados recientemente' vaciado: {'Sí' if stats['recently_deleted_emptied'] else 'No'}\n"
    return message

# Función principal
def main():
    parser = argparse.ArgumentParser(description='Herramienta de backup de fotos y videos de iCloud')
    # Argumentos existentes
    parser.add_argument('--config', default='/script-backup/config.ini', help='Archivo de configuración (por defecto: "/script-backup/config.in")')
    parser.add_argument('--album', default='All Photos', help='Nombre del álbum de iCloud (por defecto: "All Photos")')
    parser.add_argument('--destination', default='/backup-icloud', help='Directorio de destino para el backup (por defecto: "/backup-icloudd")')
    # Nuevo argumento para decidir si eliminar videos
    parser.add_argument('--delete-videos', action='store_true', help='Eliminar videos de iCloud después del backup')
    args = parser.parse_args()

    # Información de Telegram (configura estas variables con tus propios valores)
    TELEGRAM_TOKEN = 'TU_TOKEN_DE_TELEGRAM' # 
    TELEGRAM_CHAT_ID = 'TU_CHAT_ID_DE_TELEGRAM'

    try:
        username, password = get_icloud_credentials_from_config(args.config)
        api = authenticate(username, password)
        backup_photos_to_local(api, args.album, args.destination)

        # Comprobar si el usuario desea eliminar videos
        if args.delete_videos:
            delete_backed_up_videos(api, args.album, args.destination)

        empty_recently_deleted(api)
        summary_message = generate_summary_message()
        send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, summary_message + "\n🟢 Proceso completado exitosamente.")
    except Exception as e:
        send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, f"🔴 Hubo un error: {str(e)}")

if __name__ == "__main__":
    main()
