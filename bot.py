import discord
import json
import re
import nltk
from difflib import SequenceMatcher
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


nltk.download('punkt')
nltk.download('popular')


# token do bot.
TOKEN = 'MTI1NDczMzIxMzA3NTY0MDM2Mw.GQu57j.0xhXLGRQoXvz5ULfQVsXERZT5YPPTcH-cLCazs'


with open('perguntas_respostas.json', 'r', encoding='utf-8') as file:
    data = json.load(file)['questions']


intents = discord.Intents.default()
intents.message_content = True  # Habilita o intent para mensagens

client = discord.Client(intents=intents)

# Tokenizar e remover stopwords (palavras comuns que não contribuem muito para o significado)
stop_words = set(stopwords.words('portuguese'))


def normalize_text(text):
   
    normalized_text = text.lower()
    normalized_text = re.sub(r'[^\w\s]', '',
                             normalized_text)  # Remove pontuações
    normalized_text = re.sub(r'\s+', ' ',
                             normalized_text.strip())  # Remove espaços extras
    return normalized_text


def preprocess_text(text):
    # Tokeniza o texto e remove stopwords
    tokens = word_tokenize(text, language='portuguese')
    tokens = [token for token in tokens if token not in stop_words]
    return tokens


def similaridade_textual(texto1, texto2):
    # Calcula a similaridade entre dois textos usando SequenceMatcher
    matcher = SequenceMatcher(None, texto1, texto2)
    return matcher.ratio()


def get_answer(question):
    normalized_question = normalize_text(question)
    question_tokens = preprocess_text(normalized_question)

    best_match = None
    best_similarity = 0.0

    for item in data:
        normalized_item_question = normalize_text(item['question'])
        item_tokens = preprocess_text(normalized_item_question)

        similarity = similaridade_textual(question_tokens, item_tokens)

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = item['answer']

    return best_match if best_similarity >= 0.6 else None  # Limiar de similaridade ajustável


@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    print('Bot está pronto para uso!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!p'):
        question = message.content[len('!p '):]
        answer = get_answer(question)

        if answer:
            await message.channel.send(answer)
        else:
            await message.channel.send(
                'Desculpe, você parece ser meio analfabeto faça a pergunta direito.')


# Executar o bot
client.run(TOKEN)