import argparse
import os
from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudAPIResponseException
from termcolor import colored
import requests
from dotenv import load_dotenv

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
    send_telegram_message_ready = False
    parser = argparse.ArgumentParser(description='Herramienta de backup de fotos y videos de iCloud')
    # Argumentos existentes
    parser.add_argument('--album', default='All Photos', help='Nombre del álbum de iCloud (por defecto: "All Photos")')
    parser.add_argument('--destination', default='/backup-icloud', help='Directorio de destino para el backup (por defecto: "/backup-icloud")')
    parser.add_argument('--delete-videos', action='store_true', help='Eliminar videos de iCloud después del backup')
    # Nuevo argumento para controlar el envío de mensajes de Telegram
    parser.add_argument('--send-telegram', action='store_true', help='Enviar un mensaje de Telegram al finalizar (por defecto: no se envía)')

    args = parser.parse_args()

    load_dotenv()

    # Información de Telegram (configura estas variables con tus propios valores)
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

    try:
        if os.environ.get('IC_USER') is None or os.environ.get('IC_PASS') is None:
            print(colored("🔴 Cannot read credentials from .env. Aborting...", "red"))
            return
        
        api = authenticate(os.environ.get('IC_USER'), os.environ.get('IC_PASS'))
        backup_photos_to_local(api, args.album, args.destination)

        if args.delete_videos:
            delete_backed_up_videos(api, args.album, args.destination)

        empty_recently_deleted(api)
        summary_message = generate_summary_message()

        # Enviar un mensaje de Telegram si el argumento --send-telegram es usado
        if args.send_telegram and TELEGRAM_TOKEN is not None and TELEGRAM_CHAT_ID is not None:
            send_telegram_message_ready = True
        
        if send_telegram_message_ready:
            send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, summary_message + "\n🟢 Proceso completado exitosamente.")
        else:
            print(summary_message + "\n🟢 Proceso completado exitosamente.")
    except Exception as e:
        error_message = f"🔴 Hubo un error: {str(e)}"
        if send_telegram_message_ready:
            send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, error_message)
        else:
            print(error_message)

if __name__ == "__main__":
    main()