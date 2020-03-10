import os

def translate(lang,field,optional=[]):
    if lang == 'ru':
        if field == 'greetings':
            return 'Привет! Это бот технической поддержки. Проект ' + os.environ['PROJECT_KEY'] + '.\nНапишите свой запрос одним текстом.\nЧем больше сообщите нам в заявке сведений о проблеме, тем быстрее нам удастся помочь Вам.\nСпасибо.'
        if field == 'invalidInput':
            return 'Команда не распознана. Пожалуйста, попытайтесь снова или обратитесь в службу техподдержки.'
        if field == 'cancelTicketButton':
            return 'Отменить заявку'
        if field == 'ticketSent':
            return 'Заявка была отправлена.\nСсылка на заявку: '
        if field == 'veryLongFirstWordInRequest':
            return 'Заявка от бота ' + os.environ['PROJECT_KEY']
        if field == 'createdBy':
            return 'Заявка создана ботом проекта ' + os.environ['PROJECT_KEY']
        if field == 'cancelRequest':
            return 'Вы отменили отправку заявки.'
        if field == 'ticketConfirmation':
            return 'Ваш текст заявки:\n***\n'
        if field == 'tooManyRequests':
            return 'Вы отправляете слишком много запросов. Попробуйте подождать и отправить заявку позже.'
        if field == 'imTooSeriousForYourMedia':
            return 'Бот не принимает файлы, в т.ч. видео и фото в качестве заявки.\nПопробуйте отправить заявку в виде текста.'
        if field == 'requestError':
            return 'Ошибка при обработке запроса. Попробуйте снова.'
        if field == 'jiraAuthError':
            return 'Ошибка связи с Jira. Попробуйте отправить заявку еще раз.\nЕсли повторная отправка сообщения не дала результата - пишите заявку [через портал](' + optional[0] + '/servicedesk/customer/portal/' + optional[1] + ') .'
        if field == 'jiraUserNotExists':
            return 'Не найден пользователь в Jira с вашим логином.\nПишите заявку [через портал](' + optional[0] + '/servicedesk/customer/portal/' + optional[1] + ') .'
        if os.environ['ISSUE_TYPE_MODE'] == '0':
            if field == 'ticketSent':
                return 'Заявка была отправлена.\nСсылка на заявку: '
        if os.environ['ISSUE_TYPE_MODE'] == '1':
            if field == 'creatingTicket':
                return '\u23F3 Пока отправляется заявка в проект ' + os.environ['PROJECT_KEY'] + ', просим Вас указать категорию заявки (это не обязательно).\nЭто позволит быстрее помочь Вам.\nНет требуемой категории заявки - пишите заявку [через портал](' + optional[0] + '/servicedesk/customer/portal/' + optional[1] + ') .\nЕсли хотите изменить текст заявки, нажмите "Отменить заявку" и напишите еще раз.'
        elif os.environ['ISSUE_TYPE_MODE'] == '2':
            if field == 'creatingTicket':
                return 'Сейчас будет создана заявка в проекте ' + os.environ['PROJECT_KEY'] + '. Просим Вас указать категорию заявки.\nЭто позволит быстрее помочь Вам.\nНет требуемой категории заявки - пишите заявку [через портал](' + optional[0] + '/servicedesk/customer/portal/' + optional[1] + ') .\nЕсли хотите изменить текст заявки, нажмите "Отменить заявку" и напишите еще раз.'
            if field == 'cancelledByTimeout':
                return 'Отправка вашей заявки была отменена в связи с превышением допустимого времени ожидания выбора.\nПопробуйте еще раз.'
    return 'TranslationError'