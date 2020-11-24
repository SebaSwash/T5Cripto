# ---------------------------------------------------
# Tarea 5: Autenticación alternativa de emails
# Criptografía y Seguridad en Redes (02 - 2020)
# Sebastián Ignacio Toro Severino
# ---------------------------------------------------
import imaplib, re, os, csv
from getpass import getpass
from email.parser import HeaderParser
from colorama import Fore, Back, Style, init

try:
  init() # Inicialización para módulo de colores en terminal
except:
  pass

def clear_screen():
  os.system('cls' if os.name == 'nt' else 'clear')

class MailClient:
  def __init__(self):
    self.mail = None
    self.regex_list = []
    self.filepath = None

    # Se realiza la conexión al servidor IMAP de Gmail
    self.imap_server_connection()

    # Autenticación de email cliente
    self.login()

    # Se realiza la configuración inicial
    self.config()

    # Menú principal de opciones
    self.main_menu()
  
  # Método para realizar la conexión con el servidor IMAP Gmail
  def imap_server_connection(self):
    try:
      # En caso de que exista un servidor instanciado, se cierra para reconectar
      if self.mail is not None:
        self.mail.close()
        self.mail.logout()

      # Se realiza la conexión al servidor IMAP de Gmail
      self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
    
    except Exception as error:
      print(Back.RED + Fore.WHITE + '* Se ha producido el siguiente error en la conexión con el servidor:')
      print(str(error) + Style.RESET_ALL)
  
  # Método para ingresar a la cuenta de cliente
  def login(self):
    self.email = input('Email de cliente: ')
    self.password = getpass('Password: ')

    self.mail.login(self.email, self.password) # Autenticación de cuenta
  
  # Método para importar conjuntos de expresiones regulares y correos emisores
  def import_regex_file(self):
    self.regex_list = [] # Se limpia la lista actual de combinaciones almacenadas
    
    try:
      with open(self.filepath, 'r') as file:
        reader = csv.reader(file)
        # Se agrega a la lista cada una de las combinaciones correo, regex, fecha
        for line in reader:
          self.regex_list.append(line)

    except Exception as error:
      print(Back.RED + Fore.WHITE + '* Se ha producido el siguiente error al procesar el archivo:')
      print(str(error)+Style.RESET_ALL)
  
  # Método para obtener la lista de MID según las configuraciones
  def show_mid_list(self):
    try:
      # Se obtiene los códigos de mensaje y el estado, según las configuraciones
      status, [messages] = self.mail.search(None, 'FROM '+ self.email_target)

      if status != 'OK':
        raise Exception('Estado de obtención no es OK.')
      
      header_parser = HeaderParser()

      # Se abre un archivo para almacenar la lista obtenida
      filename = input('La lista será exportada a un archivo. Ingresa un nombre de archivo: ')

      export_file = open('./exports/' + filename, 'w')


      for message_num in messages.split():
        typ, msg_data = self.mail.fetch(message_num, '(BODY[HEADER])')

        # Se transforma el objeto obtenido para extraer el message-id y la fecha de envío del header.
        try:
          header = header_parser.parsestr(msg_data[0][1].decode('UTF-8'))
          print(Back.CYAN + Fore.WHITE + 'MID: ' + str(header['message-id']) + Style.RESET_ALL + ' ' + Back.YELLOW + Fore.WHITE + '(' + str(header['Date']) + ')' + Style.RESET_ALL)
          
          # Se escribe el message id obtenido en el archivo
          export_file.write(str(header['message-id']) +'  (' + str(header['Date']) + ')\n')

        except Exception as error:
          print(Back.RED + Fore.WHITE + '[Error] Se produjo el siguiente error en el mensaje ' + str(message_num) + ':')
          print(str(error)+Style.RESET_ALL)
          export_file.write('[Error msg N-' + str(message_num) + '] ' + str(error) + '\n')
      
      export_file.close()

    except Exception as error:
      print(Back.RED + Fore.WHITE + '* Se ha producido el siguiente error al obtener los mensajes:')
      print(str(error) + Style.RESET_ALL)

  # Método para verificar cada uno de los MID con la expresión regular
  def mid_list_validation(self):
    try:
      # Se obtiene los códigos de mensaje y el estado, según las configuraciones
      status, [messages] = self.mail.search(None, 'FROM '+ self.email_target)

      if status != 'OK':
        raise Exception('Estado de obtención no es OK.')

      # En caso de que se hayan obtenido correctamente, se recorren los mensajes según sus códigos
      print('')
      print(Back.WHITE + Fore.BLACK + '----------- Message IDs obtenidos -----------' + Style.RESET_ALL)
      print('')

      # Se abre un archivo para almacenar los message ids de cada mensaje en el buzón
      msg_export_file = open('./exports/messages_ids_validation','w')

      # Se escribe en el archivo las configuraciones utilizadas
      msg_export_file.write('======================================================================= Configuraciones utilizadas\n')
      msg_export_file.write('- Email de cliente: ' + self.email + '\n')
      msg_export_file.write('- Email objetivo / emisor: ' + self.email_target + '\n')
      msg_export_file.write('- Regex asociada a los MID (message id): ' + self.mid_regex + '\n')
      msg_export_file.write('- Mailbox seleccionado: ' + self.mailbox + '\n')
      msg_export_file.write('\n')
      
      header_parser = HeaderParser()
      for message_num in messages.split():
        typ, msg_data = self.mail.fetch(message_num, '(BODY[HEADER])')

        # Se transforma el objeto obtenido para extraer el message-id y la fecha de envío del header.
        try:
          header = header_parser.parsestr(msg_data[0][1].decode('UTF-8'))
          print(Back.CYAN + Fore.WHITE + 'MID: ' + str(header['message-id']) + Style.RESET_ALL + ' ' + Back.YELLOW + Fore.WHITE + '(' + str(header['Date']) + ')' + Style.RESET_ALL)

          # Se escribe el message id obtenido en el archivo
          msg_export_file.write(str(header['message-id']) +'  (' + str(header['Date']) + ')\n')

          # Se comprueba si el message id hace match con la regex (expresión regular) especificada previamente
          plain_mid = str(header['message-id']).replace('<','').replace('>','') # Se remueven los símbolos (<,>) que contienen al MID (message id)
          regex_match = re.search(self.mid_regex, plain_mid) # Matching entre regex y MID

          if regex_match is not None:
            # El message id coincide con la expresión regular especificada
            print(Back.GREEN + Fore.WHITE + 'MID válido según regex.' + Style.RESET_ALL)

            # Se escribe en el archivo la validación de la regex con el MID
            msg_export_file.write('-- Match de regex correcto.\n\n')

          else:
            # El message id NO coincide con la expresión regular especificada. Posible correo falso.
            print(Back.RED+Fore.WHITE+'[!] MID inválido según regex. Posible correo falso.' + Style.RESET_ALL)

            # Se escribe en el archivo la validación de la regex con el MID
            msg_export_file.write('* Match de regex incorrecto. Posible correo falso.\n\n')
        
        except Exception as error:
          print(Back.RED + Fore.WHITE + '[Error] Se produjo el siguiente error en el mensaje ' + str(message_num) + ':')
          print(str(error)+Style.RESET_ALL)
          msg_export_file.write('[Error msg N-' + str(message_num) + '] ' + str(error) + '\n')
        
        print('')
      
      # Se cierra el archivo generado
      msg_export_file.close()

    except Exception as error:
      print(Back.RED + Fore.WHITE + '* Se ha producido el siguiente error al obtener los mensajes:')
      print(str(error) + Style.RESET_ALL)
    
    except KeyboardInterrupt:
      pass
  
  # Menú con opciones para la ejecución del cliente
  def main_menu(self):
    while True:
      clear_screen()
      menu_str = '''
         ┌──────────────────────────────────┐ 
         │           Mail Client            │
         ├──────────────────────────────────┤
         │ [1] Modificar configuración      │
         │ [2] Ver lista de MID             │
         │ [3] Validación de mensajes       │
         │ [4] Salir                        │
         └──────────────────────────────────┘'''
      print(menu_str)
      client_option = input('Selecciona una de las opciones [1-3]: ')

      while client_option not in ['1','2','3','4']:
        client_option = input('Selecciona una de las opciones [1-3]: ')
      
      client_option = int(client_option)

      if client_option == 1:
        clear_screen()
        self.config()

      elif client_option == 2:
        self.show_mid_list()
      
      elif client_option == 3:
        self.show_config()
        self.mid_list_validation()

      elif client_option == 4:
        exit()
      
      print('')
      input('Presiona ENTER para volver al menú.')
  
  # Método para mostrar las configuraciones actuales del cliente
  def show_config(self):
    print('')
    print(Back.WHITE + Fore.BLACK + '----------- Configuraciones actuales de cliente -----------' + Style.RESET_ALL)
    print('')
    print('Email de cliente: ' + self.email)
    print('Password: ' + '*'*len(self.password))
    print('')
    print(Back.WHITE + Fore.BLACK + '----------- Configuraciones del validador -----------' + Style.RESET_ALL)
    print('')
    print('Email objetivo / emisor: ' + self.email_target)
    print('Regex asociada a los MID (message id): ' + self.mid_regex)
    print('Buzón (mailbox) seleccionado: ' + self.mailbox)
    print('')
  
  # Método para configurar variables a utilizar en el proceso
  def config(self):

    if self.filepath:
      client_option = input('¿Deseas cambiar el archivo csv? [s/n]: ')

      while client_option.lower() != 's' and client_option.lower() != 'n':
        client_option = input('¿Deseas cambiar el archivo csv? [s/n]: ')
      
      if client_option.lower() == 's':
        # Se importa el archivo con las expresiones regulares y los correos asociados (emisores)
        self.filepath = input('Ingresa la ruta del archivo csv con las combinaciones a utilizar: ')

        # Se obtiene el contenido del archivo y se registra en la aplicación
        self.import_regex_file()
    
    else:
      # No se ha asociado un archivo con las combinaciones a utilizar
      self.filepath = input('Ingresa la ruta del archivo csv con las combinaciones a utilizar: ')

      # Se obtiene el contenido del archivo y se registra en la aplicación
      self.import_regex_file()

    print('')
    print(Back.WHITE + Fore.BLACK + '----------- Configuraciones -----------' + Style.RESET_ALL)
    print('')

    # Se selecciona de la lista una de las combinaciones entre correo emisor y regex cargadas previamente
    print('Selecciona una de las combinaciones de emisor y regex a utilizar:')
    for i in range(len(self.regex_list)):
      print('['+str(i)+'] '+str(self.regex_list[i]))
    
    print('')
    regex_option = input('> ')
    
    # Se selecciona el mail box a utilizar (Recibidos, Todos, Spam, Papelera, etc.) de la lista
    try:

      self.email_target = self.regex_list[int(regex_option)][0] # Email emisor seleccionado
      self.mid_regex = self.regex_list[int(regex_option)][1] # Regex asociada al email emisor

      status, mailbox_list = self.mail.list()

      if status == 'OK':
        print('')
        print('A continuación, selecciona uno de los buzones (mailbox) para obtener los mensajes: ')
        print('')

        # Se ha obtenido correctamente cada uno de los mailbox
        for mailbox in mailbox_list:
          print('- ' + mailbox.decode('UTF-8'))
      
        print('')
        # Se selecciona un mailbox
        self.mailbox = input('> ')
        self.mail.select(self.mailbox)
    
      else:
        # Se produjo un error al recibir la lista de buzones. Se selecciona INBOX ('Recibidos') por defecto
        self.mail.select('INBOX')
        print(Back.RED + Fore.WHITE + '[Error] Se ha producido un error al obtener la lista de buzones de tu cuenta.' + Style.RESET_ALL)
        return
    
    except Exception as error:
      self.mail.select('INBOX')
      print(Back.RED + Fore.WHITE + '[Error] Se ha producido el siguiente error:')
      print(str(error) + Style.RESET_ALL)
      return
    
    self.show_config()
    input('Presiona ENTER para continuar.')

if __name__ == '__main__':
  clear_screen()
  mail_client = MailClient()