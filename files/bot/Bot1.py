import os
import glob
import logging
logging.basicConfig(filename='Bot1Log.txt', level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s', encoding="utf-8")
from dotenv import load_dotenv
#import requests
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
import re
import paramiko
from pathlib import Path
import psycopg2
from psycopg2 import Error

load_dotenv()

token = os.getenv('TG_TOKEN')
chat_id = os.getenv('TG_CHAT_ID')

logging.debug(f'Load tg token {token}')
logging.debug(f'Load chat_id {chat_id}')

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(url, json=payload)
    logging.debug(f'API Response {response}')
    if response.status_code == 200:
        print("Сообщение успешно отправлено!")
    else:
        print("Ошибка при отправке сообщения:", response.text)
        logging.error(f'API Error {response.text}')

message_text = "Привет, мир! Это сообщение отправлено через Telegram Bot API."

#send_message(token, chat_id, message_text)

def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}!')

def echo(update: Update, context):
    update.message.reply_text(update.message.text)

def findPhoneNumbersCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'findPhoneNumbers'

def findEmailsCommand(update: Update, context):
    update.message.reply_text('Введите текст для поиска адресов электронной почты: ')
    return 'findEmails'

def verifyPasswordCommand(update: Update, context):
    update.message.reply_text('Введите пароль для проверки: ')
    return 'verifyPasswords'

def getHelp(update: Update, context):
    update.message.reply_text('Доступные комманды: \n /find_phone_number - Поиск телефона в тектсе ~\n /find_email - Поиск адреса электронной почты в тесте \n /verify_password - Проверка сложноти пароля \n /help - Справка по доступным коммандам \n\n Мониторинг Linux. иформация: \n/get_release - О релизе \n /get_uname - Об архитектуры процессора, имени хоста системы и версии ядра.\n /get_uptime - О времени работы. \n /get_df - Сбор информации о состоянии файловой системы.\n /get_free - Сбор информации о состоянии оперативной памяти.\n /get_mpstat - Сбор информации о производительности системы.\n /get_w - Сбор информации о работающих в данной системе пользователях. \n /get_auths - Последние 10 входов в систему. \n /get_critical - Последние 5 критических события.\n  /get_ps - Сбор информации о запущенных процессах.\n /get_ss - Сбор информации об используемых портах.\n /get_apt_list - Сбор информации об установленных пакетах.\n /get_services - Сбор информации о запущенных сервисах. \n\n Работа с базой данных: \n/get_repl_logs - Информация о репликации базы данных.\n /get_emails - Информация о хранимых в базе данных адресах электронной почты.\n /get_phone_numbers - Информация о хранимых в базе данных телефонных номерах.')
    return

def GetAptListCommand(update: Update, context):
    update.message.reply_text('Введите all для просмотра всех пактов или имя пакета для просмотра информации')
    return 'getAptList'

def getAptList(update: Update, context):
    user_input = update.message.text
    try:
        if user_input == 'all':
            result = sshExecCommand('apt list --installed')
        else:
            result = sshExecCommand('apt list '+ user_input +' --installed')
            if not user_input in result:
                result = 'Данный пакет не найден в системе'     
    except Exception as err:
        logging.error(f'Error: {err}')        
    msgs = [result[i:i + 4096] for i in range(0, len(result), 4096)]
    for text in msgs:
        update.message.reply_text(text=text)
    return ConversationHandler.END

