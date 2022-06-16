from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


def get_incorrected_value(value: str):
    """Функция для получения некорректного значения путем изменения первого
    символа корректного значения"""

    print("Текущее значение: " + value)

    value = "f" + value[:-1]
    print("Новое значение: " + value)
    return value


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """Тест на проверку получения api-ключа при корректных
    данных почты и пароля"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в results
    status, results = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in results


def test_get_all_pets_with_valid_key(filter=''):
    """Тест проверяет, что запрос всех питомцев возвращает
       не пустой список"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, results = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(results['pets']) > 0


def test_get_api_key_without_data(email="", password=""):
    """Тест на проверку получения api-ключа без данных"""

    status, _ = pf.get_api_key(email, password)

    assert status == 403


def test_get_api_key_incorrected_without_email(email="", password=valid_password):
    """Тест на проверку получения api-ключа
       при корректном пароле и без почты"""

    status, _ = pf.get_api_key(email, password)

    assert status == 403


def test_get_api_key_incorrected_without_password(email=valid_email, password=""):
    """Тест на проверку получения api-ключа
        при корректной почте и без пароля"""

    status, _ = pf.get_api_key(email, password)

    assert status == 403


def test_get_list_of_all_pets_incorrected_key():
    """Тест на проверку получения списка всех питомцев
        при авторизации с неверным ключом"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    auth_key['key'] = get_incorrected_value(auth_key['key'])
    filter = ""

    status, results = pf.get_list_of_pets(auth_key=auth_key, filter=filter)

    assert status == 403


def test_get_list_of_my_pets_corrected():
    """Тест на проверку получения списка только питомцев пользователя"""

    filter = "my_pets"
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, results = pf.get_list_of_pets(auth_key=auth_key, filter=filter)

    assert status == 200
    count_pets = len(results['pets'])

    if count_pets != 0:
        print(f"my Pets = {len(results['pets'])}")
        print(results['pets'][0].keys())
    else:
        raise Exception("There is no my pets")


def test_add_new_pet_simple_corrected():
    """Тест на добавление нового питомца (упрощенно)"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    name = 'Pasha'
    animal_type = 'budgie'
    age = 1

    status, results = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    assert status == 200
    assert results['name'] == name


def test_add_new_pet_simple_incorrected_without_age():
    """Тест на добавление нового питомца (упрощенно) при незаполненном поле "age"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    name = 'Pasha'
    animal_type = 'budgie'
    age = None

    status, results = pf.add_new_pet_simple(auth_key, name, animal_type, age)

    assert status == 400


def test_add_new_pet():
    """Тест на добавление нового питомца (с фото)"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    name = 'Musya'
    animal_type = 'cat'
    age = '11'
    pet_photo = 'images/Musya.jpg'
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    status, results = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert results['name'] == name
    print(type(results))
    print(results)


def test_successful_delete_self_pet():
    """Тест на проверку возможности удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Korgi", "dog", "2", "images/Korgi.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Tishka', animal_type='SuperCat', age=15):
    """Тест на проверку возможности обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, results = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert results['name'] == name
    else:
        # Если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")
