# Практическая работа 3.1

## Django Web framework. Запросы и их выполнение

Проект: `practice_3_1/django_project_tran`, приложение `project_first_app` — модель автовладельцев
из практик 2.1–2.3 (копия проекта из `laboratory_work_2`).

```bash
cd practice_3_1/django_project_tran
python manage.py migrate
python manage.py seed_practice2      # данные практики 2.1
```
Запросы оформлены как management-команды, поэтому их можно запустить одной строкой:

| Задание | Команда | Файл |
| --- | --- | --- |
| 1. Создание объектов | `python manage.py practice31_task1` | `project_first_app/management/commands/practice31_task1.py` |
| 2. Фильтрация | `python manage.py practice31_task2` | `project_first_app/management/commands/practice31_task2.py` |
| 3. Агрегация и аннотация | `python manage.py practice31_task3` | `project_first_app/management/commands/practice31_task3.py` |

Добавленные `related_name`:

| Поле | related_name | Использование |
| --- | --- | --- |
| `Car.owners` (M:N through `Ownership`) | `cars` | `CarOwner.objects.filter(cars__color='Красный')` |
| `Ownership.owner` | `ownerships` | `CarOwner.objects.filter(ownerships__start_date__year=2010)` |
| `Ownership.car` | `ownerships` | `car.ownerships.all()` |
| `DriverLicense.owner` | `licenses` | `CarOwner.objects.order_by('licenses__issue_date')` |

В задании 1 автомобили добавляются владельцам через ассоциативную сущность
`Ownership.objects.create(...)`, так как у связи есть свои атрибуты (даты владения).
Через `.add()` это тоже возможно, но только с `through_defaults={'start_date': ...}`.

## Результат выполнения

```text
$ python manage.py practice31_task1
Car.objects.all():
  Lada Vesta (А001АА78), цвет: Белый
  Kia Rio (В002ВВ78), цвет: Серый
  Volkswagen Polo (С003СС78), цвет: Синий
  Skoda Octavia (Е004ЕЕ78), цвет: Чёрный
  Toyota Camry (К101КК78), цвет: Красный
  Toyota Corolla (К102КК78), цвет: Белый
  Hyundai Solaris (М201ММ78), цвет: Красный
  BMW X5 (Н301НН78), цвет: Чёрный
  Renault Logan (Р401РР78), цвет: Синий
  Lada Granta (Т501ТТ78), цвет: Серый

CarOwner.objects.filter(is_superuser=False) — владельцы, удостоверения и автомобили:
  Смирнова Анна: удостоверение 7800000001 (B — легковые автомобили); авто: Lada Vesta (А001АА78), Kia Rio (В002ВВ78), Volkswagen Polo (С003СС78), Skoda Octavia (Е004ЕЕ78)
  Петров Борис: удостоверение 7800000002 (C — грузовые автомобили); авто: Lada Vesta (А001АА78), Kia Rio (В002ВВ78), Skoda Octavia (Е004ЕЕ78)
  Иванов Олег: удостоверение 7801001111 (B — легковые автомобили); авто: Toyota Camry (К101КК78), BMW X5 (Н301НН78)
  Сидоров Олег: удостоверение 7802002222 (B — легковые автомобили); авто: Hyundai Solaris (М201ММ78)
  Кузнецова Мария: удостоверение 7803003333 (B — легковые автомобили); авто: Toyota Corolla (К102КК78), Renault Logan (Р401РР78), BMW X5 (Н301НН78)
  Попов Иван: удостоверение 7804004444 (B — легковые автомобили); авто: Lada Granta (Т501ТТ78), Toyota Corolla (К102КК78)
  Васильева Елена: удостоверение 7805005555 (B — легковые автомобили); авто: Toyota Camry (К101КК78)
  Нгуен Ван: удостоверение 7806006666 (B — легковые автомобили); авто: Renault Logan (Р401РР78), Hyundai Solaris (М201ММ78)
  Морозов Дмитрий: удостоверение 7807007777 (B — легковые автомобили); авто: Lada Granta (Т501ТТ78), BMW X5 (Н301НН78)

Всего владений: 20

$ python manage.py practice31_task2

1. Все машины марки «Toyota»
>>> Car.objects.filter(brand='Toyota')
<QuerySet [<Car: Toyota Camry (К101КК78)>, <Car: Toyota Corolla (К102КК78)>]>

2. Все водители с именем «Олег»
>>> CarOwner.objects.filter(first_name='Олег')
<QuerySet [<CarOwner: Иванов Олег>, <CarOwner: Сидоров Олег>]>

3. Случайный владелец, его id и удостоверение по этому id
>>> owner_id = CarOwner.objects.filter(licenses__isnull=False).order_by('?').first().id
>>> DriverLicense.objects.get(owner_id=owner_id)
owner = Иванов Олег, owner_id = 3
<DriverLicense: 7801001111 (B — легковые автомобили)>

4. Все владельцы красных машин
>>> CarOwner.objects.filter(cars__color='Красный').distinct()
<QuerySet [<CarOwner: Иванов Олег>, <CarOwner: Сидоров Олег>, <CarOwner: Васильева Елена>, <CarOwner: Нгуен Ван>]>

5. Владельцы, у которых владение машиной началось в 2010 году
>>> CarOwner.objects.filter(ownerships__start_date__year=2010).distinct()
<QuerySet [<CarOwner: Иванов Олег>, <CarOwner: Кузнецова Мария>, <CarOwner: Морозов Дмитрий>]>

$ python manage.py practice31_task3

1. Дата выдачи самого старшего водительского удостоверения
>>> DriverLicense.objects.aggregate(oldest=Min('issue_date'))
{'oldest': datetime.date(1996, 7, 7)}

2. Самая поздняя дата начала владения машиной модели Camry
>>> Ownership.objects.filter(car__model='Camry').aggregate(latest=Max('start_date'))
{'latest': datetime.date(2010, 2, 1)}

3. Количество машин для каждого водителя
>>> CarOwner.objects.annotate(cars_count=Count('cars'))
Смирнова Анна: 4
Петров Борис: 3
Иванов Олег: 2
Сидоров Олег: 1
Кузнецова Мария: 3
Попов Иван: 2
Васильева Елена: 1
Нгуен Ван: 2
Морозов Дмитрий: 2

4. Количество машин каждой марки
>>> Car.objects.values('brand').annotate(count=Count('id')).order_by('brand')
<QuerySet [{'brand': 'BMW', 'count': 1}, {'brand': 'Hyundai', 'count': 1}, {'brand': 'Kia', 'count': 1}, {'brand': 'Lada', 'count': 2}, {'brand': 'Renault', 'count': 1}, {'brand': 'Skoda', 'count': 1}, {'brand': 'Toyota', 'count': 2}, {'brand': 'Volkswagen', 'count': 1}]>

5. Автовладельцы, отсортированные по дате выдачи удостоверения
>>> CarOwner.objects.filter(licenses__isnull=False).order_by('licenses__issue_date').distinct()
Попов Иван: 1996-07-07
Иванов Олег: 2000-05-10
Морозов Дмитрий: 2003-04-04
Петров Борис: 2004-02-20
Кузнецова Мария: 2008-11-20
Смирнова Анна: 2009-06-15
Сидоров Олег: 2012-03-01
Васильева Елена: 2015-09-09
Нгуен Ван: 2018-01-25
```