def verifyPasswords (update: Update, context):
    user_input = update.message.text
    passwordRegex = re.compile(r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()])[A-Za-z\d!@#$%^&*()]{8,}')
    try:
        passwordCheck = passwordRegex.findall(user_input)
        logging.debug(f'PasswordCheck: {passwordCheck}')
    except Exception as err:
        logging.error(f'RegexError: {err}')
        update.message.reply_text('Произошла ошибка при проверке пароля, попробуйте позднее')     
    if not passwordCheck:
        update.message.reply_text('Простой пароль')
        return ConversationHandler.END
    update.message.reply_text('Пароль сложный')
    return ConversationHandler.END

def sshExecCommand(command):
    logging.debug(f'Entering SSHConnect')
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host = os.getenv('HOST')
    port = os.getenv('PORT')
    username = os.getenv('USERNAME')
    password = os.getenv ('PASSWORD')
    logging.debug(f'LoadedEnv {host}, {port}. {username}, {password}')
    try:
         client.connect(hostname=host, username=username, password=password, port=port)
         stdin, stdout, stderr = client.exec_command(command)
         data = stdout.read() + stderr.read()
         client.close()
    except Exception as err:
        logging.error(f'ConnectonError: {err}')
    data = str(data).replace('\\n', '\n').replace('\\t', '\t')[2:-1]
    logging.debug(f'ReleaseMessage: {data}')
    return data

def getRelease(update: Update, context):
    update.message.reply_text('Информация о ОС:')
    logging.debug(f'Entering getRelease')
    try:
         result = sshExecCommand('hostnamectl')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return 

def getUname(update: Update, context):
    update.message.reply_text('Информация о ОС:')
    logging.debug(f'Entering getUname')
    try:
         result = sshExecCommand('uname -r')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return

def getUptime(update: Update, context):
    update.message.reply_text('Время работы системы:')
    logging.debug(f'Entering getUptime')
    try:
         result = sshExecCommand('uptime')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return

def getDf(update: Update, context):
    update.message.reply_text('Информация о файловой системе:')
    logging.debug(f'Entering getDf')
    try:
         result = sshExecCommand('df -h')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return
def getFree(update: Update, context):
    update.message.reply_text('Информация о оперативной памяти:')
    logging.debug(f'Entering getFree')
    try:
         result = sshExecCommand('free')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return

def getMPstat(update: Update, context):
    update.message.reply_text('Информация о производительности системы:')
    logging.debug(f'Entering getMPstat')
    try:
         result = sshExecCommand('mpstat')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return

def getW(update: Update, context):
    update.message.reply_text('Информация о пользователях системы:')
    logging.debug(f'Entering getW')
    try:
         result = sshExecCommand('w')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return

def getAuths(update: Update, context):
    update.message.reply_text('Последние 10 входов в систему:')
    logging.debug(f'Entering getAuths')
    try:
         result = sshExecCommand('last -n 10')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return

def getCritical(update: Update, context):
    update.message.reply_text('Последние 5 критических события:')
    logging.debug(f'Entering getCritical')
    try:
         result = sshExecCommand('journalctl -p err -b -n 5 --no-pager')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    update.message.reply_text(result)
    return

def getPs(update: Update, context):
    update.message.reply_text('Информация о запущенных процессах:')
    logging.debug(f'Entering getPs')
    try:
         result = sshExecCommand('ps -aux')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    msgs = [result[i:i + 4096] for i in range(0, len(result), 4096)]
    for text in msgs:
        update.message.reply_text(text=text)
    return

def getSs(update: Update, context):
    update.message.reply_text('Информация о используемых портах:')
    logging.debug(f'Entering getSs')
    try:
         result = sshExecCommand('ss -pl')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    msgs = [result[i:i + 4096] for i in range(0, len(result), 4096)]
    for text in msgs:
        update.message.reply_text(text=text)
    return 

def getServices(update: Update, context):
    update.message.reply_text('Информация о запущенных сервисах:')
    logging.debug(f'Entering getServices')
    try:
         result = sshExecCommand('systemctl list-units --type=service --state=running')
    except Exception as err:
        update.message.reply_text('Произошла ошибка подключения, попробуйте позднее')
    msgs = [result[i:i + 4096] for i in range(0, len(result), 4096)]
    for text in msgs:
        update.message.reply_text(text=text)
    return 

def getReplLogs(update: Update, context):
    list_of_logs = glob.glob('/var/lib/postgresql/13/main/log/*')
    latest_log = max(list_of_logs, key=os.path.getctime)
    logging.debug(f'LatestLogFile: {latest_log}')
    replLogsRegex = re.compile(r"received replication command:.*")
    try: 
        with open(latest_log) as f:
                line = f.read()
                logMessage = ''
                for match in re.finditer(replLogsRegex, line):
                    logging.debug(f'ReplLogs: {match.group()}')
                    logMessage += f'{match.group()}\n'
                update.message.reply_text(logMessage)
    except Exception as err:
           logging.error(f'RegexError: {err}')                
    return

def sqlExecCommand(command):
    username = os.getenv('PG_UNAME')
    password = os.getenv('PG_PASSWORD')
    host = os.getenv('PG_HOST')
    port = os.getenv('PG_PORT')
    database = os.getenv('PG_DB')
    try:
        connection = psycopg2.connect( user=username,
                                  password = password,
                                  host = host,
                                  port = port,
                                  database = database
        )
        cursor = connection.cursor()
        cursor.execute(command)
        if cursor.pgresult_ptr is not None:
           data = cursor.fetchall()
        else:
            data = cursor.statusmessage
            insertRegex = re.compile(r'INSERT*.')
            if (insertRegex.findall(data)):
                logging.debug(f'Qery: {command} return: {data}')
                connection.commit()
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        if connection is not None:
            cursor.close()
            connection.close()  
    return data  



def getEmails(update: Update, context):
    try:
        data = sqlExecCommand(f'SELECT email from emails')
        emails = ''
        for row in data:
            emails += f'{" ".join(row)}\n'
        update.message.reply_text(emails)
    except Exception as err:
        logging.error(f'Ошибка поиска: {err}')
    return

def getPhones(update: Update, context):
    try:
        data = sqlExecCommand(f'SELECT phone from phones')
        phones = ''
        for row in data:
            phones += f'{" ".join(row)}\n'
        update.message.reply_text(phones)
    except Exception as err:
        logging.error(f'Ошибка поиска: {err}')
    return


def findEmails (update: Update, context):
    user_input = update.message.text
    emailsRegex = re.compile(r'[A-za-z0-9!#$%&\'*+-/=?^_`{|}~]{3,64}@[A-za-z0-9\-]{3,63}\.[A-Za-z]{2,15}')
    emilsTwoDotsRegex = re.compile(r'.*\.{2,}.*')
    try:
        emailsList = emailsRegex.findall(user_input)
        logging.debug(f'EmailsSearchResult1: {emailsList}')
        emailToRemove = []
        for element in emailsList:
            logging.debug(f'Element: {element}')
            emailsListFilter = emilsTwoDotsRegex.findall(element)
            logging.debug(f'EmailsSearchResult2: {emailsListFilter}')
            if emailsListFilter:
                 logging.debug(f'ElementToRemove: {emailsListFilter}')
                 emailToRemove.append(emailsListFilter[0])
        logging.debug(f'ElementToRemove: {emailToRemove}')
        for element in emailToRemove:
            emailsList.remove(element)
        logging.debug(f'EmailsSearchResultFinal: {emailsList}')

    except Exception as err:
        logging.error(f'RegexError: {err}')
        update.message.reply_text('Произошла ошибка поиска, повторите поиск позднее')
    if not emailsList:
        update.message.reply_text('Адреса электронной почты не найдены')
        return ConversationHandler.END
    update.message.reply_text('Найденные адреса электронной почты:')
    emails = ''
    for i in range(len(emailsList)):
        emails += f'{i+1}. {emailsList[i]}\n'
    update.message.reply_text(emails)
    update.message.reply_text('Хотите сохранить данные в базу? (Да/Нет)')
    key = 'stored_emails'
    context.user_data[key] = emailsList
    return 'saveEmailResult'
   

def saveEmailResult(update: Update, context):
    user_answ = update.message.text
    logging.debug(f'Ответ: {user_answ}')
    try:
        if user_answ == 'Да':
            update.message.reply_text('Сохраняю')
            key = 'stored_emails'
            emailsList = context.user_data.get(key)
            logging.debug(f'ContextData: {emailsList}')
            emails = ''
            for i in range(len(emailsList)):
                emails += f'{emailsList[i]}\n'
                slqQery = 'insert into emails (email) values (\'' + str(emailsList[i]) + '\') ON CONFLICT DO NOTHING;'
                logging.debug(f'Trying to execute: {slqQery}')
                data = sqlExecCommand(str(slqQery))
                logging.debug(f'Insert operation return data: {data}')
                returnRegex = re.compile(r'INSERT (\d) (\d)')
                retResult = returnRegex.search(data)
                if retResult:
                    logging.debug(f'Insert operation return value: {retResult.group(2)}')
                    if retResult.group(2) == '1':
                        update.message.reply_text(f'Значение: {emailsList[i]} сохранено в базу данных')
                    if retResult.group(2) == '0':
                        update.message.reply_text(f'Значение: {emailsList[i]} уже присутствует в базе данных, пропускаю')
                else:
                    logging.debug(f'Insert operation unknown return value: {data}')
                    update.message.reply_text(f'Произошла ошибка сохранения')
            return ConversationHandler.END
        elif user_answ == 'Нет':
            update.message.reply_text('Не сохраняю')
            return ConversationHandler.END 
        else:
            update.message.reply_text('Ответ да или нет')
            return 'saveEmailResult'
    except Exception as err:
        logging.error(f'saveEmailError: {err}')
        update.message.reply_text('Произошла ошибка сохранения результата, попробуйте еще раз')

def findPhoneNumbers (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    #phoneNumRegex = re.compile(r'8 \(\d{3}\) \d{3}-\d{2}-\d{2}') # формат 8 (000) 000-00-00
    phoneNumRegex = re.compile(r'(?:\+7|8)\-?\s?\(?\d{3}\)?\s?\-?\d{3}\-?\s?\d{2}\-?\s?\d{2}') #варианты записи номеров телефона. 8XXXXXXXXXX, 8(XXX)XXXXXXX, 8 XXX XXX XX XX, 8 (XXX) XXX XX XX, 8-XXX-XXX-XX-XX. Также вместо ‘8’ на первом месте может быть ‘+7’.
    try:
        phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов
        logging.debug(f'PhoneSearchResult: {phoneNumberList}')
    except Exception as err:
       logging.error(f'RegexError: {err}')
       update.message.reply_text('Произошла ошибка поиска, повторите поиск позднее')

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END # Завершаем выполнение функции
    
    update.message.reply_text('Найденные телефонные номера:')
    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text('Хотите сохранить данные в базу? (Да/Нет)')
    key = 'stored_phones'
    context.user_data[key] = phoneNumberList
    return 'savePhoneResult'
   
def savePhoneResult(update: Update, context):
    user_answ = update.message.text
    logging.debug(f'Ответ: {user_answ}')
    try:
        if user_answ == 'Да':
            update.message.reply_text('Сохраняю')
            key = 'stored_phones'
            phonesList = context.user_data.get(key)
            logging.debug(f'ContextData: {phonesList}')
            phones = ''
            for i in range(len(phonesList)):
                phones += f'{phonesList[i]}\n'
                slqQery = 'insert into phones (phone) values (\'' + str(phonesList[i]) + '\') ON CONFLICT DO NOTHING;'
                logging.debug(f'Trying to execute: {slqQery}')
                data = sqlExecCommand(str(slqQery))
                logging.debug(f'Insert operation return data: {data}')
                returnRegex = re.compile(r'INSERT (\d) (\d)')
                retResult = returnRegex.search(data)
                if retResult:
                    logging.debug(f'Insert operation return value: {retResult.group(2)}')
                    if retResult.group(2) == '1':
                        update.message.reply_text(f'Значение: {phonesList[i]} сохранено в базу данных')
                    if retResult.group(2) == '0':
                        update.message.reply_text(f'Значение: {phonesList[i]} уже присутствует в базе данных, пропускаю')
                else:
                    logging.debug(f'Insert operation unknown return value: {data}')
                    update.message.reply_text(f'Произошла ошибка сохранения')
            return ConversationHandler.END
        elif user_answ == 'Нет':
            update.message.reply_text('Не сохраняю')
            return ConversationHandler.END 
        else:
            update.message.reply_text('Ответ да или нет')
            return 'savePhoneResult'
    except Exception as err:
        logging.error(f'savePhoneResult: {err}')
        update.message.reply_text('Произошла ошибка сохранения результата, попробуйте еще раз')


def main():
		# Создайте программу обновлений и передайте ей токен вашего бота
    updater = Updater(token, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher
		
    convHandlerFindPhoneNumbers = ConversationHandler(
       entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
       states={
           'findPhoneNumbers': [MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)],
           'savePhoneResult': [MessageHandler(Filters.text & ~Filters.command, savePhoneResult)],
       },
       fallbacks=[]
    )

    convHandlerFindEmails = ConversationHandler(
       entry_points=[CommandHandler('find_email', findEmailsCommand)],
       states={
           'findEmails': [MessageHandler(Filters.text & ~Filters.command, findEmails)],
           'saveEmailResult': [MessageHandler(Filters.text & ~Filters.command, saveEmailResult)],
       },
       fallbacks=[]
    )

    convHandlerVerifyPassword = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verifyPasswordCommand)],
        states={
            'verifyPasswords' : [MessageHandler(Filters.text & ~Filters.command, verifyPasswords)]
        },
        fallbacks=[]
    )
    

    
    convHandlerGetAptList = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', GetAptListCommand)],
        states={
            'getAptList' : [MessageHandler(Filters.text & ~Filters.command, getAptList)]
        },
        fallbacks=[]
    )

		# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerFindEmails)
    dp.add_handler(convHandlerVerifyPassword)
    dp.add_handler(CommandHandler("get_release", getRelease))
    dp.add_handler(CommandHandler("get_uname", getUname))
    dp.add_handler(CommandHandler("get_uptime", getUptime))
    dp.add_handler(CommandHandler("get_df", getDf))
    dp.add_handler(CommandHandler("get_free", getFree))
    dp.add_handler(CommandHandler("get_mpstat", getMPstat))
    dp.add_handler(CommandHandler("get_w", getW))
    dp.add_handler(CommandHandler("get_auths", getAuths))
    dp.add_handler(CommandHandler("get_critical", getCritical))
    dp.add_handler(CommandHandler("get_ps", getPs))
    dp.add_handler(CommandHandler("get_ss", getSs))
    dp.add_handler(CommandHandler("get_services", getServices))
    dp.add_handler(CommandHandler("help", getHelp))
    dp.add_handler(convHandlerGetAptList)
    dp.add_handler(CommandHandler("get_repl_logs", getReplLogs))
    dp.add_handler(CommandHandler("get_emails", getEmails))
    dp.add_handler(CommandHandler("get_phone_numbers", getPhones))

	
		# Регистрируем обработчик текстовых сообщений
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

   
		
		# Запускаем бота
    updater.start_polling()

		# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
