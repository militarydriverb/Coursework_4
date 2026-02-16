"""
Скрипт для проверки загрузки переменных окружения из .env файла
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Путь к проекту
BASE_DIR = Path(__file__).resolve().parent

# Загрузка .env
env_path = BASE_DIR / '.env'
print(f"📁 Путь к .env: {env_path}")
print(f"✅ Файл .env существует: {env_path.exists()}")
print()

# Загружаем переменные
load_dotenv(override=True)

# Список переменных для проверки
env_vars = {
    'Django настройки': [
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS',
    ],
    'База данных': [
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_PORT',
    ],
    'Email': [
        'EMAIL_BACKEND',
        'EMAIL_HOST',
        'EMAIL_PORT',
        'EMAIL_USE_TLS',
        'EMAIL_USE_SSL',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
        'DEFAULT_FROM_EMAIL',
        'SERVER_EMAIL',
    ],
    'Кеширование': [
        'CACHE_ENABLED',
        'REDIS_HOST',
    ]
}

print("=" * 80)
print("ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
print("=" * 80)
print()

all_ok = True

for category, variables in env_vars.items():
    print(f"📋 {category}:")
    print("-" * 80)

    for var in variables:
        value = os.getenv(var)

        if value is not None:
            # Скрываем чувствительные данные
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = '***' + value[-4:] if len(value) > 4 else '****'
            elif 'KEY' in var:
                display_value = value[:20] + '...' if len(value) > 20 else value
            else:
                display_value = value

            print(f"  ✅ {var:<25} = {display_value}")
        else:
            print(f"  ❌ {var:<25} = НЕ НАЙДЕНА")
            all_ok = False

    print()

print("=" * 80)

if all_ok:
    print("✅ ВСЕ ПЕРЕМЕННЫЕ ЗАГРУЖЕНЫ УСПЕШНО!")
else:
    print("❌ НЕКОТОРЫЕ ПЕРЕМЕННЫЕ НЕ НАЙДЕНЫ!")
    print("   Проверьте файл .env")

print("=" * 80)
print()

# Проверка загрузки в Django settings
print("🔧 Проверка загрузки в Django settings:")
print("-" * 80)

try:
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

    from django.conf import settings

    print(f"  ✅ SECRET_KEY загружен: {'Да' if settings.SECRET_KEY else 'Нет'}")
    print(f"  ✅ DEBUG = {settings.DEBUG}")
    print(f"  ✅ ALLOWED_HOSTS = {settings.ALLOWED_HOSTS}")
    print(f"  ✅ DB_NAME = {settings.DATABASES['default']['NAME']}")
    print(f"  ✅ DB_USER = {settings.DATABASES['default']['USER']}")
    print(f"  ✅ DB_HOST = {settings.DATABASES['default']['HOST']}")
    print(f"  ✅ EMAIL_BACKEND = {settings.EMAIL_BACKEND}")
    print(f"  ✅ EMAIL_HOST = {settings.EMAIL_HOST}")
    print(f"  ✅ CACHE_ENABLED = {settings.CACHE_ENABLED}")

    print()
    print("✅ Django settings загружены корректно!")

except Exception as e:
    print(f"  ❌ Ошибка загрузки Django settings: {e}")

print("=" * 80)
