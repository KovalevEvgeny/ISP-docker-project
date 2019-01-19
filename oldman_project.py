import matplotlib.pyplot as plt
import random
import re
from wordcloud import WordCloud

class Dictogram(dict):
    def __init__(self, iterable=None):
        # Инициализируем наше распределение как новый объект класса, 
        # добавляем имеющиеся элементы
        super(Dictogram, self).__init__()
        self.types = 0  # число уникальных ключей в распределении
        self.tokens = 0  # общее количество всех слов в распределении
        self.seed = 0
        if iterable:
            self.update(iterable)

    def update(self, iterable):
        # Обновляем распределение элементами из имеющегося 
        # итерируемого набора данных
        for item in iterable:
            if item in self:
                self[item] += 1
                self.tokens += 1
            else:
                self[item] = 1
                self.types += 1
                self.tokens += 1

    def count(self, item):
        # Возвращаем значение счетчика элемента, или 0
        if item in self:
            return self[item]
        return 0

    def return_random_word(self):
        random.seed(self.seed)
        self.seed += 1
        random_key = random.sample(self, 1)
        # Другой способ:
        # random.choice(histogram.keys())
        return random_key[0]

    def return_weighted_random_word(self):
        # Сгенерировать псевдослучайное число между 0 и (n-1),
        # где n - общее число слов
        random.seed(self.seed)
        self.seed += 1
        random_int = random.randint(0, self.tokens-1)
        index = 0
#         list_of_keys = 
        # вывести 'случайный индекс:', random_int
        for key in self.keys():
            index += self[key]
            # вывести индекс
            if(index > random_int):
                # вывести list_of_keys[i]
                return key
            

def make_markov_model(order, data):
    markov_model = dict()
    for i in range(0, len(data)-order):
        # Создаем окно
        window = tuple(data[i: i+order])
        # Добавляем в словарь
        if window in markov_model:
            # Присоединяем к уже существующему распределению
            markov_model[window].update([data[i+order]])
        else:
            markov_model[window] = Dictogram([data[i+order]])
    return markov_model


def generate_random_start(model):
    # порядок модели
    order = len(next(iter(model)))
    if order == 1:
        if ('END',) in model:
            return (model[('END',)].return_weighted_random_word(),)
    else:
        # генерируем корректные начальные кортежи, то есть те, что являлись началом предложений в корпусе
        end_keys = [t for t in list(model.keys()) if t[0] == 'END']
        if end_keys:
            random.seed(99999)
            random_int = random.randint(0, sum([sum(model[key].values()) for key in end_keys]) - 1)
            index = 0
            for key in end_keys:
                index += sum(model[key].values())
                if index > random_int:
                    return key
    return random.choice(list(model.keys()))


def generate_random_sentence(length, model):
    order = len(next(iter(model)))
    if order == 1:
        current_tuple = ('END',)
    else:
        current_tuple = generate_random_start(model)
    sentence = [current_tuple]
    i = 0
    while i < length:
        # если рассматриваемый кортеж является самым последним в тексте, то может возникнуть ошибка, ибо после него ничего нет
        try:
            current_dictogram = model[current_tuple]
            random_weighted_word = current_dictogram.return_weighted_random_word()
            current_tuple = current_tuple[1:] + (random_weighted_word,)
            sentence.append(current_tuple)
            i += 1
        except:
            # в случае ошибки генерируем случайный стартовый кортеж
            new_start = generate_random_start(model)
            j = 0
            # следим за тем, чтобы длина предложения не превысила заданный порог
            while j < order and i + j < length:
                sentence.append(current_tuple[j:] + new_start[:j])
                j += 1
            i += order
    sentence = [t[0] for t in sentence][1:]
    sentence[0] = sentence[0].capitalize()
    for i in range(1, len(sentence)):
        # все слова после знаков окончания предложения выводим с большой буквы
        try:
            if sentence[i - 1] == 'END' or sentence[i - 1][-1] in ['?', '!']:
                sentence[i] = sentence[i].capitalize()
        except:
            continue
    sentence = ' '.join(sentence).replace(' END', '.')
    # если в конце сгенерированного предложения нет знака окончания предложения, то нужно добавить точку
    if sentence[-1] in ['.', '?', '!']:
        return sentence
    else:
        return sentence + '.'
    
    
text = open('oldman.txt', 'r', encoding='utf-8').read()
text = re.sub('»|”|\.', ' END', text)
# переводим несколько последовательных вхождений END в одно
text = re.sub('( END)+', ' END', text)
# далее 'END' будет заменено на точку, что не имеет смысла, если перед ним стоит '?' либо '!'
text = re.sub('\? END', '?', text)
text = re.sub('! END', '!', text)
text = re.sub('«|“|,', '', text)
text = re.sub('\n', ' ', text)
frags = [f.lower() if f != 'END' else f for f in text.split(' ') if f]

plt.figure(figsize=(20,10), facecolor='k')
tfidf_wordcloud = WordCloud(width=1600, height=800, random_state=13).generate(' '.join(frags).replace(' END ', ' '))
plt.imshow(tfidf_wordcloud, interpolation="bilinear")
plt.tight_layout(pad=0)
plt.axis("off")
plt.savefig('results/oldman_wordcloud.png')

model = make_markov_model(8, frags)
st = generate_random_sentence(1000, model)
with open("results/generated_text.txt", "w") as text_file:
    text_file.write(st)