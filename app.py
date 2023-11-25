import streamlit as st
import pandas as pd
import pickle

from PIL import Image

# ====================== главная страница ============================

# параметры главной страницы
# https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config
st.set_page_config(
    layout="wide",
    initial_sidebar_state="auto",
    page_title="weighing_scale",
    page_icon=":bowl_with_spoon:",
)


# ----------- функции -------------------------------------

# функция для загрузки картики с диска
# кэшируем иначе каждый раз будет загружатся заново
@st.cache_data
def load_image(image_path):
    image = Image.open(image_path)
    # обрезка до нужного размера с сохранинием пропорций
    MAX_SIZE = (600, 400)
    image.thumbnail(MAX_SIZE)
    return image

# функция загрузки модели
# кэшируем иначе каждый раз будет загружатся заново
@st.cache_data
def load_model(model_path):
    # загрузка сериализованной модели
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model


# ------------- загрузка картинки для страницы и модели ---------

# путь до картинки
image_path = './images/feet_on_scales.jpeg'
image = load_image(image_path)


# ---------- отрисовка текста и картинки ------------------------
st.write(
    """
    # Узнайте свой вес завтра
    """
)

# отрисовка картинки на странице
st.image(image)

st.write('Введите сегодняшние данные для получения прогноза')

user_weight = st.number_input("Вес пользователя", max_value=199.0, value=70.0, step=0.1)

if user_weight == 0:
    st.error('Вы - невесомы 	:cloud:')
    st.error('Введите корректный вес')
    st.stop()

#st.write('# Выберите модель')
model_type = st.radio(
    "Выберите модель",
    ["CatBoostRegressor", "DecisionTreeRegressor", "LinearRegression"],
    captions = ["Бустинг", "Дерево решений", "Прямая зависимость"])

cat_model = './models/cat_model.pkl'
dtr_model = './models/dtr_model.pkl'
regr_model = './models/regr_model.pkl'

# путь до модели
model_path = ''

if model_type == "CatBoostRegressor":
    model_path = cat_model

if model_type == "DecisionTreeRegressor":
    model_path = dtr_model

if model_type == "LinearRegression":
    model_path = regr_model

weight_model = load_model(model_path)


# ====================== боковое меню для ввода данных ===============

st.sidebar.header('Входные данные пользователя')

# словарь с названиями признаков и описанием для удобства
features_dict = {
    'calories_in': 'Количество полученных каллорий (Ккал)',
    'calories_out': 'Количество потраченных каллорий (Ккал)',
    'protein': 'Количество полученных белков (г)',
    'fats': 'Количество полученных жиров (г)',
    'carbs': 'Количество полученных углеводов (г)',
    'fibers': 'Количество полученных пищевых волокон (г)',
    'sugar': 'Потребление сахара (да/нет)',
    }


# Исторические минимумы и максимумы датасета
# calories_in 		224.0	4150.3
# calories_out	36.0	1941.0
# protein	20.0	229.0
# fats	8.0		173.0
# carbs	38.0	659.7
# fibers	3.0 	66.0
# sugar 0 1


# кнопки / слайдеры для ввода дынных
calories_in = st.sidebar.slider(features_dict['calories_in'], min_value=0.0, max_value=5000.0, value=2000.0, step=1.0)
calories_out = st.sidebar.slider(features_dict['calories_out'], min_value=0.0, max_value=3000.0, value=2000.0, step=1.0)
protein = st.sidebar.slider(features_dict['protein'], min_value=0.0, max_value=230.0, value=100.0, step=1.0)
fats = st.sidebar.slider(features_dict['fats'], min_value=0.0, max_value=180.0, value=50.0, step=1.0)
carbs = st.sidebar.slider(features_dict['carbs'], min_value=0.0, max_value=700.0, value=300.0, step=1.0)
fibers = st.sidebar.slider(features_dict['fibers'], min_value=0.0, max_value=70.0, value=30.0, step=1.0)
sugar_check = st.sidebar.checkbox(features_dict['sugar'], value=False)

sugar = 0

if sugar_check:
    sugar = 1

# записать входные данные в словарь и в датафрейм
data = {
    'calories_in': calories_in,
    'calories_out': calories_out,
    'protein': protein,
    'fats': fats,
    'carbs': carbs,
    'fibers': fibers,
    'sugar': sugar,
    }
df = pd.DataFrame(data, index=[0])


# =========== вывод входных данных и предсказания модели ==========

# вывести входные данные на страницу
st.write("## Ваши данные")
st.write(df)


# предикт моделью на входных данных
weight_diff = weight_model.predict(df.values)

tomorrow_weight = user_weight + weight_diff

# вывести предсказание модели
st.write("Ваш прогнозируемый вес завтра")
st.write(tomorrow_weight)


st.write("Изменение веса в %")
st.write(((tomorrow_weight / user_weight) * 100) - 100)


