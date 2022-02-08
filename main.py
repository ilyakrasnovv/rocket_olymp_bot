import csv
from telethon import TelegramClient, events, Button
from telethon.tl.custom.message import Message
import datetime

curstate = dict()
client = TelegramClient("ботяра", 1269982, "abc59d6aea8c3e69212af34e03831d92")
client.start(bot_token="5123423854:AAG2wg8gDpmE2MjLrTZgapHYV8a5JpGth2Q")
client.parse_mode = "html"
registrations = open('reg_form.csv', 'a', newline='')


async def format_registrations():
    prvs = set()
    freg = open('final_reg_form.csv', 'w', newline='')
    reg_writer = csv.writer(freg, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    regs_reader = csv.reader(open("reg_form.csv", 'r'), delimiter=',', quotechar='|')
    data = [row for row in regs_reader]
    data.reverse()
    for participant in data:
        if participant[0] in prvs:
            continue
        reg_writer.writerow(participant)
        prvs.add(participant[0])


async def write_registration(pid, ptime, pname, pclass):
    reg_writer = csv.writer(registrations, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    reg_writer.writerow([pid, ptime, pname, pclass])


async def get_name(chat_id):
    await client.send_message(chat_id, "Пришли одним сообщением своё имя и фамилию")
    curstate[chat_id] = ("await_name", "")


classes = ["5-6", "7", "8", "9"]


async def get_class(chat_id):
    await client.send_message(chat_id, "Выбери, из какого ты класса",
                              buttons=list(map(Button.text, classes)))
    curstate[chat_id] = ("await_class", curstate[chat_id][1])


ILYA = 708783390


@client.on(events.NewMessage(pattern='.*'))
async def handler(message: Message):
    sender = await message.get_sender()
    if message.text == "/send_final_csv" and sender.id == ILYA:
        await format_registrations()
        await client.send_file(sender.id, "final_reg_form.csv")
    elif message.text == "/send_csv" and sender.id == ILYA:
        await client.send_file(sender.id, "reg_form.csv")
    elif sender.id in curstate:
        state = curstate[sender.id][0]
        if state == "await_name":
            curstate[sender.id] = ("class", message.text)
            await get_class(sender.id)
        elif state == "await_class":
            text = message.text.strip()
            if text in classes:
                await write_registration(sender.id, datetime.datetime.now().strftime("%Y.%m.%d %H:%M"),
                                         curstate[sender.id][1], text)
                await message.reply(
                    f"<b>Проверь свои регистрационные данные:\nИмя Фамилия:</b> {curstate[sender.id][1]}\n<b>Класс "
                    f"обучения и участия:</b> {text}\n\nЕсли что-то не так, то зарегистрируйся заново, написав любое "
                    f"сообщение.\nПеред началом пробного тура мы вышлем сюда адрес и данные для входа в тестирующую "
                    f"систему.",
                    buttons=Button.clear())
                await client.send_message(ILYA, "Новая регистрация: " + " ".join(
                    [str(sender.id), datetime.datetime.now().strftime("%Y.%m.%d %H:%M"),
                     curstate[sender.id][1], text]))
                curstate.pop(sender.id)

            else:
                await message.reply("Выбери класс из этого списка: " + " ".join(classes))
    else:
        await client.send_message(sender.id,
                                  "Привет! Это бот олимпиады @rocket_olymp. Давай приступим к регистрации.\n\n<i><p><a "
                                  "href=\"https://rocketclass.ru/policy\">Продолжая регистрацию, вы даете согласие на "
                                  "обработку персональных данных и соглашаетесь с политикой конфиденциальности и "
                                  "получением рекламных рассылок.</a></p></i>")
        await get_name(sender.id)


try:
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
finally:
    client.disconnect()
